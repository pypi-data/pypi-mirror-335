from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import func_adl_servicex_xaodr21

_method_map = {
    'Mod2': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Mod2',
        'return_type': 'double',
    },
    'Mod': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Mod',
        'return_type': 'double',
    },
    'Px': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Px',
        'return_type': 'double',
    },
    'Py': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Py',
        'return_type': 'double',
    },
    'X': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'X',
        'return_type': 'double',
    },
    'Y': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Y',
        'return_type': 'double',
    },
    'Phi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Phi',
        'return_type': 'double',
    },
    'DeltaPhi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'DeltaPhi',
        'return_type': 'double',
    },
    'Unit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Unit',
        'return_type': 'TVector2',
    },
    'Ort': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Ort',
        'return_type': 'TVector2',
    },
    'Proj': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Proj',
        'return_type': 'TVector2',
    },
    'Norm': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Norm',
        'return_type': 'TVector2',
    },
    'Rotate': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Rotate',
        'return_type': 'TVector2',
    },
    'Phi_0_2pi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Phi_0_2pi',
        'return_type': 'double',
    },
    'Phi_mpi_pi': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Phi_mpi_pi',
        'return_type': 'double',
    },
    'DeclFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'DeclFileName',
        'return_type': 'const char *',
    },
    'ImplFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'ImplFileLine',
        'return_type': 'int',
    },
    'ImplFileName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'ImplFileName',
        'return_type': 'const char *',
    },
    'Class_Name': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Class_Name',
        'return_type': 'const char *',
    },
    'DeclFileLine': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'DeclFileLine',
        'return_type': 'int',
    },
    'Hash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Hash',
        'return_type': 'unsigned long',
    },
    'ClassName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'ClassName',
        'return_type': 'const char *',
    },
    'CheckedHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'CheckedHash',
        'return_type': 'unsigned long',
    },
    'DistancetoPrimitive': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'DistancetoPrimitive',
        'return_type': 'int',
    },
    'GetUniqueID': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetUniqueID',
        'return_type': 'unsigned int',
    },
    'GetName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetName',
        'return_type': 'const char *',
    },
    'GetIconName': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetIconName',
        'return_type': 'const char *',
    },
    'GetObjectInfo': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetObjectInfo',
        'return_type': 'char *',
    },
    'GetTitle': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetTitle',
        'return_type': 'const char *',
    },
    'HasInconsistentHash': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'HasInconsistentHash',
        'return_type': 'bool',
    },
    'InheritsFrom': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'InheritsFrom',
        'return_type': 'bool',
    },
    'IsFolder': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'IsFolder',
        'return_type': 'bool',
    },
    'IsSortable': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'IsSortable',
        'return_type': 'bool',
    },
    'IsOnHeap': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'IsOnHeap',
        'return_type': 'bool',
    },
    'IsZombie': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'IsZombie',
        'return_type': 'bool',
    },
    'Notify': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Notify',
        'return_type': 'bool',
    },
    'Read': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Read',
        'return_type': 'int',
    },
    'Write': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'Write',
        'return_type': 'int',
    },
    'TestBit': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'TestBit',
        'return_type': 'bool',
    },
    'TestBits': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'TestBits',
        'return_type': 'int',
    },
    'GetDtorOnly': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetDtorOnly',
        'return_type': 'long',
    },
    'GetObjectStat': {
        'metadata_type': 'add_method_type_info',
        'type_string': 'TVector2',
        'method_name': 'GetObjectStat',
        'return_type': 'bool',
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
class TVector2:
    "A class"


    def Mod2(self) -> float:
        "A method"
        ...

    def Mod(self) -> float:
        "A method"
        ...

    def Px(self) -> float:
        "A method"
        ...

    def Py(self) -> float:
        "A method"
        ...

    def X(self) -> float:
        "A method"
        ...

    def Y(self) -> float:
        "A method"
        ...

    def Phi(self) -> float:
        "A method"
        ...

    def DeltaPhi(self, v: TVector2) -> float:
        "A method"
        ...

    def Unit(self) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Ort(self) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Proj(self, v: TVector2) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Norm(self, v: TVector2) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Rotate(self, phi: float) -> func_adl_servicex_xaodr21.tvector2.TVector2:
        "A method"
        ...

    def Phi_0_2pi(self, x: float) -> float:
        "A method"
        ...

    def Phi_mpi_pi(self, x: float) -> float:
        "A method"
        ...

    def DeclFileName(self) -> str:
        "A method"
        ...

    def ImplFileLine(self) -> int:
        "A method"
        ...

    def ImplFileName(self) -> str:
        "A method"
        ...

    def Class_Name(self) -> str:
        "A method"
        ...

    def DeclFileLine(self) -> int:
        "A method"
        ...

    def Hash(self) -> int:
        "A method"
        ...

    def ClassName(self) -> str:
        "A method"
        ...

    def CheckedHash(self) -> int:
        "A method"
        ...

    def DistancetoPrimitive(self, px: int, py: int) -> int:
        "A method"
        ...

    def GetUniqueID(self) -> int:
        "A method"
        ...

    def GetName(self) -> str:
        "A method"
        ...

    def GetIconName(self) -> str:
        "A method"
        ...

    def GetObjectInfo(self, px: int, py: int) -> str:
        "A method"
        ...

    def GetTitle(self) -> str:
        "A method"
        ...

    def HasInconsistentHash(self) -> bool:
        "A method"
        ...

    def InheritsFrom(self, classname: int) -> bool:
        "A method"
        ...

    def IsFolder(self) -> bool:
        "A method"
        ...

    def IsSortable(self) -> bool:
        "A method"
        ...

    def IsOnHeap(self) -> bool:
        "A method"
        ...

    def IsZombie(self) -> bool:
        "A method"
        ...

    def Notify(self) -> bool:
        "A method"
        ...

    def Read(self, name: int) -> int:
        "A method"
        ...

    def Write(self, name: int, option: int, bufsize: int) -> int:
        "A method"
        ...

    def TestBit(self, f: int) -> bool:
        "A method"
        ...

    def TestBits(self, f: int) -> int:
        "A method"
        ...

    def GetDtorOnly(self) -> int:
        "A method"
        ...

    def GetObjectStat(self) -> bool:
        "A method"
        ...
