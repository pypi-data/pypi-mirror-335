from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'isSuccess': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'StatusCode',
        'method_name': 'isSuccess',
        'return_type': 'bool',
    },
    'isFailure': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'StatusCode',
        'method_name': 'isFailure',
        'return_type': 'bool',
    },
    'isRecoverable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'StatusCode',
        'method_name': 'isRecoverable',
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
            'name': 'AsgMessagingStandalone',
            'link_libraries': ["AsgMessagingStandalone"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class StatusCode:
    "A class"


    def isSuccess(self) -> bool:
        "A method"
        ...

    def isFailure(self) -> bool:
        "A method"
        ...

    def isRecoverable(self) -> bool:
        "A method"
        ...
