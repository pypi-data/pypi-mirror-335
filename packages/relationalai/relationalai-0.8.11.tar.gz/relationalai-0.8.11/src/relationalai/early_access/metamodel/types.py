"""
    Elementary IR types.
"""
from . import ir, util
import sys
from typing import cast


#
# Basic Types
#
Null = ir.ScalarType("Null")
Any = ir.ScalarType("Any")
Hash = ir.ScalarType("Hash")
String = ir.ScalarType("String")
Number = ir.ScalarType("Number")
Int = ir.ScalarType("Int")
Decimal = ir.ScalarType("Decimal")
Bool = ir.ScalarType("Bool")
Binary = ir.ScalarType("Binary") # 0 or 1
Symbol = ir.ScalarType("Symbol")

AnySet = ir.SetType(Any)
NumberSet = ir.SetType(Number)
StringSet = ir.SetType(String)
IntSet = ir.SetType(Int)

AnyList = ir.ListType(Any)
SymbolList = ir.ListType(Symbol)

def is_builtin(t: ir.Type):
    return t in builtin_types

def _compute_builtin_types() -> list[ir.Type]:
    module = sys.modules[__name__]
    types = []
    for name in dir(module):
        builtin = getattr(module, name)
        if isinstance(builtin, ir.Type):
            types.append(builtin)
    return types

builtin_types = _compute_builtin_types()
builtin_scalar_types_by_name = dict((t.name, t) for t in cast(list[ir.ScalarType], util.filter_by_type(builtin_types, ir.ScalarType)))
