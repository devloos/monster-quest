from settings import *
from monster import Monster


class MonsterIndex:
    def __init__(self, monsters: list[Monster], fonts: dict[str, pg.Font]) -> None:
        self.screen = pg.display.get_surface()
        self.monsters = monsters
        self.fonts = fonts
        self.opened = False

        self.tint = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint.set_alpha(200)

        self.main_rect = pg.FRect(
            0, 0, WINDOW_WIDTH * 0.7, WINDOW_HEIGHT * 0.8
        )
        self.main_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        self.visible_items = 6
        self.item_width = self.main_rect.width * 0.3
        self.item_height = self.main_rect.height / self.visible_items
        self.hovered_index = 0
        self.selected_index: int | None = None

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

    def draw_element_badge(self, rect: pg.FRect, monster: Monster) -> None:
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

        self.screen.blit(
            element_text,
            element_text.get_frect(center=element_rect.center)
        )

        self.screen.blit(element, element_rect)

    def draw_selected_badge(self, item_rect: pg.FRect) -> None:
        center = item_rect.topright + vector(-13, 13)

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

    def draw_monster_icon(self, item_rect: pg.FRect, monster: Monster) -> None:
        icon_rect = monster.icon.get_rect(
            center=item_rect.midright + vector(-55, 0)
        )

        self.screen.blit(monster.icon, icon_rect)

    def draw_list(self, dt: float) -> None:
        start_index = 0

        if self.hovered_index >= self.visible_items:
            start_index = self.hovered_index - self.visible_items + 1

        for index, monster in enumerate(self.monsters[start_index:]):
            top = self.main_rect.top + index * self.item_height
            item_rect = pg.FRect(
                self.main_rect.left, top, self.item_width, self.item_height
            )

            if not item_rect.colliderect(self.main_rect):
                continue

            # colors
            bg_color = COLORS['gray']
            text_color = COLORS['light']

            if self.hovered_index == index + start_index:
                bg_color = COLORS['light']
                text_color = COLORS['gray']

            pg.draw.rect(self.screen, bg_color, item_rect)

            _, monster_name_rect = self.draw_monster_name(
                item_rect, monster, text_color
            )
            self.draw_monster_icon(item_rect, monster)
            self.draw_element_badge(monster_name_rect, monster)

            if self.selected_index == index + start_index:
                self.draw_selected_badge(item_rect)

    def update(self, dt: float) -> None:
        self._input()

        self.screen.blit(self.tint, (0, 0))
        pg.draw.rect(self.screen, 'black', self.main_rect)
        self.draw_list(dt)
