from typing import Optional

import relationalai.early_access.dsl.core.types
from relationalai.early_access.dsl.core.namespaces import Namespace
from relationalai.early_access.dsl.core.relations import Relation
from relationalai.early_access.dsl.core.utils import camel_to_snake
from relationalai.early_access.dsl.utils import build_relation_name


class Type(relationalai.early_access.dsl.core.types.Type):

    # We can add relation components to a ConceptModule by invoking it
    # with arguments that interleave reading text with the Types used
    # to play various Roles
    #
    def __setattr__(self, key, value):
        if key in dir(self) and key not in self.__dict__:
            raise Exception(f"Cannot override method {key} of Type {self.name()} as an attribute.")
        else:
            if key[0] != '_':
                self._relations[key] = value
            return super().__setattr__(key, value)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __init__(self, model, nm):
        super().__init__(nm)
        self._model = model
        self._relations = {}
        self._generated_namespace = None

    def relation(self, *args, name: Optional[str] = None, namespace: Optional[Namespace]=None, functional: bool=False) -> Relation:
        self._generated_namespace = namespace
        relation = self._build_relation(name, args, functional)
        self.add_relation(relation)
        return relation

    def add_relation(self, relation: Relation):
        self._relations[relation._relname] = relation
        self.__setattr__(relation._relname, relation)

    def _build_relation(self, name, verbalization, functional):
        verb_parts = []
        roles:list[relationalai.early_access.dsl.core.types.Type] = [self]
        if isinstance(verbalization, relationalai.early_access.dsl.core.types.Type):
            roles.append(verbalization)
        else:
            for i in range(len(verbalization)):
                arg = verbalization[i]
                if isinstance(arg, str):
                    verb_parts.append(arg)
                else:
                    if isinstance(arg, relationalai.early_access.dsl.core.types.Type):
                        roles.append(arg)
                    else:
                        raise Exception(
                            f"Predicate verbalization in Type {self.name()} is {arg}, which is neither a string nor a Type")

        if name is None:
            name = build_relation_name(roles, verb_parts)
        return self._model._create_relation(name, *roles, namespace=self.generated_namespace(), functional=functional).addverb(verb_parts)

    def generated_namespace(self):
        if self._generated_namespace is None:
            ename = camel_to_snake(self.name())
            self._generated_namespace = Namespace(ename, self.namespace())
        return self._generated_namespace