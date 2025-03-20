from __future__ import annotations

import contextlib

import nshconfig as C
import torch


@contextlib.contextmanager
def rng_context(config: RNGConfig | None):
    with contextlib.ExitStack() as stack:
        if config is not None:
            stack.enter_context(
                torch.random.fork_rng(devices=range(torch.cuda.device_count()))
            )
            torch.manual_seed(config.seed)

        yield


class RNGConfig(C.Config):
    seed: int
    """Random seed to use for initialization."""
