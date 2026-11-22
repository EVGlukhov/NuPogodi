"""Load raster backgrounds and assemble the game's sprite collection."""

from dataclasses import dataclass
from xml.etree import ElementTree as ET

import pygame

from game_constants import (
    ASSET_DIR,
    CHICK_FRAME_CROPS,
    CHICK_FRAME_GROUPS,
    EGG_CROP,
    EGG_GROUPS,
    WOLF_BODY_GROUPS,
    WOLF_BASKET_GROUPS,
    WOLF_CROPS,
)
from svg_sprites import load_vector_crop, load_wolf_poses


@dataclass(frozen=True)
class GameAssets:
    """Loaded surfaces used by the game renderer."""

    background: pygame.Surface
    foreground: pygame.Surface
    wolf_poses: tuple[
        tuple[pygame.Surface, pygame.Surface],
        tuple[pygame.Surface, pygame.Surface],
    ]
    egg: pygame.Surface
    chick_frames: tuple[pygame.Surface, ...]


def load_assets() -> GameAssets:
    """Load backgrounds and extract the wolf, egg, and chick sprites."""
    background = pygame.image.load(
        ASSET_DIR / "background.png"
    ).convert_alpha()
    foreground = pygame.image.load(
        ASSET_DIR / "foreground.png"
    ).convert_alpha()
    svg_root = ET.parse(ASSET_DIR / "lcd.svg").getroot()

    left_wolf = load_wolf_poses(
        svg_root,
        WOLF_BODY_GROUPS[0],
        WOLF_BASKET_GROUPS[0],
        WOLF_CROPS[0],
    )
    right_wolf = load_wolf_poses(
        svg_root,
        WOLF_BODY_GROUPS[1],
        WOLF_BASKET_GROUPS[1],
        WOLF_CROPS[1],
    )
    egg = load_vector_crop(svg_root, EGG_GROUPS, EGG_CROP)
    chick_frames: list[pygame.Surface] = []
    for group, crop in zip(CHICK_FRAME_GROUPS, CHICK_FRAME_CROPS):
        chick = load_vector_crop(svg_root, (group,), crop)
        bounds = chick.get_bounding_rect()
        if not bounds.width or not bounds.height:
            raise ValueError(f"No visible SVG artwork matches {group!r}.")
        chick_frames.append(chick.subsurface(bounds).copy())

    return GameAssets(
        background=background,
        foreground=foreground,
        wolf_poses=(left_wolf, right_wolf),
        egg=egg,
        chick_frames=tuple(chick_frames),
    )
