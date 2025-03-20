from collections import defaultdict
import copy
from dataclasses import fields, is_dataclass
import json
import logging
from pathlib import Path
import re
import pandas as pd
from typing import Optional, Type, TypeVar, List, Dict
from nemo_library.features.focus import focusMoveAttributeBefore
from nemo_library.features.nemo_persistence_api import (
    _deserializeMetaDataObject,
    createApplications,
    createAttributeGroups,
    createDefinedColumns,
    createDiagrams,
    createMetrics,
    createPages,
    createReports,
    createRules,
    createSubProcesses,
    createTiles,
    deleteApplications,
    deleteAttributeGroups,
    deleteDefinedColumns,
    deleteDiagrams,
    deleteMetrics,
    deletePages,
    deleteReports,
    deleteRules,
    deleteSubprocesses,
    deleteTiles,
    getApplications,
    getAttributeGroups,
    getDefinedColumns,
    getDiagrams,
    getImportedColumns,
    getMetrics,
    getPages,
    getRules,
    getSubProcesses,
    getTiles,
)
from nemo_library.features.nemo_persistence_api import (
    getDependencyTree,
)
from nemo_library.features.nemo_persistence_api import (
    getReports,
)
from nemo_library.model.application import Application
from nemo_library.model.attribute_group import AttributeGroup
from nemo_library.model.defined_column import DefinedColumn
from nemo_library.model.dependency_tree import DependencyTree
from nemo_library.model.diagram import Diagram
from nemo_library.model.imported_column import ImportedColumn
from nemo_library.model.metric import Metric
from nemo_library.model.pages import Page
from nemo_library.model.report import Report
from nemo_library.model.rule import Rule
from nemo_library.model.tile import Tile
from nemo_library.model.subprocess import SubProcess
from nemo_library.utils.config import Config
from nemo_library.utils.utils import FilterType, FilterValue, log_error

__all__ = ["MetaDataLoad", "MetaDataCreate"]

T = TypeVar("T")


def MetaDataLoad(config: Config, projectname: str, prefix: str) -> None:

    functions = {
        "applications": getApplications,
        "attributegroups": getAttributeGroups,
        "definedcolumns": getDefinedColumns,
        "diagrams": getDiagrams,
        "metrics": getMetrics,
        "pages": getPages,
        "reports": getReports,
        "rules": getRules,
    }

    for name, func in functions.items():
        logging.info(f"load {name} from NEMO")
        data = func(
            config=config,
            projectname=projectname,
            filter=prefix,
            filter_type=FilterType.STARTSWITH,
            filter_value=FilterValue.DISPLAYNAME,
        )

        _export_data_to_json(config, name, data)


def MetaDataDelete(config: Config, projectname: str, prefix: str) -> None:

    get_functions = {
        "applications": getApplications,
        "attributegroups": getAttributeGroups,
        "definedcolumns": getDefinedColumns,
        "diagrams": getDiagrams,
        "metrics": getMetrics,
        "pages": getPages,
        "reports": getReports,
        "rules": getRules,
    }

    delete_functions = {
        "applications": deleteApplications,
        "pages": deletePages,
        "tiles": deleteTiles,
        "metrics": deleteMetrics,
        "definedcolumns": deleteDefinedColumns,
        "attributegroups": deleteAttributeGroups,
        "diagrams": deleteDiagrams,
        "reports": deleteReports,
        "rules": deleteRules,
    }

    for name, func in get_functions.items():
        logging.info(f"delete {name} from NEMO")
        data = func(
            config=config,
            projectname=projectname,
            filter=prefix,
            filter_type=FilterType.STARTSWITH,
            filter_value=FilterValue.DISPLAYNAME,
        )

        objects_to_delete = [obj.id for obj in data]

        delete_functions[name](config=config, **{name: objects_to_delete})


