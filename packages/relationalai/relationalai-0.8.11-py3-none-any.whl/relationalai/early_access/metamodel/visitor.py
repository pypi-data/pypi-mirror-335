"""
    Support for traversing the IR, often to search for information.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional, TypeVar, cast

from .util import OrderedSet, ordered_set
from . import ir

#--------------------------------------------------
# Visitor Abstraction
#--------------------------------------------------

@dataclass
class Visitor:

    def accept(self, n: ir.Node, parent: Optional[ir.Node]=None):
        # visit the node and decide whether to visit children
        if self.visit(n, parent):
            # accept its children
            handler = getattr(self, f"accept_{n.kind}", None)
            if handler:
                # TODO: we currently don't accept Values, only Nodes, should we?
                handler(n)

            # visit the node again
            self.post_visit(n, parent)

    def visit(self, n: ir.Node, parent: Optional[ir.Node]) -> bool:
        """ Visit the node. Returns whether children should be visited next. """
        return True

    def post_visit(self, n: ir.Node, parent: Optional[ir.Node]):
        """ Visit the node again, after children were visited. """
        pass

    #-------------------------------------------------
    # Public Types - Model
    #-------------------------------------------------

    def accept_model(self, model: ir.Model):
        for c in model.engines:
            self.accept(c, model)
        for c in model.relations:
            self.accept(c, model)
        for c in model.types:
            self.accept(c, model)
        self.accept(model.root, model)

    #-------------------------------------------------
    # Public Types - Engine
    #-------------------------------------------------

    def accept_engine(self, engine: ir.Engine):
        for c in engine.capabilities:
            self.accept(c, engine)
        for c in engine.relations:
            self.accept(c, engine)

    #-------------------------------------------------
    # Public Types - Data Model
    #-------------------------------------------------

    def accept_listtype(self, node: ir.ListType):
        self.accept(node.element_type, node)

    def accept_settype(self, node: ir.SetType):
        self.accept(node.element_type, node)

    def accept_uniontype(self, node: ir.UnionType):
        for t in node.types:
            self.accept(t, node)

    def accept_field(self, field: ir.Field):
        self.accept(field.type, field)

    def accept_relation(self, relation: ir.Relation):
        for c in relation.fields:
            self.accept(c, relation)
        for c in relation.requires:
            self.accept(c, relation)

    #-------------------------------------------------
    # Public Types - Tasks
    #-------------------------------------------------

    def accept_task(self, task: ir.Task):
        if task.engine:
            self.accept(task.engine, task)
    #
    # Task composition
    #

    def accept_logical(self, task: ir.Logical):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        for c in task.body:
            self.accept(c, task)

    def accept_union(self, task: ir.Union):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        for c in task.tasks:
            self.accept(c, task)

    def accept_sequence(self, task: ir.Sequence):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        for c in task.tasks:
            self.accept(c, task)

    def accept_match(self, task: ir.Match):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        for c in task.tasks:
            self.accept(c, task)

    def accept_until(self, task: ir.Until):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        self.accept(task.check, task)
        self.accept(task.body, task)

    def accept_wait(self, task: ir.Wait):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        self.accept(task.check, task)

    #
    # Logical Quantifiers
    #

    def accept_not(self, task: ir.Not):
        self.accept_task(task)
        self.accept(task.task, task)

    def accept_exists(self, task: ir.Exists):
        self.accept_task(task)
        for c in task.vars:
            self.accept(c, task)
        self.accept(task.task, task)

    def accept_forall(self, task: ir.ForAll):
        self.accept_task(task)
        for c in task.vars:
            self.accept(c, task)
        self.accept(task.task, task)

    #
    # Iteration (Loops)
    #
    def accept_loop(self, task: ir.Loop):
        self.accept_task(task)
        for v in task.hoisted:
            self.accept(v, task)
        self.accept(task.iter, task)
        self.accept(task.body, task)

    def accept_break(self, task: ir.Break):
        self.accept_task(task)
        self.accept(task.check, task)

    #
    # Relational Operations
    #

    def accept_var(self, var: ir.Var):
        self.accept(var.type, var)

    def accept_literal(self, lit: ir.Literal):
        self.accept(lit.type, lit)

    def accept_annotation(self, anno: ir.Annotation):
        self.accept(anno.relation, anno)
        for a in anno.args:
            if isinstance(a, ir.Node):
                self.accept(a, anno)

    def accept_update(self, task: ir.Update):
        self.accept_task(task)
        self.accept(task.relation, task)
        for a in task.args:
            if isinstance(a, ir.Node):
                self.accept(a, task)
        for a in task.annotations:
            if isinstance(a, ir.Node):
                self.accept(a, task)

    def accept_lookup(self, task: ir.Lookup):
        self.accept_task(task)
        self.accept(task.relation, task)
        for a in task.args:
            if isinstance(a, ir.Node):
                self.accept(a, task)

    def accept_output(self, task: ir.Output):
        self.accept_task(task)
        for _, var in task.aliases:
            self.accept(var, task)

    def accept_construct(self, task: ir.Construct):
        self.accept_task(task)
        for a in task.values:
            if isinstance(a, ir.Node):
                self.accept(a, task)
        self.accept(task.id_var, task)

    def accept_aggregate(self, task: ir.Aggregate):
        self.accept_task(task)
        self.accept(task.aggregation, task)
        for v in task.projection:
            self.accept(v, task)
        for v in task.group:
            self.accept(v, task)
        for a in task.args:
            if isinstance(a, ir.Node):
                self.accept(a, task)

#--------------------------------------------------
# Some generally useful visitors
#--------------------------------------------------
# TODO: consider moving this to its own module.

class HandlerVisitor(Visitor):
    """ A visitor that dispatches to type-specific methods. """
    def visit(self, n: ir.Node, parent: Optional[ir.Node]):
        handler = getattr(self, f"visit_{n.kind}", None)
        if handler:
            return handler(n, parent)
        return True


class Collector(Visitor):
    """ A visitor that collects instances that match a predicate. """
    def __init__(self, predicate: Callable[[ir.Node, Optional[ir.Node]], bool]):
        self.elements: OrderedSet = ordered_set()
        self.predicate = predicate

    def visit(self, n: ir.Node, parent: Optional[ir.Node]):
        if self.predicate(n, parent):
            self.elements.add(n)
        return True

def collect(predicate: Callable[[ir.Node, Optional[ir.Node]], bool], *nodes: ir.Node) -> OrderedSet[ir.Node]:
    """ Collect children of node that match the predicate. """
    c = Collector(predicate)
    for n in nodes:
        c.accept(n)
    return c.elements

T = TypeVar('T')
def collect_by_type(t: type[T], *nodes: ir.Node) -> OrderedSet[T]:
    """ Collect instances of the type t by traversing this node and its children. """
    return cast(OrderedSet[T],
        collect(lambda n, parent: isinstance(n, t), *nodes)
    )

def collect_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect all Vars starting at this node. """
    return cast(OrderedSet[ir.Var],
        collect(lambda n, parent: isinstance(n, ir.Var), *nodes)
    )

