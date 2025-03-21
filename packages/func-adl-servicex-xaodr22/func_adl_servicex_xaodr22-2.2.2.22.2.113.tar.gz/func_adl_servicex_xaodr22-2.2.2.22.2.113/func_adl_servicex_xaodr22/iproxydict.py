from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'addRef': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'IProxyDict',
        'method_name': 'addRef',
        'return_type': 'unsigned long',
    },
    'release': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'IProxyDict',
        'method_name': 'release',
        'return_type': 'unsigned long',
    },
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'IProxyDict',
        'method_name': 'name',
        'return_type': 'const string',
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
class IProxyDict:
    "A class"


    def addRef(self) -> int:
        "A method"
        ...

    def release(self) -> int:
        "A method"
        ...

    def name(self) -> str:
        "A method"
        ...
