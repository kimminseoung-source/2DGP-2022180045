from math import pi
from pathlib import Path

from pico2d import *
from transitions import Machine


ASSET_DIR = Path(__file__).resolve().parent


class Grass:
    def __init__(self):
        self.image = load_image(str(ASSET_DIR / 'grass.png'))

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.image = load_image(str(ASSET_DIR / 'animation_sheet.png'))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP'],
            transitions=[
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        # Machine 생성 시 초기 상태의 진입 콜백은 직접 호출한다.
        self.on_enter_IDLE()

    def on_enter_IDLE(self):
        self.frame = 0
        self.idle_started = get_time()

    def on_enter_SLEEP(self):
        self.frame = 0

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if get_time() - self.idle_started >= 3.0:
                self.fall_asleep()

    def draw(self):
        if self.state == 'IDLE':
            self.image.clip_draw(self.frame * 100, 300, 100, 100,
                                 self.x, self.y)
        elif self.state == 'SLEEP':
            # 대기 이미지를 회전시켜 누워서 잠든 모습을 표시한다.
            self.image.clip_composite_draw(0, 300, 100, 100,
                                          -pi / 2, '',
                                          self.x, self.y - 25, 100, 100)


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


if __name__ == '__main__':
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
