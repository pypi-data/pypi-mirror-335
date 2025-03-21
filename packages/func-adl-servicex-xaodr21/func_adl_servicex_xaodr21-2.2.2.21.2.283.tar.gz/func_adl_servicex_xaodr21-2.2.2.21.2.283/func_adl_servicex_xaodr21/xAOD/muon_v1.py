from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'pt': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'pt',
        'return_type': 'double',
    },
    'eta': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'eta',
        'return_type': 'double',
    },
    'phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'phi',
        'return_type': 'double',
    },
    'm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'm',
        'return_type': 'double',
    },
    'e': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'e',
        'return_type': 'double',
    },
    'rapidity': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'rapidity',
        'return_type': 'double',
    },
    'p4': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'p4',
        'return_type': 'const TLorentzVector',
    },
    'type': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'type',
        'return_type': 'xAOD::Type::ObjectType',
    },
    'charge': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'charge',
        'return_type': 'float',
    },
    'author': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'author',
        'return_type': 'xAOD::Muon_v1::Author',
    },
    'isAuthor': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isAuthor',
        'return_type': 'bool',
    },
    'allAuthors': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'allAuthors',
        'return_type': 'uint16_t',
    },
    'muonType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonType',
        'return_type': 'xAOD::Muon_v1::MuonType',
    },
    'summaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'summaryValue',
        'return_type': 'bool',
    },
    'floatSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'floatSummaryValue',
        'return_type': 'float',
    },
    'uint8SummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'uint8SummaryValue',
        'return_type': 'uint8_t',
    },
    'uint8MuonSummaryValue': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'uint8MuonSummaryValue',
        'return_type': 'float',
    },
    'parameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'parameter',
        'return_type': 'bool',
    },
    'floatParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'floatParameter',
        'return_type': 'float',
    },
    'intParameter': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'intParameter',
        'return_type': 'int',
    },
    'quality': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'quality',
        'return_type': 'xAOD::Muon_v1::Quality',
    },
    'passesIDCuts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'passesIDCuts',
        'return_type': 'bool',
    },
    'passesHighPtCuts': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'passesHighPtCuts',
        'return_type': 'bool',
    },
    'isolation': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolation',
        'return_type': 'bool',
    },
    'isolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolationCaloCorrection',
        'return_type': 'bool',
    },
    'setIsolationCaloCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationCaloCorrection',
        'return_type': 'bool',
    },
    'isolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationTrackCorrection': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationTrackCorrection',
        'return_type': 'bool',
    },
    'setIsolationCorrectionBitset': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'setIsolationCorrectionBitset',
        'return_type': 'bool',
    },
    'primaryTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'primaryTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'primaryTrackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'primaryTrackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'inDetTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'inDetTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'muonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'combinedTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'combinedTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'extrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'extrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'msOnlyExtrapolatedMuonSpectrometerTrackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'trackParticleLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'trackParticleLink',
        'return_type': 'const ElementLink<DataVector<xAOD::TrackParticle_v1>>',
    },
    'trackParticle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'trackParticle',
        'return_type': 'const xAOD::TrackParticle_v1 *',
    },
    'clusterLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'clusterLink',
        'return_type': 'const ElementLink<DataVector<xAOD::CaloCluster_v1>>',
    },
    'cluster': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'cluster',
        'return_type': 'const xAOD::CaloCluster_v1 *',
    },
    'energyLossType': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'energyLossType',
        'return_type': 'xAOD::Muon_v1::EnergyLossType',
    },
    'muonSegmentLinks': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegmentLinks',
        'return_type_element': 'ElementLink<DataVector<xAOD::MuonSegment_v1>>',
        'return_type_collection': 'const vector<ElementLink<DataVector<xAOD::MuonSegment_v1>>>',
    },
    'nMuonSegments': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'nMuonSegments',
        'return_type': 'unsigned int',
    },
    'muonSegment': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegment',
        'return_type': 'const xAOD::MuonSegment_v1 *',
    },
    'muonSegmentLink': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'muonSegmentLink',
        'return_type': 'const ElementLink<DataVector<xAOD::MuonSegment_v1>>',
    },
    'index': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'index',
        'return_type': 'unsigned int',
    },
    'usingPrivateStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'usingPrivateStore',
        'return_type': 'bool',
    },
    'usingStandaloneStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'usingStandaloneStore',
        'return_type': 'bool',
    },
    'hasStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'hasStore',
        'return_type': 'bool',
    },
    'hasNonConstStore': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'hasNonConstStore',
        'return_type': 'bool',
    },
    'clearDecorations': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'clearDecorations',
        'return_type': 'bool',
    },
    'auxdataConst': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'auxdataConst',
        'return_type': 'U',
    },
    'isAvailable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'xAOD::Muon_v1',
        'method_name': 'isAvailable',
        'return_type': 'bool',
    },
}

