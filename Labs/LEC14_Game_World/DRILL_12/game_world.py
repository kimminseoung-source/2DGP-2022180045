# 객체로 구성된 게임월드
# world = [] #게임 월드에 존재하는 모든 객체를 담는 리스트

# 계층적 구조를 갖는 게임 월드
world = [[],[],[]]     # 계층이 들어있고 그 안에 객체가 들어있음 


# 게임 월드에 객체를 담는 함수
def add_object(o, depth=0):   #depth : 0(배경), 1(캐릭터)
    world[depth].append(o)

# 게임 월드에서 객체 제거
def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    
# 게임 로직
def update():
    for layer in world:
        for o in layer:
            o.update()
    

# 게임 렌더링
def render():
    for layer in world:
        for o in layer:
            o.draw()




































# world = [[], []] # layers for game objects

# def add_object(o, depth):
#     world[depth].append(o)

# def add_objects(ol, depth):
#     world[depth] += ol

# def remove_object(o):
#     for layer in world:
#         if o in layer:
#             layer.remove(o)
#             return

#     raise Exception("Object not found")


# def update():
#     for layer in world:
#         for o in layer:
#             o.update()

# def render():
#     for layer in world:
#         for o in layer:
#             o.draw()
