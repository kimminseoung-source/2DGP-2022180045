"""DRILL 08: AI-assisted animation viewer built incrementally."""
from pathlib import Path
import pico2d as p

SPRITE_PATH = Path(__file__).with_name("samurai_animations.png")

WIDTH, HEIGHT = 800, 600


def draw_frame(sheet, rect):
    # rect uses top-left image coordinates; pico2d clips from bottom-left.
    left, top, width, height = rect
    sheet.clip_draw(left, sheet.h - top - height, width, height,
                    WIDTH / 2, HEIGHT / 2, width * 1.85, height * 1.85)


def main():
    p.open_canvas(WIDTH, HEIGHT)
    try:
        sheet = p.load_image(str(SPRITE_PATH))
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT or (
                    event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
                ):
                    running = False
            p.clear_canvas()
            draw_frame(sheet, (65, 20, 134, 211))
            p.update_canvas()
            p.delay(1 / 60)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
