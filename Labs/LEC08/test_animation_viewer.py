"""Playback contract tests; no graphics window required."""
import unittest
from types import SimpleNamespace
import animation_viewer as v


class PlaybackTests(unittest.TestCase):
    def test_five_loops_hold_and_wrap_twice(self):
        player = v.Playback(0)
        for cycle in range(2):
            for animation, (_, frames) in enumerate(v.ANIMATIONS):
                for repeat in range(5):
                    for frame in range(len(frames)):
                        self.assertEqual((player.animation_index, player.frame_index,
                                          player.completed_repeats),
                                         (animation, frame, repeat))
                        deadline = player.deadline
                        player.update(deadline - 0.001)
                        self.assertEqual(player.frame_index, frame)
                        player.update(deadline)
                self.assertTrue(player.holding)
                self.assertEqual(player.frame_index, len(frames) - 1)
                self.assertAlmostEqual(player.deadline - deadline, 1.0)
                player.update(player.deadline - 0.001)
                self.assertEqual(player.animation_index, animation)
                player.update(player.deadline)
            self.assertEqual(player.cycles, cycle + 1)
            self.assertEqual((player.animation_index, player.frame_index), (0, 0))

    def test_variable_rectangles_and_counts(self):
        v.validate_sheet(SimpleNamespace(w=2912, h=1440))
        self.assertEqual([len(frames) for _, frames in v.ANIMATIONS],
                         [5, 7, 8, 8, 10, 6])
        sizes = {(r[2], r[3]) for _, frames in v.ANIMATIONS for r in frames}
        self.assertGreater(len(sizes), 1)
        with self.assertRaises(ValueError):
            v.validate_sheet(SimpleNamespace(w=100, h=100))

    def test_enlarged_crops_fit_canvas(self):
        for (_, frames), (centers, baseline) in zip(v.ANIMATIONS, v.ANCHORS):
            for (left, top, width, height), center in zip(frames, centers):
                self.assertGreater(height * v.SCALE, v.HEIGHT / 2)
                x1 = v.WIDTH / 2 + (left - center) * v.SCALE
                y1 = v.BASELINE + (baseline - top - height) * v.SCALE
                self.assertGreaterEqual(x1, 0)
                self.assertGreaterEqual(y1, 0)
                self.assertLessEqual(x1 + width * v.SCALE, v.WIDTH)
                self.assertLessEqual(y1 + height * v.SCALE, v.HEIGHT)


if __name__ == '__main__':
    unittest.main()
