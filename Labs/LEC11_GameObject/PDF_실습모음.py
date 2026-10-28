# PDF 기준 실습 복습: 번호를 선택하고 이 파일을 실행하세요.
# 1 ESC 종료 / 2 방향키 단발 / 3 방향키 연속
# 4 마우스 이동 / 5 잔디와 소년 / 6 world와 좀비
# 주석과 코드 모두 아래에 들어 있습니다. 여러 실습을 동시에 실행하지 않습니다.
# 실제 과제 제출물이 아닌 수업 복습 참고 파일입니다.
from pathlib import Path
import os

실습번호 = 6  # 이 숫자를 1~6 중 하나로 바꾸세요.

# 아래 실습들의 상대경로 이미지가 이 파일 옆에서 검색되도록 설정합니다.
os.chdir(Path(__file__).resolve().parent)

실습코드 = {}

# ==========================================================
# 01_ESC종료
# ==========================================================
실습코드[1] = r'''
# LEC10 PDF 5~6쪽: 자동 이동 중 ESC 또는 X로 종료하기
# 준비 부분과 close_canvas를 보완해 독립 실행 예제로 구성했습니다.
from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')
running = True  # 반복을 시작하기 전에 실행 상태를 준비


def handle_events():
    global running  # 함수에서 전역 running에 값을 대입
    events = get_events()  # 함수 호출: 이벤트 목록 가져오기
    for event in events:
        if event.type == SDL_QUIT:  # 창 닫기 이벤트
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False  # 키 누름인지 먼저, ESC인지 다음에 확인


frame = 0
for x in range(0, 800, 5):  # 0부터 795까지 5씩 증가
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    # 원본 자를 위치(x,y), 자를 크기(w,h), 화면 중심 위치(x,y)
    update_canvas()
    handle_events()
    if not running:
        break  # for문은 running을 조건으로 삼지 않으므로 직접 탈출
    frame = (frame + 1) % 8  # 그림 번호 0~7 순환
    delay(0.05)

close_canvas()

'''

# ==========================================================
# 02_방향키단발이동
# ==========================================================
실습코드[2] = r'''
# LEC10 PDF 13~14쪽: 키 누름 이벤트마다 좌표 변경
from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running, x  # 이 함수에서 변경하는 전역 이름들
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                x += 10  # 오른쪽 키 누름 이벤트 한 번당 10 이동
            elif event.key == SDLK_LEFT:
                x -= 10
            elif event.key == SDLK_ESCAPE:
                running = False


running = True
x = 800 // 2  # 가운데 x좌표. //는 몫
frame = 0
while running:
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    update_canvas()
    handle_events()  # 여기서 바꾼 x는 다음 반복의 그리기에 반영
    frame = (frame + 1) % 8
    delay(0.05)

close_canvas()

'''

# ==========================================================
# 03_방향키연속이동
# ==========================================================
실습코드[3] = r'''
# LEC10 PDF 15~17쪽: 눌림/떼짐으로 dir 상태를 관리
# 이전 연습의 dir=1/-1/0 방식과 달리, PDF는 +=/-=로 두 키 상태를 합산합니다.
from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running, dir
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:  # 키 누름
            if event.key == SDLK_RIGHT:
                dir += 1
            elif event.key == SDLK_LEFT:
                dir -= 1
            elif event.key == SDLK_ESCAPE:
                running = False
        elif event.type == SDL_KEYUP:  # 키를 떼면 그 키의 기여를 취소
            if event.key == SDLK_RIGHT:
                dir -= 1
            elif event.key == SDLK_LEFT:
                dir += 1


running = True
x = 800 // 2
frame = 0
dir = 0  # +1 오른쪽, -1 왼쪽, 0 정지
while running:
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 0, 100, 100, x, 90)
    update_canvas()
    handle_events()
    frame = (frame + 1) % 8
    x += dir * 5  # 이벤트 때만이 아니라 게임 루프마다 이동
    delay(0.05)

close_canvas()

'''

