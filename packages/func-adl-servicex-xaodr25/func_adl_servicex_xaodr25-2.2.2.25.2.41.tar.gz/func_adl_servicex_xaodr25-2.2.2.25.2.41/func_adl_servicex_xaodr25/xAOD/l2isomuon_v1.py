from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'p4',
        'return_type': 'TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'type',
        'return_type': 'xAODType::ObjectType',
    },
    'roiWord': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'roiWord',
        'return_type': 'unsigned int',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'errorFlag': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'errorFlag',
        'return_type': 'int',
    },
    'sumPt01': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumPt01',
        'return_type': 'float',
    },
    'sumPt02': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumPt02',
        'return_type': 'float',
    },
    'sumPt03': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumPt03',
        'return_type': 'float',
    },
    'sumPt04': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumPt04',
        'return_type': 'float',
    },
    'sumEt01': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumEt01',
        'return_type': 'float',
    },
    'sumEt02': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumEt02',
        'return_type': 'float',
    },
    'sumEt03': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumEt03',
        'return_type': 'float',
    },
    'sumEt04': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'sumEt04',
        'return_type': 'float',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'trackIndices': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'trackIndices',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::L2IsoMuon_v1',
        'method_name': 'isAvailable',
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
            'name': 'xAODTrigMuon/versions/L2IsoMuon_v1.h',
            'body_includes': ["xAODTrigMuon/versions/L2IsoMuon_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigMuon',
            'link_libraries': ["xAODTrigMuon"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class L2IsoMuon_v1:
    "A class"


    def pt(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def m(self) -> float:
        "A method"
        ...

    def e(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr25.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr25.xaodtype.xAODType.ObjectType:
        "A method"
        ...

    def roiWord(self) -> int:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def errorFlag(self) -> int:
        "A method"
        ...

    def sumPt01(self) -> float:
        "A method"
        ...

    def sumPt02(self) -> float:
        "A method"
        ...

    def sumPt03(self) -> float:
        "A method"
        ...

    def sumPt04(self) -> float:
        "A method"
        ...

    def sumEt01(self) -> float:
        "A method"
        ...

    def sumEt02(self) -> float:
        "A method"
        ...

    def sumEt03(self) -> float:
        "A method"
        ...

    def sumEt04(self) -> float:
        "A method"
        ...

    def index(self) -> int:
        "A method"
        ...

    def usingPrivateStore(self) -> bool:
        "A method"
        ...

    def usingStandaloneStore(self) -> bool:
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

    def trackIndices(self) -> bool:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr25.type_support.cpp_generic_1arg_callback('auxdataConst', s, a, param_1))
    @property
    def auxdataConst(self) -> func_adl_servicex_xaodr25.type_support.index_type_forwarder[str]:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr25.type_support.cpp_generic_1arg_callback('isAvailable', s, a, param_1))
    @property
    def isAvailable(self) -> func_adl_servicex_xaodr25.type_support.index_type_forwarder[str]:
        "A method"
        ...
