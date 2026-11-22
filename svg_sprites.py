"""Extract and compose vector sprites from the LCD SVG sheet."""

import copy
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pygame

from game_constants import VIEWBOX_HEIGHT, VIEWBOX_WIDTH


for prefix, uri in (
    ("", "http://www.w3.org/2000/svg"),
    ("dc", "http://purl.org/dc/elements/1.1/"),
    ("cc", "http://creativecommons.org/ns#"),
    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"),
    ("inkscape", "http://www.inkscape.org/namespaces/inkscape"),
):
    ET.register_namespace(prefix, uri)


def _local_name(tag: str) -> str:
    """Return an XML tag without its namespace prefix."""
    return tag.rsplit("}", 1)[-1]


def _element_title(element: ET.Element) -> str:
    """Return the direct title text of an SVG element, if present."""
    return next(
        (
            child.text or ""
            for child in element
            if _local_name(child.tag) == "title"
        ),
        "",
    )


def _keep_matching_groups(
    element: ET.Element,
    title_prefixes: tuple[str, ...],
) -> bool:
    """Prune an SVG element to subgroups matching the requested titles.

    Args:
        element: SVG node to inspect and modify.
        title_prefixes: Group title prefixes to retain.

    Returns:
        Whether the element contains artwork that should be kept.
    """
    if any(
        _element_title(element).startswith(prefix)
        for prefix in title_prefixes
    ):
        return True
    if _local_name(element.tag) in {"path", "title"}:
        return False

    children = list(element)
    retained = [
        child
        for child in children
        if _keep_matching_groups(child, title_prefixes)
    ]
    element[:] = retained
    return bool(retained) or _local_name(element.tag) in {"defs", "style"}


def load_vector_crop(
    source_root: ET.Element,
    title_prefixes: tuple[str, ...],
    crop: tuple[int, int, int, int],
) -> pygame.Surface:
    """Render selected SVG groups and return a cropped surface.

    Args:
        source_root: Root element of the source sprite sheet.
        title_prefixes: SVG group titles to retain.
        crop: Crop rectangle in source viewBox coordinates.

    Returns:
        The rendered sprite crop with an alpha channel.
    """
    root = copy.deepcopy(source_root)
    layers = {child.get("id"): child for child in root}
    layer = layers.get("layer1")
    if layer is None:
        raise ValueError("The LCD SVG does not contain its vector artwork layer.")

    for child in list(root):
        if child.get("id") == "layer2":
            root.remove(child)

    retained = [
        item
        for item in list(layer)
        if _keep_matching_groups(item, title_prefixes)
    ]
    layer[:] = retained
    if not retained:
        raise ValueError(f"No SVG artwork matches {title_prefixes!r}.")

    with tempfile.TemporaryDirectory() as temporary_directory:
        svg_path = Path(temporary_directory) / "sprite.svg"
        ET.ElementTree(root).write(
            svg_path,
            encoding="utf-8",
            xml_declaration=True,
        )
        sheet = pygame.image.load(str(svg_path)).convert_alpha()

    x, y, width, height = crop
    source_rect = pygame.Rect(
        round(x * sheet.get_width() / VIEWBOX_WIDTH),
        round(y * sheet.get_height() / VIEWBOX_HEIGHT),
        round(width * sheet.get_width() / VIEWBOX_WIDTH),
        round(height * sheet.get_height() / VIEWBOX_HEIGHT),
    )
    return sheet.subsurface(source_rect).copy()


def load_wolf_poses(
    source_root: ET.Element,
    body_group: str,
    basket_groups: tuple[str, str],
    crop: tuple[int, int, int, int],
) -> tuple[pygame.Surface, pygame.Surface]:
    """Combine the wolf body with each of its two basket poses."""
    body = load_vector_crop(source_root, (body_group,), crop)
    poses: list[pygame.Surface] = []
    for basket_group in basket_groups:
        pose = body.copy()
        basket = load_vector_crop(source_root, (basket_group,), crop)
        pose.blit(basket, (0, 0))
        poses.append(pose)
    return poses[0], poses[1]
