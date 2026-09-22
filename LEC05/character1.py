from pico2d import *


open_canvas(800, 600)

character = load_image('character.png')
grass = load_image('grass.png')

angle = 0
while angle < 360:
    # 원 위의 현재 좌표 계산
    x = 400 + 200 * math.cos(math.radians(angle))
    y = 300 + 200 * math.sin(math.radians(angle))

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()

    angle += 1
    delay(0.01)

delay(2)
close_canvas()
