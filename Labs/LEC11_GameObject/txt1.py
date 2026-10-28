from pico2d import *
import random


# ==================================================
# 1. 잔디 클래스
# 오늘 배운 Grass 코드를 그대로 사용합니다.
# ==================================================
class Grass:
    def __init__(self):
        # Grass()를 실행하면 자동으로 호출됩니다.
        # 잔디 이미지를 이 객체의 image에 저장합니다.
        self.image = load_image('grass.png')

    def draw(self):
        # 잔디 이미지의 중심을 (400, 30)에 놓습니다.
        self.image.draw(400, 30)

    def update(self):
        # 잔디는 움직이지 않으므로 변경할 상태가 없습니다.
        pass


# ==================================================
# 2. 좀비 클래스
# 오늘 배운 Boy와 같은 구조입니다.
# 달라지는 것은 이미지, 프레임 수, 자르는 크기입니다.
# ==================================================
class Zombie:
    def __init__(self):
        # 각 좀비가 서로 다른 x좌표에서 시작합니다.
        # randint는 100과 700을 모두 포함합니다.
        self.x, self.y = random.randint(100, 700), 90

        # 첫 번째 동작 그림부터 시작합니다.
        self.frame = 0

        # 좀비 이미지를 불러옵니다.
        self.image = load_image('zombie_run_animation.png')

    def draw(self):
        # 현재 좀비 이미지는 전체 4300 × 519입니다.
        # 가로로 그림 10개가 있으므로 한 칸은 430 × 519입니다.
        #
        # clip_draw의 순서:
        # 자를 x, 자를 y, 자를 너비, 자를 높이,
        # 화면 중심 x, 화면 중심 y, 출력 너비, 출력 높이
        self.image.clip_draw(
            self.frame * 430, 0,   # 원본에서 자를 왼쪽 아래 위치
            430, 519,             # 원본에서 자를 크기
            self.x, self.y,       # 화면에 그릴 중심 위치
            42, 50                # 화면에서는 작게 표시
        )

        # 예: frame이 2이면
        # 원본의 (860, 0)에서 430 × 519만큼 자릅니다.
        #
        # 크기를 바꾸려면 마지막 42, 50을 바꾸세요.
        # 예: 약 두 배 크기는 83, 100
        # 원본에서 자르는 430, 519는 그대로 둡니다.

    def update(self):
        # 좀비의 그림은 10개입니다.
        # 그림 번호가 0 → 1 → ... → 9 → 0으로 반복됩니다.
        self.frame = (self.frame + 1) % 10

        # 매번 오른쪽으로 5픽셀 이동합니다.
        self.x += 5

        # [추가 연습] 화면 밖으로 나가면 왼쪽에서 다시 등장
        # 출력 너비가 42이므로 중심에서 반너비는 21입니다.
        # 왼쪽 끝까지 800을 넘으면 완전히 화면 밖입니다.
        if self.x - 21 > 800:
            self.x = -21

        # 기본 이동만 연습하려면 위 if문 두 줄을 빼도 됩니다.
        # 그러면 좀비는 오른쪽으로 이동하다 화면 밖으로 나갑니다.


# ==================================================
# 3. 입력 처리
# 오늘 코드와 같습니다.
# X 또는 ESC를 누르면 running을 False로 바꿉니다.
# ==================================================
def handle_events():
    global running

    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


# ==================================================
# 4. 객체 생성과 world 구성
# ==================================================
def reset_world():
    global running
    running = True

    # 잔디 객체 한 개 생성
    global grass
    grass = Grass()

    # 모든 게임 객체를 담는 리스트
    global world
    world = []

    # 객체 한 개는 append로 추가합니다.
    world.append(grass)

    # 좀비 객체 5개를 생성해서 리스트에 담습니다.
    global team
    team = [Zombie() for i in range(5)]

    # 위 한 줄은 아래와 같은 뜻입니다.
    #
    # team = []
    # for i in range(5):
    #     team.append(Zombie())
    #
    # Zombie()를 다섯 번 호출하므로 서로 다른 좀비가 생깁니다.

    # 리스트 안의 객체들을 world에 각각 추가합니다.
    world += team

    # world에는 잔디 1개 + 좀비 5개 = 총 6개 객체가 있습니다.
    #
    # 좀비 한 명만 추가한다면:
    # zom = Zombie()
    # world.append(zom)
    #
    # world += zom은 오류입니다.
    # zom은 객체 하나이고, team은 객체들의 리스트이기 때문입니다.


# ==================================================
# 5. 모든 객체의 상태 변경
# ==================================================
def update_world():
    for o in world:
        o.update()

        # o는 world에서 꺼낸 객체 하나입니다.
        # 잔디면 Grass.update()가 실행되어 아무 변화가 없습니다.
        # 좀비면 Zombie.update()가 실행되어 그림과 위치가 바뀝니다.


# ==================================================
# 6. 모든 객체를 화면에 그리기
# ==================================================
def render_world():
    clear_canvas()       # 이전 그림 지우기

    for o in world:
        o.draw()         # 잔디부터 그리고 좀비들을 그립니다.

    update_canvas()      # 그린 내용을 실제 화면에 표시합니다.


# ==================================================
# 7. 게임 실행
# 클래스와 함수는 위에서 정의하고 여기서 실제 호출합니다.
# ==================================================
open_canvas()            # 기본 800 × 600 창 열기

reset_world()            # running, 잔디, 좀비, world 준비

while running:
    handle_events()      # 입력 확인
    update_world()       # 위치와 프레임 변경
    render_world()       # 변경된 상태 그리기
    delay(0.05)          # 0.05초 대기

close_canvas()           # 반복문이 끝나면 창 닫기