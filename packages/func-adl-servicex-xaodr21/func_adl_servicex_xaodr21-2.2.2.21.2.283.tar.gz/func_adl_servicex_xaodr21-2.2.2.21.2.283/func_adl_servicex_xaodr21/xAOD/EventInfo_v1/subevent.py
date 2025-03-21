from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'time': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'time',
        'return_type': 'int16_t',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'index',
        'return_type': 'uint16_t',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'type',
        'return_type': 'xAOD::EventInfo_v1::PileUpType',
    },
    'typeName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'typeName',
        'return_type': 'const string',
    },
    'link': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'link',
        'return_type': 'const ElementLink<DataVector<xAOD::EventInfo_v1>>',
    },
    'ptr': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::EventInfo_v1::SubEvent',
        'method_name': 'ptr',
        'return_type': 'const xAOD::EventInfo_v1 *',
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
class SubEvent:
    "A class"


    def time(self) -> int:
        "A method"
        ...

    def index(self) -> int:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1.PileUpType:
        "A method"
        ...

    def typeName(self) -> str:
        "A method"
        ...

    def link(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_eventinfo_v1__.ElementLink_DataVector_xAOD_EventInfo_v1__:
        "A method"
        ...

    def ptr(self) -> func_adl_servicex_xaodr21.xAOD.eventinfo_v1.EventInfo_v1:
        "A method"
        ...
