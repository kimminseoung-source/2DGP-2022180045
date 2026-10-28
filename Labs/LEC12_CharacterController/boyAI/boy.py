from math import pi
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_LSHIFT, SDLK_RSHIFT,
    SDLK_SPACE,
    get_canvas_width, get_time, load_image,
)
from transitions import Machine


class Boy:
    def __init__(self, platforms=None):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.direction = 0
        self.pressed_keys = set()
        self.move_speed = 200  # 초당 이동 거리 (픽셀)
        self.dash_speed = 400  # Shift를 누르면 두 배 속도로 달린다.
        self.ground_y = self.y
        self.platforms = platforms if platforms is not None else []
        self.score = 0
        self.scored_platforms = set()
        self.half_width = 20
        self.half_height = 40
        self.gravity = 1200
        self.vertical_speed = 0
        self.max_charge_time = 1.2
        self.min_jump_speed = 300
        self.max_jump_speed = 650
        self.last_update = get_time()
        image_path = Path(__file__).resolve().parent.parent / 'animation_sheet.png'
        self.image = load_image(str(image_path))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'DASH', 'SLEEP', 'CHARGE', 'JUMP', 'FALL'],
            transitions=[
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP', 'DASH'], 'dest': 'RUN'},
                {'trigger': 'start_dash', 'source': ['IDLE', 'SLEEP', 'RUN'], 'dest': 'DASH'},
                {'trigger': 'stop_run', 'source': ['RUN', 'DASH'], 'dest': 'IDLE'},
                {'trigger': 'prepare_jump', 'source': ['IDLE', 'RUN', 'DASH', 'SLEEP'],
                 'dest': 'CHARGE'},
                {'trigger': 'release_jump', 'source': 'CHARGE', 'dest': 'JUMP'},
                {'trigger': 'start_fall', 'source': ['IDLE', 'RUN', 'DASH', 'SLEEP', 'CHARGE'],
                 'dest': 'FALL'},
                {'trigger': 'land', 'source': ['JUMP', 'FALL'], 'dest': 'IDLE'},
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

    def on_enter_RUN(self):
        self.frame = 0

    def on_enter_DASH(self):
        self.frame = 0

    def on_enter_CHARGE(self):
        self.frame = 0
        self.charge_started = get_time()

    def charge_ratio(self):
        return max(0.0, min(1.0,
                           (get_time() - self.charge_started) / self.max_charge_time))

    def on_enter_JUMP(self):
        self.vertical_speed = (self.min_jump_speed
                               + (self.max_jump_speed - self.min_jump_speed)
                               * self.charge_ratio())
        # 점프 시작 전의 시간이 공중 이동에 포함되지 않도록 한다.
        self.last_update = get_time()

    def on_enter_FALL(self):
        self.vertical_speed = 0

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT, SDLK_LSHIFT, SDLK_RSHIFT, SDLK_SPACE):
            return

        was_pressed = event.key in self.pressed_keys
        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        else:
            self.pressed_keys.discard(event.key)

        self.direction = (int(SDLK_RIGHT in self.pressed_keys)
                          - int(SDLK_LEFT in self.pressed_keys))
        if self.direction:
            self.face_dir = self.direction

        if event.key == SDLK_SPACE:
            if (event.type == SDL_KEYDOWN and not was_pressed
                    and self.state not in ('CHARGE', 'JUMP', 'FALL')):
                self.prepare_jump()
            elif event.type == SDL_KEYUP and self.state == 'CHARGE':
                self.release_jump()
        self.sync_movement_state()

    def sync_movement_state(self):
        # 준비 중에는 멈추고, 공중에서는 점프 상태를 유지한다.
        if self.state in ('CHARGE', 'JUMP', 'FALL'):
            return
        if self.direction:
            dash_pressed = bool(self.pressed_keys & {SDLK_LSHIFT, SDLK_RSHIFT})
            if dash_pressed and self.state != 'DASH':
                self.start_dash()
            elif not dash_pressed and self.state != 'RUN':
                self.start_run()
        elif self.state in ('RUN', 'DASH'):
            self.stop_run()

    def update(self):
        now = get_time()
        elapsed = now - self.last_update
        self.last_update = now

        if self.state in ('IDLE', 'RUN', 'DASH'):
            animation_speed = 16 if self.state == 'DASH' else 8
            self.frame = (self.frame + animation_speed * elapsed) % 8

        if self.state == 'IDLE':
            if now - self.idle_started >= 3.0:
                self.fall_asleep()
        # 짧은 시간 간격으로 나눠 이동하여 빠른 대시 중에도 발판을 통과하지 않는다.
        remaining = elapsed
        while remaining > 0:
            step = min(remaining, 1 / 120)
            self.move_with_collision(step)
            remaining -= step

    def has_support(self):
        if abs(self.y - self.ground_y) < 0.001:
            return True
        for platform in self.platforms:
            left, bottom, right, top = platform.get_bb()
            if (self.x + self.half_width > left and self.x - self.half_width < right
                    and abs(self.y - self.half_height - top) < 0.001):
                return True
        return False

    def move_with_collision(self, elapsed):
        if self.state in ('RUN', 'DASH', 'JUMP', 'FALL'):
            dash_pressed = bool(self.pressed_keys & {SDLK_LSHIFT, SDLK_RSHIFT})
            speed = self.dash_speed if dash_pressed else self.move_speed
            next_x = self.x + self.direction * speed * elapsed
            for platform in self.platforms:
                left, bottom, right, top = platform.get_bb()
                if self.y + self.half_height <= bottom or self.y - self.half_height >= top:
                    continue
                if self.direction > 0 and self.x + self.half_width <= left <= next_x + self.half_width:
                    next_x = min(next_x, left - self.half_width)
                elif self.direction < 0 and next_x - self.half_width <= right <= self.x - self.half_width:
                    next_x = max(next_x, right + self.half_width)
            self.x = max(25, min(get_canvas_width() - 25, next_x))

        if self.state not in ('JUMP', 'FALL') and not self.has_support():
            self.start_fall()

        if self.state not in ('JUMP', 'FALL'):
            return

        next_y = self.y + self.vertical_speed * elapsed - 0.5 * self.gravity * elapsed ** 2
        self.vertical_speed -= self.gravity * elapsed
        landed = False
        landing_platform = None
        if next_y < self.y:
            for platform in self.platforms:
                left, bottom, right, top = platform.get_bb()
                if self.x + self.half_width <= left or self.x - self.half_width >= right:
                    continue
                if next_y - self.half_height <= top <= self.y - self.half_height:
                    next_y = max(next_y, top + self.half_height)
                    landed = True
                    landing_platform = platform
            if next_y <= self.ground_y:
                next_y = self.ground_y
                landed = True
        else:
            for platform in self.platforms:
                left, bottom, right, top = platform.get_bb()
                if self.x + self.half_width <= left or self.x - self.half_width >= right:
                    continue
                if self.y + self.half_height <= bottom <= next_y + self.half_height:
                    next_y = min(next_y, bottom - self.half_height)
                    self.vertical_speed = 0

        self.y = next_y
        if landed:
            # 처음 착지한 발판만 점수를 지급한다.
            if landing_platform is not None and landing_platform not in self.scored_platforms:
                self.scored_platforms.add(landing_platform)
                self.score += 100
            self.vertical_speed = 0
            self.land()
            self.sync_movement_state()

    def draw(self, camera_y=0):
        screen_y = self.y - camera_y
        if self.state == 'IDLE':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_draw(int(self.frame) * 100, row, 100, 100,
                                 self.x, screen_y)
        elif self.state in ('RUN', 'DASH'):
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(int(self.frame) * 100, row, 100, 100,
                                 self.x, screen_y)
        elif self.state == 'CHARGE':
            # 전용 스프라이트 대신 이미지를 낮춰 웅크리는 준비 동작을 표현한다.
            row = 300 if self.face_dir == 1 else 200
            height = 80 - 20 * self.charge_ratio()
            self.image.clip_draw(0, row, 100, 100,
                                 self.x, screen_y - (100 - height) / 2, 100, height)
        elif self.state in ('JUMP', 'FALL'):
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(200, row, 100, 100, self.x, screen_y)
        elif self.state == 'SLEEP':
            # 바라보는 방향의 반대쪽으로 넘어져 등을 대고 눕는다.
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(0, row, 100, 100,
                                          self.face_dir * pi / 2, '',
                                          self.x, screen_y - 25, 100, 100)

