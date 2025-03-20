from numpy import array, float32, int32, complex64

IMAS_DEFAULT_INT = 999999999
IMAS_DEFAULT_FLOAT = 9e40
IMAS_DEFAULT_CPLX = complex(9e40, -9e40)
IMAS_DEFAULT_STR = ""
IMAS_DEFAULT_LIST = []
IMAS_DEFAULT_ARRAY_INT = array([], dtype=int)
IMAS_DEFAULT_ARRAY_FLT = array([], dtype=float)
IMAS_DEFAULT_ARRAY_CPLX = array([], dtype=complex)
#
# IMAS_CONVERT_TABLE = (("INT_0D", "{IMAS_NAMESPACE}int", IMAS_DEFAULT_INT),
#                       ("INT_1D", "{IMAS_NAMESPACE}ndarray[(int,), int]", IMAS_DEFAULT_ARRAY_INT),
#                       ("INT_2D", "{IMAS_NAMESPACE}ndarray[(int, int), int]", IMAS_DEFAULT_ARRAY_INT),
#                       ("INT_3D", "{IMAS_NAMESPACE}ndarray[(int, int, int), int]", IMAS_DEFAULT_ARRAY_INT),
#                       ("FLT_0D", "{IMAS_NAMESPACE}float", IMAS_DEFAULT_FLOAT),
#                       ("FLT_1D", "{IMAS_NAMESPACE}ndarray[(int,), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_2D", "{IMAS_NAMESPACE}ndarray[(int,int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_3D", "{IMAS_NAMESPACE}ndarray[(int,int, int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_4D", "{IMAS_NAMESPACE}ndarray[(int,int,int,int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_5D", "{IMAS_NAMESPACE}ndarray[(int,int,int,int,int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_6D", "{IMAS_NAMESPACE}ndarray[(int,int,int,int,int,int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("FLT_7D", "{IMAS_NAMESPACE}ndarray[(int,int,int,int,int,int,int), float]", IMAS_DEFAULT_ARRAY_FLT),
#                       ("STR_0D", "{IMAS_NAMESPACE}str", IMAS_DEFAULT_STR),
#                       ("STR_1D", "{IMAS_NAMESPACE}list[str]", []),
#                       ("STR_2D", "{IMAS_NAMESPACE}list[list[str]]", []),
#                       ("CPX_0D", "{IMAS_NAMESPACE}complex", IMAS_DEFAULT_CPLX),
#                       ("CPX_1D", "{IMAS_NAMESPACE}ndarray[(int,), complex]", IMAS_DEFAULT_ARRAY_CPLX),
#                       ("CPX_2D", "{IMAS_NAMESPACE}ndarray[(int, int), complex]", IMAS_DEFAULT_ARRAY_CPLX),
#                       ("CPX_3D", "{IMAS_NAMESPACE}ndarray[(int, int, int ), complex]", IMAS_DEFAULT_ARRAY_CPLX),
#                       ("CPX_4D", "{IMAS_NAMESPACE}ndarray[(int, int, int, int), complex]", IMAS_DEFAULT_ARRAY_CPLX),
#                       ("CPX_5D", "{IMAS_NAMESPACE}ndarray[(int, int, int, int, int), complex]", IMAS_DEFAULT_ARRAY_CPLX),
#                       ("CPX_6D", "{IMAS_NAMESPACE}ndarray[(int, int, int, int, int, int), complex]", IMAS_DEFAULT_ARRAY_CPLX)
#                       )
#
# IMAS_CONVERT_DICT = {x[0]: (x[1], x[2]) for x in IMAS_CONVERT_TABLE}

IMAS_TO_PYTHON_TYPES = {"FLT": float32, "INT": int32, "STR":str, "CPX": complex64}
