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
프레임 경계는 고정 격자가 아니다. 첫 행의 프레임들은 가로 투영이
맞닿으므로 실제 픽셀의 연결 영역과 캐릭터 경계를 함께 확인한다.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse
import math
import sys
from time import perf_counter

import pico2d as p
import pico2d.pico2d as canvas

WIDTH, HEIGHT = 1200, 800
REPEAT_COUNT = 5
HOLD_SECONDS = 0.5
DEFAULT_FPS = 10
DISPLAY_FRACTION = 0.60
RENDER_FPS = 60
MOVEMENT_MARGIN = 48
WALK_SPEED = 180
ACCELERATION_SPEED = 340
ROLL_SPEED = 300
BALL_SPEED = 420
RUN_SPEED = 460
FAST_RUN_SPEED = 680
TRAIL_INTERVAL = 0.045
TRAIL_LIFETIME = 0.24
MAX_TRAILS = 5
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
    movement_speed: float = 0.0  # 화면 픽셀/초, 0이면 제자리 동작


def make_frame(left, top, width, height, anchor_x=None, baseline=None):
    return Frame(left, top, width, height,
                 width / 2 if anchor_x is None else anchor_x,
                 height if baseline is None else baseline - top)


def validate_animations(animations, image_width, image_height):
    if not animations:
        raise ValueError("재생할 동작이 없습니다.")
    for animation in animations:
        if (not animation.frames or not math.isfinite(animation.fps) or animation.fps <= 0 or
                not math.isfinite(animation.movement_speed) or animation.movement_speed < 0):
            raise ValueError(f"잘못된 동작 정의: {animation.name}")
        for frame in animation.frames:
            if not (frame.left >= 0 and frame.top >= 0 and frame.width > 0 and
                    frame.height > 0 and frame.left + frame.width <= image_width and
                    frame.top + frame.height <= image_height):
                raise ValueError(f"이미지 범위를 벗어난 프레임: {animation.name} {frame}")


def frame_row(rectangles, baseline, centers=None):
    """행의 바닥 기준선을 공유하되 프레임 크기는 각각 유지한다."""
    if centers is not None and len(centers) != len(rectangles):
        raise ValueError("프레임 수와 몸통 기준점 수가 다릅니다.")
    return tuple(make_frame(*rectangle, baseline=baseline,
                            anchor_x=None if centers is None else centers[index])
                 for index, rectangle in enumerate(rectangles))


