from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from lightning.pytorch import Trainer

from ..util.path import path_exists, try_symlink_or_copy
from .metadata import (
    link_checkpoint_metadata,
    remove_checkpoint_metadata,
    remove_checkpoint_metadata_link,
)

log = logging.getLogger(__name__)


def link_checkpoint(
    filepath: str | Path | os.PathLike,
    linkpath: str | Path | os.PathLike,
    *,
    metadata: bool,
    remove_existing: bool = True,
):
    filepath = Path(filepath)
    linkpath = Path(linkpath)

    if remove_existing:
        try:
            if path_exists(linkpath, follow_symlinks=False):
                # follow_symlinks=False is EXTREMELY important here
                # Otherwise, we've already deleted the file that the symlink
                # used to point to, so this always returns False
                if linkpath.is_dir():
                    shutil.rmtree(linkpath)
                else:
                    linkpath.unlink(missing_ok=True)
        except Exception:
            log.warning(f"Failed to remove {linkpath}", exc_info=True)
        else:
            log.debug(f"Removed {linkpath=}")

        if metadata:
            remove_checkpoint_metadata_link(linkpath)

    try_symlink_or_copy(filepath, linkpath)
    if metadata:
        link_checkpoint_metadata(filepath, linkpath)


def remove_checkpoint(
    trainer: Trainer,
    filepath: str | Path | os.PathLike,
    *,
    metadata: bool,
):
    filepath = Path(filepath)

    trainer.strategy.remove_checkpoint(filepath)

    if metadata:
        remove_checkpoint_metadata(filepath)
