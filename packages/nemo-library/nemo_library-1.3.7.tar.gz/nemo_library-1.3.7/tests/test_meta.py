import pytest

from nemo_library import NemoLibrary
from datetime import datetime

META_PROJECT_NAME = "Business Processes"


def getNL():
    return NemoLibrary(
        config_file="tests/config.ini",
    )

def test_create():
    nl = getNL()
    nl.MetaDataCreate(META_PROJECT_NAME,"(C)")
    
def test_load():
    nl = getNL()
    nl.MetaDataLoad(META_PROJECT_NAME,"(C)")