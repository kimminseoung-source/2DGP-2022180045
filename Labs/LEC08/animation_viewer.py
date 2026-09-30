"""DRILL 08: AI-assisted animation viewer built incrementally."""
import argparse
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
FRAME_SECONDS = 0.12
REPEAT_COUNT = 5
HOLD_SECONDS = 1.0


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
        self.cycles = 0
        self.deadline = now + FRAME_SECONDS

    @property
    def holding(self):
        return self.completed_repeats == REPEAT_COUNT

    def update(self, now):
        if now < self.deadline:
            return
        if self.holding:
            self.completed_repeats = 0
            self.frame_index = 0
            self.animation_index = (self.animation_index + 1) % len(ANIMATIONS)
            if self.animation_index == 0:
                self.cycles += 1
        elif self.frame_index + 1 < len(ANIMATIONS[self.animation_index][1]):
            self.frame_index += 1
        else:
            self.completed_repeats += 1
            if self.holding:
                self.deadline = now + HOLD_SECONDS
                return
            self.frame_index = 0
        self.deadline = now + FRAME_SECONDS


def validate_sheet(sheet):
    if len(ANCHORS) != len(ANIMATIONS):
        raise ValueError("Each animation needs its own anchors.")
    for (name, frames), (centers, baseline) in zip(ANIMATIONS, ANCHORS):
        if not frames or len(frames) != len(centers):
            raise ValueError(f"{name}: frame/anchor count mismatch")
        for left, top, width, height in frames:
            if not (width > 0 and height > 0 and left >= 0 and top >= 0
                    and left + width <= sheet.w and top + height <= sheet.h):
                raise ValueError(f"{name}: frame outside sprite sheet")


def main(cycles=0):
    if not SPRITE_PATH.is_file():
        raise FileNotFoundError(f"Sprite sheet not found: {SPRITE_PATH}")
    p.open_canvas(WIDTH, HEIGHT)
    try:
        sheet = p.load_image(str(SPRITE_PATH))
        validate_sheet(sheet)
        playback = Playback(p.get_time())
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT or (
                    event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
                ):
                    running = False
            if not running:
                break
            p.clear_canvas()
            playback.update(p.get_time())
            if cycles and playback.cycles >= cycles:
                break
            draw_frame(sheet, ANIMATIONS[playback.animation_index][1][playback.frame_index],
                       playback.animation_index, playback.frame_index)
            p.update_canvas()
            p.delay(1 / 60)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, default=0,
                        help="Stop after N full sequences; 0 means forever.")
    args = parser.parse_args()
    if args.cycles < 0:
        parser.error("--cycles must be nonnegative")
    main(args.cycles)
