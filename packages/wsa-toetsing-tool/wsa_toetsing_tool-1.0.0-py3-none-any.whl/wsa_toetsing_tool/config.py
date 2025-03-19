import numpy as np

# MAPPENSTRUCTUUR
FOLDER_KNELPUNTEN = "Knelpunten"
FOLDER_TOETSING = "Toetsing"
FOLDER_BEWERKTE_INPUT = "Voorbewerkt"

# TOETSING
COL_PEIL = "peil"

# KNELPUNTEN
COL_KNELPUNTEN_NORM_COL = "NORMERING"
COL_KNELPUNTEN_SHP = {"knelpuntnummer": "KNELPUNTNR", "beschermingsniveau": "BESCHERNIV", "normering": COL_KNELPUNTEN_NORM_COL,
                      "klimaatscenario": "KLIMAATSCE", "wsa_titel": "WSA", "jaar": "JAAR", "omschrijving": "OMSCHRIJV"}

# BESTANDSNAMEN
BGT_PANDEN_RST = "bgt_panden.tif"
BGT_WATERVLAKKEN_RST = "bgt_watervlakken.tif"

# WATERSTANDSSTATISTIEK
FN_WATSTAT = "waterstandsstatistiek"
T_LIST = [10, 11, 25, 50, 100]
T_GUMBEL = [10, 25, 30, 50, 100]
COL_LIST_STAT = ['T10', 'T10_GROEI', 'T25', 'T30', 'T50', 'T100']

POST_GROEI = "_GROEI"
GROEISEIZOEN = [0, 1, 0, 0, 0]
COL_LIST = ['T10', 'T10_GROEI', 'T25', 'T50', 'T100']
COL_LIST_SHORT_DICT = {
    'T10': 'T10',
    'T10_GROEI': 'T10G',
    'T25': 'T25',
    'T50': 'T50',
    'T100': 'T100'
}

MAAIVELD_CRITERIUM = {
    'T10': 0.05,
    'T10_GROEI': 0.1,
    'T25': 0.01,
    'T50': 0.01,
    'T100': 0.0
}

METHODE_AGGREGATIE_GEBIED = ['min','mean','median','max']
INTERPOLATE_RETURN_PERIODS = {'T10': 10, 'T25': 25, 'T50': 50, 'T100': 100}

GROEISEIZOEN_DICT = dict(zip(COL_LIST, GROEISEIZOEN))
T_LIST_DICT = dict(zip(['T0'] + COL_LIST, [0] + T_LIST))
T_LABEL_DICT = dict(zip([0] + T_LIST, ['T0'] + COL_LIST))

# OVERSTROMINGSVLAKKEN
FN_PREFIX_WATERDIEPTE = "waterdiepte"
FN_PREFIX_WATERSTAND = "waterstand"

# GDAL
MEMORYLIMIT = 0.4   # factor of free physical memory
CACHELIMIT = 0.3    # factor of free physical memory

# Sobek network

FN_NTW = 'NETWORK.NTW'
CRS_28992 = "EPSG:28992"
COLS_ND = ['ID', 'Name', 'Type', 'ObjID', 'UserObjID', 'X', 'Y']
COLS_ND_FROM = [f'NdFrm{col}' for col in COLS_ND]
COLS_ND_TO = [f'NdTo{col}' for col in COLS_ND]
COL_INDEX_NODE = 'ID'
COL_NODE_TYPE = 'ObjID'
NTW_VERSION_SUPPORT = ["6.6"]
COLS_NTW = {
    'BrID': str,
    'BrName': str,
    'BrReach': np.int32,
    'BrType': np.int32,
    'BrObjID': str,
    'BrUserObjID': str,
    'BrFrmZ': np.float64,
    'BrToZ': np.float64,
    'BrDepth': np.float64,
    'BrLength': np.float64,
    'BrLengthMap': np.float64,
    'BrLengthUser': np.float64,
    'BrVolume': np.float64,
    'BrWidth': np.float64,
    'NdFrmID': str,
    'NdFrmName': str,
    'NdFrmArea': str,
    'NdFrmReach': np.int32,
    'NdFrmType': np.int32,
    'NdFrmObjID': str,
    'NdFrmUserObjID': str,
    'NdFrmX': np.float64,
    'NdFrmY': np.float64,
    'NdFrmZ': np.float64,
    'NdFrmReachDist': np.float64,
    'NdFrmSysStr': str,
    'NdFrmIden': np.int32,
    'NdToID': str,
    'NdToName': str,
    'NdToArea': str,
    'NdToReach': np.int32,
    'NdToType': np.int32,
    'NdToObjID': str,
    'NdToUserObjID': str,
    'NdToX': np.float64,
    'NdToY': np.float64,
    'NdToZ': np.float64,
    'NdToReachDist': np.float64,
    'NdToSysStr': str,
    'NdToIden': np.int32,
}
COLS_REACH = {
    'ReachID': str,
    'ReachName': str,
    'NdFrmID': str,
    'NdToID': str,
    'I1': np.int32,
    'I2': np.int32,
    'NdFrmX': np.float64,
    'NdFrmY': np.float64,
    'NdToX': np.float64,
    'NdToY': np.float64,
    'ReachLength': np.float64,
    'VectorSplit': np.int32,
    'VectorSplitLen': np.int32,
    'Equidistance': np.int32
}

COLS_BRANCH = {
    'BrID': str,
    'BrName': str,
    'NdFrmID': str,
    'NdToID': str,
    'BrLength': np.float64
}
