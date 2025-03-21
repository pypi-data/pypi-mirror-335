from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
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
class Type:
    "A class"

    class ObjectType(Enum):
        Other = 0
        CaloCluster = 1
        Jet = 2
        ParticleFlow = 3
        TrackParticle = 4
        NeutralParticle = 5
        Electron = 6
        Photon = 7
        Muon = 8
        Tau = 9
        TrackCaloCluster = 10
        Vertex = 101
        BTag = 102
        TruthParticle = 201
        TruthVertex = 202
        TruthEvent = 203
        TruthPileupEvent = 204
        L2StandAloneMuon = 501
        L2IsoMuon = 502
        L2CombinedMuon = 503
        TrigElectron = 504
        TrigPhoton = 505
        TrigCaloCluster = 506
        TrigEMCluster = 507
        EventInfo = 1001
        EventFormat = 1002
        Particle = 1101
        CompositeParticle = 1102

