from pico2d import *

open_canvas()

grass = load_image('grass.png')
character = load_image('animation_sheet.png')

# fill here
frame =0


# 왼쪽 달리기

for x in range(800, 0, -50):
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(
       frame * 100, 0,  # 1. 원본 이미지의 어디서 자를지 (x, y)
        100, 100,       # 2. 얼마나 자를지 (가로, 세로)
        x, 90,          # 4. 화면 어디에 그릴지 (중심 x, y)
        
    )
    update_canvas()

    frame = (frame + 1) % 8
    delay(0.1)


# 오른쪽 달리기

for x in range(0, 800, 50):
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(
       frame * 100, 100,  # 1. 원본 이미지의 어디서 자를지 (x, y)
        100, 100,       # 2. 얼마나 자를지 (가로, 세로)
        x, 90,          # 4. 화면 어디에 그릴지 (중심 x, y)
        
    )
    update_canvas()

    frame = (frame + 1) % 8
    delay(0.1)



# for x in range(0, 800, 5):
#     clear_canvas()
#     grass.draw(400, 30)
#     character.clip_composite_draw(
#        frame * 100, 0,  # 1. 원본 이미지의 어디서 자를지 (x, y)
#         100, 100,       # 2. 얼마나 자를지 (가로, 세로)
#         0, 'h',         # 3. 회전 각도와 뒤집기
#         x, 90,          # 4. 화면 어디에 그릴지 (중심 x, y)
#         200, 200        # 5. 화면에 얼마나 크게 그릴지 (가로, 세로)
#     )
#     update_canvas()

#     frame = (frame + 1) % 8
#     delay(0.1)


close_canvas()

