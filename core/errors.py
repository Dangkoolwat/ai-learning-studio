"""Shared build error helpers for AI Learning Studio."""

from __future__ import annotations

from pathlib import Path


class BuildError(RuntimeError):
    """Raised when the static-site build pipeline encounters a contract failure."""

    def __init__(
        self,
        stage: str,
        message: str,
        *,
        path: Path | str | None = None,
        data_file: Path | str | None = None,
        source_file: Path | str | None = None,
        page_id: str | None = None,
        field: str | None = None,
    ) -> None:
        self.stage = stage
        self.message = message
        self.path = self._coerce_path(path)
        self.data_file = self._coerce_path(data_file)
        self.source_file = self._coerce_path(source_file)
        self.page_id = page_id
        self.field = field
        super().__init__(message)

    @staticmethod
    def _coerce_path(value: Path | str | None) -> Path | None:
        if value is None:
            return None
        if isinstance(value, Path):
            return value
        return Path(value)

    def format_for_console(self) -> str:
        parts = [f"[{self.stage}]"]
        if self.path is not None:
            parts.append(f"[path={self.path.as_posix()}]")
        if self.data_file is not None:
            parts.append(f"[data={self.data_file.as_posix()}]")
        if self.source_file is not None:
            parts.append(f"[source={self.source_file.as_posix()}]")
        if self.page_id is not None:
            parts.append(f"[page={self.page_id}]")
        if self.field is not None:
            parts.append(f"[field={self.field}]")
        parts.append(self.message)
        return " ".join(parts)
