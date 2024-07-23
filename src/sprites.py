from typing import Any
from pygame import Surface
from settings import *


class Sprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], surf: Surface, z: WorldLayer, groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.z = z

    def get_y_sort(self) -> float:
        return self.rect.centery


class MonsterPatchSprite(Sprite):
    def __init__(self, pos: tuple[float, float], surf: Surface, z: WorldLayer, biome: str, groups) -> None:
        super().__init__(pos, surf, z, groups)
        self.biome = biome

    def get_y_sort(self) -> float:
        return self.rect.centery - 40


class AnimatedSprite(Sprite):
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
