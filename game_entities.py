"""Game objects and their movement rules."""

from dataclasses import dataclass
from math import hypot, pi, sqrt

from game_constants import (
    CHICK_RUN_SPEED,
    EGG_FALL_GRAVITY,
    EGG_LEFT_RAIL_ADJUSTMENT,
    EGG_RAIL_CLEARANCE,
    EGG_ROLL_RADIUS,
    TRACKS,
)


Point = tuple[float, float]
TRACK_LENGTHS = tuple(
    sum(
        hypot(end[0] - start[0], end[1] - start[1])
        for start, end in zip(track, track[1:])
    )
    for track in TRACKS
)


@dataclass
class Egg:
    """An egg rolling on a rail or falling toward a basket or the ground."""

    lane: int
    age: float
    duration: float
    falling: bool = False
    fall_age: float = 0
    fall_start_y: float = 0
    fall_target_y: float = 0
    fall_duration: float = 0
    fall_target_lane: int | None = None

    def position(self) -> Point:
        """Return the egg's current center position in scene coordinates."""
        if self.falling:
            progress = (
                min(self.fall_age / self.fall_duration, 1)
                if self.fall_duration
                else 1
            )
            end = TRACKS[self.lane][-1]
            return (
                end[0],
                self.fall_start_y
                + (self.fall_target_y - self.fall_start_y) * progress**2,
            )

        distance = self.travelled_distance()
        track = TRACKS[self.lane]

        for start, end in zip(track, track[1:]):
            segment_length = hypot(end[0] - start[0], end[1] - start[1])
            if distance <= segment_length:
                progress = distance / segment_length
                return (
                    start[0] + (end[0] - start[0]) * progress,
                    start[1] + (end[1] - start[1]) * progress,
                )
            distance -= segment_length

        return track[-1]

    def begin_fall(self, target_y: float, target_lane: int | None = None) -> None:
        """Start the egg falling vertically toward a basket or the ground.

        Args:
            target_y: Destination height in scene coordinates.
            target_lane: Basket lane that can catch the egg, if any.
        """
        _, self.fall_start_y = self.position()
        fall_distance = max(0, target_y - self.fall_start_y)
        self.falling = True
        self.fall_age = 0
        self.fall_target_y = target_y
        self.fall_duration = sqrt(2 * fall_distance / EGG_FALL_GRAVITY)
        self.fall_target_lane = target_lane

    def travelled_distance(self) -> float:
        """Return distance traveled along the rail, clamped to its endpoint."""
        progress = min(self.age / self.duration, 1)
        return TRACK_LENGTHS[self.lane] * progress

    def draw_position(self) -> Point:
        """Return a position slightly above the rail for rendering."""
        x, y = self.position()
        track = TRACKS[self.lane]
        start, rail_end = track[0], track[1]
        dx = rail_end[0] - start[0]
        dy = rail_end[1] - start[1]
        rail_length = hypot(dx, dy)
        distance = self.travelled_distance()
        exit_length = TRACK_LENGTHS[self.lane] - rail_length
        clearance_progress = min(max((distance - rail_length) / exit_length, 0), 1)
        clearance = EGG_RAIL_CLEARANCE
        if self.lane % 2 == 0:
            clearance += EGG_LEFT_RAIL_ADJUSTMENT
        clearance *= 1 - clearance_progress
        normal_x = (1 if dx > 0 else -1) * abs(dy) / rail_length
        normal_y = -abs(dx) / rail_length
        return x + normal_x * clearance, y + normal_y * clearance

    def rotation(self) -> float:
        """Return the egg's rolling angle in degrees."""
        direction = 1 if self.lane % 2 == 0 else -1
        return -direction * self.travelled_distance() * 180 / (pi * EGG_ROLL_RADIUS)


@dataclass
class Hatchling:
    """A chick running away after an egg reaches the ground."""

    x: float
    y: float
    direction: int
    age: float = 0

    def update(self, delta_time: float) -> None:
        """Advance the chick's position and animation clock."""
        self.x += self.direction * CHICK_RUN_SPEED * delta_time
        self.age += delta_time
