from __future__ import annotations
from dataclasses import dataclass, field
import time
from typing import Any, Optional, Tuple, TypeVar, Union

from relationalai.early_access.metamodel import ir
from relationalai.early_access.metamodel.observer import Observer
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set, FrozenOrderedSet



@dataclass(frozen=True)
class Compiler():
    """ Compilers can rewrite a model into a different model, and can compile a model into
    a String, usually of a different language like Rel or SQL. """
    # configurable sequence of passes
    passes: list[Pass]

    def rewrite(self, model: ir.Model, observer: Optional[Observer]=None) -> ir.Model:
        """ Apply a sequence of transformation passes over a model, creating a new model. """
        for p in self.passes:
            start = time.perf_counter()
            model = p.walk(model)
            if observer is not None:
                observer.update(p.name, model, time.perf_counter() - start)
            p.reset()
        return model

    def compile(self, model: ir.Model, observer: Optional[Observer]=None) -> str:
        model = self.rewrite(model, observer)
        start = time.perf_counter()
        result = self.do_compile(model)
        if observer is not None:
            observer.update("compile", result, time.perf_counter() - start)
        return result

    def do_compile(self, model: ir.Model) -> str:
        """ Perform the compilation from model to string. The default implementation simply
        pretty prints the model IR. """
        return ir.node_to_string(model)

