"""Navigation contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError


EXPECTED_VERSION = 1


@dataclass(frozen=True)
class NavigationSubItem:
    """A sub-item entry under a main navigation section."""

    id: str
    label: str
    description: str
    route: str

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "route": self.route,
        }


@dataclass(frozen=True)
class NavigationSection:
    """A confirmed top-level navigation section."""

    id: str
    label: str
    description: str
    order: int
    items: tuple[NavigationSubItem, ...] = ()

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "order": self.order,
            "items": [item.to_public_dict() for item in self.items],
        }


@dataclass
class NavigationData:
    """The validated navigation contract."""

    version: int
    sections: tuple[NavigationSection, ...]

    def to_public_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "sections": [section.to_public_dict() for section in self.sections],
        }


def _require_section_text(
    value: object,
    *,
    message: str,
    navigation_path: Path,
    field: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BuildError(
            "Load navigation data",
            message,
            path=navigation_path,
            data_file=navigation_path,
            field=field,
        )
    return value


def load_navigation(data_dir: Path) -> NavigationData:
    """Load and structurally validate data/navigation.json.

    The navigation JSON file is the single source of truth for menu data.
    Validation covers structure, field types, uniqueness, and route shape;
    cross-file consistency with the page registry is enforced separately by
    core.data_consistency.
    """
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
    if not sections:
        raise BuildError(
            "Load navigation data",
            "navigation must define at least one section",
            path=navigation_path,
            data_file=navigation_path,
            field="sections",
        )

    parsed_sections: list[NavigationSection] = []
    seen_section_ids: set[str] = set()
    seen_item_ids: set[str] = set()

    for section_data in sections:
        if not isinstance(section_data, dict):
            raise BuildError(
                "Load navigation data",
                "each navigation section must be a JSON object",
                path=navigation_path,
                data_file=navigation_path,
            )

        allowed_keys = {"id", "label", "description", "order", "items"}
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

        section_id = _require_section_text(
            section_data["id"],
            message="navigation section id must be a non-empty string",
            navigation_path=navigation_path,
            field="id",
        )
        if section_id in seen_section_ids:
            raise BuildError(
                "Load navigation data",
                f"duplicate navigation section id: {section_id}",
                path=navigation_path,
                data_file=navigation_path,
                field="id",
            )
        seen_section_ids.add(section_id)

        _require_section_text(
            section_data["label"],
            message=f"navigation section label must be a non-empty string for section: {section_id}",
            navigation_path=navigation_path,
            field="label",
        )
        _require_section_text(
            section_data["description"],
            message=f"navigation section description must be a non-empty string for section: {section_id}",
            navigation_path=navigation_path,
            field="description",
        )

        order = section_data["order"]
        if not isinstance(order, int) or isinstance(order, bool):
            raise BuildError(
                "Load navigation data",
                f"navigation section order must be an integer for section: {section_id}",
                path=navigation_path,
                data_file=navigation_path,
                field="order",
            )

        raw_items = section_data.get("items", [])
        if not isinstance(raw_items, list):
            raise BuildError(
                "Load navigation data",
                f"navigation section items must be a list for section: {section_id}",
                path=navigation_path,
                data_file=navigation_path,
                field="items",
            )

        parsed_items: list[NavigationSubItem] = []
        for item_data in raw_items:
            if not isinstance(item_data, dict):
                raise BuildError(
                    "Load navigation data",
                    "each navigation sub-item must be a JSON object",
                    path=navigation_path,
                    data_file=navigation_path,
                )

            item_allowed_keys = {"id", "label", "description", "route"}
            item_unexpected = set(item_data) - item_allowed_keys
            item_missing = item_allowed_keys - set(item_data)
            if item_unexpected or item_missing:
                details = []
                if item_missing:
                    details.append(f"missing keys: {', '.join(sorted(item_missing))}")
                if item_unexpected:
                    details.append(f"unexpected keys: {', '.join(sorted(item_unexpected))}")
                raise BuildError(
                    "Load navigation data",
                    "navigation sub-item fields do not match the expected contract"
                    + (" (" + "; ".join(details) + ")" if details else ""),
                    path=navigation_path,
                    data_file=navigation_path,
                )

            item_id = _require_section_text(
                item_data["id"],
                message="navigation sub-item id must be a non-empty string",
                navigation_path=navigation_path,
                field="id",
            )
            if item_id in seen_item_ids:
                raise BuildError(
                    "Load navigation data",
                    f"duplicate navigation sub-item id: {item_id}",
                    path=navigation_path,
                    data_file=navigation_path,
                )
            seen_item_ids.add(item_id)

            _require_section_text(
                item_data["label"],
                message=f"navigation sub-item label must be a non-empty string for item: {item_id}",
                navigation_path=navigation_path,
                field="label",
            )
            _require_section_text(
                item_data["description"],
                message=f"navigation sub-item description must be a non-empty string for item: {item_id}",
                navigation_path=navigation_path,
                field="description",
            )

            route = item_data["route"]
            if (
                not isinstance(route, str)
                or not route.startswith("/")
                or not route.endswith("/")
                or len(route) < 2
            ):
                raise BuildError(
                    "Load navigation data",
                    f"navigation sub-item route must be a directory path like /example/ for item: {item_id}",
                    path=navigation_path,
                    data_file=navigation_path,
                    field="route",
                )

            parsed_items.append(
                NavigationSubItem(
                    id=item_id,
                    label=item_data["label"],
                    description=item_data["description"],
                    route=route,
                )
            )

        parsed_sections.append(
            NavigationSection(
                id=section_id,
                label=section_data["label"],
                description=section_data["description"],
                order=order,
                items=tuple(parsed_items),
            )
        )

    return NavigationData(version=EXPECTED_VERSION, sections=tuple(parsed_sections))
