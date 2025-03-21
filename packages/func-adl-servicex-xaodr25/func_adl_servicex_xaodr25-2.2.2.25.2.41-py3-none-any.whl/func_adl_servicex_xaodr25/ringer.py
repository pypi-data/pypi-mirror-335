from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
}

_enum_map = {      
}

T = TypeVar('T')


def _add_method_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _method_map:
        s_update = s.MetaData(_method_map[a.func.attr])


        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Ringer:
    "A class"

    class CalJointSection(Enum):
        EM = 0
        HAD = 1
        NJointSections = 2
        UnknownJointSection = 3

    class CalJointLayer(Enum):
        PS = 0
        EM1 = 1
        EM2 = 2
        EM3 = 3
        HAD1 = 4
        HAD2 = 5
        HAD3 = 6
        NJointLayers = 7
        UnknownJointLayer = 8

