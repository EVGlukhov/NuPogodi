"""Game state, input handling, updates, and rendering."""

import random

import pygame

from game_assets import load_assets
from game_constants import (
    EGG_LANDING_Y,
    STARTING_LIVES,
    TRACKS,
)
from game_entities import Egg, Hatchling
from game_renderer import GameRenderer


class Game:
    """Coordinate gameplay state and render the current scene."""

    def __init__(self) -> None:
        """Load game assets and initialize the initial screen state."""
        self.assets = load_assets()
        self.renderer = GameRenderer(self.assets)
        self.reset()
        self.started = False

    def reset(self) -> None:
        """Reset score, lives, entities, and player selection."""
        self.score = 0
        self.lives = STARTING_LIVES
        self.player_row = 1
        self.player_column = 0
        self.eggs: list[Egg] = []
        self.hatchlings: list[Hatchling] = []
        self.spawn_timer = 0.8
        self.started = True
        self.paused = False
        self.game_over = False

    @property
    def player_lane(self) -> int:
        """Return the lane selected by the player's side and basket row."""
        return self.player_row * 2 + self.player_column

    def handle_event(self, event: pygame.event.Event) -> None:
        """Apply a keyboard event to the current game state."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not self.started or self.game_over:
                self.reset()
                return

        if self.game_over:
            return

        if event.key == pygame.K_p and self.started:
            self.paused = not self.paused
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.player_column = 0
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player_column = 1
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.player_row = 0
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.player_row = 1

    def update(self, delta_time: float) -> None:
        """Advance gameplay by the elapsed time in seconds.

        Args:
            delta_time: Time since the previous update.
        """
        if not self.started or self.paused:
            return

        for hatchling in self.hatchlings:
            hatchling.update(delta_time)
        canvas_width = self.assets.background.get_width()
        self.hatchlings = [
            hatchling
            for hatchling in self.hatchlings
            if 0 <= hatchling.x <= canvas_width
        ]
        if self.game_over:
            return

        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0:
            self.eggs.append(
                Egg(
                    lane=random.randrange(len(TRACKS)),
                    age=0,
                    duration=max(1.35, 2.5 - self.score / 160),
                )
            )
            self.spawn_timer = max(0.55, 1.2 - self.score / 400)

        remaining_eggs: list[Egg] = []
        for egg in self.eggs:
            if egg.falling:
                egg.fall_age += delta_time
                if egg.fall_age < egg.fall_duration:
                    remaining_eggs.append(egg)
                    continue

                if egg.fall_target_lane is not None:
                    if self.player_lane == egg.fall_target_lane:
                        self.score += 10
                        continue

                    egg.begin_fall(EGG_LANDING_Y)
                    remaining_eggs.append(egg)
                    continue

                side = egg.lane % 2
                x, _ = egg.position()
                self.hatchlings.append(
                    Hatchling(
                        x=x,
                        y=EGG_LANDING_Y,
                        direction=-1 if side == 0 else 1,
                    )
                )
                self.lives = max(0, self.lives - 1)
                if self.lives == 0:
                    self.game_over = True
                continue

            egg.age += delta_time
            if egg.age < egg.duration:
                remaining_eggs.append(egg)
            elif egg.lane == self.player_lane:
                self.score += 10
            elif egg.lane < 2 and self.player_lane == egg.lane + 2:
                lower_lane = self.player_lane
                egg.begin_fall(TRACKS[lower_lane][-1][1], lower_lane)
                remaining_eggs.append(egg)
            else:
                egg.begin_fall(EGG_LANDING_Y)
                remaining_eggs.append(egg)

        self.eggs = remaining_eggs if not self.game_over else []

    def draw(self, surface: pygame.Surface) -> None:
        """Render the current game state to a surface."""
        self.renderer.draw(self, surface)