def MetaDataCreate(config: Config, projectname: str, prefix: str) -> None:

    # load data from model (JSON)
    logging.info(f"load model from JSON files in folder {config.get_metadata()}")
    applications_model = _load_data_from_json(config, "applications", Application)
    attributegroups_model = _load_data_from_json(
        config, "attributegroups", AttributeGroup
    )
    definedcolumns_model = _load_data_from_json(config, "definedcolumns", DefinedColumn)
    diagrams_model = _load_data_from_json(config, "diagrams", Diagram)
    metrics_model = _load_data_from_json(config, "metrics", Metric)
    pages_model = _load_data_from_json(config, "pages", Page)
    reports_model = _load_data_from_json(config, "reports", Report)
    rules_model = _load_data_from_json(config, "rules", Rule)

    # generate objects based on modell
    tiles_model = []  # _generate_tiles(metrics_model) # no more tiles

    # sort attribute groups
    hierarchy, _ = _attribute_groups_build_hierarchy(attributegroups_model)
    attributegroups_model = attribute_groups_sort_hierarchy(hierarchy, root_key=None)

    # load data from NEMO
    logging.info(
        f"load model from NEMO files from project {projectname}, prefix {prefix}"
    )
    applications_nemo = _fetch_data_from_nemo(
        config, projectname, getApplications, prefix
    )
    attributegroups_nemo = _fetch_data_from_nemo(
        config, projectname, getAttributeGroups, prefix
    )
    definedcolumns_nemo = _fetch_data_from_nemo(
        config, projectname, getDefinedColumns, prefix
    )
    diagrams_nemo = _fetch_data_from_nemo(config, projectname, getDiagrams, prefix)
    metrics_nemo = _fetch_data_from_nemo(config, projectname, getMetrics, prefix)
    pages_nemo = _fetch_data_from_nemo(config, projectname, getPages, prefix)
    reports_nemo = _fetch_data_from_nemo(config, projectname, getReports, prefix)
    tiles_nemo = _fetch_data_from_nemo(config, projectname, getTiles, prefix)
    rules_nemo = _fetch_data_from_nemo(config, projectname, getRules, prefix)

    # reconcile data
    deletions: Dict[str, List[T]] = {}
    updates: Dict[str, List[T]] = {}
    creates: Dict[str, List[T]] = {}

    logging.info(f"reconcile both models")
    for key, model_list, nemo_list in [
        ("applications", applications_model, applications_nemo),
        ("attributegroups", attributegroups_model, attributegroups_nemo),
        ("definedcolumns", definedcolumns_model, definedcolumns_nemo),
        ("diagrams", diagrams_model, diagrams_nemo),
        ("metrics", metrics_model, metrics_nemo),
        ("pages", pages_model, pages_nemo),
        ("reports", reports_model, reports_nemo),
        ("tiles", tiles_model, tiles_nemo),
        ("rules", rules_model, rules_nemo),
    ]:
        nemo_list_cleaned = copy.deepcopy(nemo_list)
        nemo_list_cleaned = _clean_fields(nemo_list_cleaned)

        deletions[key] = _find_deletions(model_list, nemo_list)
        updates[key] = _find_updates(model_list, nemo_list_cleaned)
        creates[key] = _find_new_objects(model_list, nemo_list)

    # Start with deletions
    logging.info(f"start deletions")
    delete_functions = {
        "applications": deleteApplications,
        "pages": deletePages,
        "tiles": deleteTiles,
        "metrics": deleteMetrics,
        "definedcolumns": deleteDefinedColumns,
        "attributegroups": deleteAttributeGroups,
        "diagrams": deleteDiagrams,
        "rules": deleteRules,
        "reports": deleteReports,
    }

    for key, delete_function in delete_functions.items():
        if deletions[key]:
            objects_to_delete = [data_nemo.id for data_nemo in deletions[key]]
            delete_function(config=config, **{key: objects_to_delete})

    # Now do updates and creates in a reverse  order
    logging.info(f"start creates and updates")
    create_functions = {
        "reports": createReports,
        "rules": createRules,
        "diagrams": createDiagrams,
        "attributegroups": createAttributeGroups,
        "definedcolumns": createDefinedColumns,
        "metrics": createMetrics,
        "tiles": createTiles,
        "pages": createPages,
        "applications": createApplications,
    }

    for key, create_function in create_functions.items():
        # create new objects first
        if creates[key]:
            create_function(
                config=config, projectname=projectname, **{key: creates[key]}
            )
        # now the changes
        if updates[key]:
            create_function(
                config=config, projectname=projectname, **{key: updates[key]}
            )

    # sub processes and focus order depends on dependency tree for objects
    # refresh data from server
    logging.info(f"get dependency tree for metrics")
    metrics_nemo = _fetch_data_from_nemo(config, projectname, getMetrics, prefix)
    attributegroups_nemo = _fetch_data_from_nemo(
        config, projectname, getAttributeGroups, prefix
    )
    ics = getImportedColumns(config, projectname)

    metric_lookup = {metric.internalName: metric for metric in metrics_nemo}
    dependency_tree = {
        metric.internalName: list(set(_collect_node_internal_names(d)))
        for metric in metrics_nemo
        if (d := getDependencyTree(config=config, id=metric.id)) is not None
    }

    # reconcile focus order now
    logging.info(f"reconcile order in focus")

    # move global attribute to top
    focusMoveAttributeBefore(
        config=config, projectname=projectname, sourceInternalName="conservative_global"
    )

    # now move the other ones
    for metric_internal_name, values in dependency_tree.items():
        ics_metric = [ic for ic in ics if ic.internalName in values]
        for ic in ics_metric:
            if (
                ic.parentAttributeGroupInternalName
                != metric_lookup[metric_internal_name].parentAttributeGroupInternalName
            ):

                # special case: we have the restriction, that we cannot have linked attributes and
                # thus some fields might be in different groups. We don't want to move them now
                # we
                if ic.parentAttributeGroupInternalName not in [
                    ag.internalName for ag in attributegroups_nemo
                ]:
                    logging.info(
                        f"move: {ic.internalName} from group {ic.parentAttributeGroupInternalName} to {metric_lookup[metric_internal_name].parentAttributeGroupInternalName}"
                    )
                    focusMoveAttributeBefore(
                        config=config,
                        projectname=projectname,
                        sourceInternalName=ic.internalName,
                        groupInternalName=metric_lookup[
                            metric_internal_name
                        ].parentAttributeGroupInternalName,
                    )

    # generate sub processes
    logging.info(f"generate sub processes")
    subprocesses_nemo = _fetch_data_from_nemo(
        config, projectname, getSubProcesses, prefix
    )
    subprocesses_model = [
        SubProcess(
            columnInternalNames=_date_columns(values, ics),
            description=metric_lookup[metric_internal_name].description,
            descriptionTranslations=metric_lookup[
                metric_internal_name
            ].descriptionTranslations,
            displayName=metric_lookup[metric_internal_name].displayName,
            displayNameTranslations=metric_lookup[
                metric_internal_name
            ].displayNameTranslations,
            groupByAggregations={},
            groupByColumn="",
            internalName=metric_lookup[metric_internal_name].internalName,
            isAggregation=False,
            timeUnit="days",
            id="",
            projectId="",
            tenant="",
        )
        for (
            metric_internal_name,
            values,
        ) in dependency_tree.items()
        if len(_date_columns(values, ics)) > 1
    ]

    # reconcile data
    deletions: Dict[str, List[T]] = {}
    updates: Dict[str, List[T]] = {}
    creates: Dict[str, List[T]] = {}

    for key, model_list, nemo_list in [
        ("subprocesses", subprocesses_model, subprocesses_nemo),
    ]:
        nemo_list_cleaned = copy.deepcopy(nemo_list)
        nemo_list_cleaned = _clean_fields(nemo_list_cleaned)

        deletions[key] = _find_deletions(model_list, nemo_list)
        updates[key] = _find_updates(model_list, nemo_list_cleaned)
        creates[key] = _find_new_objects(model_list, nemo_list)

    # Start with deletions
    delete_functions = {
        "subprocesses": deleteSubprocesses,
    }

    for key, delete_function in delete_functions.items():
        if deletions[key]:
            objects_to_delete = [data_nemo.id for data_nemo in deletions[key]]
            delete_function(config=config, **{key: objects_to_delete})

    # Now do updates and creates in a reverse  order
    create_functions = {
        "subprocesses": createSubProcesses,
    }

    for key, create_function in create_functions.items():
        # create new objects first
        if creates[key]:
            create_function(
                config=config, projectname=projectname, **{key: creates[key]}
            )
        # now the changes
        if updates[key]:
            create_function(
                config=config, projectname=projectname, **{key: updates[key]}
            )


