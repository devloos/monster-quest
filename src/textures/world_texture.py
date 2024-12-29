from pygame import Surface
from src.settings import *
from src.textures.texture import Texture


class WorldTransition(Texture):
    def __init__(self, pos: tuple[float, float], size: tuple[float, float], target: tuple, groups) -> None:
        super().__init__(pos, Surface(size), WorldLayer.bg, groups)

        self.target = target
