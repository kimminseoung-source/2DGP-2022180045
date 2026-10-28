from pico2d import *
import random


def reset_world():
    global running
    running =False
    pass   


def handle_event():
    global running
    events = get_events

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False 
    pass 


def update_world():
    pass


def render_world():
    pass



open_canvas()

reset_world()

while running:
    handle_event()
    update_world()
    render_world()
    delay(1)


close_canvas()


