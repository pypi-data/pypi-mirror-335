from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'minCycle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'minCycle',
        'return_type': 'int',
    },
    'maxCycle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'maxCycle',
        'return_type': 'int',
    },
    'empty': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'empty',
        'return_type': 'bool',
    },
    'front': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'front',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'back': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'back',
        'return_type': 'const xAOD::CutBookkeeper_v1 *',
    },
    'dvlinfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'dvlinfo',
        'return_type': 'const DataModel_detail::DVLInfoBase',
    },
    'dvlinfo_v': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'dvlinfo_v',
        'return_type': 'const DataModel_detail::DVLInfoBase',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CutBookkeeperContainer_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
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

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCutFlow/CutBookkeeperContainer.h',
            'body_includes': ["xAODCutFlow/CutBookkeeperContainer.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCutFlow',
            'link_libraries': ["xAODCutFlow"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CutBookkeeperContainer_v1:
    "A class"


    def minCycle(self) -> int:
        "A method"
        ...

    def maxCycle(self) -> int:
        "A method"
        ...

    def empty(self) -> bool:
        "A method"
        ...

    def front(self) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def back(self) -> func_adl_servicex_xaodr25.xAOD.cutbookkeeper_v1.CutBookkeeper_v1:
        "A method"
        ...

    def dvlinfo(self) -> func_adl_servicex_xaodr25.DataModel_detail.dvlinfobase.DVLInfoBase:
        "A method"
        ...

    def dvlinfo_v(self) -> func_adl_servicex_xaodr25.DataModel_detail.dvlinfobase.DVLInfoBase:
        "A method"
        ...

    def trackIndices(self) -> bool:
        "A method"
        ...

    def hasStore(self) -> bool:
        "A method"
        ...

    def hasNonConstStore(self) -> bool:
        "A method"
        ...

    def clearDecorations(self) -> bool:
        "A method"
        ...
