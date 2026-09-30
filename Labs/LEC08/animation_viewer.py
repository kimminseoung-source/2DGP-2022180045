"""DRILL 08: AI-assisted animation viewer built incrementally."""
from pathlib import Path
import pico2d as p

SPRITE_PATH = Path(__file__).with_name("samurai_animations.png")

WIDTH, HEIGHT = 800, 600

ANIMATIONS = [
    ("Idle", [
        (65, 20, 134, 211), (345, 21, 132, 210),
        (662, 21, 130, 210), (967, 21, 133, 210),
        (1250, 21, 133, 210),
    ]),
    ("Walk", [
        (64, 268, 135, 207), (347, 268, 133, 208),
        (660, 269, 132, 206), (967, 268, 133, 207),
        (1248, 269, 133, 206), (1519, 269, 133, 206),
        (1807, 269, 132, 207),
    ]),
    ("Run", [
        (63, 501, 135, 210), (353, 501, 135, 213),
        (639, 502, 148, 207), (943, 502, 155, 194),
        (1245, 501, 139, 207), (1506, 502, 152, 209),
        (1795, 502, 153, 209), (2072, 501, 150, 210),
    ]),
    ("Jump", [
        (62, 736, 142, 211), (353, 736, 142, 211),
        (643, 736, 142, 211), (935, 736, 143, 211),
        (1225, 735, 144, 220), (1513, 735, 142, 218),
        (1805, 736, 138, 216), (2084, 762, 142, 186),
    ]),
    ("Attack", [
        (56, 970, 270, 211), (345, 971, 147, 211),
        (633, 971, 143, 211), (929, 970, 166, 212),
        (1219, 970, 223, 212), (1496, 970, 241, 211),
        (1779, 971, 233, 211), (2066, 970, 262, 212),
        (2362, 970, 257, 211), (2653, 970, 150, 212),
    ]),
    ("Block", [
        (56, 1200, 193, 235), (347, 1200, 190, 235),
        (633, 1212, 149, 223), (929, 1212, 232, 223),
        (1223, 1212, 212, 223), (1518, 1212, 207, 223),
    ]),
]


# Image-space body centers and row baselines keep unequal crops from shifting.
ANCHORS = [
    ([132, 411, 727, 1033, 1316], 225),
    ([131, 413, 726, 1033, 1314, 1585, 1873], 470),
    ([131, 420, 713, 1020, 1314, 1585, 1873, 2147], 708),
    ([133, 424, 714, 1006, 1297, 1584, 1874, 2155], 948),
    ([129, 421, 704, 1000, 1290, 1568, 1851, 2142, 2437, 2725], 1176),
    ([130, 420, 705, 1000, 1290, 1585], 1429),
]
SCALE = 1.85
BASELINE = 120


def draw_frame(sheet, rect, animation_index, frame_index):
    # rect uses top-left image coordinates; pico2d clips from bottom-left.
    left, top, width, height = rect
    centers, baseline = ANCHORS[animation_index]
    x = WIDTH / 2 + (left + width / 2 - centers[frame_index]) * SCALE
    y = BASELINE + (baseline - top - height / 2) * SCALE
    sheet.clip_draw(left, sheet.h - top - height, width, height,
                    x, y, width * SCALE, height * SCALE)


class Playback:
    """Time-based playback; every frame stays visible for its full duration."""
    def __init__(self, now):
        self.animation_index = 0
        self.frame_index = 0
        self.completed_repeats = 0
        self.deadline = now + 0.12

    def update(self, now):
        if now < self.deadline:
            return
        self.frame_index += 1
        if self.frame_index == len(ANIMATIONS[self.animation_index][1]):
            self.frame_index = 0
            self.completed_repeats += 1
            if self.completed_repeats == 5:
                self.completed_repeats = 0
                self.animation_index = (self.animation_index + 1) % len(ANIMATIONS)
        self.deadline = now + 0.12


def main():
    p.open_canvas(WIDTH, HEIGHT)
    try:
        sheet = p.load_image(str(SPRITE_PATH))
        playback = Playback(p.get_time())
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT or (
                    event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
                ):
                    running = False
            p.clear_canvas()
            playback.update(p.get_time())
            draw_frame(sheet, ANIMATIONS[playback.animation_index][1][playback.frame_index],
                       playback.animation_index, playback.frame_index)
            p.update_canvas()
            p.delay(1 / 60)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
