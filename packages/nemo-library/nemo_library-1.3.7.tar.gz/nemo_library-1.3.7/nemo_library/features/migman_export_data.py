import logging
import os
from nemo_library.features.nemo_persistence_api import getProjects
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    getNEMOStepsFrompAMigrationStatusFile,
    getProjectName,
    load_database,
)
from nemo_library.utils.utils import log_error

__all__ = ["MigManExportData"]


def MigManExportData(config: Config) -> None:

    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()

    # if there is a status file given, we ignore the given projects and get the project list from the status file
    proALPHA_project_status_file = config.get_migman_proALPHA_project_status_file()
    if proALPHA_project_status_file:
        projects = getNEMOStepsFrompAMigrationStatusFile(proALPHA_project_status_file)
    else:
        projects = config.get_migman_projects()

    project_list_nemo = [project.displayName for project in getProjects(config)]

    dbdf = load_database()
    for project in projects:

        # check for project in database
        filtereddbdf = dbdf[dbdf["project_name"] == project]
        if filtereddbdf.empty:
            log_error(f"project '{project}' not found in database")

        # get list of postfixes
        postfixes = filtereddbdf["postfix"].unique().tolist()

        # init project
        multi_projects_list = (
            (multi_projects[project] if project in multi_projects else None)
            if multi_projects
            else None
        )
        if multi_projects_list:
            for addon in multi_projects_list:
                for postfix in postfixes:
                    _export_data(
                        config,
                        local_project_directory,
                        project_list_nemo,
                        project,
                        addon,
                        postfix,
                    )
        else:
            for postfix in postfixes:
                _export_data(
                    config,
                    local_project_directory,
                    project_list_nemo,
                    project,
                    None,
                    postfix,
                )


def _export_data(
    config: Config,
    local_project_directory: str,
    project_list_nemo: list[str],
    project: str,
    addon: str,
    postfix: str,
) -> None:

    # export reports
    data = [
        ("to_customer", "_with_messages", "(Customer) All records with message"),
        ("to_proalpha", "", "(MigMan) All records with no message"),
    ]
    project_name = getProjectName(project, addon, postfix)

    if project_name not in project_list_nemo:
        logging.info(
            f"Project '{project_name}' not available in NEMO. No data exported"
        )
        return

    for folder, file_postfix, report_name in data:

        logging.info(
            f"Exporting '{project}', addon '{addon}', postfix '{postfix}', report name: '{report_name}' to '{folder}'"
        )
        file_name = os.path.join(
            local_project_directory,
            folder,
            f"{project_name}{file_postfix}.csv",
        )
        df = LoadReport(
            config=config,
            projectname=project_name,
            report_name=report_name,
        )
        df.to_csv(
            file_name,
            index=False,
            sep=";",
            encoding="UTF-8",
        )

        logging.info(
            f"File '{file_name}' for '{project}', addon '{addon}', postfix '{postfix}' exported '{report_name}'"
        )
