from settings import *
from abc import ABCMeta, abstractmethod


class Entity(pg.sprite.Sprite):
    __metaclass__ = ABCMeta

    def __init__(self, pos, frames: dict[str, list[pg.Surface]], state: str, shadow: pg.Surface, alert: pg.Surface, groups) -> None:
        super().__init__(groups)

        self.screen = pg.display.get_surface()

        self.frame_index = 0
        self.frames = frames

        self.state = state
        self.direction = vector()

        self.image = self.frames[self.get_state()][self.frame_index]
        self.rect = self.image.get_frect(center=pos)

        self.shadow = shadow
        self.alert = alert

        self.z = WorldLayer.main
        self.hitbox = self.rect.inflate(-(self.rect.width / 2), -60)

    @abstractmethod
    def draw(self, offset: vector) -> None:
        return

    def get_state(self):
        moving = bool(self.direction)

        if not moving:
            return f'{self.state}_idle'

        return self.state

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt

        state = self.get_state()
        if self.frame_index > len(self.frames[state]):
            self.frame_index = 0

        index = int(self.frame_index) % len(self.frames[state])
        self.image = self.frames[state][index]

    def get_y_sort(self) -> float:
        return self.rect.centery

    def face_target_pos(self, target_pos: tuple[float, float]) -> None:
        relation = vector(target_pos) - vector(self.rect.center)

        # this is using the rect since a y less than 30 means player is either
        # left or right. this is true since the rect is taller but its width
        # is shorter
        if abs(relation.y) < 30:
            self.state = 'right' if relation.x > 0 else 'left'
        else:
            self.state = 'down' if relation.y > 0 else 'up'
