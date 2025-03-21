from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr25

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
class PFODetails:
    "A class"

    class PFOAttributes(Enum):
        nPi0 = 0
        nPi0Proto = 1
        eflowRec_EM_FRAC_ENHANCED = 200
        eflowRec_ENG_FRAC_CORE = 201
        eflowRec_FIRST_ENG_DENS = 202
        eflowRec_CENTER_LAMBDA = 203
        eflowRec_SECOND_R = 204
        eflowRec_DELTA_ALPHA = 205
        eflowRec_HOT_STRIP_FRAC = 206
        eflowRec_THREE_CELL_STRIP_FRAC = 207
        eflowRec_LATERAL = 208
        eflowRec_LONGITUDINAL = 209
        eflowRec_SECOND_LAMBDA = 210
        eflowRec_ISOLATION = 211
        eflowRec_ENG_FRAC_MAX = 212
        eflowRec_ENG_BAD_CELLS = 213
        eflowRec_N_BAD_CELLS = 214
        eflowRec_BADLARQ_FRAC = 215
        eflowRec_ENG_POS = 216
        eflowRec_SIGNIFICANCE = 217
        eflowRec_CELL_SIGNIFICANCE = 218
        eflowRec_CELL_SIG_SAMPLING = 219
        eflowRec_AVG_LAR_Q = 220
        eflowRec_AVG_TILE_Q = 221
        eflowRec_LAYERENERGY_EM3 = 222
        eflowRec_LAYERENERGY_HEC0 = 223
        eflowRec_LAYERENERGY_Tile0 = 224
        eflowRec_LAYERENERGY_HEC = 225
        eflowRec_TIMING = 226
        eflowRec_tracksExpectedEnergyDeposit = 227
        eflowRec_isInDenseEnvironment = 228
        eflowRec_LAYERENERGY_EM = 229
        eflowRec_LAYERENERGY_PreSamplerB = 230
        eflowRec_LAYERENERGY_EMB1 = 231
        eflowRec_LAYERENERGY_EMB2 = 232
        eflowRec_LAYERENERGY_EMB3 = 233
        eflowRec_LAYERENERGY_PreSamplerE = 234
        eflowRec_LAYERENERGY_EME1 = 235
        eflowRec_LAYERENERGY_EME2 = 236
        eflowRec_LAYERENERGY_EME3 = 237
        eflowRec_LAYERENERGY_HEC1 = 238
        eflowRec_LAYERENERGY_HEC2 = 239
        eflowRec_LAYERENERGY_HEC3 = 240
        eflowRec_LAYERENERGY_TileBar0 = 241
        eflowRec_LAYERENERGY_TileBar1 = 242
        eflowRec_LAYERENERGY_TileBar2 = 243
        eflowRec_LAYERENERGY_TileGap1 = 244
        eflowRec_LAYERENERGY_TileGap2 = 245
        eflowRec_LAYERENERGY_TileGap3 = 246
        eflowRec_LAYERENERGY_TileExt0 = 247
        eflowRec_LAYERENERGY_TileExt1 = 248
        eflowRec_LAYERENERGY_TileExt2 = 249
        eflowRec_LAYERENERGY_FCAL0 = 250
        eflowRec_LAYERENERGY_FCAL1 = 251
        eflowRec_LAYERENERGY_FCAL2 = 252
        eflowRec_LAYERENERGY_MINIFCAL0 = 253
        eflowRec_LAYERENERGY_MINIFCAL1 = 254
        eflowRec_LAYERENERGY_MINIFCAL2 = 255
        eflowRec_LAYERENERGY_MINIFCAL3 = 256
        eflowRec_EM_PROBABILITY = 257
        eflowRec_layerVectorCellOrdering = 258
        eflowRec_radiusVectorCellOrdering = 259
        eflowRec_avgEdensityVectorCellOrdering = 260
        eflowRec_layerHED = 261
        eflowRec_ENG_CALIB_TOT = 262
        eflowRec_ENG_CALIB_FRAC_EM = 263
        eflowRec_ENG_CALIB_FRAC_HAD = 264
        eflowRec_ENG_CALIB_FRAC_REST = 265
        eflowRec_ENERGY_DigiHSTruth = 266
        eflowRec_ETA_DigiHSTruth = 267
        eflowRec_PHI_DigiHSTruth = 268
        eflowRec_SECOND_R_DigiHSTruth = 269
        eflowRec_FIRST_ENG_DENS_DigiHSTruth = 270
        eflowRec_CENTER_LAMBDA_DigiHSTruth = 271
        eflowRec_SECOND_LAMBDA_DigiHSTruth = 272
        eflowRec_ISOLATION_DigiHSTruth = 273
        eflowRec_ENG_FRAC_MAX_DigiHSTruth = 274
        eflowRec_ENG_BAD_CELLS_DigiHSTruth = 275
        eflowRec_N_BAD_CELLS_DigiHSTruth = 276
        eflowRec_BADLARQ_FRAC_DigiHSTruth = 277
        eflowRec_ENG_POS_DigiHSTruth = 278
        eflowRec_SIGNIFICANCE_DigiHSTruth = 279
        eflowRec_CELL_SIGNIFICANCE_DigiHSTruth = 280
        eflowRec_CELL_SIG_SAMPLING_DigiHSTruth = 281
        eflowRec_AVG_LAR_Q_DigiHSTruth = 282
        eflowRec_AVG_TILE_Q_DigiHSTruth = 283
        cellBased_FIRST_ETA = 400
        cellBased_SECOND_R = 401
        cellBased_SECOND_LAMBDA = 402
        cellBased_DELTA_PHI = 403
        cellBased_DELTA_THETA = 404
        cellBased_CENTER_LAMBDA = 405
        cellBased_LATERAL = 406
        cellBased_LONGITUDINAL = 407
        cellBased_ENG_FRAC_EM = 408
        cellBased_ENG_FRAC_MAX = 409
        cellBased_ENG_FRAC_CORE = 410
        cellBased_SECOND_ENG_DENS = 411
        cellBased_EM1CoreFrac = 412
        cellBased_asymmetryInEM1WRTTrk = 413
        cellBased_NHitsInEM1 = 414
        cellBased_NPosECells_PS = 415
        cellBased_NPosECells_EM1 = 416
        cellBased_NPosECells_EM2 = 417
        cellBased_firstEtaWRTClusterPosition_EM1 = 418
        cellBased_firstEtaWRTClusterPosition_EM2 = 419
        cellBased_secondEtaWRTClusterPosition_EM1 = 420
        cellBased_secondEtaWRTClusterPosition_EM2 = 421
        cellBased_energy_EM1 = 422
        cellBased_energy_EM2 = 423
        tauShots_nCellsInEta = 600
        tauShots_pt1 = 601
        tauShots_pt3 = 602
        tauShots_pt5 = 603
        tauShots_ws5 = 604
        tauShots_sdevEta5_WRTmean = 605
        tauShots_sdevEta5_WRTmode = 606
        tauShots_sdevPt5 = 607
        tauShots_deltaPt12_min = 608
        tauShots_Fside_3not1 = 609
        tauShots_Fside_5not1 = 610
        tauShots_Fside_5not3 = 611
        tauShots_fracSide_3not1 = 612
        tauShots_fracSide_5not1 = 613
        tauShots_fracSide_5not3 = 614
        tauShots_pt1OverPt3 = 615
        tauShots_pt3OverPt5 = 616
        tauShots_mergedScore = 617
        tauShots_signalScore = 618
        tauShots_nPhotons = 619
        tauShots_seedHash = 620

    class PFOParticleType(Enum):
        CaloCluster = 0
        Track = 1
        TauShot = 2
        HadronicCalo = 3
        ChargedPFO = 4
        NeutralPFO = 5
        TauTrack = 6

    class PFOLeptonType(Enum):
        PFO_electron = 0
        PFO_muon = 1
        PFO_tau = 2
        PFO_photon = 3
        PFO_nonLeptonic = 4

