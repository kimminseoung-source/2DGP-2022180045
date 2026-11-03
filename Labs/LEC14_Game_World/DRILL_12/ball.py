from pico2d import get_time, load_image

import game_world


class Ball:
    def __init__(self, x, y, face_dir):
        self.x = x + 50 * face_dir
        self.y = y
        self.face_dir = face_dir
        self.image = load_image('ball21x21.png')
        self.created_at = get_time()
        self.life_time = 5.0

    def update(self):
        self.x += 10 * self.face_dir

        if get_time() - self.created_at >= self.life_time:
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)
