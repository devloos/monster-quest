from settings import *
from util.support import calculate_monster_outlines, flip_surfaces
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
        monster_frames: dict[str, dict[str, list[pg.Surface]]],
        ui_icons: dict[str, pg.Surface], bg_surf: pg.Surface, fonts: dict[str, pg.Font]
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monster_data = {
            PLAYER: player_monsters,
            ENEMY: enemy_monsters
        }
        self.monster_frames = monster_frames
        self.ui_icons = ui_icons
        self.bg_surf = bg_surf
        self.fonts = fonts

        self.player_sprites = BattleGroup()
        self.battle_sprites = BattleGroup()
        self.enemy_sprites = BattleGroup()

        self.current_monster: BattleMonster | None = None

        self.monster_outlines = calculate_monster_outlines(self.monster_frames, 4)

        self.setup()

    def setup(self) -> None:
        for entity in (PLAYER, ENEMY):
            for index, monster in enumerate(self.monster_data[entity][:3]):
                # we use id as index
                self.create_monster(index, monster, index, entity)

    def create_monster(self, id: int, monster: Monster, pos_index: int, entity: str) -> None:
        frames: dict[str, list[pg.Surface]] = self.monster_frames[monster.name]
        outlines: dict[str, list[pg.Surface]] = self.monster_outlines[monster.name]
        groups = [self.battle_sprites]
        pos = NEW_BATTLE_POSITIONS[entity][pos_index]

        if entity == PLAYER:
            groups.append(self.player_sprites)

            for state, surfs in frames.items():
                frames[state] = flip_surfaces(surfs, True, False)

            for state, surfs in outlines.items():
                outlines[state] = flip_surfaces(surfs, True, False)

        else:
            groups.append(self.enemy_sprites)

        BattleMonster(id, pos, monster, frames, outlines, entity, self.fonts, groups)

    def update_battle_monsters(self, option) -> None:
        paused = True if option == 'pause' else False

        battle_monster: BattleMonster
        for battle_monster in self.battle_sprites.sprites():
            battle_monster.monster.paused = paused

    def check_active(self) -> None:
        battle_monster: BattleMonster
        for battle_monster in self.battle_sprites.sprites():
            if battle_monster.monster.recharge >= 100:
                self.update_battle_monsters('pause')
                battle_monster.monster.recharge = 0
                battle_monster.set_highlight(True)
                self.current_monster = battle_monster

    def update(self, dt: float) -> None:
        self.battle_sprites.update(dt)
        self.check_active()

        self.screen.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw()
