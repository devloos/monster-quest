from settings import *
from util.support import calculate_monster_outlines, flip_surfaces
from monster import Monster
from sprites.battle_monster import BattleMonster
from game_data import ATTACK_DATA
from util.draw import draw_bar
from random import randint


class SelectionMode(IntEnum):
    General = 0,
    Monster = 1,
    Attacks = 2,
    Switch = 3,
    Target = 4


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
        ui_icons: dict[str, pg.Surface], attack_frames: dict[str, pg.Surface],
        bg_surf: pg.Surface, fonts: dict[str, pg.Font]
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monster_data = {
            PLAYER: player_monsters,
            ENEMY: enemy_monsters
        }
        self.monster_frames = monster_frames
        self.ui_icons = ui_icons
        self.attack_frames = attack_frames
        self.bg_surf = bg_surf
        self.fonts = fonts

        self.player_sprites = BattleGroup()
        self.battle_sprites = BattleGroup()
        self.enemy_sprites = BattleGroup()

        self.current_monster: BattleMonster | None = None
        self.selection_mode: SelectionMode | None = None
        self.selection_side = 'player'
        self.ability_data: dict | None = None
        self.indexes = {
            SelectionMode.General: 0,
            SelectionMode.Monster: 0,
            SelectionMode.Attacks: 0,
            SelectionMode.Switch: 0,
            SelectionMode.Target: 0,
        }

        self.monster_outlines = calculate_monster_outlines(self.monster_frames, 4)

        self.setup()

    def setup(self) -> None:
        for entity in (PLAYER, ENEMY):
            for index, monster in enumerate(self.monster_data[entity][:3]):
                # we use id as index
                self.create_battle_monster(index, monster, index, entity)

    def create_battle_monster(self, id: int, monster: Monster, pos_index: int, entity: str) -> BattleMonster:
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

        BattleMonster(
            id, pos, monster, frames, self.attack_frames, outlines, entity, self.fonts, groups
        )

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

                if battle_monster in self.player_sprites:
                    self.selection_mode = SelectionMode.General

    def available_monsters(self) -> list[Monster]:
        available_monsters = []
        battle_monsters = []

        battle_monster: BattleMonster

        for battle_monster in self.player_sprites.sprites():
            battle_monsters.append(battle_monster.monster)

        for monster in self.monster_data[PLAYER]:
            if monster.health <= 0 or monster in battle_monsters:
                continue

            available_monsters.append(monster)

        return available_monsters

    def draw_general(self) -> None:
        for index, data in enumerate(BATTLE_CHOICES['full'].values()):
            ui_name = data['icon']
            if index == self.indexes[SelectionMode.General]:
                ui_name += '_highlight'

            icon_surf = self.ui_icons[ui_name]
            icon_rect = icon_surf.get_frect(
                center=self.current_monster.main_rect.midright + data['offset']
            )
            self.screen.blit(icon_surf, icon_rect)

    def draw_attacks(self) -> None:
        abilities = self.current_monster.monster.get_abilities(account_ep=True)
        visible_attacks = 4
        rect_height = 220
        rect_width = 180
        item_height = rect_height / visible_attacks

        rect = pg.FRect((0, 0), (rect_width, rect_height))
        rect.midleft = self.current_monster.main_rect.midright + vector(10, 0)

        starting_index = 0

        if self.indexes[SelectionMode.Attacks] >= visible_attacks:
            starting_index = self.indexes[SelectionMode.Attacks] - visible_attacks + 1

        for index, ability in enumerate(abilities[starting_index:], starting_index):
            visible_index = index - starting_index

            item_rect = pg.FRect(
                rect.left, rect.top + visible_index * item_height, rect_width, item_height
            )

            if not item_rect.colliderect(rect):
                continue

            bg_color = COLORS['battle-light'] if index == self.indexes[SelectionMode.Attacks] else COLORS['battle']

            divider_rect = pg.FRect((0, 0), (rect_width, 1))
            divider_rect.bottomleft = item_rect.bottomleft

            if item_rect.collidepoint(rect.midtop):
                pg.draw.rect(
                    self.screen, bg_color, item_rect,
                    border_top_left_radius=5, border_top_right_radius=5
                )
                pg.draw.rect(self.screen, COLORS['dark'], divider_rect)
            elif item_rect.collidepoint(rect.midbottom + vector(0, -1)):
                pg.draw.rect(
                    self.screen, bg_color, item_rect,
                    border_bottom_left_radius=5, border_bottom_right_radius=5
                )
            else:
                pg.draw.rect(self.screen, bg_color, item_rect)
                pg.draw.rect(self.screen, COLORS['dark'], divider_rect)

            ability_surf = self.fonts['regular'].render(ability, False, COLORS['dark'])
            ability_rect = ability_surf.get_rect(topleft=item_rect.topleft + vector(8, 3))
            self.screen.blit(ability_surf, ability_rect)

            ability_data = ATTACK_DATA[ability]

            element_surf = self.fonts['small'].render(
                ability_data['element'], False, COLORS['dark']
            )
            element_rect = element_surf.get_rect()

            element_bg_rect = element_rect.copy().inflate(15, 3)
            element_bg_rect.topleft = ability_rect.bottomleft + vector(-1, 2)
            element_rect.center = element_bg_rect.center

            pg.draw.rect(
                self.screen, COLORS[ability_data['element']],
                element_bg_rect, border_radius=5
            )
            self.screen.blit(element_surf, element_rect)

            ep_cost_surf = self.fonts['small'].render(
                f'ep: {ability_data['cost']}', False, COLORS['dark']
            )
            ep_cost_rect = ep_cost_surf.get_rect()
            ep_cost_rect.bottomright = item_rect.bottomright + vector(-8, -3)
            self.screen.blit(ep_cost_surf, ep_cost_rect)

    def draw_switch(self) -> None:
        visible_monsters = 4
        rect_height = 275
        rect_width = 200
        item_height = rect_height / visible_monsters

        rect = pg.FRect((0, 0), (rect_width, rect_height))
        rect.midleft = self.current_monster.main_rect.midright + vector(10, 0)

        starting_index = 0

        if self.indexes[SelectionMode.Switch] >= visible_monsters:
            starting_index = self.indexes[SelectionMode.Switch] - visible_monsters + 1

        monster: Monster

        for index, monster in enumerate(self.available_monsters()[starting_index:], starting_index):
            visible_index = index - starting_index

            item_rect = pg.FRect(
                rect.left, rect.top + item_height * visible_index, rect_width, item_height
            )

            if not item_rect.colliderect(rect):
                continue

            bg_color = COLORS['battle']
            text_color = COLORS['dark']

            if index == self.indexes[SelectionMode.Switch]:
                bg_color = COLORS['battle-light']
                text_color = COLORS['red']

            divider_rect = pg.FRect((0, 0), (rect_width, 1))
            divider_rect.bottomleft = item_rect.bottomleft

            if item_rect.collidepoint(rect.midtop):
                pg.draw.rect(
                    self.screen, bg_color, item_rect,
                    border_top_left_radius=5, border_top_right_radius=5
                )
                pg.draw.rect(self.screen, COLORS['dark'], divider_rect)
            elif item_rect.collidepoint(rect.midbottom + vector(0, -1)):
                pg.draw.rect(
                    self.screen, bg_color, item_rect,
                    border_bottom_left_radius=5, border_bottom_right_radius=5
                )
            else:
                pg.draw.rect(self.screen, bg_color, item_rect)
                pg.draw.rect(self.screen, COLORS['dark'], divider_rect)

            icon_surf = pg.transform.scale(monster.icon, (35, 35))
            icon_rect = icon_surf.get_frect(midleft=item_rect.midleft + vector(8, 0))

            self.screen.blit(icon_surf, icon_rect)

            name_surf = self.fonts['small'].render(
                f'{monster.name} ({monster.level})', False, text_color
            )
            name_rect = name_surf.get_rect(
                topleft=icon_rect.topright + vector(18, -8),
            )
            self.screen.blit(name_surf, name_rect)

            health_bar_rect = pg.FRect(
                (name_rect.bottomleft + vector(0, 5)), (rect_width * 0.5, 3)
            )

            draw_bar(
                self.screen, health_bar_rect, monster.health,
                monster.get_stat('max_health'), COLORS['dark'], COLORS['red']
            )

            energy_bar_rect = pg.FRect(
                (health_bar_rect.bottomleft + vector(0, 3)), (rect_width * 0.5, 3)
            )

            draw_bar(
                self.screen, energy_bar_rect, monster.energy,
                monster.get_stat('max_energy'), COLORS['dark'], COLORS['blue']
            )

    def draw_ui(self) -> None:
        if not self.current_monster:
            return

        match self.selection_mode:
            case SelectionMode.General:
                self.draw_general()

            case SelectionMode.Attacks:
                self.draw_attacks()

            case SelectionMode.Switch:
                self.draw_switch()

    def reset_selection(self, selection: SelectionMode) -> None:
        self.current_monster.set_highlight(False)
        self.current_monster = None
        self.indexes[selection] = 0
        self.selection_mode = None
        self.ability_data = None
        self.update_battle_monsters('resume')

    def selected_general_option(self) -> None:
        ATTACKS = 0
        DEFEND = 1
        SWITCH = 2
        CATCH = 3

        index = self.indexes[SelectionMode.General]

        if index == ATTACKS:
            self.selection_mode = SelectionMode.Attacks
        elif index == DEFEND:
            self.reset_selection(SelectionMode.General)
        elif index == SWITCH:
            self.selection_mode = SelectionMode.Switch
        elif index == CATCH:
            self.selection_mode = SelectionMode.Target

    def reset_monster_highlight(self, battle_monsters: list[BattleMonster]) -> None:
        for battle_monster in battle_monsters:
            battle_monster.set_highlight(False, False)

    def input(self) -> None:
        if self.current_monster == None or self.selection_mode == None:
            return

        length = 0

        match self.selection_mode:
            case SelectionMode.General:
                length = len(BATTLE_CHOICES['full'])

            case SelectionMode.Attacks:
                length = len(self.current_monster.monster.get_abilities(account_ep=True))

            case SelectionMode.Switch:
                length = len(self.available_monsters())

            case SelectionMode.Target:
                battle_monsters: list[BattleMonster]

                if self.selection_side == 'enemy':
                    battle_monsters = self.enemy_sprites.sprites()
                else:
                    battle_monsters = self.player_sprites.sprites()

                length = len(battle_monsters)

                # reset highlight
                self.reset_monster_highlight(battle_monsters)

                index = self.indexes[SelectionMode.Target]
                battle_monsters[index].set_highlight(True, False)

        keys = pg.key.get_just_pressed()

        if keys[pg.K_DOWN]:
            self.indexes[self.selection_mode] += 1

        if keys[pg.K_UP]:
            self.indexes[self.selection_mode] -= 1

        self.indexes[self.selection_mode] %= length

        if keys[pg.K_SPACE]:
            if self.selection_mode == SelectionMode.Target:
                if self.ability_data != None:
                    battle_monsters: list[BattleMonster] = self.enemy_sprites.sprites()
                    enemy_monster = battle_monsters[self.indexes[SelectionMode.Target]]

                    self.current_monster.animate_attack()
                    enemy_monster.animate_attacked(self.ability_data['animation'])

                    attack_multiplier = self.current_monster.monster.get_stat('attack')
                    amount = self.ability_data['amount'] * attack_multiplier

                    enemy_monster.monster.health -= amount

                    self.current_monster.monster.energy -= self.ability_data['cost']

                    enemy_monster.set_highlight(False, False)
                    self.indexes[SelectionMode.Target] = 0

                self.reset_selection(SelectionMode.Attacks)

            if self.selection_mode == SelectionMode.Attacks:
                abilities = self.current_monster.monster.get_abilities(account_ep=True)
                ability = abilities[self.indexes[SelectionMode.Attacks]]
                self.ability_data = ATTACK_DATA[ability]

                self.selection_mode = SelectionMode.Target
                self.selection_side = self.ability_data['target']

            if self.selection_mode == SelectionMode.Switch:
                id = self.current_monster.id
                monsters = self.available_monsters()
                self.create_battle_monster(
                    id, monsters[self.indexes[SelectionMode.Switch]], id, PLAYER
                )
                self.current_monster.kill()

                self.reset_selection(SelectionMode.Switch)

            if self.selection_mode == SelectionMode.General:
                self.selected_general_option()

        # testing but could become useful feature
        if keys[pg.K_ESCAPE]:
            self.selection_mode = SelectionMode.General
            self.indexes[SelectionMode.General] = 0
            self.ability_data = None
            self.selection_side = 'player'
            self.reset_monster_highlight(self.player_sprites.sprites())
            self.reset_monster_highlight(self.battle_sprites.sprites())
            self.current_monster.set_highlight(True, False)

    def update(self, dt: float) -> None:
        self.input()
        self.battle_sprites.update(dt)
        self.check_active()

        self.screen.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw()
        self.draw_ui()
