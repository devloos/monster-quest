from game_data import MONSTER_DATA
from util.support import import_image


class Monster:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level

        self.element = MONSTER_DATA[self.name]['stats']['element']
        self.base_stats = MONSTER_DATA[self.name]['stats']

        self.icon = import_image('graphics', 'icons', self.name)
