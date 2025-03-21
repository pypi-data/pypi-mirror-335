from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'exists': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventFormat_v1',
        'method_name': 'exists',
        'return_type': 'bool',
    },
    'get': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventFormat_v1',
        'method_name': 'get',
        'return_type': 'const xAOD::EventFormatElement *',
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
            'name': 'xAODEventFormat/versions/EventFormat_v1.h',
            'body_includes': ["xAODEventFormat/versions/EventFormat_v1.h"],
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
class EventFormat_v1:
    "A class"


    def exists(self, key: str) -> bool:
        "A method"
        ...

    def get(self, key: str, quiet: bool) -> func_adl_servicex_xaodr22.xAOD.eventformatelement.EventFormatElement:
        "A method"
        ...
