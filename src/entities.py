from settings import *


class Player(pg.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)
        self.image = pg.Surface((100, 100))
        self.image.fill('blue')
        self.rect = self.image.get_frect(center=pos)
