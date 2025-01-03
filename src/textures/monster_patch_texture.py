from src.settings import *
from pygame import Surface
from src.textures.texture import Texture
from src.overlays.battle import Battle
from src.overlays.transition import Transition
from src.sprites.player import Player
from src.util.timer import Timer
from src.monster import Monster
from random import random


class MonsterPatchTexture(Texture):
    def __init__(
        self, pos: tuple[float, float], surf: Surface, z: WorldLayer, biome: str,
        player: Player, monster_names: list[str], level: int, battle: Battle,
        transition: Transition, groups
    ) -> None:
        super().__init__(pos, surf, z, groups)
        self.biome = biome
        self.player = player
        self.monster_names = monster_names
        self.level = level
        self.battle = battle
        self.transition = transition

        self.timer = Timer(600, True, True, self.check_collision)

    def get_y_sort(self) -> float:
        return self.rect.centery - 50

    def check_collision(self):
        # if moving, no battle, colliding, and random chance
        if self.player.direction and \
           not self.battle.in_progress and \
           self.rect.collidepoint(self.player.rect.midbottom) \
           and random() < 0.2:
            monsters: list[Monster] = []
            for monster_name in self.monster_names:
                monsters.append(Monster(monster_name, self.level))

            self.transition.start(
                lambda: self.battle.setup(self.player, monsters, True, self.biome)
            )

    def update(self, _) -> None:
        self.timer.update()
