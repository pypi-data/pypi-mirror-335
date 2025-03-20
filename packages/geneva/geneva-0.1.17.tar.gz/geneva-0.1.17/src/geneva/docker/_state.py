# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# Module for tracking local packaging cache state
# Private to the docker packaging module
import os
from pathlib import Path

import attrs

from geneva.utils.sqlitekv import SQLiteKV


@attrs.define
class PackagingState:
    """Local packaging cache state"""

    # Path to the packaging cache
    store_path: Path = attrs.field(
        default=Path(os.environ.get("XDG_CONFIG_DIR", "~/.cache"))
        / "_geneva/ws_packager",
        converter=Path,
    )

    _SQLITE_NAME = "state.db"
    _state_store: SQLiteKV = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self._state_store = SQLiteKV(
            self.store_path.expanduser().resolve() / self._SQLITE_NAME,
        )

    def current_incremental_image(self, context_hash: str) -> str | None:
        return self._state_store.get(f"{context_hash}#last_pushed_image", None)

    def set_incremental_image(self, context_hash: str, image_name: str) -> None:
        self._state_store[f"{context_hash}#last_pushed_image"] = image_name
