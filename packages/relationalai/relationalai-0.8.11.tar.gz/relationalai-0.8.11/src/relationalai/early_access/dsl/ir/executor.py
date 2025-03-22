from typing import List, Optional

from pandas import DataFrame
import relationalai as rai
from relationalai.early_access.dsl.ir.compiler import Compiler
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.rel.compiler import ModelToRel


class RelExecutor:

    @staticmethod
    def execute_model(model: Model, result_cols: Optional[List[str]] = None) -> DataFrame:
        ir_model = Compiler().compile_model(model)
        rel_model = str(ModelToRel().to_rel(ir_model))
        return RelExecutor.execute(model.name, rel_model, result_cols)

    @staticmethod
    def execute(database: str, rel_model: str, result_cols: Optional[List[str]] = None) -> DataFrame:
        """Executes Rel code using the RAI client."""

        resources = rai.clients.snowflake.Resources()
        resources.config.set("use_graph_index", False)

        try:
            resources.create_graph(database)
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise e

        engine = resources.config.get("engine")
        results = resources.exec_raw(database, engine, rel_model)

        from relationalai.clients import result_helpers
        df, _ = result_helpers.format_results(results, None, result_cols)

        return df