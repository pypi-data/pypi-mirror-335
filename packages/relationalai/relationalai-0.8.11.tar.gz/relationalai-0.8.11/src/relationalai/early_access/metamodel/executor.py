from __future__ import annotations

from pandas import DataFrame
from typing import Any, Optional, Union

from relationalai.early_access.metamodel import Model, compiler

class Executor():
    """ Interface for an object that can execute the program specified by a model. """
    def execute(self, model: Model, observer: Optional[compiler.Observer]=None) -> Union[DataFrame, Any]:
        raise NotImplementedError(f"execute: {self}")
