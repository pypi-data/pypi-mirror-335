# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# a zip packager for local workspace

import hashlib
import logging
import re
import site
import sys
import tempfile
import zipfile
from pathlib import Path

import attrs

from geneva.config import CONFIG_LOADER, ConfigBase

_LOG = logging.getLogger(__name__)


@attrs.define
class _ZipperConfig(ConfigBase):
    output_path: Path | None = attrs.field(
        validator=attrs.validators.instance_of(Path),
        converter=attrs.converters.optional(Path),
    )

    @classmethod
    def name(cls) -> str:
        return "zipper"


@attrs.define
class WorkspaceZipper:
    path: Path = attrs.field(
        converter=attrs.converters.pipe(
            Path,
            Path.resolve,
            Path.absolute,
        )
    )

    @path.validator
    def _path_validator(self, attribute, value: Path) -> None:
        if not value.is_dir():
            raise ValueError("path must be a directory")

        # make sure the path is the current working directory, or
        # is part of sys.path
        if value == Path.cwd().resolve().absolute():
            return

        sys_paths = {Path(x).resolve().absolute() for x in sys.path}

        if value not in sys_paths:
            raise ValueError("path must be cwd or part of sys.path")

    output_dir: Path = attrs.field()

    @output_dir.default
    def _output_dir_default(self) -> Path:
        config = CONFIG_LOADER.load(_ZipperConfig)
        if config.output_path is not None:
            return config.output_path
        return self.path / ".geneva"

    ignore_regexs: list[re.Pattern] = attrs.field(
        factory=list,
        converter=lambda x: [re.compile(r) for r in x],
    )

    file_name: str = attrs.field(default="workspace.zip")

    def zip(self) -> tuple[Path, str]:
        """
        create a zip file for the workspace

        return the path of the zip file and the sha256 hash of the zip file
        """
        zip_path = self.output_dir / self.file_name
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for child in self.path.rglob("*"):
                if any(r.match(child) for r in self.ignore_regexs):
                    continue
                arcname = child.relative_to(self.path)
                z.write(child, arcname.as_posix())
        return zip_path, hashlib.sha256(zip_path.read_bytes()).hexdigest()


@attrs.define
class _UnzipperConfig(ConfigBase):
    output_dir: Path | None = attrs.field(
        converter=attrs.converters.optional(Path),
        default=None,
    )

    @classmethod
    def name(cls) -> str:
        return "unzipper"


# Kept separate from the zipper to avoid config mess
@attrs.define
class WorkspaceUnzipper:
    output_dir: Path = attrs.field(
        converter=attrs.converters.pipe(
            attrs.converters.default_if_none(
                CONFIG_LOADER.load(_UnzipperConfig).output_dir,
            ),
            attrs.converters.default_if_none(
                factory=tempfile.mkdtemp,
            ),
            Path,
            Path.resolve,
            Path.absolute,
        ),
        default=None,
    )

    def unzip(self, zip_path: Path, *, checksum: str) -> None:
        """
        extract the zip file to the workspace
        """
        if hashlib.sha256(zip_path.read_bytes()).hexdigest() != checksum:
            raise ValueError("workspace zip checksum mismatch")

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(self.output_dir)
        _LOG.info("extracted workspace to %s", self.output_dir)

        site.addsitedir(self.output_dir.as_posix())
        _LOG.info("added %s to sys.path", self.output_dir)
