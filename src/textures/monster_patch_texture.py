from typing import Any
from settings import *
from pygame import Surface
from textures.texture import Texture
from overlays.battle import Battle
from sprites.player import Player
from util.timer import Timer
from monster import Monster


class MonsterPatchTexture(Texture):
    def __init__(
        self, pos: tuple[float, float], surf: Surface, z: WorldLayer, biome: str,
        player: Player, monster_names: list[str], level: int, battle: Battle, groups
    ) -> None:
        super().__init__(pos, surf, z, groups)
        self.biome = biome
        self.player = player
        self.monster_names = monster_names
        self.level = level
        self.battle = battle

        self.timer = Timer(450, True, True, self.check_collision)

    def get_y_sort(self) -> float:
        return self.rect.centery - 50

    def check_collision(self):
        if not self.battle.in_progress and self.rect.colliderect(self.player.hitbox):
            monsters: list[Monster] = []
            for monster_name in self.monster_names:
                monsters.append(Monster(monster_name, self.level))

            self.battle.setup(self.player.monsters, monsters, self.biome)

    def update(self, _) -> None:
        self.timer.update()
