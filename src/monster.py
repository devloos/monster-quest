from game_data import MONSTER_DATA
from util.imports import import_image
from random import randint


class Monster:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level

        self.element = MONSTER_DATA[self.name]['stats']['element']
        self.base_stats = MONSTER_DATA[self.name]['stats']
        self.health = self.base_stats['max_health'] * self.level
        self.health -= randint(0, 150)

        self.energy = self.base_stats['max_energy'] * self.level
        self.energy -= randint(0, 50)

        self.xp = randint(0, 1000)
        self.level_up = self.level * 150

        self.icon = import_image('graphics', 'icons', self.name)

    def get_stat(self, stat: str) -> float:
        return self.base_stats[stat] * self.level
