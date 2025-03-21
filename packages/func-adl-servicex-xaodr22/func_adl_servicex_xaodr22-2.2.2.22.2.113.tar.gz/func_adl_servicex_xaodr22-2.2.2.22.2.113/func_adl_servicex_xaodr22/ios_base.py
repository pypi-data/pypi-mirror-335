from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'sync_with_stdio': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'sync_with_stdio',
        'return_type': 'bool',
    },
    'imbue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'imbue',
        'return_type': 'locale',
    },
    'getloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'getloc',
        'return_type': 'locale',
    },
    '_M_getloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': '_M_getloc',
        'return_type': 'const locale',
    },
    'xalloc': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'xalloc',
        'return_type': 'int',
    },
    'iword': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'ios_base',
        'method_name': 'iword',
        'return_type': 'long',
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
class ios_base:
    "A class"

    class event(Enum):
        erase_event = 0
        imbue_event = 1
        copyfmt_event = 2


    def sync_with_stdio(self, __sync: bool) -> bool:
        "A method"
        ...

    def imbue(self, __loc: func_adl_servicex_xaodr22.locale.locale) -> func_adl_servicex_xaodr22.locale.locale:
        "A method"
        ...

    def getloc(self) -> func_adl_servicex_xaodr22.locale.locale:
        "A method"
        ...

    def _M_getloc(self) -> func_adl_servicex_xaodr22.locale.locale:
        "A method"
        ...

    def xalloc(self) -> int:
        "A method"
        ...

    def iword(self, __ix: int) -> int:
        "A method"
        ...
