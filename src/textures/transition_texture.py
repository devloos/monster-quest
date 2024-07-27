from pygame import Surface
from settings import *
from settings import WorldLayer
from textures.texture import Texture


class TransitionTexture(Texture):
    def __init__(self, pos: tuple[float, float], size: tuple[float, float], target: tuple, groups) -> None:
        super().__init__(pos, Surface(size), WorldLayer.bg, groups)

        self.target = target