_enum_map = {
    'summaryValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'SummaryType',
            'values': [
                'numberOfContribPixelLayers',
                'numberOfBLayerHits',
                'numberOfBLayerOutliers',
                'numberOfBLayerSharedHits',
                'numberOfBLayerSplitHits',
                'expectBLayerHit',
                'expectInnermostPixelLayerHit',
                'numberOfInnermostPixelLayerHits',
                'numberOfInnermostPixelLayerOutliers',
                'numberOfInnermostPixelLayerSharedHits',
                'numberOfInnermostPixelLayerSplitHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfDBMHits',
                'numberOfPixelHits',
                'numberOfPixelOutliers',
                'numberOfPixelHoles',
                'numberOfPixelSharedHits',
                'numberOfPixelSplitHits',
                'numberOfGangedPixels',
                'numberOfGangedFlaggedFakes',
                'numberOfPixelDeadSensors',
                'numberOfPixelSpoiltHits',
                'numberOfSCTHits',
                'numberOfSCTOutliers',
                'numberOfSCTHoles',
                'numberOfSCTDoubleHoles',
                'numberOfSCTSharedHits',
                'numberOfSCTDeadSensors',
                'numberOfSCTSpoiltHits',
                'numberOfTRTHits',
                'numberOfTRTOutliers',
                'numberOfTRTHoles',
                'numberOfTRTHighThresholdHits',
                'numberOfTRTHighThresholdHitsTotal',
                'numberOfTRTHighThresholdOutliers',
                'numberOfTRTDeadStraws',
                'numberOfTRTTubeHits',
                'numberOfTRTXenonHits',
                'numberOfTRTSharedHits',
                'numberOfPrecisionLayers',
                'numberOfPrecisionHoleLayers',
                'numberOfPhiLayers',
                'numberOfPhiHoleLayers',
                'numberOfTriggerEtaLayers',
                'numberOfTriggerEtaHoleLayers',
                'numberOfGoodPrecisionLayers',
                'numberOfOutliersOnTrack',
                'standardDeviationOfChi2OS',
                'eProbabilityComb',
                'eProbabilityHT',
                'pixeldEdx',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'floatSummaryValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'SummaryType',
            'values': [
                'numberOfContribPixelLayers',
                'numberOfBLayerHits',
                'numberOfBLayerOutliers',
                'numberOfBLayerSharedHits',
                'numberOfBLayerSplitHits',
                'expectBLayerHit',
                'expectInnermostPixelLayerHit',
                'numberOfInnermostPixelLayerHits',
                'numberOfInnermostPixelLayerOutliers',
                'numberOfInnermostPixelLayerSharedHits',
                'numberOfInnermostPixelLayerSplitHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfDBMHits',
                'numberOfPixelHits',
                'numberOfPixelOutliers',
                'numberOfPixelHoles',
                'numberOfPixelSharedHits',
                'numberOfPixelSplitHits',
                'numberOfGangedPixels',
                'numberOfGangedFlaggedFakes',
                'numberOfPixelDeadSensors',
                'numberOfPixelSpoiltHits',
                'numberOfSCTHits',
                'numberOfSCTOutliers',
                'numberOfSCTHoles',
                'numberOfSCTDoubleHoles',
                'numberOfSCTSharedHits',
                'numberOfSCTDeadSensors',
                'numberOfSCTSpoiltHits',
                'numberOfTRTHits',
                'numberOfTRTOutliers',
                'numberOfTRTHoles',
                'numberOfTRTHighThresholdHits',
                'numberOfTRTHighThresholdHitsTotal',
                'numberOfTRTHighThresholdOutliers',
                'numberOfTRTDeadStraws',
                'numberOfTRTTubeHits',
                'numberOfTRTXenonHits',
                'numberOfTRTSharedHits',
                'numberOfPrecisionLayers',
                'numberOfPrecisionHoleLayers',
                'numberOfPhiLayers',
                'numberOfPhiHoleLayers',
                'numberOfTriggerEtaLayers',
                'numberOfTriggerEtaHoleLayers',
                'numberOfGoodPrecisionLayers',
                'numberOfOutliersOnTrack',
                'standardDeviationOfChi2OS',
                'eProbabilityComb',
                'eProbabilityHT',
                'pixeldEdx',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'uint8SummaryValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'SummaryType',
            'values': [
                'numberOfContribPixelLayers',
                'numberOfBLayerHits',
                'numberOfBLayerOutliers',
                'numberOfBLayerSharedHits',
                'numberOfBLayerSplitHits',
                'expectBLayerHit',
                'expectInnermostPixelLayerHit',
                'numberOfInnermostPixelLayerHits',
                'numberOfInnermostPixelLayerOutliers',
                'numberOfInnermostPixelLayerSharedHits',
                'numberOfInnermostPixelLayerSplitHits',
                'expectNextToInnermostPixelLayerHit',
                'numberOfNextToInnermostPixelLayerHits',
                'numberOfNextToInnermostPixelLayerOutliers',
                'numberOfNextToInnermostPixelLayerSharedHits',
                'numberOfNextToInnermostPixelLayerSplitHits',
                'numberOfDBMHits',
                'numberOfPixelHits',
                'numberOfPixelOutliers',
                'numberOfPixelHoles',
                'numberOfPixelSharedHits',
                'numberOfPixelSplitHits',
                'numberOfGangedPixels',
                'numberOfGangedFlaggedFakes',
                'numberOfPixelDeadSensors',
                'numberOfPixelSpoiltHits',
                'numberOfSCTHits',
                'numberOfSCTOutliers',
                'numberOfSCTHoles',
                'numberOfSCTDoubleHoles',
                'numberOfSCTSharedHits',
                'numberOfSCTDeadSensors',
                'numberOfSCTSpoiltHits',
                'numberOfTRTHits',
                'numberOfTRTOutliers',
                'numberOfTRTHoles',
                'numberOfTRTHighThresholdHits',
                'numberOfTRTHighThresholdHitsTotal',
                'numberOfTRTHighThresholdOutliers',
                'numberOfTRTDeadStraws',
                'numberOfTRTTubeHits',
                'numberOfTRTXenonHits',
                'numberOfTRTSharedHits',
                'numberOfPrecisionLayers',
                'numberOfPrecisionHoleLayers',
                'numberOfPhiLayers',
                'numberOfPhiHoleLayers',
                'numberOfTriggerEtaLayers',
                'numberOfTriggerEtaHoleLayers',
                'numberOfGoodPrecisionLayers',
                'numberOfOutliersOnTrack',
                'standardDeviationOfChi2OS',
                'eProbabilityComb',
                'eProbabilityHT',
                'pixeldEdx',
                'numberOfTrackSummaryTypes',
            ],
        },
    ],
    'uint8MuonSummaryValue': [
        {
            'metadata_type': 'define_enum',
            'namespace': 'xAOD',
            'name': 'MuonSummaryType',
            'values': [
                'primarySector',
                'secondarySector',
                'innerSmallHits',
                'innerLargeHits',
                'middleSmallHits',
                'middleLargeHits',
                'outerSmallHits',
                'outerLargeHits',
                'extendedSmallHits',
                'extendedLargeHits',
                'innerSmallHoles',
                'innerLargeHoles',
                'middleSmallHoles',
                'middleLargeHoles',
                'outerSmallHoles',
                'outerLargeHoles',
                'extendedSmallHoles',
                'extendedLargeHoles',
                'phiLayer1Hits',
                'phiLayer2Hits',
                'phiLayer3Hits',
                'phiLayer4Hits',
                'etaLayer1Hits',
                'etaLayer2Hits',
                'etaLayer3Hits',
                'etaLayer4Hits',
                'phiLayer1Holes',
                'phiLayer2Holes',
                'phiLayer3Holes',
                'phiLayer4Holes',
                'etaLayer1Holes',
                'etaLayer2Holes',
                'etaLayer3Holes',
                'etaLayer4Holes',
                'innerClosePrecisionHits',
                'middleClosePrecisionHits',
                'outerClosePrecisionHits',
                'extendedClosePrecisionHits',
                'innerOutBoundsPrecisionHits',
                'middleOutBoundsPrecisionHits',
                'outerOutBoundsPrecisionHits',
                'extendedOutBoundsPrecisionHits',
                'combinedTrackOutBoundsPrecisionHits',
                'isEndcapGoodLayers',
                'isSmallGoodSectors',
                'phiLayer1RPCHits',
                'phiLayer2RPCHits',
                'phiLayer3RPCHits',
                'phiLayer4RPCHits',
                'etaLayer1RPCHits',
                'etaLayer2RPCHits',
                'etaLayer3RPCHits',
                'etaLayer4RPCHits',
                'phiLayer1RPCHoles',
                'phiLayer2RPCHoles',
                'phiLayer3RPCHoles',
                'phiLayer4RPCHoles',
                'etaLayer1RPCHoles',
                'etaLayer2RPCHoles',
                'etaLayer3RPCHoles',
                'etaLayer4RPCHoles',
                'phiLayer1TGCHits',
                'phiLayer2TGCHits',
                'phiLayer3TGCHits',
                'phiLayer4TGCHits',
                'etaLayer1TGCHits',
                'etaLayer2TGCHits',
                'etaLayer3TGCHits',
                'etaLayer4TGCHits',
                'phiLayer1TGCHoles',
                'phiLayer2TGCHoles',
                'phiLayer3TGCHoles',
                'phiLayer4TGCHoles',
                'etaLayer1TGCHoles',
                'etaLayer2TGCHoles',
                'etaLayer3TGCHoles',
                'etaLayer4TGCHoles',
                'phiLayer1STGCHits',
                'phiLayer2STGCHits',
                'etaLayer1STGCHits',
                'etaLayer2STGCHits',
                'phiLayer1STGCHoles',
                'phiLayer2STGCHoles',
                'etaLayer1STGCHoles',
                'etaLayer2STGCHoles',
                'mmHits',
                'mmHoles',
                'cscEtaHits',
                'cscUnspoiledEtaHits',
                'numberOfMuonSummaryTypes',
            ],
        },
    ],      
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
            'name': 'xAODMuon/versions/Muon_v1.h',
            'body_includes': ["xAODMuon/versions/Muon_v1.h"],
        })


        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': 'xAODMuon',
            'link_libraries': ["xAODMuon"],
        })

        for md in _enum_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class Muon_v1:
    "A class"

    class Author(Enum):
        unknown = 0
        MuidCo = 1
        STACO = 2
        MuTag = 3
        MuTagIMO = 4
        MuidSA = 5
        MuGirl = 6
        MuGirlLowBeta = 7
        CaloTag = 8
        CaloLikelihood = 9
        ExtrapolateMuonToIP = 10
        NumberOfMuonAuthors = 11

    class MuonType(Enum):
        Combined = 0
        MuonStandAlone = 1
        SegmentTagged = 2
        CaloTagged = 3
        SiliconAssociatedForwardMuon = 4

    class ParamDef(Enum):
        spectrometerFieldIntegral = 0
        scatteringCurvatureSignificance = 1
        scatteringNeighbourSignificance = 2
        momentumBalanceSignificance = 3
        segmentDeltaEta = 4
        segmentDeltaPhi = 5
        segmentChi2OverDoF = 6
        t0 = 7
        beta = 8
        annBarrel = 9
        annEndCap = 10
        innAngle = 11
        midAngle = 12
        msInnerMatchChi2 = 13
        msInnerMatchDOF = 14
        msOuterMatchChi2 = 15
        msOuterMatchDOF = 16
        meanDeltaADCCountsMDT = 17
        CaloLRLikelihood = 18
        CaloMuonIDTag = 19
        FSR_CandidateEnergy = 20
        EnergyLoss = 21
        ParamEnergyLoss = 22
        MeasEnergyLoss = 23
        EnergyLossSigma = 24
        ParamEnergyLossSigmaPlus = 25
        ParamEnergyLossSigmaMinus = 26
        MeasEnergyLossSigma = 27

    class Quality(Enum):
        Tight = 0
        Medium = 1
        Loose = 2
        VeryLoose = 3

    class TrackParticleType(Enum):
        Primary = 0
        InnerDetectorTrackParticle = 1
        MuonSpectrometerTrackParticle = 2
        CombinedTrackParticle = 3
        ExtrapolatedMuonSpectrometerTrackParticle = 4
        MSOnlyExtrapolatedMuonSpectrometerTrackParticle = 5

    class EnergyLossType(Enum):
        Parametrized = 0
        NotIsolated = 1
        MOP = 2
        Tail = 3
        FSRcandidate = 4


    def pt(self) -> float:
        "A method"
        ...

    def eta(self) -> float:
        "A method"
        ...

    def phi(self) -> float:
        "A method"
        ...

    def m(self) -> float:
        "A method"
        ...

    def e(self) -> float:
        "A method"
        ...

    def rapidity(self) -> float:
        "A method"
        ...

    def p4(self) -> func_adl_servicex_xaodr21.tlorentzvector.TLorentzVector:
        "A method"
        ...

    def type(self) -> func_adl_servicex_xaodr21.xAOD.type.Type.ObjectType:
        "A method"
        ...

    def charge(self) -> float:
        "A method"
        ...

    def author(self) -> func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.Author:
        "A method"
        ...

    def isAuthor(self, author: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.Author) -> bool:
        "A method"
        ...

    def allAuthors(self) -> int:
        "A method"
        ...

    def muonType(self) -> func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.MuonType:
        "A method"
        ...

    def summaryValue(self, value: int, information: func_adl_servicex_xaodr21.xaod.xAOD.SummaryType) -> bool:
        "A method"
        ...

    def floatSummaryValue(self, information: func_adl_servicex_xaodr21.xaod.xAOD.SummaryType) -> float:
        "A method"
        ...

    def uint8SummaryValue(self, information: func_adl_servicex_xaodr21.xaod.xAOD.SummaryType) -> int:
        "A method"
        ...

    def uint8MuonSummaryValue(self, information: func_adl_servicex_xaodr21.xaod.xAOD.MuonSummaryType) -> float:
        "A method"
        ...

    def parameter(self, value: float, parameter: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.ParamDef) -> bool:
        "A method"
        ...

    def floatParameter(self, parameter: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.ParamDef) -> float:
        "A method"
        ...

    def intParameter(self, parameter: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.ParamDef) -> int:
        "A method"
        ...

    def quality(self) -> func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.Quality:
        "A method"
        ...

    def passesIDCuts(self) -> bool:
        "A method"
        ...

    def passesHighPtCuts(self) -> bool:
        "A method"
        ...

    def isolation(self, value: float, information: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationType) -> bool:
        "A method"
        ...

    def isolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def setIsolationCaloCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCaloCorrection, param: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationCorrectionParameter) -> bool:
        "A method"
        ...

    def isolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationTrackCorrection(self, value: float, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour, type: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationTrackCorrection) -> bool:
        "A method"
        ...

    def setIsolationCorrectionBitset(self, value: int, flavour: func_adl_servicex_xaodr21.xAOD.iso.Iso.IsolationFlavour) -> bool:
        "A method"
        ...

    def primaryTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def primaryTrackParticle(self) -> func_adl_servicex_xaodr21.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def inDetTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def muonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def combinedTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def extrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def msOnlyExtrapolatedMuonSpectrometerTrackParticleLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticleLink(self, type: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_trackparticle_v1__.ElementLink_DataVector_xAOD_TrackParticle_v1__:
        "A method"
        ...

    def trackParticle(self, type: func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.TrackParticleType) -> func_adl_servicex_xaodr21.xAOD.trackparticle_v1.TrackParticle_v1:
        "A method"
        ...

    def clusterLink(self) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_calocluster_v1__.ElementLink_DataVector_xAOD_CaloCluster_v1__:
        "A method"
        ...

    def cluster(self) -> func_adl_servicex_xaodr21.xAOD.calocluster_v1.CaloCluster_v1:
        "A method"
        ...

    def energyLossType(self) -> func_adl_servicex_xaodr21.xAOD.muon_v1.Muon_v1.EnergyLossType:
        "A method"
        ...

    def muonSegmentLinks(self) -> func_adl_servicex_xaodr21.vector_elementlink_datavector_xaod_muonsegment_v1___.vector_ElementLink_DataVector_xAOD_MuonSegment_v1___:
        "A method"
        ...

    def nMuonSegments(self) -> int:
        "A method"
        ...

    def muonSegment(self, i: int) -> func_adl_servicex_xaodr21.xAOD.muonsegment_v1.MuonSegment_v1:
        "A method"
        ...

    def muonSegmentLink(self, i: int) -> func_adl_servicex_xaodr21.elementlink_datavector_xaod_muonsegment_v1__.ElementLink_DataVector_xAOD_MuonSegment_v1__:
        "A method"
        ...

    def index(self) -> int:
        "A method"
        ...

    def usingPrivateStore(self) -> bool:
        "A method"
        ...

    def usingStandaloneStore(self) -> bool:
        "A method"
        ...

    def hasStore(self) -> bool:
        "A method"
        ...

    def hasNonConstStore(self) -> bool:
        "A method"
        ...

    def clearDecorations(self) -> bool:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr21.type_support.cpp_generic_1arg_callback('auxdataConst', s, a, param_1))
    @property
    def auxdataConst(self) -> func_adl_servicex_xaodr21.type_support.index_type_forwarder[str]:
        "A method"
        ...

    @func_adl_parameterized_call(lambda s, a, param_1: func_adl_servicex_xaodr21.type_support.cpp_generic_1arg_callback('isAvailable', s, a, param_1))
    @property
    def isAvailable(self) -> func_adl_servicex_xaodr21.type_support.index_type_forwarder[str]:
        "A method"
        ...
