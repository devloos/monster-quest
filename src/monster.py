from src.game_data import MONSTER_DATA
from src.util.imports import import_image
from random import randint
from src.game_data import ABILITY_DATA


class Monster:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level

        self.element = MONSTER_DATA[self.name]['stats']['element']
        self.base_stats = MONSTER_DATA[self.name]['stats']
        self.abilities: dict[int, str] = MONSTER_DATA[self.name]['abilities']
        self.health = self.base_stats['max_health'] * self.level
        self.energy = self.base_stats['max_energy'] * self.level

        self.recharge = 0
        self.paused = False

        self.xp = 0
        self.level_up = self.level * 150

        self.evolution: dict | None = None

        if MONSTER_DATA[self.name]['evolve']:
            self.evolution = {
                'name': MONSTER_DATA[self.name]['evolve'][0],
                'level': MONSTER_DATA[self.name]['evolve'][1]
            }

        self.icon = import_image('graphics', 'icons', self.name)

    def __repr__(self) -> str:
        return f'{self.name} - {self.level}'

    def get_stat(self, stat: str) -> float:
        return self.base_stats[stat] * self.level

    def get_stats(self) -> dict[str, float]:
        return {
            'health': self.get_stat('max_health'),
            'energy': self.get_stat('max_energy'),
            'attack': self.get_stat('attack'),
            'defense': self.get_stat('defense'),
            'speed': self.get_stat('speed'),
            'recovery': self.get_stat('recovery'),
        }

    def get_abilities(self, account_ep=False) -> list[str]:
        available_abilities = []

        for lvl, name in self.abilities.items():
            if self.level >= lvl:
                available_abilities.append(name)

            if account_ep and self.energy < ABILITY_DATA[name]['cost']:
                available_abilities.pop()

        return available_abilities

    def should_evolve(self) -> bool:
        if self.evolution == None:
            return False

        return self.level >= self.evolution['level']

    def update_xp(self, amount: float) -> None:
        # should we level up
        if self.xp + amount > self.level_up:
            self.level += 1
            overflow_amount = (self.xp + amount) - self.level_up
            self.xp = overflow_amount
            self.level_up = self.level * 150
        else:
            self.xp += amount

    def limit_stats(self) -> None:
        self.health = max(0, min(self.health, self.get_stat('max_health')))
        self.energy = max(0, min(self.energy, self.get_stat('max_energy')))

    def update(self, dt: float) -> None:
        self.limit_stats()

        if not self.paused:
            self.recharge += self.get_stat('speed') * dt
