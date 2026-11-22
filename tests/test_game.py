"""Tests for game controls, scoring, misses, and rendering."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game import Game
from game_constants import EGG_LANDING_Y, STARTING_LIVES, TRACKS
from game_entities import Egg


def key_event(key: int) -> pygame.event.Event:
    """Create a key-down event for game input tests."""
    return pygame.event.Event(pygame.KEYDOWN, key=key)


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.game = Game()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def setUp(self) -> None:
        self.game.reset()
        self.game.spawn_timer = 10

    def _set_player_lane(self, lane: int) -> None:
        self.game.player_row, self.game.player_column = divmod(lane, 2)

    def test_keyboard_selects_side_basket_and_pause(self) -> None:
        self.game.handle_event(key_event(pygame.K_RIGHT))
        self.game.handle_event(key_event(pygame.K_UP))
        self.assertEqual(self.game.player_lane, 1)

        self.game.handle_event(key_event(pygame.K_p))
        self.assertTrue(self.game.paused)
        self.game.handle_event(key_event(pygame.K_p))
        self.assertFalse(self.game.paused)

    def test_matching_basket_catches_eggs_on_all_four_lanes(self) -> None:
        for lane in range(len(TRACKS)):
            with self.subTest(lane=lane):
                self.game.reset()
                self.game.spawn_timer = 10
                self._set_player_lane(lane)
                self.game.eggs = [Egg(lane=lane, age=2.49, duration=2.5)]

                self.game.update(0.02)

                self.assertEqual(self.game.score, 10)
                self.assertEqual(self.game.lives, STARTING_LIVES)
                self.assertEqual(self.game.eggs, [])
                self.assertEqual(self.game.hatchlings, [])

    def test_upper_egg_falls_into_lower_basket_on_either_side(self) -> None:
        for upper_lane, lower_lane in ((0, 2), (1, 3)):
            with self.subTest(upper_lane=upper_lane):
                self.game.reset()
                self.game.spawn_timer = 10
                self._set_player_lane(lower_lane)
                self.game.eggs = [
                    Egg(lane=upper_lane, age=2.49, duration=2.5)
                ]

                self.game.update(0.02)
                egg = self.game.eggs[0]
                self.assertTrue(egg.falling)
                self.assertEqual(egg.fall_target_lane, lower_lane)

                self.game.update(egg.fall_duration + 0.01)

                self.assertEqual(self.game.score, 10)
                self.assertEqual(self.game.lives, STARTING_LIVES)
                self.assertEqual(self.game.eggs, [])

    def test_wrong_side_miss_loses_life_and_hatches_a_chick_at_ground(self) -> None:
        self._set_player_lane(3)
        self.game.eggs = [Egg(lane=0, age=2.49, duration=2.5)]

        self.game.update(0.02)
        egg = self.game.eggs[0]
        self.assertIsNone(egg.fall_target_lane)
        self.assertEqual(self.game.lives, STARTING_LIVES)

        self.game.update(egg.fall_duration + 0.01)

        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, STARTING_LIVES - 1)
        self.assertEqual(len(self.game.hatchlings), 1)
        self.assertEqual(self.game.hatchlings[0].direction, -1)
        self.assertEqual(self.game.hatchlings[0].y, EGG_LANDING_Y)

    def test_changing_basket_during_drop_causes_a_miss(self) -> None:
        self._set_player_lane(2)
        self.game.eggs = [Egg(lane=0, age=2.49, duration=2.5)]
        self.game.update(0.02)
        egg = self.game.eggs[0]
        self._set_player_lane(0)

        self.game.update(egg.fall_duration + 0.01)
        self.assertIsNone(egg.fall_target_lane)
        self.assertEqual(self.game.lives, STARTING_LIVES)

        self.game.update(egg.fall_duration + 0.01)

        self.assertEqual(self.game.lives, STARTING_LIVES - 1)
        self.assertEqual(len(self.game.hatchlings), 1)

    def test_spawner_uses_selected_random_lane(self) -> None:
        self.game.spawn_timer = 0

        with patch("game.random.randrange", return_value=3):
            self.game.update(0.01)

        self.assertEqual(len(self.game.eggs), 1)
        self.assertEqual(self.game.eggs[0].lane, 3)

    def test_game_over_locks_movement_and_enter_restarts(self) -> None:
        self.game.game_over = True
        original_selection = (self.game.player_row, self.game.player_column)

        for key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self.game.handle_event(key_event(key))

        self.assertEqual(
            (self.game.player_row, self.game.player_column),
            original_selection,
        )

        self.game.handle_event(key_event(pygame.K_RETURN))

        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.lives, STARTING_LIVES)

    def test_last_miss_ends_game_but_hatchling_keeps_running(self) -> None:
        self._set_player_lane(3)
        self.game.lives = 1
        egg = Egg(lane=0, age=2.5, duration=2.5)
        egg.begin_fall(EGG_LANDING_Y)
        egg.fall_age = egg.fall_duration - 0.01
        self.game.eggs = [egg]

        self.game.update(0.02)

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.lives, 0)
        self.assertEqual(self.game.eggs, [])
        self.assertEqual(len(self.game.hatchlings), 1)

        chick = self.game.hatchlings[0]
        initial_x = chick.x
        self.game.update(0.1)
        self.assertLess(chick.x, initial_x)

    def test_pause_stops_spawning_and_updates(self) -> None:
        egg = Egg(lane=0, age=0, duration=2.5)
        self.game.eggs = [egg]
        self.game.spawn_timer = 0
        self.game.paused = True

        self.game.update(0.5)

        self.assertEqual(egg.age, 0)
        self.assertEqual(self.game.spawn_timer, 0)
        self.assertEqual(self.game.eggs, [egg])

    def test_renderer_draws_a_complete_frame(self) -> None:
        self.game.eggs = [Egg(lane=0, age=0.5, duration=2.5)]
        frame = pygame.Surface((1221, 801), pygame.SRCALPHA)

        self.game.draw(frame)

        self.assertEqual(frame.get_size(), (1221, 801))
        self.assertEqual(len(self.game.assets.chick_frames), 3)
        self.assertEqual(self.game.assets.background.get_size(), (1221, 801))


if __name__ == "__main__":
    unittest.main()
