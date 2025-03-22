"""
    Functions to simplify the creation of IR nodes using some common variations.
"""
from __future__ import annotations
from typing import Any, Tuple, Optional, Sequence as PySequence, Union
import decimal

from relationalai.early_access.metamodel import ir, types
from relationalai.early_access.metamodel.util import OrderedSet, FrozenOrderedSet, frozen, ordered_set
from relationalai.early_access.metamodel.visitor import collect_by_type


#-------------------------------------------------
# Public Types - Model
#-------------------------------------------------

def model(
        engines: OrderedSet[ir.Engine],
        relations: OrderedSet[ir.Relation],
        types: OrderedSet[ir.Type],
        root: ir.Task):
    return ir.Model(
        engines.frozen(),
        relations.frozen(),
        types.frozen(),
        root
    )

def compute_model(root: ir.Task) -> ir.Model:
    return model(
        collect_by_type(ir.Engine, root),
        collect_by_type(ir.Relation, root),
        collect_by_type(ir.Type, root),
        root
    )

def install(model: ir.Model, logical_task: ir.Logical) -> ir.Model:
    """ Return a new model that represents this model with the logical task as the root task. """

    # the model's root is interpreted as the "installed model", we want a model that
    # computes those tasks and succeeds only if the incoming logical task l succeeds. To do
    # so, we create a new model whose root task is a logical; this logical succeeds if l
    # succeeds, taking into account the installed model. So we wrap the installed model in a
    # union with an empty Task, which always succeeds, to guarantee that the installed model
    # always "succeeds".

    # TODO: when installing a logical, we may need to bring new engines, relations and types;
    # we can either extend this function's interface to receive that (basically a new model
    # to be merged), or we can traverse `l` to lookup engines/relations/types to add to the
    # new model.
    # TODO: is it OK to make an empty Task represent "success"?
    return ir.Model(
        model.engines, model.relations, model.types,
        logical(
            [logical_task, union([model.root, ir.Task(None)])]
        )
    )

def install_logical(rules: ir.Logical, select: ir.Logical, engine: Optional[ir.Engine]=None) -> ir.Logical:
    """ Similar to install but only manipulating the tasks."""
    # TODO - this may not be necessary because it is OK if the `select` logical fails, it just
    # returns false, i.e. no values.
    return logical([
        select,
        union([rules, ir.Task(None)])
    ], [], engine)

#-------------------------------------------------
# Public Types - Engine
#-------------------------------------------------

def capability(name: str):
    return ir.Capability(name)

def engine(name: str, platform: str, relations:OrderedSet[ir.Relation], info: Any=None, capabilities: OrderedSet[ir.Capability]=ordered_set()):
    return ir.Engine(name, platform, info, capabilities.frozen(), relations.frozen())

#-------------------------------------------------
# Public Types - Data
#-------------------------------------------------

def scalar_type(name: str):
    return ir.ScalarType(name)

def list_type(element_type: ir.Type):
    return ir.ListType(element_type)

def set_type(element_type: ir.Type):
    return ir.SetType(element_type)

def union_type(types: list[ir.Type]):
    return ir.UnionType(FrozenOrderedSet(types))

def field(name: str, type: ir.Type, input: bool=False):
    return ir.Field(name, type, input)

def input_field(name:str, type: ir.Type):
    return ir.Field(name, type, True)


# property helpers
def relation(name: str, fields: list[ir.Field], requires: OrderedSet[ir.Capability]=ordered_set()):
    return ir.Relation(name, tuple(fields), requires.frozen())

def entity(type: ir.ScalarType):
    return relation(type.name, [field("id", type)])

def property(name: str, key_name: str, key_type: ir.Type, value_name:str, value_type: ir.Type):
    return relation(
        name,
        [field(key_name, key_type), field(value_name, value_type)]
    )

#-------------------------------------------------
# Public Types - Tasks
#-------------------------------------------------

def success():
    return ir.Task(None)

#
# Task composition
#