def _date_columns(
    columns: List[str], imported_columns: List[ImportedColumn]
) -> List[str]:
    date_cols = []
    for col in columns:
        ic = None
        for ic_search in imported_columns:
            if ic_search.internalName == col:
                ic = ic_search

        if ic and ic.dataType == "date":
            date_cols.append(col)

    return date_cols


def _collect_node_internal_names(tree: DependencyTree) -> List[str]:
    names = [tree.nodeInternalName]
    for dep in tree.dependencies:
        names.extend(_collect_node_internal_names(dep))
    return names


def _attribute_groups_build_hierarchy(attribute_groups):
    hierarchy = defaultdict(list)
    group_dict = {group.internalName: group for group in attribute_groups}

    for group in attribute_groups:
        parent_name = group.parentAttributeGroupInternalName
        hierarchy[parent_name].append(group)

    return hierarchy, group_dict


def attribute_groups_sort_hierarchy(hierarchy, root_key=None):
    sorted_list = []

    def add_children(parent):
        for child in sorted(hierarchy.get(parent, []), key=lambda x: x.displayName):
            sorted_list.append(child)
            add_children(child.internalName)

    add_children(root_key)
    return sorted_list


def _fetch_data_from_nemo(config: Config, projectname: str, func, prefix: str):
    return func(
        config=config,
        projectname=projectname,
        filter=prefix,
        filter_type=FilterType.STARTSWITH,
    )


