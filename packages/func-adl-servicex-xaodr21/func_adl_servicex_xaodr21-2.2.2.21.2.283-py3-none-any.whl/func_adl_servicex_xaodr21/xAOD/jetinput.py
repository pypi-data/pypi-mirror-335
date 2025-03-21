from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'isValidConstitType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'isValidConstitType',
        'return_type': 'bool',
    },
    'typeName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'typeName',
        'return_type': 'const string',
    },
    'inputType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::JetInput',
        'method_name': 'inputType',
        'return_type': 'xAOD::JetInput::Type',
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
class JetInput:
    "A class"

    class Type(Enum):
        LCTopo = 0
        EMTopo = 1
        TopoTower = 2
        Tower = 3
        Truth = 4
        TruthWZ = 5
        Track = 6
        PFlow = 7
        LCPFlow = 8
        EMPFlow = 9
        EMCPFlow = 10
        Jet = 11
        LCTopoOrigin = 12
        EMTopoOrigin = 13
        TrackCaloCluster = 14
        UFO = 15
        UFOCHS = 16
        UFOCSSK = 17
        TruthDressedWZ = 18
        EMTopoOriginSK = 19
        EMTopoOriginCS = 20
        EMTopoOriginVor = 21
        EMTopoOriginCSSK = 22
        EMTopoOriginVorSK = 23
        LCTopoOriginSK = 24
        LCTopoOriginCS = 25
        LCTopoOriginVor = 26
        LCTopoOriginCSSK = 27
        LCTopoOriginVorSK = 28
        EMPFlowSK = 29
        EMPFlowCS = 30
        EMPFlowVor = 31
        EMPFlowCSSK = 32
        EMPFlowVorSK = 33
        HI = 34
        TruthCharged = 35
        EMTopoOriginTime = 36
        EMTopoOriginSKTime = 37
        EMTopoOriginCSSKTime = 38
        EMTopoOriginVorSKTime = 39
        EMPFlowTime = 40
        EMPFlowSKTime = 41
        EMPFlowCSSKTime = 42
        EMPFlowVorSKTime = 43
        PFlowCustomVtx = 44
        EMPFlowByVertex = 45
        Other = 100
        Uncategorized = 1000


    def isValidConstitType(self, t: func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type) -> bool:
        "A method"
        ...

    def typeName(self, t: func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type) -> str:
        "A method"
        ...

    def inputType(self, n: str) -> func_adl_servicex_xaodr21.xAOD.jetinput.JetInput.Type:
        "A method"
        ...
