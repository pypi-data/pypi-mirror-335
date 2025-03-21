from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoIAuxContainer_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'size': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoIAuxContainer_v1',
        'method_name': 'size',
        'return_type': 'unsigned int',
    },
    'resize': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoIAuxContainer_v1',
        'method_name': 'resize',
        'return_type': 'bool',
    },
    'name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::jFexMETRoIAuxContainer_v1',
        'method_name': 'name',
        'return_type': 'const char *',
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
            'name': 'xAODTrigger/versions/jFexMETRoIAuxContainer_v1.h',
            'body_includes': ["xAODTrigger/versions/jFexMETRoIAuxContainer_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODTrigger',
            'link_libraries': ["xAODTrigger"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class jFexMETRoIAuxContainer_v1:
    "A class"


    def clearDecorations(self) -> bool:
        "A method"
        ...

    def size(self) -> int:
        "A method"
        ...

    def resize(self, size: int) -> bool:
        "A method"
        ...

    def name(self) -> str:
        "A method"
        ...
