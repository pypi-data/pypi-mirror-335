from __future__ import annotations

import contextlib
import copy
from collections.abc import Callable, Sequence
from typing import Any, Literal, Protocol, runtime_checkable

import nshconfig as C
import torch
import torch.nn as nn
from typing_extensions import deprecated, override

from .nonlinearity import NonlinearityConfig, NonlinearityConfigBase


@runtime_checkable
class LinearModuleConstructor(Protocol):
    def __call__(
        self, in_features: int, out_features: int, bias: bool = True
    ) -> nn.Module: ...


class ResidualSequential(nn.Sequential):
    @override
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return input + super().forward(input)


class MLPConfig(C.Config):
    bias: bool = True
    """Whether to include bias terms in the linear layers."""

    no_bias_scalar: bool = True
    """Whether to exclude bias terms when the output dimension is 1."""

    nonlinearity: NonlinearityConfig | None = None
    """Activation function to use between layers."""

    ln: bool | Literal["pre", "post"] = False
    """Whether to apply layer normalization before or after the linear layers."""

    dropout: float | None = None
    """Dropout probability to apply between layers."""

    residual: bool = False
    """Whether to use residual connections between layers."""

    seed: int | None = None
    """Random seed to use for initialization. If None, the default Torch behavior is used."""

    @deprecated("Use `nt.nn.MLP(config=...)` instead.")
    def create_module(
        self,
        dims: Sequence[int],
        pre_layers: Sequence[nn.Module] = [],
        post_layers: Sequence[nn.Module] = [],
        linear_cls: LinearModuleConstructor = nn.Linear,
    ):
        kwargs: dict[str, Any] = {
            "bias": self.bias,
            "no_bias_scalar": self.no_bias_scalar,
            "nonlinearity": self.nonlinearity,
            "ln": self.ln,
            "dropout": self.dropout,
            "residual": self.residual,
            "seed": self.seed,
        }
        return MLP(
            dims,
            **kwargs,
            pre_layers=pre_layers,
            post_layers=post_layers,
            linear_cls=linear_cls,
        )


@contextlib.contextmanager
def custom_seed_context(seed: int | None):
    with contextlib.ExitStack() as stack:
        if seed is not None:
            stack.enter_context(
                torch.random.fork_rng(devices=range(torch.cuda.device_count()))
            )
            torch.manual_seed(seed)

        yield


def MLP(
    dims: Sequence[int],
    activation: NonlinearityConfigBase
    | nn.Module
    | Callable[[], nn.Module]
    | None = None,
    nonlinearity: NonlinearityConfigBase
    | nn.Module
    | Callable[[], nn.Module]
    | None = None,
    bias: bool | None = None,
    no_bias_scalar: bool | None = None,
    ln: bool | Literal["pre", "post"] | None = None,
    dropout: float | None = None,
    residual: bool | None = None,
    pre_layers: Sequence[nn.Module] = [],
    post_layers: Sequence[nn.Module] = [],
    linear_cls: LinearModuleConstructor = nn.Linear,
    seed: int | None = None,
    config: MLPConfig | None = None,
):
    """
    Constructs a multi-layer perceptron (MLP) with the given dimensions and activation function.

    Args:
        dims (Sequence[int]): List of integers representing the dimensions of the MLP.
        nonlinearity (Callable[[], nn.Module] | None, optional): Activation function to use between layers.
        activation (Callable[[], nn.Module] | None, optional): Activation function to use between layers.
        bias (bool | None, optional): Whether to include bias terms in the linear layers.
        no_bias_scalar (bool | None, optional): Whether to exclude bias terms when the output dimension is 1.
        ln (bool | Literal["pre", "post"] | None, optional): Whether to apply layer normalization before or after the linear layers.
        dropout (float | None, optional): Dropout probability to apply between layers.
        residual (bool | None, optional): Whether to use residual connections between layers.
        pre_layers (Sequence[nn.Module], optional): List of layers to insert before the linear layers. Defaults to [].
        post_layers (Sequence[nn.Module], optional): List of layers to insert after the linear layers. Defaults to [].
        linear_cls (LinearModuleConstructor, optional): Linear module constructor to use. Defaults to nn.Linear.
        seed (int | None, optional): Random seed to use for initialization. If None, the default Torch behavior is used.
        config (MLPConfig | None, optional): Configuration object for the MLP. Parameters specified directly take precedence.

    Returns:
        nn.Sequential: The constructed MLP.
    """

    # Resolve parameters: arg if not None, otherwise config value if config exists, otherwise default
    resolved_bias = bias if bias is not None else (config.bias if config else True)
    resolved_no_bias_scalar = (
        no_bias_scalar
        if no_bias_scalar is not None
        else (config.no_bias_scalar if config else True)
    )
    resolved_nonlinearity = (
        nonlinearity
        if nonlinearity is not None
        else (config.nonlinearity if config else None)
    )
    resolved_ln = ln if ln is not None else (config.ln if config else False)
    resolved_dropout = (
        dropout if dropout is not None else (config.dropout if config else None)
    )
    resolved_residual = (
        residual if residual is not None else (config.residual if config else False)
    )
    resolved_seed = seed if seed is not None else (config.seed if config else None)

    with custom_seed_context(resolved_seed):
        if activation is None:
            activation = resolved_nonlinearity

        if len(dims) < 2:
            raise ValueError("mlp requires at least 2 dimensions")
        if resolved_ln is True:
            resolved_ln = "pre"
        elif isinstance(resolved_ln, str) and resolved_ln not in ("pre", "post"):
            raise ValueError("ln must be a boolean or 'pre' or 'post'")

        layers: list[nn.Module] = []
        if resolved_ln == "pre":
            layers.append(nn.LayerNorm(dims[0]))

        layers.extend(pre_layers)

        for i in range(len(dims) - 1):
            in_features = dims[i]
            out_features = dims[i + 1]
            bias_ = resolved_bias and not (
                resolved_no_bias_scalar and out_features == 1
            )
            layers.append(linear_cls(in_features, out_features, bias=bias_))
            if resolved_dropout is not None:
                layers.append(nn.Dropout(resolved_dropout))
            if i < len(dims) - 2:
                match activation:
                    case NonlinearityConfigBase():
                        layers.append(activation.create_module())
                    case nn.Module():
                        # In this case, we create a deep copy of the module to avoid sharing parameters (if any).
                        layers.append(copy.deepcopy(activation))
                    case Callable():
                        layers.append(activation())
                    case _:
                        raise ValueError(
                            "Either `nonlinearity` or `activation` must be provided"
                        )

        layers.extend(post_layers)

        if resolved_ln == "post":
            layers.append(nn.LayerNorm(dims[-1]))

        cls = ResidualSequential if resolved_residual else nn.Sequential
        return cls(*layers)
