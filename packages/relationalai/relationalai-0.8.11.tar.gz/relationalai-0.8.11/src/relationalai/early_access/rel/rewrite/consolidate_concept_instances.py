from __future__ import annotations
from typing import Any, Optional
import json
import hashlib

from relationalai.early_access.metamodel import ir, factory as f
from relationalai.early_access.metamodel.compiler import Pass

import relationalai.early_access.metamodel.types as irtypes

class ConsolidateConceptInstances(Pass):
    """A pass that consolidates concept instance updates into a single definition per concept."""

    def __init__(self):
        super().__init__()
        self.concept_updates = {}  # Track updates by relation name
        self.entity_ids = {}  # Track entity IDs by relation name

    def is_concept_instance(self, update: ir.Update) -> bool:
        """Check if this update represents a concept instance with key-value pairs"""
        return (update.effect == ir.Effect.derive and
                len(update.args) % 2 == 0 and
                all(isinstance(arg, ir.Literal) and
                    isinstance(arg.value, str)
                    for i in range(0, len(update.args), 2)  # Check even-indexed args (keys)
                    for arg in [update.args[i]]))  # Get the arg to check

    def handle_update(self, node: ir.Update, parent: ir.Node, ctx:Optional[Any]=None) -> ir.Update:
        if self.is_concept_instance(node):
            rel_name = node.relation.name
            if rel_name not in self.concept_updates:
                self.concept_updates[rel_name] = []
                self.entity_ids[rel_name] = set()

            self.concept_updates[rel_name].append(node)

            # Generate a unique ID for this entity
            m = hashlib.md5()
            for arg in node.args:
                m.update(str(self.emit_value(arg)).encode())
            instance_id = f"0x{m.hexdigest()[:32]}"
            self.entity_ids[rel_name].add(instance_id)

            # Return a dummy update that will be filtered out later
            return f.derive(node.relation, [])  # Empty update that will be filtered
        return node

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None) -> ir.Logical:
        # Filter out empty logical nodes and empty updates
        new_body = [
            task for task in self.walk_list(node.body, node)
            if not (
                (isinstance(task, ir.Logical) and not task.body) or
                (isinstance(task, ir.Update) and not task.args)
            )
        ]
        if not new_body:
            return f.logical([])
        return f.logical(new_body)

    def handle_model(self, model: ir.Model, parent: None, ctx:Optional[Any]=None) -> ir.Model:
        # First traverse the tree to collect all concept instances
        result = super().handle_model(model, parent)

        # Then create consolidated definitions
        consolidated_updates = []

        # First add entity definitions (unary relations)
        for rel_name, ids in self.entity_ids.items():
            if ids:
                entity_rel = f.relation(rel_name, [f.field("v1", irtypes.Any)])
                entity_args = [f.lit(id) for id in sorted(ids)]
                consolidated_updates.append(f.derive(entity_rel, entity_args))

        # Then add attribute definitions
        for rel_name, updates in self.concept_updates.items():
            # Group by attribute name
            instances = {}
            for update in updates:
                args = update.args
                m = hashlib.md5()
                for arg in args:
                    m.update(str(self.emit_value(arg)).encode())
                instance_id = f"0x{m.hexdigest()[:32]}"

                for i in range(0, len(args), 2):
                    attr_name = self.emit_value(args[i]).strip('"')
                    value = args[i+1]
                    if attr_name not in instances:
                        instances[attr_name] = []
                    instances[attr_name].append((instance_id, value))

            for attr_name, pairs in sorted(instances.items()):
                if not pairs:
                    continue

                attr_rel = f.relation(attr_name, [
                    f.field("v1", irtypes.Any),
                    f.field("v2", irtypes.Any)
                ])

                args = []
                for id, val in sorted(pairs):
                    args.extend([f.lit(id), val])

                if args:
                    consolidated_updates.append(f.derive(attr_rel, args))

        if consolidated_updates:
            # Append consolidated updates directly to root's body
            if isinstance(result.root, ir.Logical):
                new_body = list(result.root.body) + [f.logical(consolidated_updates)]
                result = ir.Model(
                    result.engines,
                    result.relations,
                    result.types,
                    f.logical(new_body)
                )

        return result

    def emit_value(self, value: ir.Value) -> str:
        """Helper to convert IR values to strings for hashing"""
        if isinstance(value, ir.Literal):
            return json.dumps(value.value)
        return str(value)
