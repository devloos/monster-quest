from settings import *
from monster import Monster
from util.draw import draw_bar


class MonsterIndex:
    def __init__(
        self, monsters: list[Monster], monster_frames: dict[str, dict[str, list[pg.Surface]]], fonts: dict[str, pg.Font]
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monsters = monsters
        self.monster_frames = monster_frames
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
        element_rect = element.get_rect(
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
        icon_rect = monster.icon.get_rect(
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

    def draw_main_energy_bar(self, rect: pg.FRect) -> None:
        energy_bar_rect = pg.FRect((0, 0), (rect.width * 0.45, 30))
        energy_bar_rect.topright = rect.bottomright + vector(-15, 15)

        draw_bar(
            self.screen, energy_bar_rect, 60, 100, COLORS['black'], COLORS['blue'], 2
        )

        energy_bar_text_surf = self.fonts['regular'].render(
            'EP: 60/100', False, COLORS['white']
        )
        energy_bar_text_rect = energy_bar_text_surf.get_rect(
            left=energy_bar_rect.left + 10,
            centery=energy_bar_rect.centery
        )
        self.screen.blit(energy_bar_text_surf, energy_bar_text_rect)

    def draw_main_health_bar(self, rect: pg.FRect) -> None:
        health_bar_rect = pg.FRect(
            rect.left + 15, rect.bottom + 15,
            rect.width * 0.45, 30
        )

        draw_bar(
            self.screen, health_bar_rect, 25, 100, COLORS['black'], COLORS['red'], 2
        )

        health_bar_text_surf = self.fonts['regular'].render(
            'HP: 25/100', False, COLORS['white']
        )
        health_bar_text_rect = health_bar_text_surf.get_rect(
            left=health_bar_rect.left + 10,
            centery=health_bar_rect.centery
        )
        self.screen.blit(health_bar_text_surf, health_bar_text_rect)

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
        self.draw_main_health_bar(top_rect)
        self.draw_main_energy_bar(top_rect)

    def update(self, dt: float) -> None:
        self._input()

        self.screen.blit(self.tint, (0, 0))
        self.draw_list()
        self.draw_main(dt)
