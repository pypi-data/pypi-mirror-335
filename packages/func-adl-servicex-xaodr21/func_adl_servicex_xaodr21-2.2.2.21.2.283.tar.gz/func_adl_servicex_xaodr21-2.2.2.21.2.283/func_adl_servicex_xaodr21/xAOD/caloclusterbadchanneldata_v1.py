from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'eta',
        'return_type': 'float',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'phi',
        'return_type': 'float',
    },
    'layer': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'layer',
        'return_type': 'CaloSampling::CaloSample',
    },
    'badChannel': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::CaloClusterBadChannelData_v1',
        'method_name': 'badChannel',
        'return_type': 'unsigned int',
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
            'name': 'xAODCaloEvent/versions/CaloClusterBadChannelData_v1.h',
            'body_includes': ["xAODCaloEvent/versions/CaloClusterBadChannelData_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODCaloEvent',
            'link_libraries': ["xAODCaloEvent"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class CaloClusterBadChannelData_v1:
    "A class"


    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def layer(self) -> func_adl_servicex_xaodr21.calosampling.CaloSampling.CaloSample:
        "A method"
        ...

    def badChannel(self) -> int:
        "A method"
        ...
