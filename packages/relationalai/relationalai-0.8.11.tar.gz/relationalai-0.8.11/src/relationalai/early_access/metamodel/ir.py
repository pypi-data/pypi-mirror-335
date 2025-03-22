"""
    Intermediate Representation of RelationalAI programs.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from itertools import count
from typing import Any, IO, Optional, Tuple, TypeVar, Union as PyUnion

from .util import FrozenOrderedSet

import json
import rich

#--------------------------------------------------
# IR Nodes
#--------------------------------------------------

_global_id = count(0)
def next_id():
    return next(_global_id)

@dataclass(frozen=True)
class Node:
    # A generated id that is not used on comparisons and hashes
    id: int = field(default_factory=next_id, init=False, compare=False, hash=False)

    @property
    def kind(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return node_to_string(self)

#-------------------------------------------------
# Public Types - Model
#-------------------------------------------------

@dataclass(frozen=True)
class Model(Node):
    """Represents the whole universe of elements that make up a program."""
    engines: FrozenOrderedSet["Engine"]
    relations: FrozenOrderedSet["Relation"]
    types: FrozenOrderedSet["Type"]
    root: Task


#-------------------------------------------------
# Public Types - Engine
#-------------------------------------------------

@dataclass(frozen=True)
class Capability(Node):
    """Engine capabilities, such as 'graph algorithms', 'solver', 'constant time count', etc"""
    name: str

@dataclass(frozen=True)
class Engine(Node):
    """The entity that owns a Task and provides access to certain relations."""
    name: str
    platform: str # SQL, Rel, JS, OpenAI, etc
    info: Any
    capabilities: FrozenOrderedSet[Capability]
    relations: FrozenOrderedSet["Relation"]


#-------------------------------------------------
# Public Types - Data Model
#-------------------------------------------------

@dataclass(frozen=True)
class ScalarType(Node):
    """The named type."""
    name: str

@dataclass(frozen=True)
class ListType(Node):
    """A type that represents a list of elements of some other type."""
    element_type: Type

@dataclass(frozen=True)
class SetType(Node):
    """A type that represents a set of elements of some other type."""
    element_type: Type

@dataclass(frozen=True)
class UnionType(Node):
    """A type that represents either one of a set of types."""
    types: FrozenOrderedSet[Type]

# The type of a field in a relation
Type = PyUnion[ScalarType, ListType, SetType, UnionType]

@dataclass(frozen=True)
class Field(Node):
    """A named field in a relation."""
    name: str
    type: Type
    input: bool # must be grounded as the relation cannot compute it


@dataclass(frozen=True)
class Relation(Node):
    """A relation represents the schema of a set of tuples."""
    name: str
    fields: Tuple[Field, ...]
    requires: FrozenOrderedSet[Capability]


#-------------------------------------------------
# Public Types - Tasks
#-------------------------------------------------

@dataclass(frozen=True)
class Task(Node):
    engine: Optional[Engine]

#
# Task composition
#

@dataclass(frozen=True)
class Logical(Task):
    """Execute sub-tasks up to fix-point."""
    # Executes tasks concurrently. Succeeds if every task succeeds.
    hoisted: Tuple[Var, ...]
    body: Tuple[Task, ...]

@dataclass(frozen=True)
class Union(Task):
    """Execute sub-tasks in any order."""
    # Executes tasks concurrently. Succeeds if at least one task succeeds.
    hoisted: Tuple[Var, ...]
    tasks: Tuple[Task, ...]

@dataclass(frozen=True)
class Sequence(Task):
    """Execute sub-tasks one at a time, in this order."""
    # Executes tasks in order. Stops when a task fails. Succeeds if all tasks succeed.
    hoisted: Tuple[Var, ...]
    tasks: Tuple[Task, ...]

@dataclass(frozen=True)
class Match(Task):
    """Execute sub-tasks in order until the first succeeds."""
    # Executes tasks in order. Stops when a task succeeds. Succeeds if some task succeeds.
    hoisted: Tuple[Var, ...]
    tasks: Tuple[Task, ...]

@dataclass(frozen=True)
class Until(Task):
    """Execute both `check` and `body` concurrently, until check succeeds."""
    hoisted: Tuple[Var, ...]
    check: Task
    body: Task

@dataclass(frozen=True)
class Wait(Task):
    hoisted: Tuple[Var, ...]
    check: Task

# TODO: DynamicLookup


#
# Logical Quantifiers
#

@dataclass(frozen=True)
class Not(Task):
    """Logical negation of the sub-task."""
    task: Task

@dataclass(frozen=True)
class Exists(Task):
    """Existential quantification over the sub-task."""
    vars: Tuple[Var, ...]
    task: Task

@dataclass(frozen=True)
class ForAll(Task):
    """Universal quantification over the sub-task."""
    vars: Tuple[Var, ...]
    task: Task


#
# Iteration (Loops)
#

# loops body until a break condition is met
@dataclass(frozen=True)
class Loop(Task):
    """Execute the body in a loop, incrementing the iter variable, until a break sub-task in
    the body succeeds."""
    hoisted: Tuple[Var, ...]
    iter: Var
    body: Task

@dataclass(frozen=True)
class Break(Task):
    """Break a surrounding Loop if the `check` succeeds."""
    check: Task


#
# Relational Operations
#

@dataclass(frozen=True)
class Var(Node):
    """A variable with an optional name, that can point to objects of this type."""
    type: Type
    name: str

@dataclass(frozen=True)
class Literal(Node):
    """A literal value with a specific type."""
    type: Type
    value: Any

Value = PyUnion[str, int, float, bool, None, Var, Literal, Type, Relation, Tuple["Value", ...], FrozenOrderedSet["Value"]]

@dataclass(frozen=True)
class Annotation(Node):
    """Meta information that can be attached to Updates."""
    relation: Relation
    args: Tuple[Value, ...]

class Effect(Enum):
    """Possible effects of an Update."""
    derive = "derive"
    insert = "insert"
    delete = "delete"

@dataclass(frozen=True)
class Update(Task):
    """Updates the relation with these arguments. The update can derive new tuples
    temporarily, can insert new tuples persistently, or delete previously persisted tuples."""
    relation: Relation
    args: Tuple[Value, ...]
    effect: Effect
    annotations: FrozenOrderedSet[Annotation]

@dataclass(frozen=True)
class Lookup(Task):
    """Lookup tuples from this relation, filtering with these arguments."""
    relation: Relation
    args: Tuple[Value, ...]

@dataclass(frozen=True)
class Output(Task):
    """Output the value of these vars, giving them these column names."""
    aliases: FrozenOrderedSet[Tuple[str, Var]]

@dataclass(frozen=True)
class Construct(Task):
    """Construct an id from these values, and bind the id to this var."""
    values: Tuple[Value, ...]
    id_var: Var

@dataclass(frozen=True)
class Aggregate(Task):
    """Perform an aggregation with these arguments."""
    aggregation: Relation
    projection: Tuple[Var, ...]
    group: Tuple[Var, ...]
    args: Tuple[Value, ...]


#--------------------------------------------------
# Printer
#--------------------------------------------------

infix = ["+", "-", "*", "/", "%", "=", "!=", "<", "<=", ">", ">="]

def indent_print(depth, io: Optional[IO[str]], *args) -> None:
    """ Helper to print the arguments into the io with indented based on depth. """
    if io is None:
        rich.print("    " * depth + " ".join(map(str, args)))
    else:
        io.write("    " * depth + " ".join(map(str, args)) + "\n")

def print_hoisted(depth, io: Optional[IO[str]], name, hoisted: Tuple[Var, ...]):
    if hoisted:
        indent_print(depth, io, f"{name} ⇑\\[{', '.join([h.name for h in hoisted])}]")
    else:
        indent_print(depth, io, name)

def value_to_string(value:PyUnion[Value, Tuple[Value, ...]]) -> str:
    """ Return a string representation of the value. """
    if isinstance(value, (int, str, float, bool)):
        return json.dumps(value)
    elif value is None:
        return "None"
    elif isinstance(value, Var):
        return value.name
    elif isinstance(value, Literal):
        return f"{json.dumps(value.value)}"
    elif isinstance(value, ListType):
        return f"[{value_to_string(value.element_type)}]"
    elif isinstance(value, SetType):
        return f"{{{value_to_string(value.element_type)}}}"
    elif isinstance(value, UnionType):
        return f"{{{'; '.join(map(value_to_string, value.types))}}}"
    elif isinstance(value, ScalarType):
        return f"{value.name}"
    elif isinstance(value, Relation):
        return value.name
    elif isinstance(value, Tuple):
        return f"({', '.join(map(value_to_string, value))})"
    elif isinstance(value, FrozenOrderedSet):
        return f"{{{', '.join(map(value_to_string, value))}}}"
    else:
        raise NotImplementedError(f"value_to_string not implemented for {type(value)}")

def node_to_string(node:Node|Tuple[T, ...]|FrozenOrderedSet[T]) -> str:
    io = StringIO()
    pprint(node, io = io)
    return io.getvalue()

T = TypeVar('T', bound=Node)
def pprint(node:Node|Tuple[T, ...]|FrozenOrderedSet[T], depth=0, io: Optional[IO[str]] = None) -> None:
    """ Pretty print the node into the io, starting with indentation based on depth. If io is None,
    print into the standard output. """

    if isinstance(node, Tuple) or isinstance(node, FrozenOrderedSet):
        for n in node:
            pprint(n, depth, io)
    # model
    elif isinstance(node, Model):
        indent_print(depth, io, "Model")
        if len(node.engines) > 0:
            indent_print(depth + 1, io, "engines:")
        pprint(node.engines, depth + 2, io)
        if len(node.relations) > 0:
            indent_print(depth + 1, io, "relations:")
        pprint(node.relations, depth + 2, io)
        if len(node.types) > 0:
            indent_print(depth + 1, io, "types:")
        pprint(node.types, depth + 2, io)
        indent_print(depth + 1, io, "root:")
        pprint(node.root, depth + 2, io)

    # engine
    elif isinstance(node, Capability):
        indent_print(depth, io, node.name)
    elif isinstance(node, Engine):
        indent_print(depth, io, f"Engine ({node.name}, {node.platform})")
        indent_print(depth + 1, io, node.info)
        indent_print(depth + 1, io, ', '.join([c.name for c in node.capabilities]))
        pprint(node.relations, depth + 1, io)

    # data model
    elif isinstance(node, (ScalarType, ListType, SetType, UnionType)):
        indent_print(depth, io, value_to_string(node))
    elif isinstance(node, Field):
        s = f"{node.name}: {value_to_string(node.type)} {'(input)' if node.input else ''}"
        indent_print(depth, io, s)
    elif isinstance(node, Relation):
        indent_print(depth, io, node.name)
        pprint(node.fields, depth + 1, io)
        if len(node.requires) > 0:
            indent_print(depth + 1, io, "requires:")
            pprint(node.requires, depth + 2, io)

    # tasks

    # Task composition
    elif isinstance(node, Logical):
        print_hoisted(depth, io, "Logical", node.hoisted)
        pprint(node.body, depth + 1, io)
    elif isinstance(node, Sequence):
        print_hoisted(depth, io, "Sequence", node.hoisted)
        pprint(node.tasks, depth + 1, io)
    elif isinstance(node, Union):
        print_hoisted(depth, io, "Union", node.hoisted)
        pprint(node.tasks, depth + 1, io)
    elif isinstance(node, Match):
        print_hoisted(depth, io, "Match", node.hoisted)
        pprint(node.tasks, depth + 1, io)
    elif isinstance(node, Until):
        print_hoisted(depth, io, "Until", node.hoisted)
        pprint(node.check, depth + 1, io)
        pprint(node.body, depth + 1, io)
    elif isinstance(node, Wait):
        print_hoisted(depth, io, "Match", node.hoisted)
        pprint(node.check, depth + 1, io)

    # Relational Operations
    elif isinstance(node, Var):
        indent_print(0, io, value_to_string(node))
    elif isinstance(node, Literal):
        indent_print(0, io, value_to_string(node))
    elif isinstance(node, Annotation):
        if node.args:
            indent_print(depth, io, f"@{node.relation.name}{value_to_string(node.args)}")
        else:
            indent_print(depth, io, f"@{node.relation.name}")
    elif isinstance(node, Update):
        rel_name = node.relation.name
        annos = "" if not node.annotations else f" {' '.join(str(a) for a in node.annotations)}"
        indent_print(depth, io, f"→ {node.effect.value} {rel_name}{value_to_string(node.args)}{annos}")
    elif isinstance(node, Lookup):
        rel_name = node.relation.name
        if rel_name in infix:
            args = [value_to_string(arg) for arg in node.args]
            if len(node.args) == 2:
                indent_print(depth, io, f"{args[0]} {rel_name} {args[1]}")
            elif len(node.args) == 1:
                indent_print(depth, io, f"{rel_name}{args[0]}")
            elif len(node.args) == 3:
                indent_print(depth, io, f"{args[2]} = {args[0]} {rel_name} {args[1]}")
        else:
            indent_print(depth, io, f"{rel_name}{value_to_string(node.args)}")
    elif isinstance(node, Output):
        args = []
        for k, v in node.aliases:
            ppv = value_to_string(v)
            if k != ppv:
                args.append(f"{ppv} as '{k}'")
            else:
                args.append(ppv)
        indent_print(depth, io, f"→ output({', '.join(args)})")
    elif isinstance(node, Construct):
        values = [value_to_string(v) for v in node.values]
        indent_print(depth, io, f"construct({', '.join(values)}, {value_to_string(node.id_var)})")
    elif isinstance(node, Aggregate):
        indent_print(depth, io, f"{node.aggregation.name}([{value_to_string(node.projection)}], [{value_to_string(node.group)}], [{value_to_string(node.args)}])")

    # Logical Quantifiers
    elif isinstance(node, Not):
        indent_print(depth, io, "Not")
        pprint(node.task, depth + 1, io)
    elif isinstance(node, Exists):
        indent_print(depth, io, f"Exists({', '.join([value_to_string(v) for v in node.vars])})")
        pprint(node.task, depth + 1, io)
    elif isinstance(node, ForAll):
        indent_print(depth, io, f"ForAll({', '.join([value_to_string(v) for v in node.vars])})")
        pprint(node.task, depth + 1, io)

    # Iteration (Loops)
    elif isinstance(node, Loop):
        print_hoisted(depth, io, f"Loop ⇓\\[{value_to_string(node.iter)}]", node.hoisted)
        pprint(node.body, depth + 1, io)

    elif isinstance(node, Break):
        indent_print(depth, io, "Break")
        pprint(node.check, depth + 1, io)

    elif isinstance(node, Task):
        # empty task represents success
        indent_print(depth, io, "Success")

    else:
        # return
        raise NotImplementedError(f"pprint not implemented for {type(node)}")
