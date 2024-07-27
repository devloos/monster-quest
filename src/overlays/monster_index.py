from settings import *
from monster import Monster


class MonsterIndex:
    def __init__(self, monsters: list[Monster], fonts: list[pg.Font]) -> None:
        self.screen = pg.display.get_surface()
        self.monsters = monsters
        self.fonts = fonts

    def update(self, dt) -> None:
        pass
