import pandas as pd

from relationalai.early_access.dsl.core.relations import rule, Relation
from relationalai.early_access.dsl.physical_metadata.tabular_source import TabularSource

class TabularSourceModule:
    def generate(self, table: TabularSource, data: pd.DataFrame):
        for index, row in data.iterrows():
            for column in data.columns:
                value = row[column]
                if pd.notna(value):
                    self._row_to_value_rule(table.__getattribute__(column), index, value)

    @staticmethod
    def _row_to_value_rule(relation: Relation, row, value):
        with relation:
            @rule()
            def row_to_value(r, v):
                r == row
                v == value