ANIMATIONS = (
    Animation("대기와 표정", (
        make_frame(1, 39, 29, 39, 14, 78),
        make_frame(31, 40, 26, 38, 13, 78),
        make_frame(58, 39, 28, 39, 14, 78),
        make_frame(86, 40, 30, 38, 15, 78),
        make_frame(118, 40, 30, 38, 14, 78),
        make_frame(150, 40, 30, 38, 14, 78),
        make_frame(182, 40, 29, 38, 14, 78),
    )),
    Animation("위 바라보기", (
        make_frame(211, 39, 29, 38, 17, 78),
        make_frame(240, 39, 29, 38, 16, 78),
    )),
    Animation("웅크리기", (make_frame(270, 45, 24, 32, baseline=78),)),
    Animation("몸 말기", (make_frame(302, 51, 29, 26, baseline=78),)),
    Animation("걷기", frame_row((
        (8, 80, 26, 37), (37, 80, 27, 37), (65, 80, 31, 38),
        (97, 80, 37, 37), (135, 80, 32, 35), (170, 79, 32, 38),
        (206, 79, 26, 38), (238, 80, 24, 37), (263, 80, 30, 37),
        (295, 80, 36, 37), (334, 80, 32, 36), (370, 79, 29, 38),
    ), 118, (16, 16, 18, 21, 20, 20, 16, 16, 18, 21, 20, 20)), fps=12, movement_speed=WALK_SPEED),
    Animation("가속", frame_row((
        (1, 124, 33, 40), (39, 124, 35, 39), (89, 125, 35, 38),
        (130, 121, 34, 42), (181, 122, 34, 41), (228, 122, 33, 40),
    ), 164, (22, 23, 23, 23, 19, 19)), fps=16, movement_speed=ACCELERATION_SPEED),
    Animation("몸 회전", frame_row((
        (1, 169, 29, 30), (35, 167, 29, 31), (67, 169, 30, 29),
        (98, 169, 31, 29), (131, 168, 29, 30), (162, 168, 29, 31),
        (193, 170, 30, 29), (230, 170, 31, 29),
    ), 200), fps=16, movement_speed=ROLL_SPEED),
    Animation("공 회전", (
        make_frame(268, 170, 30, 30, baseline=200),
        *frame_row(((1, 206, 30, 27), (36, 206, 29, 27), (70, 206, 29, 27),
                    (105, 206, 29, 27), (139, 206, 29, 27), (174, 206, 29, 27)), 233),
    ), fps=18, movement_speed=BALL_SPEED),
    Animation("달리기", frame_row((
        (1, 239, 29, 35), (36, 239, 30, 35), (74, 239, 31, 35),
        (111, 238, 31, 36), (149, 239, 30, 35), (186, 238, 31, 36),
    ), 274, (18, 18, 21, 21, 21, 21)), fps=16, movement_speed=RUN_SPEED),
    Animation("빠른 달리기", frame_row((
        (1, 283, 29, 35), (36, 283, 30, 35), (72, 286, 39, 31),
        (123, 285, 39, 32), (172, 286, 39, 31), (218, 285, 38, 32),
    ), 318, (18, 18, 26, 26, 26, 26)), fps=20, movement_speed=FAST_RUN_SPEED),
    Animation("방향 돌기", frame_row((
        (1, 326, 24, 45), (31, 327, 29, 44), (65, 327, 20, 44),
        (90, 327, 25, 43), (119, 327, 25, 43), (149, 327, 20, 44),
    ), 371, (12, 15, 10, 12, 12, 10))),
    Animation("넘어지기", frame_row(((184, 341, 40, 28), (232, 341, 39, 27)), 370)),
    Animation("균형 잡기", frame_row((
        (1, 379, 27, 38), (31, 379, 31, 36), (64, 379, 31, 36), (99, 377, 33, 38),
        (136, 379, 32, 36), (176, 379, 33, 36), (217, 379, 33, 36), (254, 378, 33, 36),
    ), 417, (14, 13, 14, 17, 14, 14, 14, 14))),
    Animation("놀라기", frame_row(((6, 429, 34, 40), (49, 426, 34, 43)), 469)),
    Animation("손 모으기", frame_row(((96, 427, 23, 39), (125, 427, 23, 39)), 468)),
)


class Playback:
    def __init__(self, animations=ANIMATIONS, layout=None):
        if not animations:
            raise ValueError("재생할 동작이 없습니다.")
        self.animations = animations
        self.layout = display_layout(animations) if layout is None else layout
        self.position_x = self.layout[1]
        self.direction = 1
        self.trails = []
        self.trail_elapsed = 0.0
        self.scene_scroll = 0.0
        self.animation_index = 0
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.completed_repeats = 0
        self.holding = False
        self.hold_elapsed = 0.0
        self.cycles = 0

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, delta_seconds):
        if not math.isfinite(delta_seconds) or delta_seconds < 0:
            raise ValueError("경과 시간은 유한한 0 이상의 값이어야 합니다.")
        if self.holding:
            self.hold_elapsed += delta_seconds
            if self.hold_elapsed >= HOLD_SECONDS:
                self.next_animation()
            return
        interval = 1 / self.animation.fps
        step = min(delta_seconds, interval)
        self.trails = [(f, x, direction, age + step)
                       for f, x, direction, age in self.trails if age + step < TRAIL_LIFETIME]
        if self.animation.movement_speed:
            self.trail_elapsed += step
            if self.trail_elapsed >= TRAIL_INTERVAL:
                self.trails.append((self.frame, self.position_x, self.direction, 0.0))
                self.trails = self.trails[-MAX_TRAILS:]
                self.trail_elapsed %= TRAIL_INTERVAL
            self.scene_scroll += self.animation.movement_speed * self.direction * step * 0.35
            # 프레임 재생과 같은 지연 보정으로 한 번의 갱신에서 순간이동하지 않는다.
            distance = self.animation.movement_speed * min(delta_seconds, interval)
            bounds = movement_bounds(self.animation, self.layout)
            self.position_x, self.direction = reflected_movement(
                self.position_x, self.direction, distance, *bounds)
        # 긴 창 이동/시스템 지연에서는 한 프레임만 진행한다.
        # 보이지 않은 프레임과 동작을 건너뛰지 않고 다음 표시 시간을 새로 보장한다.
        if delta_seconds >= interval:
            self.frame_elapsed = interval
        else:
            self.frame_elapsed += delta_seconds
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
                    self.trails.clear()

    def next_animation(self):
        self.animation_index = (self.animation_index + 1) % len(self.animations)
        if self.animation_index == 0:
            self.cycles += 1
        self.frame_index = 0
        self.completed_repeats = 0
        self.frame_elapsed = 0.0
        self.hold_elapsed = 0.0
        self.holding = False
        self.position_x = self.layout[1]
        self.direction = 1
        self.trails.clear()
        self.trail_elapsed = 0.0


