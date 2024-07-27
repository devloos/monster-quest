from settings import *
from pygame import Surface
from textures.texture import Texture


class CollidableTexture(Texture):
    def __init__(self, pos: tuple[float, float], surf: Surface, groups) -> None:
        super().__init__(pos, surf, WorldLayer.main, groups)

        # keep width the same and subtract 40 percent of the height
        self.hitbox = self.rect.inflate(0, self.rect.height * -0.5)
