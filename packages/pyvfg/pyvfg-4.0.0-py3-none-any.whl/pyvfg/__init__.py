# -*- coding: utf-8 -*-

from .errors import *
from .versions.vfg_0_4_0 import *
from .versions.vfg_0_4_0_utils import (
    get_graph,
    set_graph,
    vfg_from_dict,
    vfg_from_json,
    vfg_to_json,
    vfg_to_json_schema,
    vfg_upgrade,
)


# by request
@property
def __version__() -> str:
    import importlib_metadata

    return importlib_metadata.version("pyvfg")


# for compatibility
VFGPydanticType = VFG
# TODO: Check whether this still works
validate_graph = VFG.validate