def collect_quantified_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect all Vars that are children of Exists and ForAll. """
    return cast(OrderedSet[ir.Var],
        collect(lambda n, parent: isinstance(parent, (ir.Exists, ir.ForAll)), *nodes)
    )

def collect_aggregate_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect vars that are declared by aggregates in Rel (projection + over). """
    return cast(OrderedSet[ir.Var],
        # TODO - when dealing with multiple aggregations we will need to consider groupbys
        collect(
            lambda n, parent:
                # var is in an aggregate and either
                isinstance(parent, (ir.Aggregate)) and (
                # var is in the projection
                n in parent.projection or
                # var is in the "over" parameter
                (len(parent.args) > 1 and n == parent.args[-2])
                ),
            *nodes)
    )

def collect_implicit_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect vars except the quantified vars. """
    return collect_vars(*nodes) - collect_quantified_vars(*nodes) - collect_aggregate_vars(*nodes)



@dataclass
class ReadWriteVisitor(Visitor):
    """
    Compute the set of reads and writes for Logical nodes.

    Note that reads are Lookups and writes are Updates. We don't consider Output a write
    because it is not targeting a relation.
    """
    # TODO: we currently only compute for Logical nodes, but it may be useful for other nodes
    _reads: dict[ir.Logical, OrderedSet[ir.Relation]] = field(default_factory=dict)
    _writes: dict[ir.Logical, OrderedSet[ir.Relation]] = field(default_factory=dict)

    def reads(self, key: ir.Logical):
        # TODO - use a singleton empty set
        return self._reads[key] if key in self._reads else ordered_set()

    def writes(self, key: ir.Logical):
        return self._writes[key] if key in self._writes else ordered_set()

    _stack: list[ir.Logical] = field(default_factory=list)

    def visit(self, n: ir.Node, parent: Optional[ir.Node]):
        if isinstance(n, ir.Logical):
            self._stack.append(n)
        elif isinstance(n, ir.Lookup) or isinstance(n, ir.Aggregate):
            for lu in self._stack:
                if lu not in self._reads:
                    self._reads[lu] = ordered_set()
                if isinstance(n, ir.Lookup):
                    self._reads[lu].add(n.relation)
                else:
                    self._reads[lu].add(n.aggregation)
        elif isinstance(n, ir.Update):
            for lu in self._stack:
                if lu not in self._writes:
                    self._writes[lu] = ordered_set()
                self._writes[lu].add(n.relation)
        return True

    def post_visit(self, n: ir.Node, parent: Optional[ir.Node]):
        if isinstance(n, ir.Logical):
            self._stack.pop()
