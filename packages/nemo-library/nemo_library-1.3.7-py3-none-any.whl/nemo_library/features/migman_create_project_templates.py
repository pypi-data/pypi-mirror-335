import logging
import os
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    getNEMOStepsFrompAMigrationStatusFile,
    initializeFolderStructure,
    load_database,
)
from nemo_library.utils.utils import log_error
import pandas as pd


__all__ = ["MigManCreateProjectTemplates"]


def MigManCreateProjectTemplates(config: Config) -> None:

    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()

    # if there is a status file given, we ignore the given projects and get the project list from the status file
    proALPHA_project_status_file = config.get_migman_proALPHA_project_status_file()
    if proALPHA_project_status_file:
        projects = getNEMOStepsFrompAMigrationStatusFile(proALPHA_project_status_file)
    else:
        projects = config.get_migman_projects()

    # initialize project folder structure
    initializeFolderStructure(local_project_directory)

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
                    _create_project_template_file(
                        dbdf, local_project_directory, project, addon, postfix
                    )
        else:
            for postfix in postfixes:
                _create_project_template_file(
                    dbdf, local_project_directory, project, None, postfix
                )


def _create_project_template_file(
    dbdf: pd.DataFrame,
    local_project_directory: str,
    project: str,
    addon: str,
    postfix: str,
) -> None:

    logging.info(
        f"Create project template file for '{project}', addon '{addon}', postfix '{postfix}'"
    )

    dbdf = dbdf[(dbdf["project_name"] == project) & (dbdf["postfix"] == postfix)]
    columns = dbdf["import_name"].to_list()
    data = {col: [""] for col in columns}
    templatedf = pd.DataFrame(data=data, columns=columns)
    templatedf.to_csv(
        os.path.join(
            local_project_directory,
            "templates",
            f"{project}{" " + addon if addon else ""}{(" (" + postfix + ")") if postfix else ""}.csv",
        ),
        index=False,
        sep=";",
        encoding="UTF-8",
    )
