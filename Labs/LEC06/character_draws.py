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
    for x in range(50, 750, 5):
        
        draw_character(x,550)
    
    pass


def draw_right():
    print('right')
    pass

def draw_left():
    print('left')
    pass

def draw_bottom():
    print('bottom')
    pass



#  ===============================

def draw_rectangle():
    print("RECTANGLE")
    draw_top()
    draw_right()
    draw_bottom()
    draw_left()

    pass

def draw_triangle():
    print("TRIANGLE")
    pass

while True:
    draw_circle()
    # draw_rectangle()
    # draw_triangle()
    
    pass

close_canvas()
