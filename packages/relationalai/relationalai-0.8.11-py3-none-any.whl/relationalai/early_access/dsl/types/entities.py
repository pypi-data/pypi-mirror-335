from relationalai.early_access.dsl.core.exprs import _
from relationalai.early_access.dsl.core.relations import Relation, RelationSignature, rule
from relationalai.early_access.dsl.core.rules import Rule, Vars
from relationalai.early_access.dsl.core.types.standard import standard_value_types, Hash
from relationalai.early_access.dsl.types import Type


class AbstractEntityType(Type):

    def __init__(self, model, nm):
        super().__init__(model, nm)
        self._poprel = None

    def population(self):
        if self._poprel is None:
            self._poprel = Relation(self.namespace(), self.name(), RelationSignature(self))
        return self._poprel

    def ctor_name(self): return f"^{self.name()}"

    def entity(self): return True

    def addrule(self, rule):
        relation = self._model.external_relation(self.name(), self)
        if not isinstance(rule, Rule):
            # Assume that rule is a Python function that, when invoked can build a rule
            rule = Rule(relation).elaborate(rule)
        relation._rules.append(rule)
        return rule

    @staticmethod
    def root_unconstrained_type():
        return standard_value_types['Hash']

class EntityType(AbstractEntityType):

    def __init__(self, model, nm, *args):
        super().__init__(model, nm)
        self._domain = [*args]
        self._constructor = None

    def __xor__(self, args):
        return self.constructor()(*args)

    def build_relation_variable(self, args, kwargs):
        if len(args) == 0:
            raise Exception(f"Unexpected error in EntityType {self.name()}")

        if len(args) > 1:
            raise Exception(f"Cannot declare type variable of EntityType {self.name()} by supplying more than a type")

        if len(kwargs) != 0:
            raise Exception(
                f"Cannot use keyword arguments when instantiating a type parameter for EntityType {self.name()}")

        type = args[0]
        self._domain.append(type)
        return type

    def build_scalar_variable(self, args, kwargs):
        if len(args) == 0:
            raise Exception(f"Unexpected error in EntityType {self.name()}")

        if len(args) > 1:
            raise Exception(f"Cannot declare type variable of EntityType {self.name()} by supplying more than a type")

        if len(kwargs) != 0:
            raise Exception(
                f"Cannot use keyword arguments when instantiating a type parameter for EntityType {self.name()}")

        type = args[0]
        self._domain.append(type)
        return type

    # An EntityTypeConstructor is an n-ary functional Relation that maps tuples of
    # arity (n-1) to instances of the EntityType.
    #
    def constructor(self):
        if self._constructor is None:
            # Create a constructor function (relation) when this EntityType is created
            ctortype = self.ctordomain().copy()
            ctortype.append(self)
            self._constructor = Relation(self.namespace(),
                                         self.ctor_name(),
                                         RelationSignature(*tuple(ctortype)))
        return self._constructor

    def ctordomain(self):
        return self._domain

    def add_instance(self, val):
        if not isinstance(val, str):
            raise Exception(
                f"Attempt to add non-string instance {val} to entity type {self.name()}, but currently on string instances supported.")

        self.relation(f"is {val}", name=val)

        with self.__dict__[val]:
            @rule()
            def r(v): self^(val, v)

    def first(self, relation):
        with self:
            @rule()
            def r(e):
                relation(e, _)

    def filtered_by(self, filter, value):
        with self:
            @rule()
            def r(e):
                v = Vars(Hash)
                #
                value(v)
                filter(e, v)


    def qualified_name(self):
        return self._name

    def pprint(self):
        domain_str = ", ".join([f"x{i} in {t.name()}" for i, t in enumerate(self._domain)])
        return f"entity type {self.name()}({domain_str})"
