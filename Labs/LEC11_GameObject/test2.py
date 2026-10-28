# from pico2d import * 
# import random

# # reset, handle, update, render 했는데 이제 뭘해야하지? 
# # 어떻게 reset할건가??
# # 어떻게 handle 채우지?


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400,30)
        pass

    def update(self):
        pass


class Boy:
    def __init__(self):
        self.image = load_image('run_animation.png')
        self.x, self.y = random.randint(100,500),90
        self.frame=0


        pass

    def draw(self):
        self.image.clip_draw(self.frame*100, 0,100,100,self.x,self.y)

        pass

    def update(self):
        self.frame = (self.frame +1)%8
        self.x+=5

        pass


class Zombie:
    def __init__(self):
        self.image = load_image('Zombie_grass_object.py')
        self.x, self.y = 0,90
        self.frame=0
        
    def draw(self):
        self.image.clip_draw(self.frame*self.image.w, self.image.h, self.image.w//10, self.image.h, 0, 90, 200, 150)

    def update(self):
        self.frame = (self.frame +1 ) & 10
        self.x +=5
        pass

    pass
#===========================================
def reset_world():
    global running
    global world
    global Team
    
    running = True

    # 어떤 내용을 채워야할까?
    grass = Grass()

    world =[]
    world.append(grass)
    
    boy = Boy()
    world.append(boy)

    Team = [Boy() for i in range (0,11)]
    world += Team

    global Zom
    zom = Zombie()
    world.append(zom)

    pass


#===========================================
def handel_event():
    # 어떤 내용들을 채워야할까?
    global running
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key() == SDLK_ESCAPE:
            running = False

def update_world():
    # 어떤 내용들을 채워야할까?
    for o in world:
        o.update()
    
    pass



def render_world():
    clear_canvas()

    for o in world:
        o.draw()

    update_canvas()

    pass

#===========================================
open_canvas()

reset_world()


while running:
    handel_event()
    update_world()
    render_world()
    delay(0.05)



# close_canvas()

# LEC 11 
# 시작 시 화면 바닥부분에 랜덤한 20개 풍선 x 좌표 랜덤
# 풍선이 위로 올라감, 상승 속도는 풍선마다 다름
# 풍선이 화면 맨위에 도달하면 화면 밖으로 사라지지 않고 그 자리에서 위아래로 출렁

# 1. 랜덤한 풍선 20개 생성
# 1-1 풍선 화면이 띄우기, 
# 2. 풍선이 위로 향함, 속도는 다르게
# 3. 풍선이 위에 도달하면 그자리에서 둥둥 머물기


# 클래스를 만들고, 객체들을 생성하는 방식

# 커밋을 적절하게 할 것


# from pico2d import * 
# import random

# class Ball:
#     def __init__(self):
#         self.image = load_image('ball21x21.png')
#         self.x, self.y = random.randint(100, 700), 90

#     def draw(self):
#         self.image.draw(400,30)
#         pass

#     def update(self):
#         pass
    
#     pass

# def reset_world():
#     global running
#     global world

#     running = True


#     world = []
    
#     ball = Ball()
#     world.append(ball)
#     pass

# def handle_event():
#     global running
#     events = get_events()

#     for event in events:
#         if event.type == SDL_QUIT:
#             running =False
#         elif event.type == SDL_KEYDOWN and event.key() == SDLK_ESCAPE:
#             running = False


# def update_world():
#     for o in world:
#         o.update()
#     pass

# def render_world():
#     clear_canvas()

#     for o in world:
#         o.update()

#     update_canvas()
    
#     pass


# open_canvas()

# reset_world()

# while running:
#     handle_event()
#     update_world()
#     render_world()
#     delay(0.5)

# close_canvas()
