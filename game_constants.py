"""Shared scene geometry, asset coordinates, and gameplay tuning."""

from pathlib import Path
from typing import Final


VIEWBOX_WIDTH: Final = 1570.4845
VIEWBOX_HEIGHT: Final = 989.1816
ASSET_DIR: Final = Path(__file__).resolve().parent / "assets"
TRACKS: Final = (
    ((35, 262), (245, 355), (310, 420)),
    ((1186, 262), (976, 355), (911, 420)),
    ((35, 438), (245, 545), (300, 540)),
    ((1186, 438), (976, 545), (921, 540)),
)
WOLF_POSITIONS: Final = ((360, 500), (861, 500))
WOLF_CROPS: Final = (
    (330, 370, 500, 520),
    (780, 370, 500, 520),
)
EGG_CROP: Final = (95, 265, 110, 110)
WOLF_BODY_GROUPS: Final = ("1.1.0", "1.2.1")
WOLF_BASKET_GROUPS: Final = (
    ("1.1.1", "1.0.0"),
    ("1.3.1", "1.3.0"),
)
EGG_GROUPS: Final = ("3.0.1",)
CHICK_FRAME_GROUPS: Final = ("0.1.0", "0.2.0", "0.2.1")
CHICK_FRAME_CROPS: Final = (
    (1322, 788, 74, 110),
    (1402, 789, 77, 108),
    (1490, 788, 79, 110),
)
CHICK_SIZE: Final = (42, 62)
CHICK_ANIMATION_FPS: Final = 8
CHICK_RUN_SPEED: Final = 260
EGG_FALL_GRAVITY: Final = 1000
EGG_LANDING_Y: Final = 635
STARTING_LIVES: Final = 3
EGG_ROLL_RADIUS: Final = 18
EGG_RAIL_CLEARANCE: Final = 18
EGG_LEFT_RAIL_ADJUSTMENT: Final = 4
