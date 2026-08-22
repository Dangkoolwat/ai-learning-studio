"""Cross-file consistency validation for AI Learning Studio data files."""

from __future__ import annotations

from core.errors import BuildError
from core.navigation import NavigationData
from core.page_registry import PageRegistry


STAGE = "Validate navigation and registry consistency"


def validate_navigation_registry_consistency(
    navigation: NavigationData,
    registry: PageRegistry,
) -> None:
    """Enforce consistency contracts between navigation.json and page-registry.json.

    Contracts:
    - every navigation section must own at least one registered page
    - every navigation section must have a landing page whose id matches the section id
    - every navigation sub-item must reference a registered page and mirror its
      title, description, and route exactly
    - every registry page flagged navigation=true must appear either as a
      navigation sub-item or as a section landing page
    """
    pages_by_id = {page.id: page for page in registry.pages}
    section_ids = {section.id for section in navigation.sections}
    nav_item_ids: set[str] = set()

    for section in navigation.sections:
        section_pages = [page for page in registry.pages if page.section == section.id]
        if not section_pages:
            raise BuildError(
                STAGE,
                f"navigation section has no registered pages: {section.id}",
                section=section.id,
            )

        landing = pages_by_id.get(section.id)
        if landing is None:
            raise BuildError(
                STAGE,
                f"navigation section is missing its landing page in the page registry: {section.id}",
                section=section.id,
            )

        for item in section.items:
            nav_item_ids.add(item.id)
            page = pages_by_id.get(item.id)
            if page is None:
                raise BuildError(
                    STAGE,
                    f"navigation item does not exist in the page registry: {item.id}",
                    section=section.id,
                    page_id=item.id,
                )
            if item.label != page.title:
                raise BuildError(
                    STAGE,
                    "navigation item label does not match the registry page title"
                    f" (navigation: {item.label!r} / registry: {page.title!r})",
                    section=section.id,
                    page_id=item.id,
                    field="label",
                )
            if item.description != page.description:
                raise BuildError(
                    STAGE,
                    "navigation item description does not match the registry page description"
                    f" (navigation: {item.description!r} / registry: {page.description!r})",
                    section=section.id,
                    page_id=item.id,
                    field="description",
                )
            if item.route != page.route:
                raise BuildError(
                    STAGE,
                    "navigation item route does not match the registry page route"
                    f" (navigation: {item.route!r} / registry: {page.route!r})",
                    section=section.id,
                    page_id=item.id,
                    field="route",
                )

    for page in registry.pages:
        if page.navigation and page.id not in nav_item_ids and page.id not in section_ids:
            raise BuildError(
                STAGE,
                f"page marked navigation=true is missing from navigation data: {page.id}",
                page_id=page.id,
            )
