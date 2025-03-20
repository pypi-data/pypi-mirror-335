import json
import logging
import os
import traceback
import pandas as pd

from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    getNEMOStepsFrompAMigrationStatusFile,
    getProjectName,
    load_database,
)

__all__ = ["MigManPrecheckFiles"]


def MigManPrecheckFiles(config: Config) -> None:

    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()

    # if there is a status file given, we ignore the given projects and get the project list from the status file
    proALPHA_project_status_file = config.get_migman_proALPHA_project_status_file()
    if proALPHA_project_status_file:
        projects = getNEMOStepsFrompAMigrationStatusFile(proALPHA_project_status_file)
    else:
        projects = config.get_migman_projects()

    dbdf = load_database()
    status = {}
    for project in projects:

        try:
            # check for project in database
            filtereddbdf = dbdf[dbdf["project_name"] == project]
            if filtereddbdf.empty:
                raise ValueError(f"project '{project}' not found in database")

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
                        _check_data(
                            config,
                            dbdf,
                            local_project_directory,
                            project,
                            addon,
                            postfix,
                        )
            else:
                for postfix in postfixes:
                    _check_data(
                        config, dbdf, local_project_directory, project, None, postfix
                    )

            status[project] = "ok"

        except Exception as e:
            status[project] = str(e) #traceback.format_exc()
            continue

    for project in projects:
        logging.info(
            f"status of project {project}: {json.dumps(status[project],indent=4)}"
        )


def _check_data(
    config: Config,
    dbdf: pd.DataFrame,
    local_project_directory: str,
    project: str,
    addon: str,
    postfix: str,
) -> None:

    # check for file first
    project_name = getProjectName(project, addon, postfix)
    file_name = os.path.join(
        local_project_directory,
        "srcdata",
        f"{project_name}.csv",
    )

    if os.path.exists(file_name):

        # read the file now and check the fields that are filled in that file
        datadf = pd.read_csv(
            file_name,
            sep=";",
            dtype=str,
        )

        # drop all columns that are totally empty
        columns_to_drop = datadf.columns[datadf.isna().all()]
        datadf_cleaned = datadf.drop(columns=columns_to_drop)

        dbdf = dbdf[(dbdf["project_name"] == project) & (dbdf["postfix"] == postfix)]
        columns_migman = dbdf["import_name"].to_list()

        for col in datadf_cleaned.columns:
            if not col in columns_migman:
                raise ValueError(
                    f"file {file_name} contains column '{col}' that is not defined in MigMan Template"
                )
