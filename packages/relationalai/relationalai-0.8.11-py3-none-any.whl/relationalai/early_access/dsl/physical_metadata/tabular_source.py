from relationalai.early_access.dsl.core.types.standard import RowId, Integer
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.dsl.types.values import ValueType


class TabularSource:
    def __init__(self, name: str, schema: dict[str, ValueType], model: Model):
        self._name = name
        self._schema = schema

        self.basic_type_schema = {
            k: "Int64" if v.root_unconstrained_type() == Integer else "string"
            for k, v in schema.items()
        }

        for column_name, column_type in schema.items():
            setattr(self, column_name,
                    model.external_relation(f"{self._name}:{column_name}", RowId, column_type))
