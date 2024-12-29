from src.settings import *
from pygame import Surface


class Texture(pg.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], surf: Surface, z: WorldLayer, groups) -> None:
        super().__init__(groups)
        self.screen = pg.display.get_surface()
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy()

    def get_y_sort(self) -> float:
        return self.rect.centery

    def draw(self, offset: vector) -> None:
        self.screen.blit(
            self.image, self.rect.topleft + offset
        )
