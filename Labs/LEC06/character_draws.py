# 실습 과제 진행
import math
from pico2d import *

open_canvas(800, 600)

character = load_image('character.png')

clear_canvas()
character.draw(400, 300)
update_canvas()
delay(2)

# ==============================
def draw_circle():
    print("CIRCLE")
    for degree in range(0, 361, 5):  # 0도부터 360도까지 한 바퀴
        angle = math.radians(degree)
        x = 400 + 200 * math.cos(angle)
        y = 300 + 200 * math.sin(angle)

        draw_character(x,y)

# ==============================

def draw_character(x, y):
    get_events()
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.1)

def draw_top():
    print('TOP')
    for y in range(50, 550, 20):
        draw_character(50,y)
        if y == 550:
            draw_right()

    pass


def draw_right():
    print('right')
    for x in range(50, 750, 20):
        draw_character(x,550)
        if x == 750:
            draw_bottom()
    pass

def draw_left():
    print('left')
    for x in range(750, 50, -20):
        draw_character(x,50)
        if x == 50:
            draw_top()
    pass

def draw_bottom():
    print('bottom')
    for y in range(550, 50, -20):
        draw_character(750,y)
        if y == 50:
            draw_left()
    pass

def draw_rectangle():
    print("RECTANGLE")
    draw_top()
    draw_right()
    draw_bottom()
    draw_left()

    pass

# ==============================
def draw_triangle():
    print("TRIANGLE")
    draw_rightdown()
    draw_left()
    draw_rightup()
    pass

def draw_rightdown():
    print("RIGHTDOWN")
    for x in range(400, 750, 20):     
        y = 600 - (x - 400) * (250 / 350)
        draw_character(x, y)
        if x == 750:
            draw_left()

    pass

def draw_left():
    print("LEFT")
    for x in range(750, 50, -20):
        y = 50 + (x - 50) * (250 / 700)
        draw_character(x, y)
        if x == 50:
            draw_rightup()
    pass

def draw_rightup():
    print("RIGHTUP")

    pass



# =================================
while True:
    # draw_circle()
    # draw_rectangle()
    draw_triangle()
    
    pass

close_canvas()
