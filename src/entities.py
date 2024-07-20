from typing import Any
from settings import *


class Player(pg.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)
        self.image = pg.Surface((100, 100))
        self.image.fill('blue')
        self.rect = self.image.get_frect(center=pos)

        self.direction = vector()

    def _input(self):
        keys = pg.key.get_pressed()
        input_vector = vector()

        if keys[pg.K_UP]:
            input_vector.y -= 1

        if keys[pg.K_DOWN]:
            input_vector.y += 1

        if keys[pg.K_LEFT]:
            input_vector.x -= 1

        if keys[pg.K_RIGHT]:
            input_vector.x += 1

        self.direction = input_vector

    def move(self, dt: float):
        self.rect.center += self.direction * 250 * dt

    def update(self, dt: float) -> None:
        self._input()
        self.move(dt)
