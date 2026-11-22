"""Tests for egg and hatchling movement."""

import unittest

from game_constants import EGG_LANDING_Y, TRACKS
from game_entities import Egg, Hatchling


class EggMovementTests(unittest.TestCase):
    def test_egg_starts_and_finishes_on_each_track(self) -> None:
        for lane, track in enumerate(TRACKS):
            with self.subTest(lane=lane):
                egg = Egg(lane=lane, age=0, duration=2.5)
                self.assertEqual(egg.position(), track[0])

                egg.age = egg.duration
                self.assertEqual(egg.position(), track[-1])

    def test_egg_falls_from_the_track_to_its_target_height(self) -> None:
        egg = Egg(lane=0, age=2.5, duration=2.5)
        egg.begin_fall(target_y=540, target_lane=2)
        start_x, start_y = egg.position()

        egg.fall_age = egg.fall_duration / 2
        middle_x, middle_y = egg.position()
        self.assertEqual(middle_x, start_x)
        self.assertGreater(middle_y, start_y)
        self.assertLess(middle_y, 540)

        egg.fall_age = egg.fall_duration
        self.assertEqual(egg.position(), (start_x, 540))
        self.assertEqual(egg.fall_target_lane, 2)

    def test_egg_is_lifted_over_the_rail_but_not_while_falling(self) -> None:
        egg = Egg(lane=0, age=1.25, duration=2.5)
        self.assertNotEqual(egg.draw_position(), egg.position())

        egg.age = egg.duration
        egg.begin_fall(EGG_LANDING_Y)
        self.assertEqual(egg.draw_position(), egg.position())

    def test_hatchling_moves_and_advances_its_animation_clock(self) -> None:
        chick = Hatchling(x=300, y=EGG_LANDING_Y, direction=-1)

        chick.update(0.5)

        self.assertEqual(chick.x, 170)
        self.assertEqual(chick.y, EGG_LANDING_Y)
        self.assertEqual(chick.age, 0.5)


if __name__ == "__main__":
    unittest.main()
