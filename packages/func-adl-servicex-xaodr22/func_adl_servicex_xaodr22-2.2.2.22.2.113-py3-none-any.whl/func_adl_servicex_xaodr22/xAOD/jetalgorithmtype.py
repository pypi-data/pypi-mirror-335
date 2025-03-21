from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

_method_map = {
    'algName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetAlgorithmType',
        'method_name': 'algName',
        'return_type': 'const string',
    },
    'algId': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetAlgorithmType',
        'method_name': 'algId',
        'return_type': 'xAOD::JetAlgorithmType::ID',
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
class JetAlgorithmType:
    "A class"

    class ID(Enum):
        kt_algorithm = 0
        cambridge_algorithm = 1
        antikt_algorithm = 2
        genkt_algorithm = 3
        cambridge_for_passive_algorithm = 11
        genkt_for_passive_algorithm = 13
        ee_kt_algorithm = 50
        ee_genkt_algorithm = 53
        plugin_algorithm = 99
        undefined_jet_algorithm = 999


    def algName(self, id: func_adl_servicex_xaodr22.xAOD.jetalgorithmtype.JetAlgorithmType.ID) -> str:
        "A method"
        ...

    def algId(self, n: str) -> func_adl_servicex_xaodr22.xAOD.jetalgorithmtype.JetAlgorithmType.ID:
        "A method"
        ...
