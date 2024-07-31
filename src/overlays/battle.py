from settings import *
from monster import Monster
from sprites.monster import MonsterSprite


class Battle:
    def __init__(
        self, player_monsters: list[Monster], enemy_monsters: list[Monster],
        monster_frames: dict[str, dict[str, list[pg.Surface]]], bg_surf: pg.Surface,
        fonts: dict[str, pg.Font]
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monster_data = {
            PLAYER: player_monsters,
            ENEMY: enemy_monsters
        }
        self.monster_frames = monster_frames
        self.bg_surf = bg_surf
        self.fonts = fonts

        self.player_sprites = pg.sprite.Group()
        self.battle_sprites = pg.sprite.Group()
        self.enemy_sprites = pg.sprite.Group()

        self.setup()

    def setup(self) -> None:
        for entity in (PLAYER, ENEMY):
            for index, monster in enumerate(self.monster_data[entity][:3]):
                # we use id as index
                self.create_monster(index, monster, index, entity)

    def create_monster(self, id: int, monster: Monster, pos_index: int, entity: str) -> None:
        frames = self.monster_frames[monster.name]
        groups = [self.battle_sprites]
        pos = NEW_BATTLE_POSITIONS[entity][pos_index]

        if entity == PLAYER:
            groups.append(self.player_sprites)
        else:
            groups.append(self.enemy_sprites)

        MonsterSprite(id, pos, frames, entity, groups)

    def update(self, dt: float) -> None:
        self.screen.blit(self.bg_surf, (0, 0))

        self.battle_sprites.update(dt)
        self.battle_sprites.draw(self.screen)
