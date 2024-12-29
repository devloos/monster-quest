from src.settings import *
from pygame import Surface
from src.textures.texture import Texture


class AnimatedTexture(Texture):
    def __init__(self, pos: tuple[float, float], frames: list[Surface], z: WorldLayer, groups) -> None:
        if len(frames) == 0:
            raise Exception('Frames array needed.')

        super().__init__(pos, frames[0], z, groups)

        self.frames = frames
        self.frame_index = 0

    def animate(self, dt) -> None:
        self.frame_index += ANIMATION_SPEED * dt

        if self.frame_index > len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt) -> None:
        self.animate(dt)
