from __future__ import annotations
from typing import Any, Iterable, Sequence as PySequence, cast, Tuple, Union
from dataclasses import dataclass

from relationalai.early_access.metamodel import ir, compiler as c, builtins as bt, types

from relationalai.early_access.metamodel.rewrite import Splinter
from relationalai.early_access.metamodel.visitor import ReadWriteVisitor
from relationalai.early_access.metamodel.util import group_by

from relationalai.early_access.rel import rel, rewrite

#--------------------------------------------------
# Compiler
#--------------------------------------------------

class Compiler(c.Compiler):
    def __init__(self):
        super().__init__([
            Splinter(),
            rewrite.ConsolidateConceptInstances()
        ])

    def do_compile(self, model: ir.Model) -> str:
        return str(ModelToRel().to_rel(model))



@dataclass
class ModelToRel:
    """ Generates Rel from an IR Model, assuming the compiler rewrites were done. """

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------

    def to_rel(self, model: ir.Model) -> rel.Program:
        return rel.Program(tuple([
            *self._generate_declares(model),
            *self._generate_rules(model),
        ]))

    #--------------------------------------------------
    # Top level handlers
    #--------------------------------------------------

    def _generate_declares(self, m: ir.Model) -> list[rel.Declare]:
        """ Generate declare statements for relations that are used but never updated. """
        rw = ReadWriteVisitor()
        rw.accept(m)

        root = cast(ir.Logical, m.root)

        reads = rw.reads(root) - rw.writes(root) - bt.builtin_relations
        reads = list(filter(lambda r: not r.name.startswith('^'), reads))

        declares: list[rel.Declare] = []
        for r in reads:
            # In case parameter name starts with ':' use its name instead of type name
            def requires_name(field: ir.Field):
                if isinstance(field.type, ir.ScalarType):
                    t = field.type
                    return rel.MetaValue(t.name[1:]) if t.name.startswith(':') else rel.Var(t.name)
                else:
                    return rel.Var("_")
            types = rel.Product(tuple([requires_name(f) for f in r.fields]))

            # Example: declare test(x...) requires {(:a, Int, String)}(x...)
            x = rel.Var("x", True)
            declares.append(rel.Declare(
                rel.atom(r.name, tuple([x])),
                rel.Atom(types, tuple([x]))
            ))
        return declares

    def _generate_rules(self, m: ir.Model) -> list[rel.Def]:
        """ Generate rules for the root of this model.

        Assumes the model already was processed such that it contains a root Logical with
        children that are also Logical tasks representing the rules to generate.
        """
        rules: list[rel.Def] = []
        root = cast(ir.Logical, m.root)
        for child in root.body:
            rules.extend(self._generate_rule(cast(ir.Logical, child)))
        return rules

    def _generate_rule(self, rule: ir.Logical) -> list[rel.Def]:
        """ Generate rules for a nested Logical in a model.

        This is for a top-level Logical, under the root Logical.
        """

        effects, other, aggregates = self._split_tasks(rule.body)
        if not effects:
            raise Exception("Cannot create top-level rule without effects.")

        elif len(effects) == 1:
            # a single effect with a body becomes a single rule
            effect = effects[0]
            annos = effect.annotations if isinstance(effect, ir.Update) else []
            return [rel.Def(
                self._effect_name(effect),
                self._effect_args(effect),
                self.generate_logical_body(other, aggregates),
                self.generate_annotations(annos)
            )]
        else:
            # currently we can only deal with multiple effects if they are all updates with
            # no body, which is the pattern for inserting hardcoded data.
            if other or aggregates:
                raise NotImplementedError("Body in logical task with multiple effects.")
            if any(isinstance(effect, ir.Output) for effect in effects):
                raise NotImplementedError("Output in logical task with multiple effects.")
            sample = cast(ir.Update, effects[0]).effect
            if any(cast(ir.Update, effect).effect != sample for effect in effects):
                raise NotImplementedError("Different types of effects in logical task.")

            # Group updates by relation name
            relation_groups = group_by(cast(list[ir.Update], effects), lambda e: e.relation.name)

            # Process each relation group
            defs = []
            for name, updates in relation_groups.items():
                bodies = []
                for update in updates:
                    bodies.append(self.handle(update))
                update = updates.some()
                defs.append(
                    rel.Def(
                        name,
                        self._effect_args(update),
                        rel.Union(tuple(bodies)),
                        self.generate_annotations(update.annotations)
                    )
                )
            return defs

    def generate_logical_body(self, other, aggregates):
        """ Generate the body of a rule for a Logical that contains these aggregates and
        other tasks (i.e. no effects)."""

        if not aggregates:
            # no aggregates, just return an expression for the body
            return self.generate_body_expr(other)
        else:
            # push the body into the aggregates; this assumes a rewrite pass already
            # prepared the body to contain only what's needed by the aggregates
            exprs = []
            for agg in aggregates:
                # TODO - some aggregations have multiple results, they need special handling
                result = self.handle_var(cast(ir.Var, agg.args[-1]))

                # vars in the relational abstraction are agg's "projection" + "over"
                ir_vars = list(agg.projection)
                if len(agg.args) > 1: # e.g. count does not have "over"
                    ir_vars.append(cast(ir.Var, agg.args[-2]))

                abstraction = rel.RelationalAbstraction(
                    self.handle_vars(tuple(ir_vars)),
                    self.generate_body_expr(other)
                )
                exprs.append(rel.atom(
                    agg.aggregation.name,
                    tuple([ abstraction, result ])
                ))
            return exprs[0] if len(exprs) == 1 else rel.And(tuple(exprs))

    def generate_body_expr(self, tasks: list[ir.Task]):
        """ Helper to generate the an expression from the tasks, wrapping in Ands if necessary. """
        return self.handle(tasks[0]) if len(tasks) == 1 else rel.And(tuple([self.handle(b) for b in tasks]))

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    def handle(self, n: Union[ir.Value, ir.Node]):
        if isinstance(n, ir.Node):
            handler = getattr(self, f"handle_{n.kind}", None)
            if handler:
                return handler(n)
            else:
                raise Exception(f"Rel Compiler handler for '{n.kind}' node not implemented.")
        else:
            # TODO - every call to handle_value with None needs to get a type wired
            return self.handle_value(None, n)

    def handle_list(self, n):
        return tuple([self.handle(x) for x in n])

    def handle_value(self, type: Any, value: Any) -> Union[rel.Primitive, rel.MetaValue]:
        if type == types.Symbol:
            return rel.MetaValue(value)
        else:
            return value

    def handle_value_list(self, types, values) -> Tuple[Union[rel.Primitive, rel.MetaValue], ...]:
        return tuple([self.handle_value(t, v) for t, v in zip(types, values)])

    #
    # DATA MODEL
    #
    def handle_scalartype(self, n: ir.ScalarType):
        return n.name
    # TODO - what to generate for other kinds of types?




    #
    # TASKS
    #
    def handle_logical(self, n: ir.Logical) -> rel.Expr:
        # Generate nested expressions for a nested logical
        effects, other, aggregates = self._split_tasks(n.body)
        if effects:
            raise Exception("Cannot process nested logical with effects.")
        return self.generate_logical_body(other, aggregates)

    #
    # LOGICAL QUANTIFIERS
    #
    def handle_not(self, n: ir.Not):
        return rel.Not(self.handle(n.task))

    def handle_exists(self, n: ir.Exists):
        return rel.Exists(
            self.handle_vars(n.vars),
            self.handle(n.task)
        )

    #
    # ITERATION
    #

    #
    # RELATIONAL OPERATIONS
    #

    def handle_vars(self, vars: Tuple[ir.Var, ...]):
        return tuple([self.handle_var(v) for v in vars])

    def handle_var(self, n: ir.Var):
        name = n.name
        if name == "_" or name.startswith(':'):
            return rel.Var(name)
        else:
            return rel.Var(f"_{name}")

    def handle_literal(self, n: ir.Literal):
        return self.handle_value(n.type, n.value)

    def generate_annotations(self, annos: Iterable[ir.Annotation]):
        """ Helper to cast the handling of ir.Annotations into a tuple of rel.Annotations. """
        return cast(Tuple[rel.Annotation, ...], self.handle_list(annos))

    def handle_annotation(self, n: ir.Annotation):
        return rel.Annotation(
            n.relation.name,
            self.handle_value_list([f.type for f in n.relation.fields], n.args)
        )

    def handle_update(self, n: ir.Update):
        return rel.atom(
            n.relation.name,
            self.handle_list(n.args)
        )

    def handle_lookup(self, n: ir.Lookup):
        return rel.atom(
            n.relation.name,
            self.handle_list(n.args)
        )

    def handle_construct(self, n: ir.Construct):
        args = [self.handle(v) for v in n.values] + [self.handle(n.id_var)]
        return rel.atom("rel_primitive_hash_tuple_uint128", tuple(args))

    def handle_aggregate(self, n: ir.Aggregate):
        # TODO: this is very incorrect
        args = n.projection + n.group + n.args
        args = [self.handle(a) for a in args]
        return rel.atom(n.aggregation.name, tuple(args))


    #--------------------------------------------------
    # Helpers
    #--------------------------------------------------

    def _split_tasks(self, tasks: PySequence[ir.Task]) -> tuple[list[ir.Task], list[Union[ir.Update, ir.Output]], list[ir.Aggregate]]:
        effects = []
        aggregates = []
        other_body = []
        for task in tasks:
            if isinstance(task, (ir.Update, ir.Output)):
                effects.append(task)
            elif isinstance(task, ir.Aggregate):
                aggregates.append(task)
            else:
                other_body.append(task)
        return effects, other_body, aggregates


    def _effect_name(self, n: ir.Task):
        if isinstance(n, ir.Output):
            return "output"
        elif isinstance(n, ir.Update):
            return n.relation.name
        else:
            raise Exception(f"Cannot retrieve effect name from node {type(n)}")

    def _effect_args(self, n: ir.Task):
        if isinstance(n, ir.Output):
            # TODO - deal with output aliases
            args = []
            for _, v in n.aliases:
                args.append(self.handle(v))
            return tuple(args)
        elif isinstance(n, ir.Update):
            args = []
            for a in n.args:
                args.append(self.handle(a))
            return tuple(args)
        else:
            raise Exception(f"Cannot retrieve effect params from node {type(n)}")
