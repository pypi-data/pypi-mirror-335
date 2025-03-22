from __future__ import annotations

from typing import Any, Optional, Sequence as PySequence, cast

from relationalai.early_access.metamodel import ir, compiler as c, factory as f, types
from relationalai.early_access.metamodel.visitor import collect_implicit_vars

class Splinter(c.Pass):
    """
    Splits multi-headed rules into multiple rules. Additionally, infers missing Exists tasks.
    """

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None):
        # only process the topmost logical
        if isinstance(parent, ir.Model):
            final = []
            for child in node.body:
                final.extend(self.split(cast(ir.Logical, child)))
            return ir.Logical(
                node.engine,
                node.hoisted,
                tuple(final)
            )
        else:
            return node

    def split(self, node: ir.Logical) -> list[ir.Logical]:
        # Split this logical, which represents a rule, into potentially many logicals, one
        # for each head (update or output)
        effects, body = self.split_items(node.body)
        if not body:
            return [node]

        effects_vars = collect_implicit_vars(*effects)
        body_vars = collect_implicit_vars(*body)
        implicit_vars = list(body_vars - effects_vars)

        if len(effects) > 1:
            connection = f.relation(f"q{node.id}", [f.field("", types.Any) for v in effects_vars])
            if implicit_vars:
                args = [f.exists(implicit_vars, f.logical(body))]
            else:
                args = body
            final:list[ir.Logical] = [f.logical([*args, f.derive(connection, list(effects_vars))])]
            for effect in effects:
                effect_vars = collect_implicit_vars(effect)
                lookup_vars = [(v if v in effect_vars else f.wild()) for v in effects_vars]
                final.append(f.logical([f.lookup(connection, lookup_vars), effect]))
            return final

        if implicit_vars:
            return [f.logical([f.exists(implicit_vars, f.logical(body)), *effects])]
        else:
            return [node]


    def split_items(self, items: PySequence[ir.Task]) -> tuple[list[ir.Task], list[ir.Task]]:
        effects = []
        body = []
        for item in items:
            if isinstance(item, (ir.Update, ir.Output)):
                effects.append(item)
            else:
                body.append(item)
        return effects, body
