from pico2d import *
from boy import Boy
from grass import Grass

import game_world   # 게임 월드 모듈 임포트

# Game object class here


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
    # global world
    global boy

    # world = []
    boy = Boy()
    game_world.add_object(boy, 1)  # 게임 월드에 객체를 담는 함수 호출
    # world.append(boy)

    grass = Grass()
    game_world.add_object(grass, 0)
    # world.append(grass)




def update_world():
    game_world.update()  
    # for o in world:
    #     o.update()
    pass


def render_world():
    clear_canvas()
    game_world.render()
    # for o in world:
    #     o.draw()
    update_canvas()


running = True



open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
