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
        theme_id: str | None = None,
        section: str | None = None,
        token_name: str | None = None,
        page_id: str | None = None,
        field: str | None = None,
        renderer_id: str | None = None,
        page_type: str | None = None,
        page_route: str | None = None,
        control_block_type: str | None = None,
        control_block_index: int | None = None,
        control_block_id: str | None = None,
        invalid_key: str | None = None,
    ) -> None:
        self.stage = stage
        self.message = message
        self.path = self._coerce_path(path)
        self.data_file = self._coerce_path(data_file)
        self.source_file = self._coerce_path(source_file)
        self.theme_id = theme_id
        self.section = section
        self.token_name = token_name
        self.page_id = page_id
        self.field = field
        self.renderer_id = renderer_id
        self.page_type = page_type
        self.page_route = page_route
        self.control_block_type = control_block_type
        self.control_block_index = control_block_index
        self.control_block_id = control_block_id
        self.invalid_key = invalid_key
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
        if self.theme_id is not None:
            parts.append(f"[theme={self.theme_id}]")
        if self.section is not None:
            parts.append(f"[section={self.section}]")
        if self.token_name is not None:
            parts.append(f"[token={self.token_name}]")
        if self.page_id is not None:
            parts.append(f"[page={self.page_id}]")
        if self.field is not None:
            parts.append(f"[field={self.field}]")
        if self.renderer_id is not None:
            parts.append(f"[renderer={self.renderer_id}]")
        if self.page_type is not None:
            parts.append(f"[page_type={self.page_type}]")
        if self.page_route is not None:
            parts.append(f"[route={self.page_route}]")
        if self.control_block_type is not None:
            parts.append(f"[block={self.control_block_type}]")
        if self.control_block_index is not None:
            parts.append(f"[index={self.control_block_index}]")
        if self.control_block_id is not None:
            parts.append(f"[block_id={self.control_block_id}]")
        if self.invalid_key is not None:
            parts.append(f"[key={self.invalid_key}]")
        parts.append(self.message)
        return " ".join(parts)
