from typing import Optional

from relationalai.early_access.dsl.core.types import Type
from relationalai.early_access.dsl.core.utils import generate_stable_uuid, camel_to_snake
from relationalai.early_access.dsl.core.namespaces import Namespace
from relationalai.early_access.dsl.core.relations import Relation, RelationSignature, rule
from relationalai.early_access.dsl.graph.graph import is_acyclic_graph
from relationalai.early_access.dsl.ontologies.constraints import Unique, Mandatory, Constraint
from relationalai.early_access.dsl.ontologies.relationships import Relationship, Attribute
from relationalai.early_access.dsl.ontologies.subtyping import SubtypeArrow, InclusiveSubtypeConstraint, ExclusiveSubtypeConstraint
from relationalai.early_access.dsl.types.entities import EntityType
from relationalai.early_access.dsl.types.values import ValueType, ValueSubtype
from relationalai.early_access.dsl.utils import build_relation_name, extract_relation_text_with_signature


class Model:
    def __init__(self, name: str, is_primary: bool = True):
        self.name = name
        self.is_primary = is_primary
        self._value_types = {}
        self._entity_types = {}
        self._relationships = {}
        self._constraints = set()
        self._subtype_arrows = set()
        self._subtype_constraints = set()
        self._relations = {}

    def guid(self):
        return generate_stable_uuid(self.name)

    def value_type(self, name: str, *args) -> ValueType:
        vt = ValueType(self, name, *args)
        self._validate_type_name(name)
        self._value_types[name] = vt
        return vt

    def value_sub_type(self, name: str, super_type: Type) -> ValueSubtype:
        vt = ValueSubtype(self, name, super_type)
        self._validate_type_name(name)
        self._value_types[name] = vt
        return vt

    def entity_type(self, name: str, *args) -> EntityType:
        et = EntityType(self, name, *args)
        self._validate_type_name(name)
        self._entity_types[name] = et
        return et

    def entity_sub_type(self, name: str, super_type: Type) -> EntityType:
        et = self.entity_type(name)
        self.subtype_arrow(super_type, [et])
        return et

    def exclusive_entity_type(self, name: str, *args) -> EntityType:
        et = self.entity_type(name)
        self.subtype_arrow(et, list(args), exclusive=True)
        return et

    def inclusive_entity_type(self, name: str, *args) -> EntityType:
        et = self.entity_type(name)
        self.subtype_arrow(et, list(args), inclusive=True)
        return et

    def subtype_arrow(self, type: Type, sub_types:list[Type], exclusive=False, inclusive=False) -> set[SubtypeArrow]:
        arrows = set()
        for sub in sub_types:
            # For example: AdminAccount -> Account
            a = SubtypeArrow(sub, type)
            arrows.add(a)
            self._subtype_arrows.add(a)
            # TODO: [AN]: we generate these relations to be compatible with SLS. We need to get rid of subtype relationship notion from ontology later.
            if isinstance(type, EntityType):
                self._generate_subtype_relationship(sub, type)
        self._validate_cyclic_arrows()
        if exclusive:
            self._subtype_constraints.add(ExclusiveSubtypeConstraint(arrows))
        if inclusive:
            self._subtype_constraints.add(InclusiveSubtypeConstraint(arrows))
        self._declare_subtype_rules(type, sub_types)
        return arrows

    def exclusive_subtype_constraint(self, *arrows: SubtypeArrow) -> ExclusiveSubtypeConstraint:
        cnstr = ExclusiveSubtypeConstraint(set(arrows))
        self._subtype_constraints.add(cnstr)
        return cnstr

    def inclusive_subtype_constraint(self, *arrows: SubtypeArrow) -> InclusiveSubtypeConstraint:
        cnstr = InclusiveSubtypeConstraint(set(arrows))
        self._subtype_constraints.add(cnstr)
        return cnstr

    def relationship(self, *args, relation_name: Optional[str] = None) -> Relationship:
        """
        Create a new relationship with the given reading.
        'args' contains Sequence of Types followed by text fragments.
        """
        return Relationship(self, *args, relation_name=relation_name)

    def external_relation(self, name: str, *sig: Type, namespace: Namespace = Namespace.top,
                          functional: bool = False) -> Relation:
        """
        Create a new external relation with the given namespace, name and signature.

        """
        return self._create_relation(name, *sig, namespace=namespace, functional=functional)


    def relation(self, *args, namespace: Namespace = Namespace.top, name: Optional[str] = None) -> Relation:
        """
        Create a new relation with the given namespace and name using the given verbalization (Sequence of Types and text fragments).

        """
        text_frags, sig = extract_relation_text_with_signature(*args)
        namespace = Namespace(camel_to_snake(sig[0].name()), namespace)
        if name is None:
            name = build_relation_name(sig, text_frags)
        return self._create_relation(name, *sig, namespace=namespace)

    def attribute(
            self,
            concept,
            attr,
            mandatory: bool = False,
            primary_key: bool = False,
            reading_text: Optional[str] = None,
            reverse_reading_text: Optional[str] = None
    ) -> Attribute:
        """
        Creates a new attribute relationship with the given parameters.

        Parameters:
            concept: The concept the attribute is associated with.
            attr: The entity type or value type playing the attribute role.
            mandatory (bool, optional): Whether the concept's role in this relationship is mandatory. Defaults to False.
            primary_key (bool, optional): Whether the attribute is a preferred identifier for the concept. Defaults to False.
            reading_text (str, optional): The forward reading description of the relationship (e.g., "is classified by").
            reverse_reading_text (str, optional): The reverse reading description of the relationship (e.g., "classifies").

        Example:
            # Equivalent logic:

            rel = model.relationship(concept, 'has', attr)
            rel.relation(rel.role_at(1), reverse_reading_text, rel.role_at(0), name=reverse_rel_name)
            model.unique(rel.concept)
            model.mandatory(rel.concept)

        Returns:
            Attribute: The newly created attribute relationship.
        """
        return Attribute(
            model=self,
            concept=concept,
            attr=attr,
            mandatory=mandatory,
            primary_key=primary_key,
            reading_text=reading_text,
            reverse_reading_text=reverse_reading_text
        )

    def constraint(self, constraint):
        # Generic constraint addition with validation
        self._validate_constaint_roles(constraint)
        self._constraints.add(constraint)

    # Syntactic sugar methods
    def unique(self, *roles):
        self.constraint(Unique(*roles))

    def primary_key(self, *roles):
        for r in roles:
            self.mandatory(r)
        self.constraint(Unique(*roles, is_preferred_identifier=True))

    def mandatory(self, role):
        self.constraint(Mandatory(role))

    def lookup_concept(self, name) -> Optional[Type]:
        if name in self._value_types:
            return self._value_types[name]
        if name in self._entity_types:
            return self._entity_types[name]
        return None

    def lookup_relationship(self, name) -> Optional[Relationship]:
        if name in self._relationships:
            return self._relationships[name]
        return None

    @staticmethod
    def _declare_subtype_rules(super_type, sub_types):
        with super_type:
            for sub in sub_types:
                @rule()
                def r(t):
                    sub(t)

    def pprint(self) -> str:
        result = [f"Model: {self.name} (Primary: {self.is_primary})"]
        result.append("\nValue Types:")
        for vt in self._value_types.values():
            result.append(f"  {vt.pprint()}")
        result.append("\nEntity Types:")
        for et in self._entity_types.values():
            result.append(f"  {et.pprint()}")
        result.append("\nRelationships:")
        for rel in self._relationships.values():
            result.append(f"  {rel.pprint()}")
        result.append("\nSubtype Arrows:")
        for arrow in self._subtype_arrows:
            result.append(f"  {arrow.pprint()}")
        return "\n".join(result)

    def _add_relationship(self, rel: Relationship):
        self._validate_relationship_name(rel._name())
        self._relationships[rel._name()] = rel

    def _create_relation(self, name: str, *sig: Type, namespace: Namespace = Namespace.top,
                         functional: bool = False) -> Relation:
        relation = Relation(namespace, name, RelationSignature(*sig))
        if functional:
            relation.function()
        if relation.entityid() in self._relations:
            existed_relation = self._relations[relation.entityid()]
            self._validate_relation(existed_relation, *sig)
            return existed_relation
        self._relations[relation.entityid()] = relation
        return relation

    def _validate_type_name(self, name):
        if name in self._entity_types:
            raise Exception(
                f"The name '{name}' is used to declare an entity type.")
        if name in self._value_types:
            raise Exception(
                f"The name '{name}' is used to declare a value type.")

    def _validate_relationship_name(self, name):
        if name in self._relationships:
            raise Exception(
                f"The name '{name}' is used to declare a relationship.")

    def _validate_relation(self, relation: Relation, *requested_sig: Type):
        if len(requested_sig) != len(relation._signature._types):
            raise Exception(
                f"The relation '{relation.qualified_name()}' already exists but provided signature arity doesn't match.")
        for idx in range(len(relation._signature._types)):
            item = relation._signature._types[idx]
            if not isinstance(item, type(requested_sig[idx])):
                raise Exception(
                    f"The relation '{relation.qualified_name()}' already exists but provided signature doesn't match.")

    def _validate_constaint_roles(self, constraint: Constraint):
        for role in constraint.roles():
            if role.part_of.is_empty():
                raise Exception(
                    f"Failed add constraint {constraint}. Role {role.ref_name()} is part of relation without readings.")

    def _validate_cyclic_arrows(self):
        if not is_acyclic_graph(list(self._entity_types.keys()), list(map(lambda a: a.to_name_tuple(), self._subtype_arrows))):
            raise Exception("Failed to add subtype arrow. The model graph should be acyclic.")

    def _generate_subtype_relationship(self, entity_type, super_type):
        rel = self.relationship()
        (
            rel._set_subtype()
                .role(super_type, unique=True)
                .role(entity_type, unique=True, mandatory=True)
                .relation(rel.role_at(1), "is a subtype of", rel.role_at(0))
        )
