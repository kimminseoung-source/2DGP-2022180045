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
    draw_triangle_bottom()
    draw_rightup()
    pass


def draw_rightdown():
    # 꼭대기 → 오른쪽 아래
    for i in range(101):
        x = 400 + 2 * i
        y = 446 - 3.46 * i
        draw_character(x, y)


def draw_triangle_bottom():
    # 오른쪽 아래 → 왼쪽 아래
    for i in range(101):
        x = 600 - 4 * i
        y = 100
        draw_character(x, y)


def draw_rightup():
    # 왼쪽 아래 → 꼭대기
    for i in range(101):
        x = 200 + 2 * i
        y = 100 + 3.46 * i
        draw_character(x, y)


# =================================
while True:
    draw_circle()
    draw_rectangle()
    draw_triangle()
    
    pass

close_canvas()
