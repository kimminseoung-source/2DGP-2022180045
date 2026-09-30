"""DRILL 08: AI-assisted animation viewer built incrementally."""
import pico2d as p

WIDTH, HEIGHT = 800, 600


def main():
    p.open_canvas(WIDTH, HEIGHT)
    try:
        p.clear_canvas()
        p.update_canvas()
        p.delay(0.1)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
