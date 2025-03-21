from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

_method_map = {
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'locale',
        'method_name': 'name',
        'return_type': 'string',
    },
    'global': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'locale',
        'method_name': 'global',
        'return_type': 'locale',
    },
    'classic': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'locale',
        'method_name': 'classic',
        'return_type': 'const locale',
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


        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class locale:
    "A class"

    class (unnamed)(Enum):
        _S_categories_size = 12


    def name(self) -> str:
        "A method"
        ...

    def global(self, __loc: locale) -> func_adl_servicex_xaodr25.locale.locale:
        "A method"
        ...

    def classic(self) -> func_adl_servicex_xaodr25.locale.locale:
        "A method"
        ...
