from settings import *
from pygame import Surface
from textures.texture import Texture


class MonsterPatchTexture(Texture):
    def __init__(self, pos: tuple[float, float], surf: Surface, z: WorldLayer, biome: str, groups) -> None:
        super().__init__(pos, surf, z, groups)
        self.biome = biome

    def get_y_sort(self) -> float:
        return self.rect.centery - 40