# ==========================================================
# 04_마우스이동
# ==========================================================
실습코드[4] = r'''
# LEC10 PDF 19~23쪽: 마우스 위치로 캐릭터 위치 변경
from pico2d import *

TUK_WIDTH, TUK_HEIGHT = 1280, 1024
open_canvas(TUK_WIDTH, TUK_HEIGHT)
tuk_ground = load_image('TUK_GROUND.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running, x, y
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_MOUSEMOTION:
            x, y = event.x, TUK_HEIGHT - 1 - event.y
            # 마우스: 왼쪽 위가 원점. pico2d: 왼쪽 아래가 원점.
            # 같은 화면 위치를 표현하려고 y를 뒤집는다.
            # 높이 1024의 픽셀 좌표는 0~1023이므로 -1이 필요.
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


running = True
frame = 0
x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
hide_cursor()  # 게임 창 안의 마우스 포인터 숨기기
while running:
    clear_canvas()
    tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
    character.clip_draw(frame * 100, 100 * 1, 100, 100, x, y)
    update_canvas()
    handle_events()
    frame = (frame + 1) % 8
    delay(0.05)

close_canvas()

'''

# ==========================================================
# 05_잔디와소년한명
# ==========================================================
실습코드[5] = r'''
# LEC11 PDF 19~24쪽: 클래스와 게임 함수로 역할 분리
from pico2d import *


class Grass:
    def __init__(self):  # Grass()로 객체 생성 시 자동 초기화
        self.image = load_image('grass.png')  # self: 이 객체 자신

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass  # 잔디는 상태 변화 없음


class Boy:
    def __init__(self):
        self.x, self.y = 0, 90  # 위치는 이 객체의 속성
        self.frame = 0
        self.image = load_image('run_animation.png')

    def update(self):  # 상태 변경
        self.frame = (self.frame + 1) % 8
        self.x += 5

    def draw(self):  # 상태를 화면에 표현
        self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)


def handle_events():
    global running
    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global running, grass, boy
    running = True  # global만으로 값이 만들어지지는 않음: 실제 대입 필요
    grass = Grass()
    boy = Boy()


def update_world():
    grass.update()
    boy.update()


def render_world():
    clear_canvas()
    grass.draw()
    boy.draw()
    update_canvas()


open_canvas()
reset_world()  # 이 호출이 실행되어야 running과 객체들이 준비됨
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)
close_canvas()

'''

# ==========================================================
# 06_world목록과좀비
# ==========================================================
실습코드[6] = r'''
# LEC11 PDF 32~39쪽: 여러 소년 -> world 공통 관리 -> 좀비 추가
from pico2d import *
import random


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)


class Boy:
    def __init__(self):
        self.x, self.y = random.randint(100, 700), 90  # PDF 35쪽: 겹침 줄이기
        self.frame = random.randint(0, 7)  # PDF 37쪽: 그림도 다르게 시작
        self.image = load_image('run_animation.png')

    def update(self):
        self.frame = (self.frame + 1) % 8
        self.x += 5

    def draw(self):
        self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)


class Zombie:
    def __init__(self):
        self.x, self.y = 100, 170  # PDF 39쪽의 시작 위치
        self.frame = 0
        self.image = load_image('zombie_run_animation.png')

    def update(self):
        self.frame = (self.frame + 1) % 10
        self.x += 5

    def draw(self):
        frame_width = self.image.w // 10  # 같은 크기의 10칸이 가로 한 줄
        frame_height = self.image.h
        self.image.clip_draw(
            self.frame * frame_width, 0,  # 원본 자를 위치
            frame_width, frame_height,   # 원본 자를 크기
            self.x, self.y,               # 화면 중심 위치
            frame_width // 2, frame_height // 2  # PDF: 원본의 절반 크기
        )
        # 연습에서 쓴 40,50과 달리 PDF는 한 칸 크기의 절반으로 표시.
        # 출력 크기만 마지막 두 값으로 변경한다. 자를 크기는 유지한다.


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global running, world
    running = True
    world = []
    grass = Grass()
    world.append(grass)  # 객체 하나 추가
    team = [Boy() for i in range(11)]  # 소년 11개를 각각 생성
    world += team  # 리스트 항목들을 각각 추가
    zombie = Zombie()
    world.append(zombie)  # 객체 하나에 += 사용하면 오류
    # world에는 잔디 1 + 소년 11 + 좀비 1 = 총 13개


def update_world():
    for o in world:
        o.update()  # 실제 객체 종류에 따라 다른 update 실행


def render_world():
    clear_canvas()
    for o in world:
        o.draw()  # update가 아니라 draw. 잔디부터 순서대로 그림
    update_canvas()


open_canvas()
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)
close_canvas()

'''

if __name__ == '__main__':
    if 실습번호 not in 실습코드:
        raise ValueError('실습번호는 1~6이어야 합니다.')
    exec(compile(실습코드[실습번호], __file__, 'exec'), globals())