def movement_bounds(animation, layout):
    """양쪽 방향과 모든 프레임의 팔다리·효과를 포함한 안전한 기준점 범위."""
    scale = layout[0]
    radius = max(max(abs(f.anchor_x), abs(f.width - f.anchor_x))
                 for f in animation.frames) * scale
    return MOVEMENT_MARGIN + radius, WIDTH - MOVEMENT_MARGIN - radius


def reflected_movement(position, direction, distance, left, right):
    """경계 너머의 이동량을 반사하여 속도를 유지하고 진행 방향을 갱신한다."""
    span = right - left
    if span <= 0:
        return (left + right) / 2, direction
    phase = position - left if direction > 0 else 2 * span - (position - left)
    phase = (phase + distance) % (2 * span)
    if phase < span:
        return left + phase, 1
    return right - (phase - span), -1


def display_layout(animations):
    frames = [frame for animation in animations for frame in animation.frames]
    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)
    scale = min(WIDTH * DISPLAY_FRACTION / max_width,
                HEIGHT * DISPLAY_FRACTION / max_height)
    # 잘라내기 중심이 아닌 기준점에 정렬한 전체 프레임의 외곽을 계산한다.
    left = min(-frame.anchor_x for frame in frames)
    right = max(frame.width - frame.anchor_x for frame in frames)
    bottom = min(frame.anchor_y - frame.height for frame in frames)
    top = max(frame.anchor_y for frame in frames)
    scale = min(scale, WIDTH * 0.9 / (right - left), HEIGHT * 0.9 / (top - bottom))
    return (scale, WIDTH / 2 - (left + right) * scale / 2,
            HEIGHT / 2 - (bottom + top) * scale / 2)


def draw_frame(sheet, frame, layout, position_x=None, direction=1):
    scale, origin_x, origin_y = layout
    origin_x = origin_x if position_x is None else position_x
    x = origin_x + direction * (frame.width / 2 - frame.anchor_x) * scale
    y = origin_y + (frame.anchor_y - frame.height / 2) * scale
    if direction < 0:
        sheet.clip_composite_draw(*frame.clip_rect(sheet.h), 0, "h", x, y,
                                  frame.width * scale, frame.height * scale)
    else:
        sheet.clip_draw(*frame.clip_rect(sheet.h), x, y,
                        frame.width * scale, frame.height * scale)


def quit_requested(events):
    """재생 상태와 관계없이 매 루프에서 종료 입력을 처리한다."""
    return any(event.type == p.SDL_QUIT or
               event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE
               for event in events)


def scene_line(x1, y1, x2, y2, color):
    """무대 선 좌표는 캐릭터와 같은 좌하단 기준을 사용한다."""
    p.SDL_SetRenderDrawColor(canvas.renderer, *color, 255)
    p.SDL_RenderDrawLine(canvas.renderer, round(x1), round(HEIGHT - y1),
                        round(x2), round(HEIGHT - y2))


