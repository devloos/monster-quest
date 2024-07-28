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

    def display_list(self, dt: float) -> None:
        for index, monster in enumerate(self.monsters):
            top = self.main_rect.top + index * self.item_height + index
            self.item_rect = pg.FRect(
                self.main_rect.left, top, self.item_width, self.item_height
            )

            pg.draw.rect(self.screen, 'dark gray', self.item_rect)

            monster_name = self.fonts['regular'].render(
                monster.name, False, COLORS['white']
            )
            monster_name_rect = monster_name.get_frect(
                topleft=self.item_rect.topleft + vector(20, 20)
            )

            self.screen.blit(monster_name, monster_name_rect)

            # todo: add shadow effect and border
            element = pg.Surface((60, 20), pg.SRCALPHA).convert_alpha()
            element_rect = element.get_rect(
                topleft=monster_name_rect.bottomleft + vector(0, 10)
            )

            pg.draw.rect(
                element, COLORS[monster.element],
                pg.FRect(0, 0, 60, 20), border_radius=10
            )

            element_text = self.fonts['small'].render(
                monster.element, False, COLORS['black']
            )

            element.blit(
                element_text,
                element_text.get_frect(center=element_rect.center)
            )

            self.screen.blit(element, element_rect)

            icon_rect = monster.icon.get_rect(
                midright=self.item_rect.midright + vector(-25, 0)
            )
            self.screen.blit(monster.icon, icon_rect)

    def update(self, dt: float) -> None:
        self.screen.blit(self.tint, (0, 0))
        pg.draw.rect(self.screen, 'black', self.main_rect)
        self.display_list(dt)
