"""
    Elementary IR relations.
"""
import sys

from . import ir, factory as f
from . import types

#
# Relations
#

# Conversions
string = f.relation("string", [f.input_field("a", types.Any), f.field("b", types.String)])
parse_date = f.relation("parse_date", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.Number)])
parse_datetime = f.relation("parse_datetime", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.Number)])
parse_decimal = f.relation("parse_decimal", [f.input_field("a", types.Int), f.input_field("b", types.Int), f.input_field("c", types.String), f.field("d", types.Decimal)])

# Comparators
def _comparator(name: str):
    return f.relation(name, [f.input_field("a", types.Number), f.input_field("b", types.Number)])

gt = _comparator(">")
gte = _comparator(">=")
lt = _comparator("<")
lte = _comparator("<=")
neq = _comparator("!=")
eq = _comparator("=")

# Arithmetic operators
def _binary_op(name: str):
    return f.relation(name, [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", types.Number)])

plus = _binary_op("+")
minus = _binary_op("-")
div = _binary_op("/")
mul = _binary_op("*")
mod = _binary_op("%")

abs = f.relation("abs", [f.input_field("a", types.Number), f.field("b", types.Number)])

# Other
# TODO careful with range - unlike rel, python stops at stop-1
range = f.relation("range", [
    f.input_field("start", types.Number),
    f.input_field("stop", types.Number),
    f.input_field("step", types.Number),
    f.field("result", types.NumberSet),
])
concat = f.relation("concat", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.String)])
hash = f.relation("rel_primitive_hash_tuple", [f.input_field("args", types.AnyList), f.field("hash", types.Hash)])

solverlib_fo_appl = f.relation("rel_primitive_solverlib_fo_appl", [
    f.input_field("op", types.Int),
    f.input_field("args", types.AnyList),
    f.field("result", types.String),
])

# Aggregations
def aggregation(name: str, params: list[ir.Field]):
    """Defines an aggregation, which is a Relation whose first 2 fields are a projection
    and a group, followed by the params."""
    fields = [
        f.input_field("projection", types.AnyList),
        f.input_field("group", types.AnyList)
    ] + params
    return f.relation(name, fields)

concat = aggregation("concat", [
    f.input_field("sep", types.String),
    f.input_field("over", types.StringSet),
    f.field("result", types.String)
])
# note that count does not need "over" because it counts the projection
count = aggregation("count", [
    f.field("result", types.Number)
])
stats = aggregation("stats", [
    f.input_field("over", types.NumberSet),
    f.field("std_dev", types.Number),
    f.field("mean", types.Number),
    f.field("median", types.Number),
])
sum = aggregation("sum", [
    f.input_field("over", types.NumberSet),
    f.field("result", types.Number)
])
max = aggregation("max", [
    f.input_field("over", types.NumberSet),
    f.field("result", types.Number)
])
min = aggregation("min", [
    f.input_field("over", types.NumberSet),
    f.field("result", types.Number)
])

solverlib_ho_appl = aggregation("rel_primitive_solverlib_ho_appl", [
    f.input_field("op", types.Int),
    f.field("result", types.String),
])

def is_builtin(t: ir.Relation):
    return t in builtin_relations

def _compute_builtin_relations() -> list[ir.Relation]:
    module = sys.modules[__name__]
    types = []
    for name in dir(module):
        builtin = getattr(module, name)
        if isinstance(builtin, ir.Relation):
            types.append(builtin)
    return types

builtin_relations = _compute_builtin_relations()
builtin_relations_by_name = dict((r.name, r) for r in builtin_relations)
