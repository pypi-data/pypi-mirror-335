from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Sequence as PySequence, cast
import itertools

import pandas as pd

from relationalai.clients import result_helpers
from relationalai.early_access.metamodel import factory as f, ir, builtins, types
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.builder.util import sanitize
from relationalai.early_access.rel.executor import RelExecutor

#--------------------------------------------------
# Global ID
#--------------------------------------------------

_global_id = itertools.count(0)

#--------------------------------------------------
# Producer
#--------------------------------------------------

class Producer():
    def __init__(self, model:Model) -> None:
        self._id = next(_global_id)
        self._model = model

    #--------------------------------------------------
    # Infix operator overloads
    #--------------------------------------------------

    def _bin_op(self, op, left, right) -> Expression:
        res = Var(self._model, None, self._model.Concept("Number"))
        return Expression(self._model, self._model._builtin_relationships[op], left, right, res)

    def __add__(self, other):
        return self._bin_op("+", self, other)
    def __radd__(self, other):
        return self._bin_op("+", other, self)

    def __mul__(self, other):
        return self._bin_op("*", self, other)
    def __rmul__(self, other):
        return self._bin_op("*", other, self)

    def __sub__(self, other):
        return self._bin_op("-", self, other)
    def __rsub__(self, other):
        return self._bin_op("-", other, self)

    def __truediv__(self, other):
        return self._bin_op("/", self, other)
    def __rtruediv__(self, other):
        return self._bin_op("/", other, self)

    def __floordiv__(self, other):
        return self._bin_op("//", self, other)
    def __rfloordiv__(self, other):
        return self._bin_op("//", other, self)

    def __pow__(self, other):
        return self._bin_op("^", self, other)
    def __rpow__(self, other):
        return self._bin_op("^", other, self)

    def __mod__(self, other):
        return self._bin_op("%", self, other)
    def __rmod__(self, other):
        return self._bin_op("%", other, self)

    def __neg__(self):
        return self._bin_op("*", self, -1)

    #--------------------------------------------------
    # Filter overloads
    #--------------------------------------------------

    def _filter(self, op, left, right) -> Expression:
        return Expression(self._model, self._model._builtin_relationships[op], left, right)

    def __gt__(self, other):
        return self._filter(">", self, other)
    def __ge__(self, other):
        return self._filter(">=", self, other)
    def __lt__(self, other):
        return self._filter("<", self, other)
    def __le__(self, other):
        return self._filter("<=", self, other)
    def __eq__(self, other) -> Any:
        return self._filter("=", self, other)
    def __ne__(self, other) -> Any:
        return self._filter("!=", self, other)

    #--------------------------------------------------
    # getattr
    #--------------------------------------------------

    def __getattr__(self, name:str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__} has no attribute {name}")
        if name not in self._relationships:
            any_concept = self._model.Concept("Any")
            self._relationships[name] = Relationship(
                (any_concept, any_concept), parent=self, prop_name=name, model=self._model
            )
        return self._relationships[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, Relationship) and not name.startswith("_"):
            value._parent = self
            self._relationships[name] = value
        else:
            super().__setattr__(name, value)

    #--------------------------------------------------
    # Hash
    #--------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._id)

    #--------------------------------------------------
    # Fallbacks
    #--------------------------------------------------

    def select(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.select` not implemented")

    def where(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.where` not implemented")

    def require(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.require` not implemented")

    def then(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.then` not implemented")

    def alias(self, name: Optional[str] = None) -> Any:
        """
        Create an alias for this producer.

        If name is provided, creates a column alias for use in select statements.
        If name is not provided, creates a table alias (must be implemented by subclasses).
        """
        if name is not None:
            # Create an expression with the = operator and add an _alias_name attribute
            expr = Expression(self._model, self._model._builtin_relationships["="], self, Var(self._model, name))
            expr._alias_name = name  # Add this attribute to identify it as an alias expression
            return expr
        raise NotImplementedError(f"Table aliasing not implemented for {type(self).__name__}")

#--------------------------------------------------
# Concept
#--------------------------------------------------

class Concept(Producer):
    def __init__(self, name:str, model:Model):
        super().__init__(model)
        self._name = name
        self._alias_parent = self
        self._alias_count = 0
        self._alias_name = name
        self._relationships = {}

    def alias(self, name: Optional[str] = None) -> Any:
        if name is not None:
            return super().alias(name)

        c = Concept(self._name, self._model)
        parent = self._alias_parent
        c._alias_parent = parent
        parent._alias_count += 1
        c._alias_name = parent._name + str(parent._alias_count)
        return c

    def require(self, *args: Any) -> Fragment:
        return select(self).require(*args)

    # TODO maybe delete from_csv. Note from Sam:
    # Personally I'm in favor of a less coupled design. If we own the CSV ingestion, then we're going to be taking requests about adding certain kwargs, etc. If we let people do the ingestion on their own and just take the resulting data frame, then we separate concerns.
    def from_csv(self, path: str, keys: Any = None, rels: Any = None) -> Concept:
        return self.from_df(pd.read_csv(path), keys=keys, rels=rels)

    def from_df(self, df: pd.DataFrame, keys: Optional[list[str]] = None, rels: Optional[list[str]] = None) -> Concept:
        key_names = keys or df.columns
        rel_names = rels or [c for c in df.columns if c not in key_names]
        for row in df.itertuples(index=False):
            # construct entity using keys and derive properties
            self(
                **{k.lower(): getattr(row, k) for k in key_names}
            ).then(
                *[getattr(self, k.lower())(self, getattr(row, k)) for k in rel_names]
            )
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._model._construct(self, args, kwargs)

    def __str__(self):
        return self._alias_name

#--------------------------------------------------
# Relationship
#--------------------------------------------------

@dataclass
class Field():
    name:str
    type:Any

class Relationship(Producer):
    def __init__(self, *args:Any, parent:Producer|None, prop_name:str, model:Model):
        super().__init__(model)
        self._parent = parent
        self._name = prop_name
        self._prop_name = prop_name
        self._alias_parent = self
        self._alias_count = 0
        self._alias_name = prop_name
        self._relationships = {}
        self._fields:list[Field] = []
        for arg in args:
            if isinstance(arg, str) and not self._name:
                self._name = sanitize(arg).lower()
            else:
                self._fields.append(Field("", arg))
        model.relationships.append(self)

    def alias(self, name: Optional[str] = None) -> Any:
        if name is not None:
            return super().alias(name)

        r = Relationship(parent=self._parent, prop_name=self._prop_name, model=self._model)
        parent = self._alias_parent
        r._alias_parent = parent
        parent._alias_count += 1
        r._alias_name = parent._name + str(parent._alias_count)
        return r

    def __call__(self, *args: Any) -> Any:
        clean_args = list(args)
        if len(args) < len(self._fields):
            if self._parent:
                clean_args = [self._parent, *clean_args]
        return self._model._derive(self, clean_args)

    def __str__(self):
        if self._parent and self._prop_name:
            return f"{self._parent}.{self._alias_name}"
        return self._name

#--------------------------------------------------
# Expression
#--------------------------------------------------

class Expression(Producer):
    def __init__(self, model:Model, op:Relationship|Concept, *params:Any):
        super().__init__(model)
        self._op = op
        self._params = params

    def __str__(self):
        return f"({self._op} {' '.join(map(str, self._params))})"

    def __getattr__(self, name: str):
        raise AttributeError(f"Expression has no attribute {name}")

    # def where(self, *args: Any) -> Fragment:
    #     return where(*args, model=self._model)

    # def when(self, *args: Any) -> Fragment:
    #     return self._model.where(*args).then(self)

    def per(self, *args: Any) -> Expression:
        if isinstance(self._op, Aggregate):
            self._op._group = list(args)
            return self
        else:
            raise NotImplementedError(f"per is only supported for aggregates, not {type(self._op)}")

#--------------------------------------------------
# Var
#--------------------------------------------------

class Var(Producer):
    def __init__(self, model:Model, name:Optional[str]=None, type:Any=None):
        super().__init__(model)
        if not name:
            name = f"v{self._id}"
        self._name = name
        self._type = type

    def __str__(self):
        return str(self._name) if self._name else f"v{self._id}"

    def __getattr__(self, name: str):
        raise AttributeError(f"Var has no attribute {name}")

    def __hash__(self) -> int:
        return hash(self._id)

#--------------------------------------------------
# Fragment
#--------------------------------------------------

class Fragment():
    def __init__(self, parent:Fragment|None=None, kind:str="", items=None, model:Model|None=None):
        self._id = next(_global_id)
        self._stack = parent._stack + [self] if parent else [self]
        self._kind = kind
        self._items = list(items or [])
        self._model = parent._model if parent else model

    def select(self, *args: Any) -> Fragment:
        return select(*args, parent=self, model=self._model)

    def where(self, *args: Any) -> Fragment:
        return where(*args, parent=self, model=self._model)

    def require(self, *args: Any) -> Fragment:
        return require(*args, parent=self, model=self._model)

    def then(self, *args: Any) -> Fragment:
        return then(*args, parent=self, model=self._model)

    def _to_str(self):
        items = '\n  '.join(map(str, self._items))
        return f"{self._kind.upper()}\n  {items}"

    def __str__(self):
        return "\n".join([item._to_str() for item in self._stack])

    def __iter__(self):
        # Iterate over the rows of the fragment's results
        return self.to_df().itertuples(index=False)

    def inspect(self):
        # @TODO what format? maybe ignore row indices?
        print(self.to_df())

    def to_df(self):
        """Convert the fragment's results to a pandas DataFrame."""
        # @TODO currently this code assumes a Rel executor; should dispatch based on config
        if not self._model:
            raise ValueError("Cannot execute fragment without a model context")

        # from logscope import log
        # log(*self._model.rules)
        # log(self)

        builder_compiler = Compiler()
        rule_tasks = [builder_compiler.compile_fragment(rule, effects_only=True) for rule in self._model.rules]
        fragment_task = builder_compiler.compile_fragment(self)

        # log(*rule_tasks)
        # log(fragment_task)

        root = f.logical(rule_tasks + [fragment_task])
        ir_model = f.compute_model(root)

        executor = RelExecutor(self._model.name or "pyrel_main", dry_run=self._model._dry_run)
        results = executor.execute(ir_model)
        if isinstance(results, pd.DataFrame):
            return results
        else:
            # Convert results to DataFrame using the helper from snowflake.py
            df, _ = result_helpers.format_results(results, None)  # Pass None for task parameter
            return df


#--------------------------------------------------
# Select / Where
#--------------------------------------------------

def _get_model_or_error(args: tuple, model:Model|None=None) -> Model:
    if not model:
        # get model from first Producer or Fragment in args
        for arg in args:
            if isinstance(arg, (Producer, Fragment)) and arg._model:
                model = arg._model
                break
    if not model:
        raise ValueError("Cannot create fragment without a model context")
    return model

def select(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return _get_model_or_error(args, model=model).select(*args, parent=parent)

def where(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return _get_model_or_error(args, model=model).where(*args, parent=parent)

def require(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return _get_model_or_error(args, model=model).require(*args, parent=parent)

def then(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return _get_model_or_error(args, model=model).then(*args, parent=parent)


#--------------------------------------------------
# Model
#--------------------------------------------------

class Model():
    def __init__(self, name:str, dry_run: bool = False):
        self._id = next(_global_id)
        self.name = name
        self._dry_run = dry_run
        self.concepts:dict[str, Concept] = {}
        self.relationships:list[Relationship] = []
        self._builtin_relationships:dict[str, Relationship] = {}
        self.rules:OrderedSet[Fragment] = ordered_set()
        self._import_builtins()

    def _import_builtins(self):
        for attribute_name in dir(builtins):
            builtin = getattr(builtins, attribute_name)
            if isinstance(builtin, ir.Relation):
                self._builtin_relationships[builtin.name] = \
                    Relationship(parent=None, prop_name=builtin.name, model=self)
        for attribute_name in dir(types):
            builtin = getattr(types, attribute_name)
            if isinstance(builtin, ir.ScalarType):
                # TODO - if this is a list/set/union, should we create a concept as well?
                self.Concept(builtin.name)

    def Concept(self, name:str) -> Concept:
        if name not in self.concepts:
            self.concepts[name] = Concept(name, model=self)
        return self.concepts[name]

    def Relationship(self, *args) -> Relationship:
        return Relationship(*args, parent=None, prop_name="", model=self)

    def Vars(self, *types) -> list[Var]:
        if len(types) == 1 and isinstance(types[0], int):
            return [Var(self) for _ in range(types[0])]
        elif len(types) == 1 and isinstance(types[0], str):
            items = types[0].split()
            name_type = [item.split(":") if ":" in item else [item, None] for item in items]
            return [Var(self, name=pair[0], type=pair[1]) for pair in name_type]
        return [Var(self, type=type) for type in types]

    def _add_fragment(self, kind:str, *args: Any, parent:Fragment|None=None) -> Fragment:
        fragment = Fragment(parent=parent, kind=kind, items=args, model=self)
        # Add rule to the model, but remove any incomplete sub-fragments from the rules first
        for item in fragment._stack + fragment._items:
            if isinstance(item, Fragment) and item in self.rules:
                self.rules.remove(item)
        self.rules.add(fragment)
        return fragment

    def where(self, *args: Any, parent=None) -> Fragment:
        """Create a where fragment in this model's context"""
        return self._add_fragment("where", *args, parent=parent)

    def select(self, *args: Any, parent=None) -> Fragment:
        """Create a select fragment in this model's context"""
        return self._add_fragment("select", *args, parent=parent)

    def require(self, *args: Any, parent=None) -> Fragment:
        """Create a require fragment in this model's context"""
        return self._add_fragment("require", *args, parent=parent)

    def then(self, *args: Any, parent=None) -> Fragment:
        """Create an effects fragment in this model's context"""
        return self._add_fragment("effects", *args, parent=parent)

    def _construct(self, con: Concept, args, kwargs: dict) -> Fragment:
        return self._add_fragment("construct", con, args, kwargs)

    def _derive(self, rel: Relationship, args) -> Fragment:
        return self._add_fragment("derive", rel, args)

    def count(self, *args):
        """Create a count aggregate"""
        return Aggregate(self, "count", *args)

    def sum(self, *args):
        """Create a sum aggregate"""
        return Aggregate(self, "sum", *args)

    def min(self, *args):
        """Create a min aggregate"""
        return Aggregate(self, "min", *args)

    def max(self, *args):
        """Create a max aggregate"""
        return Aggregate(self, "max", *args)

    def avg(self, *args):
        """Create an average aggregate"""
        return Aggregate(self, "avg", *args)


#--------------------------------------------------
# Compile
#--------------------------------------------------

class CompilerContext():
    def __init__(self):
        self.var_map:dict[Concept|Relationship|Expression|Var, ir.Var] = {}
        self.items:OrderedSet[ir.Task] = OrderedSet()
        self.group_contexts = {}

    def to_var(self, item:Concept|Relationship|Expression|Var) -> ir.Var:
        if item not in self.var_map:
            name = ""
            if isinstance(item, Var):
                name = item._name or ""
            elif isinstance(item, (Concept, Relationship)):
                name = item._alias_name or ""
                if isinstance(item, Relationship) and isinstance(item._parent, Concept):
                    name = f"{item._parent._alias_name}_{name}"
            name = name.lower()
            self.var_map[item] = f.var(name, types.Any)
        return self.var_map[item]

    def add(self, item:ir.Task):
        self.items.add(item)

    def clone(self):
        c = CompilerContext()
        c.var_map = self.var_map.copy()
        return c


class Compiler():
    def __init__(self):
        self.types:dict[Concept, ir.Type] = {}
        self.relations:dict[Relationship|Concept, ir.Relation] = {}

    def to_type(self, concept:Concept) -> ir.Type:
        if concept not in self.types:
            if concept._name in types.builtin_scalar_types_by_name:
                self.types[concept] = types.builtin_scalar_types_by_name[concept._name]
            else:
                self.types[concept] = f.scalar_type(concept._name)
        return self.types[concept]

    def to_relation(self, item:Concept|Relationship) -> ir.Relation:
        if item not in self.relations:
            if isinstance(item, Concept):
                fields = [f.field(item._name.lower(), self.to_type(item))]
                relation = f.relation(item._name, fields)
            elif isinstance(item, Relationship):
                if item._name in builtins.builtin_relations_by_name:
                    relation = builtins.builtin_relations_by_name[item._name]
                else:
                    fields = [f.field(cur.name, types.Any) for cur in item._fields]
                    relation = f.relation(item._name, fields)
            self.relations[item] = relation
            return relation
        else:
            return self.relations[item]

    def compile_effect(self, ctx:CompilerContext, effect) -> PySequence[ir.Value]:
        if isinstance(effect, Concept):
            res = f.derive(self.to_relation(effect), [ctx.to_var(effect)])
        elif isinstance(effect, Expression):
            args = []
            op = effect._op
            if isinstance(op, Concept):
                rel = self.to_relation(op)
                for param in effect._params:
                    subs = self.compile_action(ctx, param)
                    args.append(subs[-1])
                # kwargs = getattr(effect, '_kwargs', {})
                # for name, value in kwargs.items():
                #     args.append(f.lit(name))
                #     args.append(f.lit(value))
                res = f.derive(rel, args)
            elif isinstance(op, Relationship) and op._parent:
                parent = self.compile_action(ctx, op._parent)
                args.append(parent[-1])
                rel = self.to_relation(op)
                for param in effect._params:
                    subs = self.compile_action(ctx, param)
                    args.append(subs[-1])
                res = f.derive(rel, args)
            else:
                rel = self.to_relation(op)
                for param in effect._params:
                    subs = self.compile_action(ctx, param)
                    args.append(subs[-1])
                res = f.derive(rel, args)
        elif isinstance(effect, Fragment):
            if effect._kind == "effects" and len(effect._items) == 1:
                return self.compile_effect(ctx, effect._items[0])
            elif effect._kind == "construct":
                return [self.compile_construct(ctx, *effect._items)]
            elif effect._kind == "derive":
                return [self.compile_derive(ctx, *effect._items)]
            else:
                raise ValueError(f"Cannot compile effect with fragment: {effect}")
        else:
            raise ValueError(f"Cannot compile effect: {effect}")
        ctx.add(res)
        return res.args

    def compile_construct(self, ctx: CompilerContext, con: Concept, args, kwargs: dict) -> ir.Var:
        # TODO handle args
        typ = cast(ir.ScalarType, self.to_type(con))
        var = ctx.to_var(con)
        ctx.add(f.derive(f.entity(typ), [var]))
        props = {}
        for k, v in kwargs.items():
            prop = f.property(k, con._name, typ, k, types.Any)
            comp_v = self.compile_action(ctx, v)[-1]
            props[prop] = comp_v
            ctx.add(f.derive(prop, [var, comp_v]))
        ctx.add(f.construct(var, props))
        return var

    def compile_derive(self, ctx: CompilerContext, rel: Relationship, args) -> ir.Var:
        assert len(args) <= 2 # TODO
        if len(args) == 1:
            key = rel._parent
            assert key and isinstance(key, Concept)
            val = args[0]
        else:
            key = args[0]
            val = args[1]
        prop = f.property(rel._name, key._name, self.to_type(key), rel._name, types.Any)
        val = self.compile_action(ctx, val)[-1]
        var = ctx.to_var(key)
        ctx.add(f.derive(prop, [var, val]))
        return var

    def compile_aggregate(self, ctx: CompilerContext, agg: Aggregate) -> ir.Var:
        """Compile an aggregate expression into IR"""
        agg_relation = f.relation(agg._name, [
            f.field("result", types.Any)
        ])

        # Handle projection vars and arg to be aggregated over
        proj_vars = []
        new_args = []
        if agg._name == "count" and not agg._args:
            new_args.append(f.lit(1))
        else:
            for i, arg in enumerate(agg._args):
                subs = self.compile_action(ctx, arg)
                if subs:  # Make sure subs is not None and not empty
                    if i < len(agg._args) - 1:
                        var = subs[-1]
                        if not isinstance(var, ir.Var):
                            # Only vars are supported in the projection list
                            var = f.var("proj", types.Any)
                            ctx.add(f.lookup(builtins.eq, [var, subs[-1]]))
                        proj_vars.append(subs[-1])
                    else:
                        # The last arg is the one to be aggregated over, and goes in the args list
                        new_args.append(subs[-1])
                else:
                    raise ValueError(f"Failed to compile aggregate argument: {arg}")

        # Handle group-by vars
        group_vars = []
        for group_var in agg._group:
            subs = self.compile_action(ctx, group_var)
            if subs:  # Make sure subs is not None and not empty
                var = subs[-1]
                if not isinstance(var, ir.Var):
                    # Only vars are supported in the group list
                    var = f.var("group", types.Any)
                    ctx.add(f.lookup(builtins.eq, [var, subs[-1]]))
                group_vars.append(var)
            else:
                raise ValueError(f"Failed to compile group variable: {group_var}")

        result_var_name = f"v{agg._id}"
        result_var = f.var(result_var_name, types.Any)
        new_args.append(result_var)

        agg_task = f.aggregate(agg_relation, proj_vars, group_vars, new_args)
        ctx.add(agg_task)

        if agg._where:
            for action in agg._where._items:
                self.compile_action(ctx, action)

        return result_var

    def compile_action(self, ctx: CompilerContext, action) -> PySequence[ir.Value]:
        if isinstance(action, Concept):
            res = f.lookup(self.to_relation(action), [ctx.to_var(action)])
        elif isinstance(action, Expression):
            rel = self.to_relation(action._op)
            args = []
            for param in action._params:
                subs = self.compile_action(ctx, param)
                args.append(subs[-1])
            if len(args) < len(rel.fields):
                args.append(f.var("", types.Any))
            res = f.lookup(rel, args)
        elif isinstance(action, Var):
            return [ctx.to_var(action)]
        elif isinstance(action, (str, int, float)):
            return [f.lit(action)]
        elif isinstance(action, Relationship):
            if isinstance(action, Aggregate):
                result_var = self.compile_aggregate(ctx, action)
                return [result_var]
            elif action._parent:
                parent = self.compile_action(ctx, action._parent)
                res = f.lookup(self.to_relation(action), [parent[-1], ctx.to_var(action)])
            else:
                raise ValueError(f"Cannot compile parentless relationship: {action}")
        elif isinstance(action, Fragment):
            if action._kind == "effects" and len(action._items) == 1:
                return self.compile_action(ctx, action._items[0])
            else:
                raise ValueError(f"Cannot compile action with fragment: {action}")
        elif isinstance(action, GroupingContext):
            return []
        else:
            raise ValueError(f"Cannot compile action {action} of type {type(action.__class__.__name__)}")

        if res is None:
            raise ValueError(f"Failed to compile action: {action}")

        ctx.add(res)
        return res.args

    def compile_fragment(self, fragment:Fragment, effects_only:bool=False) -> ir.Task:
        ctx = CompilerContext()
        reordered = []
        cur_effect = None

        ctx.group_contexts = {}

        for item in fragment._stack:
            if item._kind == "where":
                for action in item._items:
                    if isinstance(action, GroupingContext):
                        ctx.group_contexts[id(action)] = action
                    elif isinstance(action, Var) and hasattr(action, "_value") and isinstance(action._value, GroupingContext):
                        ctx.group_contexts[action._name] = action._value

        for item in fragment._stack:
            if item._kind in ["select", "require", "effects"]:
                cur_effect = item
            else:
                reordered.append(item)
        if cur_effect:
            reordered.append(cur_effect)

        for item in reordered:
            if item._kind == "select":
                aliases = []
                for ix, action in enumerate(item._items):
                    # Check whether this is an alias expression
                    if isinstance(action, Expression) and hasattr(action, '_alias_name'):
                        value_expr = action._params[0]
                        value_res = self.compile_action(ctx, value_expr)
                        if value_res and len(value_res) > 0:
                            aliases.append((action._alias_name, value_res[-1]))
                        else:
                            raise ValueError(f"Failed to compile alias expression: {action}")
                    else:
                        # Regular expression
                        res = self.compile_action(ctx, action)
                        if res and len(res) > 0:
                            name = ix
                            if isinstance(res[-1], ir.Var):
                                name = res[-1].name or f"v{res[-1].id}"
                            aliases.append((name, res[-1]))
                        else:
                            raise ValueError(f"Failed to compile select item: {action}")
                ctx.add(f.output(aliases))
            elif item._kind == "where":
                for action in item._items:
                    # Skip GroupingContext objects in where clauses
                    if isinstance(action, GroupingContext):
                        continue
                    try:
                        self.compile_action(ctx, action)
                    except Exception as e:
                        raise ValueError(f"Error compiling where clause action {action}: {e}")
            elif item._kind == "require":
                pass
            elif item._kind == "effects":
                for action in item._items:
                    self.compile_effect(ctx, action)
            elif item._kind == "construct":
                self.compile_construct(ctx, *item._items)
            elif item._kind == "derive":
                self.compile_derive(ctx, *item._items)

        if effects_only and not any(isinstance(i, ir.Update) for i in ctx.items.list):
            # If effects_only is true, only tasks involving updates
            # TODO this may not be a sufficient check - what if there are updates nested deeper inside?
            return f.logical([]) # TODO or f.success() but this causes error currently

        return f.logical(list(ctx.items))

#--------------------------------------------------
# Aggregate
#--------------------------------------------------

class Aggregate(Relationship):
    def __init__(self, model: Model, name: str, *args: Any):
        super().__init__(parent=None, prop_name=name, model=model)
        self._name = name
        self._args = args
        self._projection = []
        self._group = []
        self._where = None

    def per(self, *args: Any) -> Aggregate:
        """Specify the grouping variables for this aggregate"""
        self._group = list(args)
        return self

    def where(self, *args: Any) -> Aggregate:
        """Add filters to the aggregation"""
        # Create a where fragment that will be applied to this aggregate
        fragment = Fragment(parent=None, kind="where", items=args, model=self._model)
        self._where = fragment
        return self

    def alias(self, name: Optional[str] = None) -> Any:
        """Create an alias for this aggregate"""
        if name is not None:
            # Create an expression with the = operator and add an _alias_name attribute
            expr = Expression(self._model, self._model._builtin_relationships["="], self, Var(self._model, name))
            expr._alias_name = name  # Add this attribute to identify it as an alias expression
            return expr
        return super().alias(name)

    def __str__(self):
        args_str = ", ".join(map(str, self._args))
        group_str = ", ".join(map(str, self._group)) if self._group else ""
        return f"{self._name}({args_str}){' per ' + group_str if group_str else ''}"

def _create_aggregate_function(name: str):
    """Create an aggregate function with the given name"""
    def aggregate_function(*args: Any, model: Optional['Model'] = None) -> Aggregate:
        model = _get_model_or_error(args, model=model)
        return Aggregate(model, name, *args)
    return aggregate_function

# Define the standard aggregate functions
count = _create_aggregate_function("count")
sum = _create_aggregate_function("sum")
min = _create_aggregate_function("min")
max = _create_aggregate_function("max")
avg = _create_aggregate_function("avg")

class GroupingContext:
    def __init__(self, model: 'Model', *group_keys: Any):
        self._model = model
        self._group_keys = group_keys
        # Add a unique ID to help with identification
        self._id = next(_global_id)

    def __str__(self):
        keys_str = ", ".join(str(key) for key in self._group_keys)
        return f"per({keys_str})"

    def count(self, *args: Any) -> Aggregate:
        if not args:
            if self._group_keys:
                agg = Aggregate(self._model, "count", self._group_keys[0])
            else:
                agg = Aggregate(self._model, "count", 1)
        else:
            agg = Aggregate(self._model, "count", *args)

        agg._group = list(self._group_keys)
        return agg

    def sum(self, *args: Any) -> Aggregate:
        agg = Aggregate(self._model, "sum", *args)
        agg._group = list(self._group_keys)
        return agg

    def avg(self, *args: Any) -> Aggregate:
        agg = Aggregate(self._model, "avg", *args)
        agg._group = list(self._group_keys)
        return agg

    def min(self, *args: Any) -> Aggregate:
        agg = Aggregate(self._model, "min", *args)
        agg._group = list(self._group_keys)
        return agg

    def max(self, *args: Any) -> Aggregate:
        agg = Aggregate(self._model, "max", *args)
        agg._group = list(self._group_keys)
        return agg

def per(*args: Any, model: Optional['Model'] = None) -> GroupingContext:
    model = _get_model_or_error(args, model=model)
    return GroupingContext(model, *args)

def distinct(value: Any) -> 'Expression':
    """Create a distinct expression that removes duplicates"""
    if isinstance(value, Producer):
        model = value._model
        return Expression(model, model._builtin_relationships["distinct"], value)
    else:
        raise ValueError(f"Cannot create distinct expression from {value}")

__all__ = ["select", "where", "require", "then", "distinct", "per", "count", "sum", "min", "max", "avg"]

#--------------------------------------------------
# Todo
#--------------------------------------------------
"""
- [] construct
- [] static data handling
- [] Quantifiers
    - [] not
    - [] exists
    - [] forall
- [] Aggregates
- [] Require
- [] Multi-step chaining
- [] oneof
- [] anyof
- [] query when iterating over a select
- [] capture all rules
- [] implement aliasing
    - [] Concept
    - [] Relationship
    - [] Expression
- [] support defining relationships via madlibs Relationship("{Person} was born on {birthday:Date}")
- [] handle relationships with multiple name fields being accessed via prop:
    Package.shipment = Relationship("{Package} in {Shipment} on {Date}")
    Package.shipment.date, Package.shipment.shipment, Package.shipment.package
- [] import handling
    - [] table
    - [] csv

"""
