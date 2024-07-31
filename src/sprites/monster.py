from settings import *
from random import uniform


class MonsterSprite(pg.sprite.Sprite):
    def __init__(self, id: int, pos: tuple[float, float], frames: dict[str, list[pg.Surface]], entity: str, groups) -> None:
        super().__init__(groups)

        self.id = id
        self.frames = frames
        self.frame_index = 0
        self.state = 'idle'
        self.entity = entity
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)

        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def frame_length(self) -> int:
        return len(self.frames[self.state])

    def animate(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt

        if self.frame_index > self.frame_length():
            self.frame_index = 0

        self.image = self.frames[self.state][
            int(self.frame_index) % self.frame_length()
        ]

    def update(self, dt: float) -> None:
        self.animate(dt)