def draw_stage(playback):
    ground = playback.layout[2] - 12
    # 원본 픽셀을 변경하지 않고 SDL 도형으로 야간 무대와 원근 바닥을 그린다.
    for top in range(0, HEIGHT, 16):
        depth = top / HEIGHT
        p.SDL_SetRenderDrawColor(canvas.renderer, 6 + int(depth * 5),
                                10 + int(depth * 10), 24 + int(depth * 16), 255)
        rect = p.SDL_Rect(0, top, WIDTH, min(16, HEIGHT - top))
        p.SDL_RenderFillRect(canvas.renderer, rect)
    for t in (0.12, 0.24, 0.39, 0.58, 0.8, 1.0):
        y = ground * (1 - t * t)
        scene_line(0, y, WIDTH, y, (16, 39, 58))
    offset = playback.scene_scroll % 120
    for x in range(-240, WIDTH + 241, 120):
        bottom_x = x - offset
        horizon_x = WIDTH / 2 + (bottom_x - WIDTH / 2) * .38
        scene_line(horizon_x, ground, bottom_x, 0, (18, 47, 67))
    scene_line(0, ground, WIDTH, ground, (32, 129, 161))
    scene_line(0, ground - 3, WIDTH, ground - 3, (12, 56, 81))
    # 바닥의 기준선과 캐릭터를 따라가는 그림자로 이동을 뚜렷하게 보여 준다.
    for row in range(-7, 8):
        half_width = 80 * math.sqrt(max(0, 1 - (row / 8) ** 2))
        scene_line(playback.position_x - half_width, ground + 4 + row,
                   playback.position_x + half_width, ground + 4 + row, (4, 8, 17))
    if playback.animation.movement_speed and not playback.holding:
        for index, height in enumerate((80, 135, 200)):
            start = playback.position_x - playback.direction * (140 + index * 18)
            length = min(220, playback.animation.movement_speed * .28)
            scene_line(start, playback.layout[2] + height,
                       start - playback.direction * length, playback.layout[2] + height,
                       (28, 72 + index * 9, 106 + index * 10))


def draw_character(sheet, playback):
    try:
        for frame, x, direction, age in playback.trails:
            sheet.opacify(.22 * (1 - age / TRAIL_LIFETIME))
            draw_frame(sheet, frame, playback.layout, x, direction)
    finally:
        # 잔상 이후의 본체와 다음 프레임은 항상 완전히 불투명하게 표시한다.
        sheet.opacify(1.0)
    draw_frame(sheet, playback.frame, playback.layout, playback.position_x, playback.direction)


def ordered_animations(first_name=None):
    if first_name is None:
        return ANIMATIONS
    for index, animation in enumerate(ANIMATIONS):
        if animation.name == first_name:
            return ANIMATIONS[index:] + ANIMATIONS[:index]
    raise ValueError(f"알 수 없는 동작: {first_name}")


def viewer_title(playback):
    if playback.holding:
        state = "0.5초 대기"
    elif playback.animation.movement_speed:
        state = "오른쪽 이동" if playback.direction > 0 else "왼쪽 이동"
    else:
        state = "제자리 동작"
    repeat = min(playback.completed_repeats + 1, REPEAT_COUNT)
    return f"소닉 뷰어 | {playback.animation.name} | {state} | {repeat}/{REPEAT_COUNT}"


def run_viewer(cycles=None, sprite_path=SPRITE_PATH, start_animation=None):
    """옵션을 생략하면 무한 반복. cycles는 검증용 전체 순환 횟수."""
    sheet = None
    animations = ordered_animations(start_animation)
    p.open_canvas(WIDTH, HEIGHT)
    try:
        try:
            if not sprite_path.is_file():
                raise FileNotFoundError("이미지 파일이 없습니다.")
            sheet = p.load_image(str(sprite_path))
            validate_animations(animations, sheet.w, sheet.h)
            layout = display_layout(animations)
        except (OSError, ValueError) as error:
            reason = str(error) or p.IMG_GetError().decode("utf-8", errors="replace")
            print(f"이미지 로딩 실패: {sprite_path}\n원인: {reason}",
                  file=sys.stderr)
            return 1
        running = True
        playback = Playback(animations, layout=layout)
        previous_time = perf_counter()
        while running:
            loop_start = perf_counter()
            delta_seconds = loop_start - previous_time
            previous_time = loop_start
            running = not quit_requested(p.get_events())
            if not running:
                break
            playback.update(delta_seconds)
            if cycles is not None and playback.cycles >= cycles:
                break
            draw_stage(playback)
            # pico2d의 FPS 제목을 현재 동작 상태로 갱신한다.
            p.SDL_SetWindowTitle(canvas.window, viewer_title(playback).encode("utf-8"))
            draw_character(sheet, playback)
            p.update_canvas()
            p.delay(max(0, 1 / RENDER_FPS - (perf_counter() - loop_start)))
    finally:
        # 이미지 텍스처를 렌더러보다 먼저 해제한다.
        sheet = None
        p.close_canvas()
    return 0


