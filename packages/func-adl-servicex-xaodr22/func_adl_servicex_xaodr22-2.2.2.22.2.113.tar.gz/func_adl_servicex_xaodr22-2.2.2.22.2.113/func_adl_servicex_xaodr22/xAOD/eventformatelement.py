from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'branchName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventFormatElement',
        'method_name': 'branchName',
        'return_type': 'const string',
    },
    'className': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventFormatElement',
        'method_name': 'className',
        'return_type': 'const string',
    },
    'parentName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventFormatElement',
        'method_name': 'parentName',
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

        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEventFormat/EventFormatElement.h',
            'body_includes': ["xAODEventFormat/EventFormatElement.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODEventFormat',
            'link_libraries': ["xAODEventFormat"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class EventFormatElement:
    "A class"


    def branchName(self) -> str:
        "A method"
        ...

    def className(self) -> str:
        "A method"
        ...

    def parentName(self) -> str:
        "A method"
        ...
