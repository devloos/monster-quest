from settings import *
from monster import Monster
from sprites.battle_monster import BattleMonster


class BattleGroup(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()

    def draw(self) -> None:
        sprite: BattleMonster

        for sprite in self:
            sprite.draw()


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

        self.player_sprites = BattleGroup()
        self.battle_sprites = BattleGroup()
        self.enemy_sprites = BattleGroup()

        self.setup()

    def setup(self) -> None:
        for entity in (PLAYER, ENEMY):
            for index, monster in enumerate(self.monster_data[entity][:3]):
                # we use id as index
                self.create_monster(index, monster, index, entity)

    def create_monster(self, id: int, monster: Monster, pos_index: int, entity: str) -> None:
        frames: dict[str, list[pg.Surface]] = self.monster_frames[monster.name]
        groups = [self.battle_sprites]
        pos = NEW_BATTLE_POSITIONS[entity][pos_index]

        if entity == PLAYER:
            groups.append(self.player_sprites)

            state: str
            frame_surfs: list[pg.Surface]
            for state, frame_surfs in self.monster_frames[monster.name].items():
                frames[state] = []

                for frame_surf in frame_surfs:
                    frames[state].append(
                        pg.transform.flip(frame_surf, True, False)
                    )
        else:
            groups.append(self.enemy_sprites)

        BattleMonster(id, pos, monster, frames, entity, self.fonts, groups)

    def update(self, dt: float) -> None:
        self.screen.blit(self.bg_surf, (0, 0))

        self.battle_sprites.update(dt)
        self.battle_sprites.draw()
