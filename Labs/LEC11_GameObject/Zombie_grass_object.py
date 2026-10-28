from pico2d import *
import random




#=======================================

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400,30)

    def update(self):
        pass

    pass


class Boy:
    def __init__(self):
        self.image = load_image('run_animation.png')
        self.frame=0                                    #
        self.x, self.y = random.randint(100, 700), 90   # 
        
    def draw(self):
        self.image.clip_draw(self.frame * 100 , 0, 100,100, self.x, self.y) #
        
    def update(self):
        self.frame = (self.frame +1 ) % 8
        self.x +=5

class Zombie:
    def __init__ (self):
        self.image = load_image('Zombie_run_animation.png')
        self.frame=0
        self.x,self.y=0, 90

    def draw(self):
        self.image.clip_draw(self.frame * self.image.w //10, 0, self.image.w//10, self.image.h,self.x, self.y, 120,70)

    def update(self):
        self.frame=(self.frame +1)%10
        self.x+=5    


#=========================================
def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
    pass


#=========================================
def reset_world():
    global running
    running = True

    # 땅 객체 생성
    global grass
    grass = Grass()

    global world
    world = []
    world.append(grass)

    # 소년을 생성한다.
    # global boy
    # boy = Boy()
    # world.append(boy)

    # 팀 객체를 생성한다.
    global team
    team = [Boy() for i in range(0,5)]
    world += team

    global Zom
    Zom = Zombie()
    world.append(Zom)

    pass

#=========================================
def update_world():
    for o in world:
        o.update()

    pass

#=========================================
def render_world():
    clear_canvas()
    for o in world:
        o.draw()

    update_canvas()
    pass

# ========================================

open_canvas()

reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)

close_canvas()