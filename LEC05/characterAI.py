from pico2d import *

open_canvas(800, 600)

character = load_image('character.png')
grass = load_image('grass.png')

x = 400
y = 300


# 현재 화면을 그리는 함수
def draw_scene():
    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()
    delay(0.01)


# 지정한 방향으로 캐릭터를 움직이는 함수
def move(dx, dy, count):
    global x, y

    for i in range(count):
        x += dx
        y += dy
        draw_scene()


# 한 변이 200픽셀인 정사각형 이동
move(2, 0, 100)     # 오른쪽
move(0, 2, 100)     # 위쪽
move(-2, 0, 100)    # 왼쪽
move(0, -2, 100)    # 아래쪽

delay(2)
close_canvas()