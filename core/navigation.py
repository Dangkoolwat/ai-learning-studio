"""Navigation contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError


EXPECTED_VERSION = 1
EXPECTED_SECTIONS = (
    {"id": "ai-practice", "label": "AI 체험 실습", "order": 1},
    {"id": "ready-to-use", "label": "바로 사용하기", "order": 2},
    {"id": "ai-assistant", "label": "AI 도우미", "order": 3},
    {"id": "image-ai", "label": "이미지 AI", "order": 4},
)


@dataclass(slots=True, frozen=True)
class NavigationSection:
    """A confirmed top-level navigation section."""

    id: str
    label: str
    order: int

    def to_public_dict(self) -> dict[str, object]:
        return {"id": self.id, "label": self.label, "order": self.order}


@dataclass(slots=True)
class NavigationData:
    """The validated navigation contract."""

    version: int
    sections: tuple[NavigationSection, ...]

    def to_public_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "sections": [section.to_public_dict() for section in self.sections],
        }


def load_navigation(data_dir: Path) -> NavigationData:
    navigation_path = data_dir / "navigation.json"
    if not navigation_path.is_file():
        raise BuildError(
            "Load navigation data",
            "data/navigation.json is missing",
            path=navigation_path,
            data_file=navigation_path,
        )

    try:
        payload = json.loads(navigation_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError(
            "Load navigation data",
            f"data/navigation.json is not valid JSON: {exc.msg}",
            path=navigation_path,
            data_file=navigation_path,
        ) from exc

    if not isinstance(payload, dict):
        raise BuildError(
            "Load navigation data",
            "navigation data must be a JSON object",
            path=navigation_path,
            data_file=navigation_path,
        )

    version = payload.get("version")
    if version != EXPECTED_VERSION:
        raise BuildError(
            "Load navigation data",
            f"navigation version must be {EXPECTED_VERSION}",
            path=navigation_path,
            data_file=navigation_path,
            field="version",
        )

    sections = payload.get("sections")
    if not isinstance(sections, list):
        raise BuildError(
            "Load navigation data",
            "navigation sections must be a JSON array",
            path=navigation_path,
            data_file=navigation_path,
            field="sections",
        )
    if len(sections) != len(EXPECTED_SECTIONS):
        raise BuildError(
            "Load navigation data",
            f"navigation must define exactly {len(EXPECTED_SECTIONS)} sections",
            path=navigation_path,
            data_file=navigation_path,
            field="sections",
        )

    parsed_sections: list[NavigationSection] = []
    for expected, section_data in zip(EXPECTED_SECTIONS, sections, strict=True):
        if not isinstance(section_data, dict):
            raise BuildError(
                "Load navigation data",
                "each navigation section must be a JSON object",
                path=navigation_path,
                data_file=navigation_path,
            )

        allowed_keys = {"id", "label", "order"}
        unexpected_keys = set(section_data) - allowed_keys
        missing_keys = allowed_keys - set(section_data)
        if unexpected_keys or missing_keys:
            details = []
            if missing_keys:
                details.append(f"missing keys: {', '.join(sorted(missing_keys))}")
            if unexpected_keys:
                details.append(f"unexpected keys: {', '.join(sorted(unexpected_keys))}")
            raise BuildError(
                "Load navigation data",
                "navigation section fields do not match the expected contract"
                + (" (" + "; ".join(details) + ")" if details else ""),
                path=navigation_path,
                data_file=navigation_path,
            )

        if section_data["id"] != expected["id"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section id must be {expected['id']}",
                path=navigation_path,
                data_file=navigation_path,
                field="id",
            )
        if section_data["label"] != expected["label"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section label must be {expected['label']}",
                path=navigation_path,
                data_file=navigation_path,
                field="label",
            )
        if section_data["order"] != expected["order"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section order must be {expected['order']}",
                path=navigation_path,
                data_file=navigation_path,
                field="order",
            )

        parsed_sections.append(
            NavigationSection(
                id=section_data["id"],
                label=section_data["label"],
                order=section_data["order"],
            )
        )

    return NavigationData(version=EXPECTED_VERSION, sections=tuple(parsed_sections))
