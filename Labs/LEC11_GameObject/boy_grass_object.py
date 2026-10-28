from pico2d import *
import random


# Game object class here
class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass
    
    pass


class Boy:
    def __init__(self):
        self.x, self.y = random.randint(100, 700), 90
        self.frame = 0
        self.image = load_image('run_animation.png')

    def draw(self):
        self.image.clip_draw(self.frame * 100, 0,100,100, self.x, self.y)

    def update(self):
        self.frame = (self.frame + 1) % 8
        self.x +=5


 # ================================================



class zombie:
    def __init__(self):
        self.x, self.y = 0,90
        self.frame =0
        self.image = load_image('zombie_run_animation.png')

    def draw(self):
        self.image.clip_draw(self.frame*430,0,430,519,self.x,self.y,40, 50)

    def update(self):
        self.frame = (self.frame +1) % 10
        self.x +=5



#===================================================

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global running
    running = True

    # 땅 객체를 생성한다.
    global grass
    grass= Grass()

    global world
    world = []
    world.append(grass)

    # 소년 객체를 생성한다
    # global boy
    # boy = Boy()

    global team
    team = [Boy() for i in range(0,11)] # 소년 객체를 11개 생성한다.
    world += team

    # 좀비 객체를 생성한다
    global zom
    zom = zombie()
    world.append(zom)

def update_world():
    # grass.update()  # 땅 객체 호출
    # boy.update()    # 소년 객체 호출
    # for boy in team:  # 팀에 있는 소년 객체들을 호출한다.
        # boy.update()
    for o in world:
        o.update()
    
    pass

def render_world():
    clear_canvas()
    # grass.draw()    # 땅 객체를 그린다.
    # boy.draw()      # 소년 객체를 그린다.
    # for boy in team:  # 팀에 있는 소년 객체들을 그린다.
        # boy.draw()
    for o in world:
        o.draw()

    update_canvas()

open_canvas()

reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)

close_canvas()