@dataclass
class Pass():
    """ A traversal over the model.

    This class provides handler methods for all types of nodes in the IR.

    The default implementation assumes that we will start traversal with a `Model` node, and
    that we are only interested in rewriting the model's root task. Therefore, the default
    handler implementation for engines and the data model simply return the node being
    traversed, as we don't want to modify them by default.

    Sub-classes can overwrite any of the handler methods to provide custom modifications.
    """
    # TODO: do we really need this?
    seen:OrderedSet[Any]  = field(default_factory=ordered_set)

    @property
    def name(self):
        return self.__class__.__name__

    def reset(self):
        self.seen.clear()

    T = TypeVar('T', bound=Union[ir.Node, ir.Value])
    def walk(self, node: T, parent=None, ctx:Optional[Any]=None) -> T:
        # if node is a value, just return it
        if not isinstance(node, ir.Node):
            return node

        # node is actually some Node type, handle with the appropriate handler
        handler = getattr(self, f"handle_{node.kind}", None)
        if handler:
            return handler(node, parent, ctx)
        else:
            raise NotImplementedError(f"walk: {node.kind}")

    def walk_set(self, items: FrozenOrderedSet[T], parent=None, ctx:Optional[Any]=None) -> FrozenOrderedSet[T]:
        return ordered_set(*[self.walk(n, parent, ctx) for n in items]).frozen()

    def walk_list(self, items: Tuple[T, ...], parent=None, ctx:Optional[Any]=None) -> Tuple[T, ...]:
        return tuple([self.walk(n, parent, ctx) for n in items])

    U = TypeVar('U', bound=Union[ir.Node, ir.Value, FrozenOrderedSet[ir.Relation]])

    def walk_dict(self, items: dict[str, U], parent=None, ctx:Optional[Any]=None) -> dict[str, U]:
        d = dict()
        for k, v in items.items():
            if isinstance(v, FrozenOrderedSet):
                d[k] = self.walk_set(v, parent, ctx) # type: ignore
            else:
                d[k] = self.walk(v, parent, ctx)
        return d



    #-------------------------------------------------
    # Public Types - Model
    #-------------------------------------------------

    def handle_model(self, model: ir.Model, parent: None, ctx:Optional[Any]=None):
        return ir.Model(
            self.walk_set(model.engines, model),
            self.walk_set(model.relations, model),
            self.walk_set(model.types, model),
            self.walk(model.root, model),
        )

    #-------------------------------------------------
    # Public Types - Engine
    #-------------------------------------------------

    def handle_capability(self, node: ir.Capability, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    def handle_engine(self, node: ir.Engine, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    #-------------------------------------------------
    # Public Types - Data Model
    #-------------------------------------------------

    def handle_scalartype(self, node: ir.ScalarType, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    def handle_listtype(self, node: ir.ListType, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    def handle_settype(self, node: ir.SetType, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    def handle_uniontype(self, node: ir.UnionType, parent: ir.Node, ctx:Optional[Any]=None):
        # TODO - we could traverse the children
        return node

    def handle_field(self, node: ir.Field, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    def handle_relation(self, node: ir.Relation, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    #-------------------------------------------------
    # Public Types - Tasks
    #-------------------------------------------------

    def handle_task(self, node: ir.Task, parent: ir.Node, ctx:Optional[Any]=None):
        return node

    #
    # Task composition
    #

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Logical(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk_list(node.body, node, ctx)
        )

    def handle_union(self, node: ir.Union, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Union(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk_list(node.tasks, node, ctx)
        )

    def handle_sequence(self, node: ir.Sequence, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Sequence(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk_list(node.tasks, node, ctx)
        )

    def handle_match(self, node: ir.Match, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Match(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk_list(node.tasks, node, ctx)
        )

    def handle_until(self, node: ir.Until, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Until(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk(node.check, node, ctx),
            self.walk(node.body, node, ctx)
        )

    def handle_wait(self, node: ir.Wait, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Wait(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk(node.check, node, ctx)
        )

    #
    # Relational Operations
    #

    def handle_var(self, node: ir.Var, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Var(
            self.walk(node.type, node, ctx),
            node.name or f"v{node.id}"
        )

    def handle_literal(self, node: ir.Literal, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Literal(
            self.walk(node.type, node, ctx),
            node.value
        )

    def handle_update(self, node: ir.Update, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Update(
            node.engine,
            self.walk(node.relation, node, ctx),
            self.walk_list(node.args, node, ctx),
            node.effect,
            node.annotations
        )

    def handle_lookup(self, node: ir.Lookup, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Lookup(
            node.engine,
            self.walk(node.relation, node, ctx),
            self.walk_list(node.args, node, ctx)
        )

    def handle_output(self, node: ir.Output, parent: ir.Node, ctx:Optional[Any]=None):
        s = ordered_set()
        for k, v in node.aliases:
            s.add((k, self.walk(v, ctx)))
        return ir.Output(node.engine, s.frozen())

    def handle_construct(self, node: ir.Construct, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Construct(
            node.engine,
            self.walk_list(node.values, node, ctx),
            node.id_var
        )

    def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Aggregate(
            node.engine,
            self.walk(node.aggregation, node, ctx),
            self.walk_list(node.projection, node, ctx),
            self.walk_list(node.group, node, ctx),
            self.walk_list(node.args, node, ctx)
        )

    #
    # Logical Quantifiers
    #

    def handle_not(self, node: ir.Not, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Not(
            node.engine,
            self.walk(node.task, node, ctx)
        )

    def handle_exists(self, node: ir.Exists, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Exists(
            node.engine,
            self.walk_list(node.vars, node, ctx),
            self.walk(node.task, node, ctx)
        )

    def handle_forall(self, node: ir.ForAll, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.ForAll(
            node.engine,
            self.walk_list(node.vars, node, ctx),
            self.walk(node.task, node, ctx),
        )

    #
    # Iteration (Loops)
    #
    def handle_loop(self, node: ir.Loop, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Loop(
            node.engine,
            self.walk_list(node.hoisted, node, ctx),
            self.walk(node.iter, node, ctx),
            self.walk(node.body, node, ctx),
        )

    def handle_break(self, node: ir.Break, parent: ir.Node, ctx:Optional[Any]=None):
        return ir.Break(
            node.engine,
            self.walk(node.check, node, ctx),
        )


class Clone(Pass):
    """ A pass that does not, thereby cloning the IR. """
    pass