def logical(body: PySequence[ir.Task], hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Logical(engine, tuple(hoisted), tuple(body))

def sequence(tasks: PySequence[ir.Task], hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Sequence(engine, tuple(hoisted), tuple(tasks))

def union(tasks: PySequence[ir.Task], hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Union(engine, tuple(hoisted), tuple(tasks))

def match(tasks: PySequence[ir.Task], hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Match(engine, tuple(hoisted), tuple(tasks))

def until(check: ir.Task, body: ir.Task, hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Until(engine, tuple(hoisted), check, body)

def wait(check: ir.Task, hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Wait(engine, tuple(hoisted), check)

#
# Relational Operations
#

def var(name: str, type: Union[ir.Type, None] = None) -> ir.Var:
    if type is None:
        return ir.Var(types.Any, name)
    else:
        return ir.Var(type, name)

def wild() -> ir.Var:
    return var("_", types.Any)

def literal(value: Any, type: Union[ir.Type, None] = None) -> ir.Value:
    """ Create a Literal with this type. If type is not present, attempt to figure out the
    appropriate type. See: `l`. """
    if type is None:
        return lit(value)
    else:
        return ir.Literal(type, value)

def lit(value: Any) -> ir.Value:
    """ Ensure this value is an appropriate ir.Value. This function wraps common python values
     in ir.Literals, and supports lists of values. """
    if isinstance(value, ir.Literal):
        return value
    elif isinstance(value, str):
        return ir.Literal(types.String, value)
    elif isinstance(value, int):
        return ir.Literal(types.Int, value)
    elif isinstance(value, float):
        return ir.Literal(types.Decimal, value)
    elif isinstance(value, bool):
        return ir.Literal(types.Bool, value)
    elif isinstance(value, decimal.Decimal):
        return ir.Literal(types.Decimal, float(value))
    elif isinstance(value, list):
        return tuple([lit(v) for v in value])
    else:
        raise NotImplementedError(f"literal value: {value} of type {type(value)}")

def annotation(relation: ir.Relation, args: PySequence[ir.Value]) -> ir.Annotation:
    return ir.Annotation(relation, tuple(args))

def derive(relation: ir.Relation, args: PySequence[ir.Value], annos: Optional[PySequence[ir.Annotation]]=None, engine: Optional[ir.Engine]=None):
    return ir.Update(engine, relation, tuple(args), ir.Effect.derive, frozen() if annos is None else FrozenOrderedSet(annos))

def insert(relation: ir.Relation, args: PySequence[ir.Value], annos: Optional[PySequence[ir.Annotation]]=None, engine: Optional[ir.Engine]=None):
    return ir.Update(engine, relation, tuple(args), ir.Effect.insert, frozen() if annos is None else FrozenOrderedSet(annos))

def delete(relation: ir.Relation, args: PySequence[ir.Value], annos: Optional[PySequence[ir.Annotation]]=None, engine: Optional[ir.Engine]=None):
    return ir.Update(engine, relation, tuple(args), ir.Effect.delete, frozen() if annos is None else FrozenOrderedSet(annos))

def lookup(relation: ir.Relation, args: PySequence[ir.Value], engine: Optional[ir.Engine]=None):
    return ir.Lookup(engine, relation, tuple(args))

def update(relation: ir.Relation, args: PySequence[ir.Value], effect: ir.Effect, annos: Optional[PySequence[ir.Annotation]]=None, engine: Optional[ir.Engine]=None):
    return ir.Update(engine, relation, tuple(args), effect, frozen() if annos is None else FrozenOrderedSet(annos))

def output(vars: PySequence[Union[ir.Var, Tuple[str, ir.Var]]], engine: Optional[ir.Engine]=None):
    """Create an output task that will return values bound to these variables. The vars
    sequence can contain plain Vars, in which case the alias used in the output is the
    variable name. This alias can be customized by adding a tuple (alias, Var) to vars.
    """
    s = ordered_set()
    for x in vars:
        if isinstance(x, ir.Var):
            s.add((x.name, x))
        else:
            s.add(x)
    return ir.Output(engine, s.frozen())


def construct(var: ir.Var, bindings: dict[ir.Relation, Any], engine: Optional[ir.Engine]=None):
    """Create a Construct node that will create an id and bind to this var. The id will be a
    hash of the types of the var, followed by the name and value of the bindings."""
    values = []
    values.append(var.type)
    for relation, value in bindings.items():
        values.append(ir.Literal(types.String, relation.name))
        values.append(value)
    return ir.Construct(engine, tuple(values), var)

def aggregate(aggregation: ir.Relation, projection: PySequence[ir.Var], group: PySequence[ir.Var], args: PySequence[Any], engine: Optional[ir.Engine]=None):
    return ir.Aggregate(engine, aggregation, tuple(projection), tuple(group), tuple(args))


#
# Logical Quantifiers
#

def not_(task: ir.Task, engine: Optional[ir.Engine]=None):
    return Not(task, engine)

def Not(task: ir.Task, engine: Optional[ir.Engine]=None):
    return ir.Not(engine, task)

def exists(vars: PySequence[ir.Var], task: ir.Task, engine: Optional[ir.Engine]=None):
    return ir.Exists(engine, tuple(vars), task)

def for_all(vars: PySequence[ir.Var], task: ir.Task, engine: Optional[ir.Engine]=None):
    return ir.ForAll(engine, tuple(vars), task)


#
# Iteration (Loops)
#

# loops body until a break condition is met
def loop(iter: ir.Var, body: ir.Task, hoisted: PySequence[ir.Var]=[], engine: Optional[ir.Engine]=None):
    return ir.Loop(engine, tuple(hoisted), iter, body)

def break_(check: ir.Task, engine: Optional[ir.Engine]=None):
    return Break(check, engine)

def Break(check: ir.Task, engine: Optional[ir.Engine]=None):
    return ir.Break(engine, check)
