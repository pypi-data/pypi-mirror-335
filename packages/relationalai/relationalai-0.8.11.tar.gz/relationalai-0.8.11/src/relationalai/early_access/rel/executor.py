from __future__ import annotations

from pandas import DataFrame
from typing import Any, Optional, Union
import relationalai as rai

from relationalai.early_access.metamodel import ir, compiler, executor as e
from relationalai.early_access.rel import Compiler

class RelExecutor(e.Executor):
    """Executes Rel code using the RAI client."""

    def __init__(self, database: str, dry_run: bool = False) -> None:
        super().__init__()
        self.database = database
        self.dry_run = dry_run


    def execute(self, model: ir.Model, observer: Optional[compiler.Observer]=None) -> Union[DataFrame, Any]:
        """
        Execute Rel code for a given model/database name.

        Args:
            model: The name of the model/database
            rel_code: The fragment to execute
            rules: Optional list of rule fragments to compile before the rel_code

        Returns:
            The result of executing the Rel code
        """

        rel_compiler = Compiler()
        full_code = rel_compiler.compile(model, observer)

        # from logscope import log
        # log(full_code)

        if self.dry_run:
            return DataFrame()

        resources = rai.clients.snowflake.Resources()
        resources.config.set("use_graph_index", False)

        try:
            resources.create_graph(self.database)
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise e

        engine = resources.config.get("engine")
        return resources.exec_raw(self.database, engine, full_code)
