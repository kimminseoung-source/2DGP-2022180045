from pathlib import Path

import pico2d
from pico2d import *


# Game object class here

from grass import Grass, Platform
from boy import Boy


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)


def reset_world():
    global world, boy, platforms, camera_y, score_font

    world = []

    grass = Grass()
    world.append(grass)

    camera_y = 0
    font_path = Path(pico2d.__file__).resolve().parent / 'data' / 'ConsolaMalgun.ttf'
    score_font = load_font(str(font_path), 28)
    platforms = []
    boy = Boy(platforms)
    world.append(boy)
    extend_platforms()


def extend_platforms():
    # 기존 180 x 30 크기에서 가로/세로를 각각 1/3로 줄인다.
    # 최대 충전 점프 높이(약 176px) 안에서 다음 발판에 닿도록 배치한다.
    centers = (280, 400, 520, 400)
    while not platforms or platforms[-1].top < camera_y + get_canvas_height() + 240:
        index = len(platforms)
        center_x = centers[index % len(centers)]
        top = 170 + index * 120
        platforms.append(Platform(center_x - 30, top - 10, center_x + 30, top))


def update_world():
    global camera_y
    for o in world:
        o.update()
    # 충돌 좌표는 그대로 두고 그릴 때만 카메라 높이를 뺀다.
    camera_y = max(0, boy.y - get_canvas_height() * 0.55)
    extend_platforms()


def render_world():
    clear_canvas()
    for o in world:
        if o is not boy:
            o.draw(camera_y)
    for platform in platforms:
        if platform.top >= camera_y and platform.bottom <= camera_y + get_canvas_height():
            platform.draw(camera_y)
    boy.draw(camera_y)
    # 카메라가 움직여도 점수는 화면 왼쪽 위에 고정한다.
    score_font.draw(22, get_canvas_height() - 37, f'SCORE: {boy.score}', (255, 255, 255))
    score_font.draw(20, get_canvas_height() - 35, f'SCORE: {boy.score}', (20, 30, 45))
    update_canvas()


if __name__ == '__main__':
    running = True
    open_canvas()
    try:
        reset_world()
        while running:
            handle_events()
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()
