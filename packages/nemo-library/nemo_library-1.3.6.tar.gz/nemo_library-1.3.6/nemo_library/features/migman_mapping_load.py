import logging
import os
import pandas as pd
from nemo_library.features.nemo_persistence_api import createReports
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.model.report import Report
from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadFile
from nemo_library.utils.migmanutils import (
    getMappingFilePath,
    getMappingRelations,
    sqlQueryInMappingTable,
)

__all__ = ["MigManLoadMapping"]


def MigManLoadMapping(config: Config):

    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    mapping_fields = config.get_migman_mapping_fields()
    mappingrelationsdf = getMappingRelations(config=config)

    # iterate every given field upload data
    for field in mapping_fields:

        logging.info(f"working on mapping field {field}...")

        # check for mapping file
        projectname = f"Mapping {field}"
        file_path = getMappingFilePath(projectname, local_project_directory)
        logging.info(f"checking for data file {file_path}")

        if os.path.exists(file_path):
            ReUploadFile(
                config=config,
                projectname=projectname,
                filename=file_path,
                update_project_settings=False,
            )
            logging.info(f"upload to project {projectname} completed")

        # maybe the source data have been updated, so we update our mapping data now
        # sequence is important, we first have to upload the file that was given (see above)
        # since we are now going to overwrite the file with fresh data now

        mappingrelationsdf_filtered = mappingrelationsdf[
            mappingrelationsdf["mapping_field"] == field
        ]

        # collect data
        collectData(
            config=config,
            projectname=projectname,
            field=field,
            mappingrelationsdf=mappingrelationsdf_filtered,
            local_project_directory=local_project_directory,
        )


def collectData(
    config: Config,
    projectname: str,
    field: str,
    mappingrelationsdf: pd.DataFrame,
    local_project_directory: str,
):

    queryforreport = sqlQueryInMappingTable(
        config=config,
        field=field,
        newProject=False,
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
        config=config, projectname=projectname, report_name="source mapping"
    )

    file_path = getMappingFilePath(projectname, local_project_directory)

    # export file as a template for mappings
    df.to_csv(
        file_path,
        index=False,
        sep=";",
        na_rep="",
    )

    # and upload it immediately
    ReUploadFile(
        config=config,
        projectname=projectname,
        filename=file_path,
        update_project_settings=False,
    )
    logging.info(f"upload to project {projectname} completed")
