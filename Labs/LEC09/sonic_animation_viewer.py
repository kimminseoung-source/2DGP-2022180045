"""소닉 애니메이션 뷰어 — Python 3 / pico2d, 단일 파일 구현.

이미지 조사 (원본 399×525, 좌상단 기준, 아래 순서로 재생):
  01 대기와 표정: 첫 행 앞의 7프레임
  02 위 바라보기: 첫 행의 다음 2프레임
  03 웅크리기: 첫 행의 다음 1프레임 (독립 포즈)
  04 몸 말기: 첫 행의 마지막 1프레임 (독립 포즈)
  05 걷기: 두 번째 행의 12프레임
  06 가속: 세 번째 행의 6프레임
  07 몸 회전: 네 번째 행 앞의 8프레임
  08 공 회전: 네 번째 행 마지막 1 + 다섯 번째 행 6프레임
  09 달리기: 여섯 번째 행의 6프레임
  10 빠른 달리기: 일곱 번째 행의 6프레임
  11 방향 돌기: 여덟 번째 행 앞의 6프레임
  12 넘어지기: 여덟 번째 행 마지막 2프레임
  13 균형 잡기: 아홉 번째 행의 8프레임
  14 놀라기: 열 번째 행 앞의 2프레임
  15 손 모으기: 열 번째 행 마지막 2프레임

합계 15동작 / 76프레임. 이름은 이미지의 포즈에 따른 설명이다.
제외: 상단 제목, 하단 제작자 문구, 문구 옆 노란색/갈색 캐릭터.
하단 두 그림은 크레딧 장식으로 분류하며 본문 동작 시퀀스에 넣지 않는다.
프레임 경계는 고정 격자가 아니다. 첫 행은 신발이 서로 맞닿으므로
투명 픽셀의 연결 여부만으로 분할하지 않고 실제 캐릭터 경계를 사용한다.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
from time import perf_counter

import pico2d as p

WIDTH, HEIGHT = 800, 600
REPEAT_COUNT = 5
HOLD_SECONDS = 0.5
DEFAULT_FPS = 10
DISPLAY_FRACTION = 0.65
RENDER_FPS = 60
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int
    anchor_x: float
    anchor_y: float

    def clip_rect(self, image_height):
        """좌상단 원본 좌표를 pico2d의 좌하단 잘라내기 좌표로 변환."""
        return self.left, image_height - self.top - self.height, self.width, self.height


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    fps: float = DEFAULT_FPS


def make_frame(left, top, width, height, anchor_x=None, baseline=None):
    return Frame(left, top, width, height,
                 width / 2 if anchor_x is None else anchor_x,
                 height if baseline is None else baseline - top)


def validate_animations(animations, image_width, image_height):
    for animation in animations:
        if not animation.frames or animation.fps <= 0:
            raise ValueError(f"잘못된 동작 정의: {animation.name}")
        for frame in animation.frames:
            if not (frame.left >= 0 and frame.top >= 0 and frame.width > 0 and
                    frame.height > 0 and frame.left + frame.width <= image_width and
                    frame.top + frame.height <= image_height):
                raise ValueError(f"이미지 범위를 벗어난 프레임: {animation.name} {frame}")


ANIMATIONS = (
    Animation("대기와 표정", (
        make_frame(1, 39, 29, 39, 14, 78),
        make_frame(31, 40, 26, 38, 13, 78),
        make_frame(58, 39, 29, 39, 14, 78),
        make_frame(87, 40, 29, 38, 14, 78),
        make_frame(118, 40, 30, 38, 14, 78),
        make_frame(150, 40, 30, 38, 14, 78),
        make_frame(182, 40, 31, 38, 14, 78),
    )),
)


class Playback:
    def __init__(self, animations=ANIMATIONS):
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.completed_repeats = 0
        self.holding = False
        self.hold_elapsed = 0.0

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, delta_seconds):
        if self.holding:
            self.hold_elapsed += delta_seconds
            return
        interval = 1 / self.animation.fps
        self.frame_elapsed += min(delta_seconds, interval)
        if self.frame_elapsed >= interval:
            self.frame_elapsed -= interval
            if self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                # 마지막 프레임의 표시 시간이 끝나야 한 회 완료이다.
                self.completed_repeats += 1
                if self.completed_repeats < REPEAT_COUNT:
                    self.frame_index = 0
                else:
                    self.holding = True
                    self.hold_elapsed = 0.0
                    self.frame_elapsed = 0.0


def display_layout(animations):
    frames = [frame for animation in animations for frame in animation.frames]
    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)
    scale = min(WIDTH * DISPLAY_FRACTION / max_width,
                HEIGHT * DISPLAY_FRACTION / max_height)
    return scale, WIDTH / 2, (HEIGHT - max_height * scale) / 2


def draw_frame(sheet, frame, layout):
    scale, origin_x, origin_y = layout
    x = origin_x + (frame.width / 2 - frame.anchor_x) * scale
    y = origin_y + (frame.anchor_y - frame.height / 2) * scale
    sheet.clip_draw(*frame.clip_rect(sheet.h), x, y,
                    frame.width * scale, frame.height * scale)


def quit_requested(events):
    """재생 상태와 관계없이 매 루프에서 종료 입력을 처리한다."""
    return any(event.type == p.SDL_QUIT or
               event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
               for event in events)


def main():
    """뷰어의 실행 진입점."""
    p.open_canvas(WIDTH, HEIGHT)
    try:
        try:
            if not SPRITE_PATH.is_file():
                raise FileNotFoundError("이미지 파일이 없습니다.")
            sheet = p.load_image(str(SPRITE_PATH))
            validate_animations(ANIMATIONS, sheet.w, sheet.h)
            layout = display_layout(ANIMATIONS)
        except (OSError, ValueError) as error:
            print(f"이미지 로딩 실패: {SPRITE_PATH}\n원인: {error or 'PNG를 읽을 수 없습니다.'}",
                  file=sys.stderr)
            return 1
        running = True
        playback = Playback()
        previous_time = perf_counter()
        while running:
            loop_start = perf_counter()
            delta_seconds = loop_start - previous_time
            previous_time = loop_start
            running = not quit_requested(p.get_events())
            if not running:
                break
            playback.update(delta_seconds)
            p.clear_canvas()
            draw_frame(sheet, playback.frame, layout)
            p.update_canvas()
            p.delay(max(0, 1 / RENDER_FPS - (perf_counter() - loop_start)))
    finally:
        p.close_canvas()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
