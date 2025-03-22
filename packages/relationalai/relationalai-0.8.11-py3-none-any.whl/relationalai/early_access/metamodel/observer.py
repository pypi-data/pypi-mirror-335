from __future__ import annotations
from dataclasses import dataclass, field

from typing import Any, Tuple
import datetime as dt

class Observer():
    """ An object that receives updates on the progress of a compilation or execution. """
    def update(self, key: str, result: Any, timing: float):
        # TODO - this API is good for compiler passes, but we may want to improve it, e.g.
        # to add sources, etc, everything that is needed by the debugger.
        pass

@dataclass(frozen=True)
class ObserverList(Observer):
    """ An observer that calls multiple observers. """
    observers: list[Observer]

    def update(self, key: str, result: Any, timing: float):
        for o in self.observers:
            o.update(key, result, timing)

@dataclass(frozen=True)
class Capture(Observer):
    """ An observer that just captures all updates in a list. """
    passes: list[Tuple[str, Any, float]] = field(default_factory=list)

    def update(self, key: str, result: Any, timing: float):
        self.passes.append((key, result, timing))

@dataclass(frozen=True)
class Logger(Observer):
    """ An observer that just prints the updates to stdout. """
    def update(self, key: str, result: Any, timing: float):
        if result is None:
            print(f"[{dt.datetime.now()}] ({timing}) {key}")
        else:
            print(f"[{dt.datetime.now()}] ({timing}) {key}: {result}")
