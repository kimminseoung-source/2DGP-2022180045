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
]


def draw_frame(sheet, rect):
    # rect uses top-left image coordinates; pico2d clips from bottom-left.
    left, top, width, height = rect
    sheet.clip_draw(left, sheet.h - top - height, width, height,
                    WIDTH / 2, HEIGHT / 2, width * 1.85, height * 1.85)


def main():
    p.open_canvas(WIDTH, HEIGHT)
    try:
        sheet = p.load_image(str(SPRITE_PATH))
        animation_index = 0
        frame_index = 0
        next_frame_at = p.get_time() + 0.12
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT or (
                    event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
                ):
                    running = False
            p.clear_canvas()
            now = p.get_time()
            if now >= next_frame_at:
                frame_index += 1
                if frame_index == len(ANIMATIONS[animation_index][1]):
                    frame_index = 0
                    animation_index = (animation_index + 1) % len(ANIMATIONS)
                next_frame_at = now + 0.12
            draw_frame(sheet, ANIMATIONS[animation_index][1][frame_index])
            p.update_canvas()
            p.delay(1 / 60)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
