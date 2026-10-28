from pathlib import Path

from pico2d import load_image



class Grass:
    def __init__(self):
        image_path = Path(__file__).resolve().parent.parent / 'grass.png'
        self.image = load_image(str(image_path))

    def draw(self, camera_y=0):
        self.image.draw(400, 30 - camera_y)

    def update(self):
        pass


class Platform:
    image = None

    def __init__(self, left, bottom, right, top):
        self.left, self.bottom = left, bottom
        self.right, self.top = right, top
        if Platform.image is None:
            image_path = Path(__file__).resolve().parent.parent / 'grass.png'
            Platform.image = load_image(str(image_path))

    def get_bb(self):
        return self.left, self.bottom, self.right, self.top

    def draw(self, camera_y=0):
        self.image.draw((self.left + self.right) / 2,
                        (self.bottom + self.top) / 2 - camera_y,
                        self.right - self.left, self.top - self.bottom)

    def update(self):
        pass
