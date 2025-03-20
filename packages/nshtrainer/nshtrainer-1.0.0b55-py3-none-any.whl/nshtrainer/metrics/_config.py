from __future__ import annotations

import builtins
from typing import Any, Literal

import nshconfig as C


class MetricConfig(C.Config):
    monitor: str
    """The name of the metric to monitor."""

    mode: Literal["min", "max"]
    """
    The mode of the primary metric:
    - "min" for metrics that should be minimized (e.g., loss)
    - "max" for metrics that should be maximized (e.g., accuracy)
    """

    @property
    def best(self):
        return builtins.min if self.mode == "min" else builtins.max

    def is_better(self, a: Any, b: Any):
        return self.best(a, b) == a
