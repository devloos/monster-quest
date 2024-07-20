from pygame import Surface
from settings import *


class Sprite(pg.sprite.Sprite):
    def __init__(self, pos, surf: Surface, groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