def self_test():
    """창을 열지 않고 재생 경계와 데이터·배치를 검증한다."""
    import struct
    from types import SimpleNamespace
    import unittest

    class ViewerTests(unittest.TestCase):
        def test_source_coordinates_and_inventory(self):
            with SPRITE_PATH.open("rb") as image:
                header = image.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            image_width, image_height = struct.unpack(">II", header[16:24])
            validate_animations(ANIMATIONS, image_width, image_height)
            self.assertEqual(len(ANIMATIONS), 15)
            frames = [f for a in ANIMATIONS for f in a.frames]
            self.assertEqual(len(frames), 76)
            self.assertEqual(len({(f.left, f.top, f.width, f.height) for f in frames}), 76)
            for f in frames:
                self.assertEqual(f.clip_rect(image_height)[1], image_height - f.top - f.height)

        def test_invalid_animation_data(self):
            f = ANIMATIONS[0].frames[0]
            for actions in ((), (Animation("빈 동작", ()),),
                            (Animation("속도 0", (f,), 0),),
                            (Animation("무한 속도", (f,), math.inf),),
                            (Animation("음수 이동 속도", (f,), movement_speed=-1),),
                            (Animation("무한 이동 속도", (f,), movement_speed=math.inf),),
                            (Animation("영역 오류", (make_frame(398, 0, 2, 3),)),)):
                with self.assertRaises(ValueError):
                    validate_animations(actions, 399, 525)

        def test_frame_duration_and_fifth_repeat(self):
            player = Playback()
            player.update(.099)
            self.assertEqual(player.frame_index, 0)
            player.update(.001)
            self.assertEqual(player.frame_index, 1)
            for _ in range(33):
                player.update(.1)
            self.assertEqual((player.completed_repeats, player.frame_index), (4, 6))
            self.assertFalse(player.holding)
            player.update(.1)
            self.assertTrue(player.holding)
            self.assertEqual(player.completed_repeats, 5)
            self.assertEqual(player.frame_index, 6)

        def test_half_second_hold_and_reset(self):
            player = Playback()
            for _ in range(35):
                player.update(.1)
            last_frame = player.frame
            player.update(.499)
            self.assertTrue(player.holding)
            self.assertEqual(player.frame, last_frame)
            self.assertEqual(player.animation_index, 0)
            player.update(.001)
            self.assertEqual((player.animation_index, player.frame_index,
                              player.completed_repeats, player.holding,
                              player.frame_elapsed, player.hold_elapsed),
                             (1, 0, 0, False, 0, 0))

        def test_single_frame_animation(self):
            player = Playback((ANIMATIONS[2],))
            for repeat in range(5):
                self.assertEqual(player.completed_repeats, repeat)
                player.update(.1)
            self.assertTrue(player.holding)
            player.update(.5)
            self.assertEqual(player.cycles, 1)
            self.assertEqual(player.frame_index, 0)

        def test_two_complete_cycles(self):
            player = Playback()
            for cycle in range(2):
                for index, action in enumerate(ANIMATIONS):
                    self.assertEqual(player.animation_index, index)
                    for _ in range(len(action.frames) * REPEAT_COUNT):
                        player.update(1 / action.fps)
                    self.assertEqual(player.completed_repeats, REPEAT_COUNT)
                    self.assertTrue(player.holding)
                    player.update(.499)
                    self.assertEqual(player.animation_index, index)
                    player.update(.001)
                self.assertEqual(player.cycles, cycle + 1)
                self.assertEqual(player.animation_index, 0)

        def test_different_frame_counts_and_speeds(self):
            f = ANIMATIONS[0].frames[0]
            player = Playback((Animation("느림", (f,), 5),
                               Animation("빠름", (f, f, f), 20)))
            for _ in range(5):
                player.update(.2)
            player.update(.5)
            self.assertEqual(player.animation_index, 1)
            player.update(.025)
            self.assertEqual(player.frame_index, 0)
            player.update(.025)
            self.assertEqual(player.frame_index, 1)
            for _ in range(14):
                player.update(.05)
            self.assertTrue(player.holding)

        def test_long_delay_and_invalid_elapsed_time(self):
            player = Playback()
            player.update(.099)
            player.update(20)
            self.assertEqual(player.frame_index, 1)
            self.assertEqual(player.frame_elapsed, 0)
            player.update(.099)
            self.assertEqual(player.frame_index, 1)
            for value in (-1, math.inf, math.nan):
                with self.assertRaises(ValueError):
                    player.update(value)
            player = Playback((ANIMATIONS[2], ANIMATIONS[1]))
            for _ in range(5):
                player.update(.1)
            player.update(20)
            self.assertEqual(player.animation_index, 1)
            self.assertEqual(player.completed_repeats, 0)
            self.assertEqual(player.frame_elapsed, 0)

        def test_all_frames_fit_at_uniform_scale(self):
            scale, x, y = display_layout(ANIMATIONS)
            frames = [f for a in ANIMATIONS for f in a.frames]
            self.assertAlmostEqual(max(f.height for f in frames) * scale, HEIGHT * DISPLAY_FRACTION)
            for f in frames:
                self.assertGreaterEqual(x - f.anchor_x * scale, 0)
                self.assertLessEqual(x + (f.width - f.anchor_x) * scale, WIDTH)
                self.assertGreaterEqual(y + (f.anchor_y - f.height) * scale, 0)
                self.assertLessEqual(y + f.anchor_y * scale, HEIGHT)

        def test_exit_inputs_during_playback_and_hold(self):
            player = Playback()
            for holding in (False, True):
                player.holding = holding
                self.assertTrue(quit_requested([SimpleNamespace(type=p.SDL_QUIT)]))
                self.assertTrue(quit_requested([
                    SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_ESCAPE)]))
                self.assertFalse(quit_requested([
                    SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_SPACE)]))
                self.assertFalse(quit_requested([]))

        def test_motion_speeds_and_stationary_actions(self):
            layout = display_layout(ANIMATIONS)
            moving = {a.name for a in ANIMATIONS if a.movement_speed}
            self.assertEqual(moving, {"걷기", "가속", "몸 회전", "공 회전", "달리기", "빠른 달리기"})
            for action in ANIMATIONS:
                player = Playback((action,), layout)
                start = player.position_x
                player.update(.05)
                self.assertAlmostEqual(player.position_x - start, action.movement_speed * .05)
                self.assertEqual(player.direction, 1)
            self.assertLess(WALK_SPEED, RUN_SPEED)
            self.assertLess(RUN_SPEED, FAST_RUN_SPEED)

        def test_reflection_and_all_moving_frame_bounds(self):
            self.assertEqual(reflected_movement(95, 1, 10, 0, 100), (95, -1))
            self.assertEqual(reflected_movement(5, -1, 10, 0, 100), (5, 1))
            self.assertEqual(reflected_movement(20, -1, 250, 0, 100), (30, 1))
            layout = display_layout(ANIMATIONS)
            scale = layout[0]
            for action in ANIMATIONS:
                if not action.movement_speed:
                    continue
                left, right = movement_bounds(action, layout)
                for position in (left, (left + right) / 2, right):
                    for direction in (-1, 1):
                        for f in action.frames:
                            center = position + direction * (f.width / 2 - f.anchor_x) * scale
                            self.assertGreaterEqual(center - f.width * scale / 2,
                                                    MOVEMENT_MARGIN - 1e-9)
                            self.assertLessEqual(center + f.width * scale / 2,
                                                 WIDTH - MOVEMENT_MARGIN + 1e-9)
                player = Playback((action,), layout)
                directions = set()
                for _ in range(200):
                    player.update(.025)
                    directions.add(player.direction)
                    self.assertGreaterEqual(player.position_x, left)
                    self.assertLessEqual(player.position_x, right)
                self.assertIn(-1, directions)

        def test_motion_stops_during_hold_and_resets_between_actions(self):
            layout = display_layout(ANIMATIONS)
            player = Playback((ANIMATIONS[4], ANIMATIONS[0]), layout)
            for _ in range(len(player.animation.frames) * REPEAT_COUNT):
                player.update(.1)
            self.assertTrue(player.holding)
            final_position, final_direction = player.position_x, player.direction
            player.update(.499)
            self.assertEqual((player.position_x, player.direction), (final_position, final_direction))
            player.update(.001)
            self.assertEqual(player.animation_index, 1)
            self.assertEqual((player.position_x, player.direction), (layout[1], 1))
            player.update(.1)
            self.assertEqual(player.position_x, layout[1])
            player = Playback((ANIMATIONS[4],), layout)
            player.update(20)
            self.assertAlmostEqual(player.position_x - layout[1], WALK_SPEED / ANIMATIONS[4].fps)

        def test_rendering_faces_movement_direction(self):
            calls = []
            sheet = SimpleNamespace(h=525,
                                    clip_draw=lambda *args: calls.append(("normal", args)),
                                    clip_composite_draw=lambda *args: calls.append(("flipped", args)))
            frame = ANIMATIONS[4].frames[0]
            layout = display_layout(ANIMATIONS)
            draw_frame(sheet, frame, layout, 400, 1)
            draw_frame(sheet, frame, layout, 400, -1)
            self.assertEqual(calls[0][0], "normal")
            self.assertEqual(calls[1][0], "flipped")
            self.assertEqual(calls[1][1][5], "h")
            self.assertAlmostEqual(calls[0][1][4] + calls[1][1][6], 800)

        def test_start_animation_preserves_full_cycle(self):
            self.assertIs(ordered_animations(), ANIMATIONS)
            actions = ordered_animations("걷기")
            self.assertEqual(actions[0].name, "걷기")
            self.assertEqual(len(actions), 15)
            self.assertEqual(sum(len(a.frames) for a in actions), 76)
            self.assertEqual(set(a.name for a in actions), set(a.name for a in ANIMATIONS))
            with self.assertRaises(ValueError):
                ordered_animations("없는 동작")

        def test_title_distinguishes_movement_and_hold(self):
            player = Playback()
            self.assertIn("제자리 동작", viewer_title(player))
            player = Playback(ordered_animations("걷기"))
            self.assertIn("걷기 | 오른쪽 이동", viewer_title(player))
            player.direction = -1
            self.assertIn("왼쪽 이동", viewer_title(player))
            player.holding = True
            self.assertIn("0.5초 대기", viewer_title(player))

        def test_trails_expire_and_stop_with_animation(self):
            player = Playback(ordered_animations("빠른 달리기"))
            player.update(.05)
            self.assertEqual(len(player.trails), 1)
            for _ in range(10):
                player.update(.05)
                self.assertLessEqual(len(player.trails), MAX_TRAILS)
                self.assertTrue(all(age < TRAIL_LIFETIME for _, _, _, age in player.trails))
            while not player.holding:
                player.update(.05)
            self.assertEqual(player.trails, [])
            position = player.position_x
            player.update(.49)
            self.assertEqual(player.trails, [])
            self.assertEqual(player.position_x, position)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ViewerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("순환 횟수는 1 이상의 정수여야 합니다.")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description="소닉 동작을 5회 재생하고 0.5초 대기하는 뷰어")
    parser.add_argument("--self-test", action="store_true", help="창 없이 내부 검증 실행")
    parser.add_argument("--cycles", type=positive_integer, help="지정한 전체 순환 횟수 후 종료")
    parser.add_argument("--start-animation", choices=[a.name for a in ANIMATIONS],
                        help="선택한 동작부터 시작하여 전체 순서를 순환")
    args = parser.parse_args(argv)
    return self_test() if args.self_test else run_viewer(args.cycles, start_animation=args.start_animation)


if __name__ == "__main__":
    raise SystemExit(main())
