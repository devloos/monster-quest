from settings import *
from monster import Monster
from util.draw import draw_bar
from util.imports import import_folder_dict
from game_data import ATTACK_DATA


class MonsterIndex:
    def __init__(
        self, monsters: list[Monster], monster_frames: dict[str, dict[str, list[pg.Surface]]], fonts: dict[str, pg.Font]
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monsters = monsters
        self.monster_frames = monster_frames
        self.ui_icons = import_folder_dict('graphics', 'ui')
        self.fonts = fonts
        self.opened = False

        self.tint = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint.set_alpha(200)

        self.monster_index_rect = pg.FRect(
            0, 0, WINDOW_WIDTH * 0.7, WINDOW_HEIGHT * 0.8
        )
        self.monster_index_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        self.visible_items = 6
        self.item_width = self.monster_index_rect.width * 0.3
        self.item_height = self.monster_index_rect.height / self.visible_items
        self.hovered_index = 0
        self.selected_index: int | None = None
        self.frame_index = 0

    def _input(self) -> None:
        keys = pg.key.get_just_pressed()

        if keys[pg.K_UP]:
            self.hovered_index -= 1

        if keys[pg.K_DOWN]:
            self.hovered_index += 1

        if keys[pg.K_SPACE]:
            if self.selected_index != None:
                temp_monster = self.monsters[self.hovered_index]
                self.monsters[self.hovered_index] = self.monsters[self.selected_index]
                self.monsters[self.selected_index] = temp_monster
                self.selected_index = None
            else:
                self.selected_index = self.hovered_index

        self.hovered_index = self.hovered_index % len(self.monsters)

    def draw_list_element(self, rect: pg.FRect, monster: Monster) -> None:
        # todo: add shadow effect and border
        element = pg.Surface((60, 20), pg.SRCALPHA).convert_alpha()
        element_rect = element.get_frect(
            topleft=rect.bottomleft + vector(0, 10)
        )

        pg.draw.rect(
            element, COLORS[monster.element],
            pg.FRect(0, 0, 60, 20), border_radius=10
        )

        element_text = self.fonts['small'].render(
            monster.element, False, COLORS['black']
        )

        self.screen.blit(element, element_rect)

        self.screen.blit(
            element_text,
            element_text.get_frect(
                center=element_rect.center
            )
        )

    def draw_selected_badge(self, item_rect: pg.FRect) -> None:
        center = item_rect.topright + vector(-16, 13)

        pg.draw.circle(
            self.screen, COLORS['gold'], center, radius=9, width=4
        )

    def draw_monster_name(
        self, item_rect: pg.FRect, monster: Monster, text_color: str
    ) -> tuple[pg.Surface, pg.FRect]:
        monster_name = self.fonts['regular'].render(
            monster.name, False, text_color
        )

        monster_name_rect = monster_name.get_frect(
            topleft=item_rect.topleft + vector(20, 20)
        )

        self.screen.blit(monster_name, monster_name_rect)

        return monster_name, monster_name_rect

    def draw_list_monster(self, item_rect: pg.FRect, monster: Monster) -> None:
        icon_rect = monster.icon.get_frect(
            center=item_rect.midright + vector(-55, 0)
        )

        self.screen.blit(monster.icon, icon_rect)

    def draw_list(self) -> None:

        # draw list background
        bg_rect = pg.Rect(
            self.monster_index_rect.topleft, (self.item_width,
                                              self.monster_index_rect.height)
        )

        pg.draw.rect(
            self.screen, COLORS['gray'], bg_rect,
            border_bottom_left_radius=8, border_top_left_radius=8
        )

        # draw items in list
        start_index = 0

        if self.hovered_index >= self.visible_items:
            start_index = self.hovered_index - self.visible_items + 1

        for index, monster in enumerate(self.monsters[start_index:]):
            top = self.monster_index_rect.top + index * self.item_height
            item_rect = pg.FRect(
                self.monster_index_rect.left, top, self.item_width, self.item_height
            )

            if not item_rect.colliderect(self.monster_index_rect):
                continue

            # colors
            bg_color = COLORS['gray']
            text_color = COLORS['light']

            if self.hovered_index == index + start_index:
                bg_color = COLORS['light']
                text_color = COLORS['gray']

            divider_rect = pg.FRect(0, 0, self.item_width, 2)
            divider_rect.bottomleft = item_rect.bottomleft

            if item_rect.collidepoint(self.monster_index_rect.topleft):
                pg.draw.rect(
                    self.screen, bg_color, item_rect, border_top_left_radius=8
                )
                pg.draw.rect(self.screen, COLORS['light-gray'], divider_rect)
            elif item_rect.collidepoint(self.monster_index_rect.bottomleft + vector(1, -1)):
                # added vector offset to handle bug not detecting the collision
                pg.draw.rect(
                    self.screen, bg_color, item_rect, border_bottom_left_radius=8
                )
            else:
                pg.draw.rect(self.screen, bg_color, item_rect)
                pg.draw.rect(self.screen, COLORS['light-gray'], divider_rect)

            _, monster_name_rect = self.draw_monster_name(
                item_rect, monster, text_color
            )
            self.draw_list_monster(item_rect, monster)
            self.draw_list_element(monster_name_rect, monster)

            if self.selected_index == index + start_index:
                self.draw_selected_badge(item_rect)

        shadow = pg.Surface((4, self.monster_index_rect.height))
        shadow.set_alpha(100)
        self.screen.blit(
            shadow,
            (self.monster_index_rect.left +
             self.item_width - 4, self.monster_index_rect.top)
        )

    def draw_main_level(self, monster: Monster, rect: pg.FRect) -> None:
        level_surf = self.fonts['regular'].render(
            f'lvl: {monster.level}', False, COLORS['white']
        )
        level_rect = level_surf.get_frect(
            bottomleft=rect.bottomleft + vector(10, -16)
        )
        self.screen.blit(level_surf, level_rect)

        draw_bar(
            self.screen, pg.FRect(level_rect.bottomleft, (100, 4)),
            monster.xp, monster.level_up,
            COLORS['dark'], COLORS['white']
        )

    def draw_main_element(self, monster: Monster, rect: pg.FRect) -> None:
        # draw element
        element_surf = self.fonts['regular'].render(
            monster.element, False, COLORS['white']
        )
        element_rect = element_surf.get_frect(
            bottomright=rect.bottomright + vector(-10, -10)
        )
        self.screen.blit(element_surf, element_rect)

    def draw_main_name(self, monster: Monster, rect: pg.FRect) -> None:
        name_surf = self.fonts['bold'].render(
            monster.name, False, COLORS['white']
        )
        name_rect = name_surf.get_frect(
            topleft=rect.topleft + vector(10, 10)
        )
        self.screen.blit(name_surf, name_rect)

    def draw_main_energy_bar(self, monster: Monster, rect: pg.FRect) -> pg.FRect:
        energy_bar_rect = pg.FRect((0, 0), (rect.width * 0.45, 30))
        energy_bar_rect.topright = rect.bottomright + vector(-15, 15)

        draw_bar(
            self.screen, energy_bar_rect,
            monster.energy, monster.get_stat('max_energy'),
            COLORS['black'], COLORS['blue'], 2
        )

        energy_bar_text_surf = self.fonts['regular'].render(
            f'EP: {monster.energy}/{monster.get_stat('max_energy')}',
            False, COLORS['white']
        )
        energy_bar_text_rect = energy_bar_text_surf.get_frect(
            midleft=energy_bar_rect.midleft + vector(10, 0),
        )
        self.screen.blit(energy_bar_text_surf, energy_bar_text_rect)

        return energy_bar_rect

    def draw_main_health_bar(self, monster: Monster, rect: pg.FRect) -> pg.FRect:
        health_bar_rect = pg.FRect(
            rect.left + 15, rect.bottom + 15,
            rect.width * 0.45, 30
        )

        draw_bar(
            self.screen, health_bar_rect,
            monster.health, monster.get_stat('max_health'),
            COLORS['black'], COLORS['red'], 2
        )

        health_bar_text_surf = self.fonts['regular'].render(
            f'HP: {monster.health}/{monster.get_stat('max_health')}',
            False, COLORS['white']
        )
        health_bar_text_rect = health_bar_text_surf.get_frect(
            midleft=health_bar_rect.midleft + vector(10, 0),
        )
        self.screen.blit(health_bar_text_surf, health_bar_text_rect)

        return health_bar_rect

    def draw_main_monster(self, monster: Monster, rect: pg.FRect, dt: float) -> None:
        self.frame_index += ANIMATION_SPEED * dt
        length = len(self.monster_frames[monster.name]['idle'])

        if self.frame_index > length:
            self.frame_index = 0

        monster_surf = self.monster_frames[monster.name]['idle'][
            int(self.frame_index) % length
        ]
        monster_rect = monster_surf.get_frect(center=rect.center)
        self.screen.blit(monster_surf, monster_rect)

    def draw_main_stats(self, monster: Monster, stats_rect: pg.FRect) -> None:
        title_surf = self.fonts['regular'].render(
            'Stats', False, COLORS['white']
        )
        title_rect = title_surf.get_frect(topleft=stats_rect.topleft)
        self.screen.blit(title_surf, title_rect)

        monster_stats = monster.get_stats()
        normalized_stats_height = stats_rect.height - title_rect.height
        stat_height = normalized_stats_height / len(monster_stats)

        for index, (stat, value) in enumerate(monster_stats.items()):
            item_rect = pg.FRect(
                stats_rect.left, title_rect.bottom + stat_height * index,
                stats_rect.width, stat_height
            )

            # icon
            icon_surf = self.ui_icons[stat]
            icon_rect = icon_surf.get_frect(
                midleft=item_rect.midleft + vector(8, 0)
            )
            self.screen.blit(icon_surf, icon_rect)

            # text
            stat_text = self.fonts['regular'].render(
                stat, False, COLORS['white']
            )
            stat_text_rect = stat_text.get_frect(
                top=item_rect.top,
                left=icon_rect.right + 25
            )
            self.screen.blit(stat_text, stat_text_rect)

            # bar
            stat_bar_rect = pg.FRect(
                (stat_text_rect.bottomleft + vector(0, 2)),
                (item_rect.width - icon_rect.width - 33, 4)
            )

            # max stat defines the potential a monster
            # can reach, it is a setting var in settings
            draw_bar(
                self.screen, stat_bar_rect, value,
                MAX_STATS[stat] * monster.level,
                COLORS['black'], COLORS['white']
            )

    def draw_main(self, dt: float) -> None:
        monster = self.monsters[self.hovered_index]

        main_rect = pg.FRect(
            self.monster_index_rect.left + self.item_width,
            self.monster_index_rect.top, self.monster_index_rect.width - self.item_width,
            self.monster_index_rect.height
        )

        pg.draw.rect(
            self.screen, COLORS['dark'], main_rect, border_top_right_radius=8, border_bottom_right_radius=8
        )

        top_rect = pg.FRect(
            main_rect.topleft, (main_rect.width, main_rect.height * 0.4)
        )
        pg.draw.rect(
            self.screen, COLORS[monster.element], top_rect, border_top_right_radius=8
        )

        self.draw_main_monster(monster, top_rect, dt)
        self.draw_main_name(monster, top_rect)
        self.draw_main_level(monster, top_rect)
        self.draw_main_element(monster, top_rect)
        health_bar_rect = self.draw_main_health_bar(monster, top_rect)
        energy_bar_rect = self.draw_main_energy_bar(monster, top_rect)

        stats_height = main_rect.bottom - health_bar_rect.bottom
        stats_rect = pg.FRect(
            (health_bar_rect.bottomleft), (health_bar_rect.width, stats_height)
        ).inflate(0, -40)

        self.draw_main_stats(monster, stats_rect)

        abilities_rect = stats_rect.copy().move_to(left=energy_bar_rect.left)

        title_surf = self.fonts['regular'].render(
            'Abilities', False, COLORS['white']
        )
        title_rect = title_surf.get_frect(topleft=abilities_rect.topleft)
        self.screen.blit(title_surf, title_rect)

        # what do we need
        # previous element, check collision, draw under title offset by index

        # calculated before hand, this also includes row padding
        ability_height = 40
        previous_ability_rect: pg.FRect | None = None
        row = 0

        for name in monster.get_abilities():
            ability_surf = self.fonts['regular'].render(
                name, False, COLORS['black']
            )

            ability_bg_rect = ability_surf.get_frect().inflate(20, 6)

            # if first element
            if previous_ability_rect == None:
                ability_bg_rect.topleft = title_rect.bottomleft
            else:
                ability_bg_rect.midleft = previous_ability_rect.midright + \
                    vector(10, 0)

                collision_rect = pg.FRect(
                    abilities_rect.topright, (2, abilities_rect.height)
                )

                if ability_bg_rect.colliderect(collision_rect):
                    row += 1

                    ability_bg_rect.topleft = title_rect.bottomleft + \
                        vector(0, row * ability_height)

            pg.draw.rect(
                self.screen, COLORS[ATTACK_DATA[name]['element']],
                ability_bg_rect, border_radius=12
            )

            ability_rect = ability_surf.get_frect(
                center=ability_bg_rect.center)

            self.screen.blit(ability_surf, ability_rect)

            previous_ability_rect = ability_bg_rect

    def update(self, dt: float) -> None:
        self._input()

        self.screen.blit(self.tint, (0, 0))
        self.draw_list()
        self.draw_main(dt)
