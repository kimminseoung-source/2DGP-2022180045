from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')
grass = load_image('grass.png')

angle = 0.0
trail = []
game_is_running = True

while game_is_running:
    # 창 닫기와 ESC 입력 처리
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            game_is_running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_is_running = False

    # 반지름이 커졌다 작아졌다 하도록 계산
    radius = 180 + 50 * math.sin(angle * 3)

    # 캐릭터 위치 계산
    x = 400 + radius * math.cos(angle)
    y = 300 + radius * math.sin(angle)

    # 지나온 위치 저장
    trail.append((x, y))

    # 최근 위치 25개만 유지
    if len(trail) > 25:
        trail.pop(0)

    clear_canvas()
    grass.draw(400, 30)

    # 잔상 그리기
    for i in range(0, len(trail), 5):
        trail_x, trail_y = trail[i]

        size = 25 + i
        character.draw(trail_x, trail_y, size, size)

    # 이동 방향으로 캐릭터 회전
    character.rotate_draw(
        angle + math.pi / 2,
        x,
        y,
        80,
        80
    )

    update_canvas()

    angle += 0.03
    delay(0.01)

close_canvas()