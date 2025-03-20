from __future__ import annotations

import logging
from typing import Literal

from lightning.pytorch.utilities.exceptions import MisconfigurationException
from typing_extensions import final, override, assert_never
from lightning.pytorch import Trainer
from lightning.pytorch.callbacks import Callback
from ..metrics import MetricConfig
from .base import CallbackConfigBase, callback_registry

log = logging.getLogger(__name__)


@final
@callback_registry.register
class MetricValidationCallbackConfig(CallbackConfigBase):
    name: Literal["metric_validation"] = "metric_validation"

    error_behavior: Literal["raise", "warn"] = "raise"
    """
    Behavior when an error occurs during validation:
    - "raise": Raise an error and stop the training.
    - "warn": Log a warning and continue the training.
    """

    validate_default_metric: bool = True
    """Whether to validate the default metric from the root config."""

    metrics: list[MetricConfig] = []
    """List of metrics to validate."""

    @override
    def create_callbacks(self, trainer_config):
        metrics = self.metrics.copy()
        if (
            self.validate_default_metric
            and (default_metric := trainer_config.primary_metric) is not None
        ):
            metrics.append(default_metric)

        yield MetricValidationCallback(self, metrics)


class MetricValidationCallback(Callback):
    def __init__(
        self,
        config: MetricValidationCallbackConfig,
        metrics: list[MetricConfig],
    ):
        super().__init__()

        self.config = config
        self.metrics = metrics

    def _check_metrics(self, trainer: Trainer):
        metric_names = ", ".join(metric.monitor for metric in self.metrics)
        log.info(f"Validating metrics: {metric_names}...")
        logged_metrics = set(trainer.logged_metrics.keys())

        invalid_metrics: list[str] = []
        for metric in self.metrics:
            if metric.monitor not in logged_metrics:
                invalid_metrics.append(metric.monitor)

        if invalid_metrics:
            msg = (
                f"The following metrics were not found in logged metrics: {invalid_metrics}\n"
                f"List of logged metrics: {list(trainer.logged_metrics.keys())}"
            )
            match self.config.error_behavior:
                case "raise":
                    raise MisconfigurationException(msg)
                case "warn":
                    log.warning(msg)
                case _:
                    assert_never(self.config.error_behavior)

    @override
    def on_sanity_check_end(self, trainer, pl_module):
        super().on_sanity_check_end(trainer, pl_module)

        self._check_metrics(trainer)

    @override
    def on_validation_end(self, trainer, pl_module):
        super().on_validation_end(trainer, pl_module)

        self._check_metrics(trainer)
