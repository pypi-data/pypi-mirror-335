from collections import OrderedDict, defaultdict
from typing import Optional

from relationalai.early_access.dsl.core.exprs import contextStack
from relationalai.early_access.dsl.core.namespaces import Namespace
from relationalai.early_access.dsl.core.types import Type
from relationalai.early_access.dsl.core.utils import generate_stable_uuid, camel_to_snake
from relationalai.early_access.dsl.ontologies.constraints import Unique, Mandatory
from relationalai.early_access.dsl.ontologies.readings import Reading
from relationalai.early_access.dsl.ontologies.roles import Role
from relationalai.early_access.dsl.types import Type as DslType
from relationalai.early_access.dsl.utils import extract_relation_text_with_signature


class Relationship:

    def __init__(self, model, *args, relation_name: Optional[str] = None):
        self._model = model
        self._is_subtype = False
        self._readings_map = OrderedDict()
        self._rolemap = OrderedDict()
        self._constraints = []
        if not contextStack.empty():
            tp = contextStack.root_context()
            if isinstance(tp, Namespace):
                self._namespace = tp
            else:
                self._namespace = Namespace.top
        else:
            self._namespace = Namespace.top
        if len(args) != 0:
            reading = self._reading_from_args(*args, relation_name=relation_name)
            for role in reading.roles:
                self._add_role(role)
            self._add_relation(reading)

    def __call__(self, *args, **kwargs):
        return self.relation(*args, **kwargs)

    def __enter__(self):
        contextStack.push(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        contextStack.pop()
        pass

    def __getitem__(self, key):
        return self._readings_map[key]

    def __setitem__(self, key, value):
        if key in self._readings_map:
            raise Exception(
                f'Cannot provide multiple Readings for the relation name {key} in Relationship {self._name}')
        else:
            if not isinstance(value, Reading):
                value = Reading(*value)

            if value.rel_name is not None:
                # [VAMI] TODO: check if we need this warning
                # warn(f'Overriding rel_name of Reading "{value.verbalize()}" from "{value.rel_name}" to "{key}"')
                pass
            self._readings_map[key] = value
            value.rel_name = key
            return value

    def __setattr__(self, key: str, value: Role) -> None:
        if key.startswith('_') or key in self.__dict__:
            super().__setattr__(key, value)
        elif isinstance(value, Role):
            value.part_of = self
            self._add_role(value)
            super().__setattr__(key, value)
        else:
            raise TypeError(f'Expected a Role instance for "{key}", got {type(value)}')

    def __getattr__(self, key):
        if key in self._rolemap:
            return self._rolemap[key]
        else:
            raise AttributeError(f'Relationship {self._name} has no Role named {key}')

    def _reading_from_args(self, *args, relation_name: Optional[str] = None):
        text_frags, sig = extract_relation_text_with_signature(*args)
        grouped_sig = defaultdict(list)
        for t in sig:
            grouped_sig[t.name()].append(t)
        reading_args = []
        index_map = {}
        # store indexes for roles player by the same Concept
        for t_name in grouped_sig:
            group_size = len(grouped_sig[t_name])
            if group_size > 1:
                index_map[t_name] = group_size
        for idx, t in enumerate(sig):
            reading_args.append(Role(t, self, idx, name=self._get_role_name(t, index_map)))
            if idx < len(text_frags):
                reading_args.append(text_frags[idx])
        return Reading(*reading_args, name=relation_name)

    def _get_role_name(self, t, index_map):
        name = None
        if t.name() in index_map:
            idx = index_map.get(t.name())
            index_map[t.name()] -= 1
            name = f"{camel_to_snake(t.name())}{idx}"
        return name

    def _name(self):
        return list(self._readings_map.values())[0].to_relationship_name()

    def _set_subtype(self):
        self._is_subtype = True
        return self

    def is_subtype(self):
        return self._is_subtype

    def guid(self):
        return generate_stable_uuid(self._name())

    def role(self, concept, name: Optional[str] = None, unique: bool = False, primary_key: bool = False,
             mandatory: bool = False) -> 'Relationship':
        role = Role(concept, pos=self.arity(), name=name, rel=self)
        self._add_role(role)
        setattr(self, role.ref_name(), role)

        # check constraints
        if unique and not primary_key:
            self.unique(role)
        if mandatory and not primary_key:
            self.mandatory(role)
        if primary_key:
            self.primary_key(role)
        return self

    def role_at(self, idx):
        if idx < 0 or idx >= self.arity():
            raise Exception(f'Role index {idx} out of bounds for Relationship {self._name}')
        return list(self._rolemap.values())[idx]

    def arity(self):
        return len(self._rolemap)

    def relation(self, *args, name: Optional[str] = None) -> 'Relationship':
        return self._add_relation(Reading(*args, name=name))

    def _add_role(self, rol):
        self._rolemap[rol.ref_name()] = rol
        return self

    def _add_reading(self, rdg):
        if not isinstance(rdg, Reading):
            raise Exception(f'Tried to add non-Reading {rdg} as a reading of Relationship {self._name}')

        self[rdg.to_rel_name()] = rdg

    def _add_relation(self, reading: Reading) -> 'Relationship':
        self._add_reading(reading)
        first_player = reading.roles[0].player()
        namespace = Namespace(camel_to_snake(first_player.name()), self._namespace)
        relation = self._model._create_relation(reading.to_rel_name(), *reading.types(), namespace=namespace).addverb(
            reading.text_frags)
        # do not add relations to standard types like String, Date, Integer etc.
        if isinstance(first_player, DslType):
            first_player.add_relation(relation)
        # sync relationship and roles with the model once relationship have at least 1 reading
        if len(self._readings_map) == 1:
            self._model._add_relationship(self)
            for c in self._constraints:
                self._model.constraint(c)
        return self

    def build_relation_variable(self, args, kwargs):
        return self.new_role(args, kwargs)

    def build_scalar_variable(self, args, kwargs):
        return self.new_role(args, kwargs)

    def new_role(self, args, kwargs):
        if len(args) == 0:
            raise Exception(f'Unexpected error in Relationship {self._name}')

        if len(args) > 2:
            raise Exception(
                f'Cannot declare role of Relationship {self._name} by supplying more than a player type and a UUID')

        if len(kwargs) != 0:
            raise Exception(
                f'Cannot use keyword arguments when instantiating a type parameter for Relationship {self._name}')

        type = args[0]

        pre_bound_text = kwargs['pre_bound_text'] if 'pre_bound_text' in kwargs else None
        post_bound_text = kwargs['post_bound_text'] if 'post_bound_text' in kwargs else None

        if not isinstance(type, Type):
            raise Exception('Can only instantiate a Role with a Type as its player')
        role = Role(type, self, self.arity()).verbalization(pre_bound_text, post_bound_text)

        self._add_role(role)
        return role

    def readings(self):
        return list(self._readings_map.values())

    # Constraints

    def unique(self, *roles):
        """Add a uniqueness constraint on specified roles."""
        self._add_constraint(Unique(*roles))
        return self

    def mandatory(self, *roles):
        """Add a mandatory constraint on specified roles."""
        self._add_constraint(Mandatory(*roles))
        return self

    def primary_key(self, *roles):
        """Set the (composite) primary key & uniqueness constraint."""
        self._add_constraint(Unique(*roles, is_preferred_identifier=True))
        for r in roles:
            self._add_constraint(Mandatory(r))
        return self

    def _add_constraint(self, con):
        self._constraints.append(con)
        if not self.is_empty():
            self._model.constraint(con)

    # pretty printing readings
    def pprint(self):
        return f'relationship {self._name()}[{", ".join([r.verbalize() for r in self.readings()])}]'

    def is_empty(self):
        return len(self.readings()) == 0

class Attribute(Relationship):
    def __init__(
            self,
            model,
            concept,
            attr,
            mandatory: bool = False,
            primary_key: bool = False,
            reading_text: Optional[str] = None,
            reverse_reading_text: Optional[str] = None
    ):
        if reading_text is None:
            reading_text = 'has'

        super().__init__(model, concept, reading_text, attr)
        concept_role = self.role_at(0)
        self.unique(concept_role)
        if mandatory:
            self.mandatory(concept_role)

        attr_role = self.attr()
        if primary_key:
            self.primary_key(attr_role)

        if reverse_reading_text is not None:
            self.relation(attr_role, reverse_reading_text, concept_role)

    def attr(self):
        return self.role_at(1)

def _reading_to_relationship_name(reading: str) -> str:
    """
    Takes a readable `reading` string and returns the middle part of the Relationship name.

    This is done by removing spaces and converting the result to PascalCase."""
    return ''.join(word.capitalize() for word in reading.split(' '))
