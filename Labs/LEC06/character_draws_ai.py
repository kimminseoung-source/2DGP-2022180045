"""DRILL 06 AI 버전: 원 → 사각형 → 정삼각형을 무한 반복합니다.

같은 폴더의 character.png를 사용합니다. ESC 또는 창 닫기로 종료합니다.
"""
import math
from pathlib import Path

import pico2d as p

WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 250  # 초당 이동 거리(픽셀)
CENTER = (400, 300)
RADIUS = 200


def draw_character(character, x, y):
    """이벤트 처리와 화면 갱신. 종료 요청이 있으면 False를 반환합니다."""
    for event in p.get_events():
        if event.type == p.SDL_QUIT or (
            event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
        ):
            return False
    p.clear_canvas()
    character.draw(x, y)
    p.update_canvas()
    p.delay(1 / FPS)
    return True


def draw_circle(character):
    print("CIRCLE", flush=True)
    frames = math.ceil(2 * math.pi * RADIUS / SPEED * FPS)
    for frame in range(frames + 1):
        angle = 2 * math.pi * frame / frames
        x = CENTER[0] + RADIUS * math.cos(angle)
        y = CENTER[1] + RADIUS * math.sin(angle)
        if not draw_character(character, x, y):
            return False
    return True


def draw_line(character, start, end):
    """두 점 사이를 보간하며 끝점까지 이동합니다."""
    frames = max(1, math.ceil(math.dist(start, end) / SPEED * FPS))
    for frame in range(frames + 1):
        progress = frame / frames
        x = start[0] + (end[0] - start[0]) * progress
        y = start[1] + (end[1] - start[1]) * progress
        if not draw_character(character, x, y):
            return False
    return True


def draw_polygon(character, vertices):
    for start, end in zip(vertices, vertices[1:]):
        if not draw_line(character, start, end):
            return False
    return True


def draw_rectangle(character):
    print("RECTANGLE", flush=True)
    # 원의 끝점 (600, 300)에서 출발해 사각형을 돌고 같은 점으로 돌아옵니다.
    return draw_polygon(character, (
        (600, 300), (600, 500), (200, 500),
        (200, 100), (600, 100), (600, 300),
    ))


def draw_triangle(character):
    print("TRIANGLE", flush=True)
    # 같은 원 위에서 120도씩 떨어진 세 점은 정삼각형을 이룹니다.
    offset = 100 * math.sqrt(3)
    return draw_polygon(character, (
        (600, 300), (300, 300 + offset),
        (300, 300 - offset), (600, 300),
    ))


def main():
    p.open_canvas(WIDTH, HEIGHT)
    try:
        character = p.load_image(str(Path(__file__).with_name("character.png")))
        while True:
            for movement in (draw_circle, draw_rectangle, draw_triangle):
                if not movement(character):
                    return
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
