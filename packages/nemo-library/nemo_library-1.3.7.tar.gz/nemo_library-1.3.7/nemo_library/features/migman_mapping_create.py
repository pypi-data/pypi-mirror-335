import logging
import pandas as pd
from nemo_library.features.nemo_persistence_api import (
    createImportedColumns,
    createReports,
    getImportedColumns,
    getProjects,
)
from nemo_library.features.nemo_persistence_api import createProjects
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.model.imported_column import ImportedColumn
from nemo_library.model.project import Project
from nemo_library.model.report import Report
from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadFile
from nemo_library.features.focus import focusCoupleAttributes
from nemo_library.utils.migmanutils import (
    getMappingFilePath,
    getMappingRelations,
    sqlQueryInMappingTable,
)
from nemo_library.utils.utils import (
    get_display_name,
)

__all__ = ["MigManCreateMapping"]


def MigManCreateMapping(config: Config):

    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    mapping_fields = config.get_migman_mapping_fields()
    additional_fields = config.get_migman_additional_fields()
    mappingrelationsdf = getMappingRelations(config=config)

    # get all projects
    projects_display_names = [project.displayName for project in getProjects(config)]

    # iterate every given field and check whether to create the appropriate project and upload data
    for field in mapping_fields:

        logging.info(f"working on mapping field {field}...")

        mappingrelationsdf_filtered = mappingrelationsdf[
            mappingrelationsdf["mapping_field"] == field
        ]

        # if project does not exist, create it
        projectname = f"Mapping {field}"
        if not projectname in projects_display_names:

            # create project
            createMappingProject(config=config, field=field, projectname=projectname)

            # create fields
            createMappingImportedColumnns(
                config=config,
                projectname=projectname,
                field=field,
                additional_fields=additional_fields,
            )

            # collect data and fill template
            loadData(
                config=config,
                projectname=projectname,
                field=field,
                mappingrelationsdf=mappingrelationsdf_filtered,
                local_project_directory=local_project_directory,
            )

            # couple attributes in focus
            coupleAttributes(config=config, projectname=projectname)

        else:
            logging.info(f"project {projectname} found.")


def createMappingProject(
    config: Config,
    projectname: str,
    field: str,
) -> str:
    """
    Creates a mapping project for a specific field if it does not already exist.

    This function checks if a project with the name "Mapping {field}" exists in the system.
    If it does not exist, it creates the project with a description. The function then
    returns the name of the project.

    Args:
        config (Config): Configuration object containing authentication and system settings.
        field (str): The name of the field for which the mapping project is to be created.

    Returns:
        str: The name of the mapping project.
    """

    logging.info(f"'{projectname}' not found, create it")
    createProjects(
        config=config,
        projects=[
            Project(displayName=projectname, description=f"Mapping for field '{field}'")
        ],
    )


def createMappingImportedColumnns(
    config: Config,
    projectname: str,
    field: str,
    additional_fields: dict[str, list[str]],
) -> dict[str, str]:

    fields = []

    additionalfields_filtered = (
        additional_fields[field]
        if additional_fields and field in additional_fields
        else None
    )
    if additionalfields_filtered:
        for additionalField in additionalfields_filtered:
            fields.append(get_display_name(f"source {additionalField}"))
    fields.append(get_display_name(f"source {field}"))
    fields.append(get_display_name(f"target {field}"))

    ics = getImportedColumns(config=config, projectname=projectname)
    ics_display_name = [ic.displayName for ic in ics]

    new_columns = []
    for idx, fld in enumerate(fields):
        if not fld in ics_display_name:
            new_columns.append(
                ImportedColumn(
                    displayName=fld,
                    dataType="string",
                    focusOrder=f"{idx:03}",
                )
            )

    if new_columns:
        createImportedColumns(
            config=config,
            projectname=projectname,
            importedcolumns=new_columns,
        )


def loadData(
    config: Config,
    projectname: str,
    field: str,
    mappingrelationsdf: pd.DataFrame,
    local_project_directory: str,
) -> None:

    queryforreport = sqlQueryInMappingTable(
        config=config,
        field=field,
        newProject=True,
        mappingrelationsdf=mappingrelationsdf,
    )

    createReports(
        config=config,
        projectname=projectname,
        reports=[
            Report(
                displayName="source mapping",
                querySyntax=queryforreport,
                description="load all source values and map them",
            )
        ],
    )

    df = LoadReport(
        config=config,
        projectname=projectname,
        report_name="source mapping",
    )

    # export file as a template for mappings
    file_path = getMappingFilePath(projectname, local_project_directory)
    df.to_csv(
        file_path,
        index=False,
        sep=";",
        na_rep="",
    )
    logging.info(f"mapping file '{file_path}' generated with source contents")

    # and upload it immediately
    ReUploadFile(
        config=config,
        projectname=projectname,
        filename=file_path,
        update_project_settings=False,
    )
    logging.info(f"upload to project {projectname} completed")


def coupleAttributes(
    config: Config,
    projectname: str,
) -> None:

    ics = getImportedColumns(
        config=config,
        projectname=projectname,
    )
    ics_display_name = [ic.displayName for ic in ics]
    focusCoupleAttributes(
        config=config,
        projectname=projectname,
        attributenames=ics_display_name,
        previous_attribute=None,
    )
