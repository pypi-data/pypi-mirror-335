from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr22

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
class EgammaParameters:
    "A class"

    class EgammaType(Enum):
        electron = 0
        unconvertedPhoton = 1
        convertedPhoton = 2
        NumberOfEgammaTypes = 3

    class ShowerShapeType(Enum):
        e011 = 0
        e033 = 1
        e132 = 2
        e1152 = 3
        ethad1 = 4
        ethad = 5
        ehad1 = 6
        f1 = 7
        f3 = 8
        f1core = 9
        f3core = 10
        e233 = 11
        e235 = 12
        e255 = 13
        e237 = 14
        e277 = 15
        e333 = 16
        e335 = 17
        e337 = 18
        e377 = 19
        weta1 = 20
        weta2 = 21
        e2ts1 = 22
        e2tsts1 = 23
        fracs1 = 24
        widths1 = 25
        widths2 = 26
        poscs1 = 27
        poscs2 = 28
        asy1 = 29
        pos = 30
        pos7 = 31
        barys1 = 32
        wtots1 = 33
        emins1 = 34
        emaxs1 = 35
        r33over37allcalo = 36
        ecore = 37
        Reta = 38
        Rphi = 39
        Eratio = 40
        Rhad = 41
        Rhad1 = 42
        DeltaE = 43
        NumberOfShowerShapes = 44

    class TrackCaloMatchType(Enum):
        deltaEta0 = 0
        deltaEta1 = 1
        deltaEta2 = 2
        deltaEta3 = 3
        deltaPhi0 = 4
        deltaPhi1 = 5
        deltaPhi2 = 6
        deltaPhi3 = 7
        deltaPhiFromLastMeasurement = 8
        deltaPhiRescaled0 = 9
        deltaPhiRescaled1 = 10
        deltaPhiRescaled2 = 11
        deltaPhiRescaled3 = 12
        NumberOfTrackMatchProperties = 13

    class VertexCaloMatchType(Enum):
        convMatchDeltaEta1 = 0
        convMatchDeltaEta2 = 1
        convMatchDeltaPhi1 = 2
        convMatchDeltaPhi2 = 3
        NumberOfVertexMatchProperties = 4

    class ConversionType(Enum):
        unconverted = 0
        singleSi = 1
        singleTRT = 2
        doubleSi = 3
        doubleTRT = 4
        doubleSiTRT = 5
        NumberOfVertexConversionTypes = 6

    class BitDefOQ(Enum):
        DeadHVPS = 0
        DeadHVS1S2S3Core = 1
        DeadHVS1S2S3Edge = 2
        NonNominalHVPS = 3
        NonNominalHVS1S2S3 = 4
        MissingFEBCellCore = 5
        MissingFEBCellEdgePS = 6
        MissingFEBCellEdgeS1 = 7
        MissingFEBCellEdgeS2 = 8
        MissingFEBCellEdgeS3 = 9
        MaskedCellCore = 10
        MaskedCellEdgePS = 11
        MaskedCellEdgeS1 = 12
        MaskedCellEdgeS2 = 13
        MaskedCellEdgeS3 = 14
        BadS1Core = 15
        SporadicNoiseLowQCore = 16
        SporadicNoiseLowQEdge = 17
        HighQCore = 18
        HighQEdge = 19
        AffectedCellCore = 20
        AffectedCellEdgePS = 21
        AffectedCellEdgeS1 = 22
        AffectedCellEdgeS2 = 23
        AffectedCellEdgeS3 = 24
        HECHighQ = 25
        OutTime = 26
        LArQCleaning = 27
        DeadCellTileS0 = 28
        DeadCellTileS1S2 = 29
        HighRcell = 30

