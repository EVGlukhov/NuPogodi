"""Sprite preparation and drawing for the game scene."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game_assets import GameAssets
from game_constants import (
    CHICK_ANIMATION_FPS,
    CHICK_SIZE,
    STARTING_LIVES,
    WOLF_POSITIONS,
)

if TYPE_CHECKING:
    from game import Game


class GameRenderer:
    """Prepare reusable sprites and draw a frame from game state."""

    def __init__(self, assets: GameAssets) -> None:
        """Scale source assets and create fonts used by the interface."""
        self.assets = assets
        self.wolf_sprites = tuple(
            tuple(
                pygame.transform.smoothscale(pose, (250, 260))
                for pose in side_poses
            )
            for side_poses in assets.wolf_poses
        )
        self.egg_sprite = pygame.transform.smoothscale(assets.egg, (48, 56))
        chick_frames = tuple(
            pygame.transform.smoothscale(sprite, CHICK_SIZE)
            for sprite in assets.chick_frames
        )
        self.chick_sprites = (
            tuple(pygame.transform.flip(sprite, True, False) for sprite in chick_frames),
            chick_frames,
        )
        self.title_font = pygame.font.Font(None, 52)
        self.message_font = pygame.font.Font(None, 30)
        self.hud_font = pygame.font.Font(None, 32)

    def draw(self, game: Game, surface: pygame.Surface) -> None:
        """Draw the background, actors, falling objects, and interface."""
        surface.blit(self.assets.background, (0, 0))
        surface.blit(self.assets.foreground, (0, 0))
        self._draw_wolf(game, surface)
        self._draw_eggs(game, surface)
        self._draw_hatchlings(game, surface)
        self._draw_interface(game, surface)

    def _draw_wolf(self, game: Game, surface: pygame.Surface) -> None:
        """Draw the wolf with its currently selected basket."""
        wolf = self.wolf_sprites[game.player_column][game.player_row]
        surface.blit(
            wolf,
            wolf.get_rect(center=WOLF_POSITIONS[game.player_column]),
        )

    def _draw_eggs(self, game: Game, surface: pygame.Surface) -> None:
        """Draw eggs above the scene layers so missed falls remain visible."""
        for egg in game.eggs:
            rolling_egg = pygame.transform.rotate(
                self.egg_sprite,
                round(egg.rotation()),
            )
            surface.blit(
                rolling_egg,
                rolling_egg.get_rect(center=egg.draw_position()),
            )

    def _draw_hatchlings(self, game: Game, surface: pygame.Surface) -> None:
        """Draw running chicks using the animation frame for their age."""
        for hatchling in game.hatchlings:
            side = 0 if hatchling.direction < 0 else 1
            frames = self.chick_sprites[side]
            frame_index = int(hatchling.age * CHICK_ANIMATION_FPS) % len(frames)
            chick = frames[frame_index]
            surface.blit(chick, chick.get_rect(center=(hatchling.x, hatchling.y)))

    def _draw_interface(self, game: Game, surface: pygame.Surface) -> None:
        """Draw the score, remaining lives, and current screen overlay."""
        self._draw_text(
            surface,
            self.hud_font,
            f"Score: {game.score}     Lives: {game.lives}/{STARTING_LIVES}",
            (610, 55),
        )

        if not game.started:
            self._draw_text(surface, self.title_font, "NU, POGODI!", (610, 260))
            self._draw_text(
                surface,
                self.message_font,
                "Press ENTER to start",
                (610, 315),
            )
            self._draw_text(
                surface,
                self.message_font,
                "LEFT/RIGHT: side  |  UP/DOWN: basket  |  P: pause",
                (610, 355),
            )
        elif game.game_over:
            self._draw_text(surface, self.title_font, "GAME OVER", (610, 270))
            self._draw_text(
                surface,
                self.message_font,
                "Press ENTER to play again",
                (610, 325),
            )
        elif game.paused:
            self._draw_text(surface, self.title_font, "PAUSED", (610, 280))
            self._draw_text(
                surface,
                self.message_font,
                "Press P to continue",
                (610, 335),
            )

    @staticmethod
    def _draw_text(
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        center: tuple[float, float],
    ) -> None:
        """Render interface text centered at a scene coordinate."""
        image = font.render(text, True, (28, 38, 37))
        surface.blit(image, image.get_rect(center=center))
