import importlib
import logging
import re
from typing import Tuple
import pandas as pd
from nemo_library.utils.utils import (
    get_display_name,
    get_import_name,
    get_internal_name,
)

__all__ = ["MigManInitDatabase"]


def MigManInitDatabase() -> None:
    dfs = []
    for resource in importlib.resources.contents(
        "nemo_library.templates.migmantemplates"
    ):
        dfs.append(_process_file(resource))

    databasedf = pd.concat(dfs)
    databasedf.to_pickle("./nemo_library/templates/migmantemplates.pkl")


def _process_file(resource: str) -> pd.DataFrame:

    # strip project name and postfix from file name
    project, postfix = _extract_project_and_postfix(resource)
    logging.info(
        f"Processing file '{resource}' for project '{project}' with postfix '{postfix}'"
    )

    # load dummy headers from first line
    dummyheaders = _import_dummy_header(resource)
    dfdesc = _import_datadescription(resource, dummyheaders)
    df = _add_calculated_fields(dfdesc, project, postfix)
    return df


def _extract_project_and_postfix(resource: str) -> Tuple[str, str]:
    """
    Extracts the project name and postfix from the given resource string.

    Args:
        resource (str): The resource string (e.g., filename).

    Returns:
        tuple: A tuple containing the project name and postfix, or None if the pattern does not match.
    """
    pattern = re.compile(
        r"^Template (?P<project>.*?) (?P<postfix>MAIN|Add\d+)\.csv$", re.IGNORECASE
    )
    match = pattern.match(resource)
    if match:
        return match.group("project"), match.group("postfix")
    else:
        logging.error(f"filename '{resource}' does not match expected pattern")
        return None, None


def _import_dummy_header(resource: str) -> pd.DataFrame:
    with importlib.resources.open_binary(
        "nemo_library.templates.migmantemplates", resource
    ) as file:

        dfdummy = pd.read_csv(
            file,
            nrows=1,
            encoding="ISO-8859-1",
            sep=";",
        )

    dummyheaders = dfdummy.columns
    return dummyheaders


def _import_datadescription(resource: str, dummyheaders: pd.DataFrame) -> pd.DataFrame:
    with importlib.resources.open_binary(
        "nemo_library.templates.migmantemplates", resource
    ) as file:
        dfdesc = pd.read_csv(
            file,
            skiprows=2,
            encoding="ISO-8859-1",
            sep=";",
        )
    dfdesc["migman_header_label"] = dummyheaders

    dfdesc["Format"] = dfdesc["Data Type"]
    dfdesc["Data Type"] = dfdesc["Location in proALPHA"]
    dfdesc["Location in proALPHA"] = dfdesc["Description / Remark"]
    dfdesc.drop(columns=["Description / Remark"], inplace=True)

    dfdesc.loc[dfdesc["Location in proALPHA"].isna(), "Location in proALPHA"] = dfdesc[
        "migman_header_label"
    ]
    dfdesc.loc[dfdesc["Column Name"].isna(), "Column Name"] = dfdesc["Column"]
    dfdesc.loc[dfdesc["Data Type"].isna(), "Data Type"] = "CHARACTER"
    dfdesc.loc[dfdesc["Format"].isna(), "Format"] = "x(20)"
    return dfdesc


def _add_calculated_fields(
    dfdesc: pd.DataFrame, project: str, postfix: str
) -> pd.DataFrame:
    dfdesc["project_name"] = project
    dfdesc["postfix"] = postfix if postfix != "MAIN" else ""
    dfdesc["display_name"] = dfdesc.apply(
        lambda row: get_display_name(row["Location in proALPHA"], row.name), axis=1
    )
    dfdesc["internal_name"] = dfdesc.apply(
        lambda row: get_internal_name(row["Location in proALPHA"], row.name), axis=1
    )
    dfdesc["import_name"] = dfdesc.apply(
        lambda row: get_import_name(row["Location in proALPHA"], row.name), axis=1
    )
    return dfdesc
