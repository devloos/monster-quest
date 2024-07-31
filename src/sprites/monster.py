from typing import Any
from settings import *


class MonsterSprite(pg.sprite.Sprite):
    def __init__(self, id: int, pos: tuple[float, float], frames: dict[str, list[pg.Surface]], entity: str, groups) -> None:
        super().__init__(groups)

        self.id = id
        self.frames = frames
        self.frame_index = 0
        self.state = 'idle'
        self.entity = entity

        self.compute_image()
        self.rect = self.image.get_rect(center=pos)

    def frame_length(self) -> int:
        return len(self.frames[self.state])

    def compute_image(self):
        self.image = self.frames[self.state][
            int(self.frame_index) % self.frame_length()
        ]

        if self.entity == PLAYER:
            self.image = pg.transform.flip(self.image, True, False)

    def update(self, dt: float) -> None:
        self.frame_index += ANIMATION_SPEED * dt

        if self.frame_index > self.frame_length():
            self.frame_index = 0

        self.compute_image()
