import os
import shutil
import pytest


from nemo_library import NemoLibrary


def getNL():
    return NemoLibrary(
        config_file="tests/config.ini",
    )

def test_createOrUpdateRulesByConfigFile():
    nl = getNL( )
    nl.createOrUpdateRulesByConfigFile("./tests/NEMO_RULE_CONFIGURATION.xlsx")