def _load_data_from_json(config, file: str, cls: Type[T]) -> List[T]:
    """
    Loads JSON data from a file and converts it into a list of DataClass instances,
    handling nested structures recursively.
    """
    path = Path(config.get_metadata()) / f"{file}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [_deserializeMetaDataObject(item, cls) for item in data]


def _generate_tiles(metrics: List[Metric]) -> List[Tile]:
    tiles = [
        Tile(
            aggregation="Mean",
            description=f"Tile for metric {metric.displayName}",
            descriptionTranslations={},
            displayName=metric.displayName,
            displayNameTranslations={},
            frequency="Month",
            graphic="",
            internalName=metric.internalName,
            status="Mandatory",
            tileGroup="",
            tileGroupTranslations={},
            tileSourceID=metric.id,
            tileSourceInternalName=metric.internalName,
            type="Metric",
            unit="",
            id="",
            projectId="",
            tenant="",
        )
        for metric in metrics
    ]

    return tiles


def _find_deletions(model_list: List[T], nemo_list: List[T]) -> List[T]:
    model_keys = {obj.internalName for obj in model_list}
    return [obj for obj in nemo_list if obj.internalName not in model_keys]


def _find_updates(model_list: List[T], nemo_list: List[T]) -> List[T]:
    updates = []
    nemo_dict = {getattr(obj, "internalName"): obj for obj in nemo_list}
    for model_obj in model_list:
        key = getattr(model_obj, "internalName")
        if key in nemo_dict:
            nemo_obj = nemo_dict[key]
            if is_dataclass(model_obj) and is_dataclass(nemo_obj):
                differences = {
                    attr.name: (
                        getattr(model_obj, attr.name),
                        getattr(nemo_obj, attr.name),
                    )
                    for attr in fields(model_obj)
                    if getattr(model_obj, attr.name) != getattr(nemo_obj, attr.name)
                }

            if differences:
                for attrname, (new_value, old_value) in differences.items():
                    logging.info(f"{attrname}: {old_value} --> {new_value}")
                updates.append(model_obj)

    return updates


def _find_new_objects(model_list: List[T], nemo_list: List[T]) -> List[T]:
    nemo_keys = {getattr(obj, "internalName") for obj in nemo_list}
    return [obj for obj in model_list if getattr(obj, "internalName") not in nemo_keys]


def _export_data_to_json(config: Config, file: str, data):
    data = _clean_fields(data)
    path = Path(config.get_metadata()) / f"{file}.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            [element.to_dict() for element in data], file, indent=4, ensure_ascii=True
        )


def _clean_fields(data):
    for element in data:
        element.id = ""
        element.tenant = ""
        element.projectId = ""
        element.tileSourceID = ""
        element.focusOrder = ""

        if isinstance(element, Diagram):
            for value in element.values:
                value.id = ""

        elif isinstance(element, Page):
            for visual in element.visuals:
                visual.id = ""

    return data


def _extract_fields(formulas_dict):
    field_pattern = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")

    extracted_fields = {}

    for key, formulas in formulas_dict.items():
        extracted_fields[key] = set()
        for formula in formulas:
            if isinstance(formula, str) and formula.strip():
                fields = field_pattern.findall(formula)
                extracted_fields[key].update(fields)

    return {k: sorted(v) for k, v in extracted_fields.items()}
