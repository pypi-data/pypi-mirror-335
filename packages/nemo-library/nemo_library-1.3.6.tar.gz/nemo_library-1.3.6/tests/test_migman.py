import os
import shutil
import pytest


from nemo_library import NemoLibrary


def getNL():
    return NemoLibrary(
        config_file="tests/config.ini",
    )


def test_clean():
    nl = getNL()
    projects = nl.getProjects()
    project_map = {project.displayName: project.id for project in projects}
    delete = []
    for project in nl.config.get_migman_projects():
        if project in project_map:
            delete.append(project_map[project])
        
    for mapping in nl.config.get_migman_mapping_fields():
        if f"Mapping {mapping}" in project_map:
            delete.append(project_map[f"Mapping {mapping}"])

    if delete:
        nl.deleteProjects(delete)
    
def test_MigManCreateProjectTemplates():
    nl = getNL()
    test_dir = nl.config.get_migman_local_project_directory()
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    assert not os.path.exists(test_dir)

    nl.MigManCreateProjectTemplates()

    assert os.path.exists(test_dir)


def test_MigManLoadData():
    nl = getNL()
    shutil.copy(
        "./tests/migman_master/CUSTOMERS.csv",
        os.path.join(nl.config.get_migman_local_project_directory(), "srcdata"),
    )
    shutil.copy(
        "./tests/migman_master/Ship-To Addresses (Customers).csv",
        os.path.join(nl.config.get_migman_local_project_directory(), "srcdata"),
    )
    nl.MigManLoadData()


def test_MigManCreateMapping():
    nl = getNL()
    nl.MigManCreateMapping()

def test_MigManLoadMapping():
    nl = getNL()
    nl.MigManLoadMapping()

def test_MigManApplyMapping():
    nl = getNL()
    nl.MigManApplyMapping()

def test_MigManExportData():
    nl = getNL()
    nl.MigManExportData()
    assert os.path.exists(
        os.path.join(
            nl.config.get_migman_local_project_directory(),
            "to_customer",
            "Customers_with_messages.csv",
        )
    )
    assert os.path.exists(
        os.path.join(
            nl.config.get_migman_local_project_directory(),
            "to_proalpha",
            "Customers.csv",
        )
    )


def test_final():
    nl = getNL()
    test_dir = nl.config.get_migman_local_project_directory()
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    projects = nl.getProjects()
    project_map = {project.displayName: project.id for project in projects}
    delete = []
    for project in nl.config.get_migman_projects():
        delete.append(project_map[project])
        
    for mapping in nl.config.get_migman_mapping_fields():
        delete.append(project_map[f"Mapping {mapping}"])
        
    nl.deleteProjects(delete)
