from settings import *
from random import uniform
from monster import Monster

MAIN_RECT_WIDTH = 200
MAIN_RECT_HEIGHT = 315
BORDER_WIDTH = 2


class BattleMonster(pg.sprite.Sprite):
    def __init__(
        self, id: int, pos: tuple[float, float], monster: Monster,
        frames: dict[str, list[pg.Surface]], entity: str, fonts: dict[str, pg.Font], groups
    ) -> None:
        super().__init__(groups)

        self.screen = pg.display.get_surface()
        self.id = id
        self.monster = monster
        self.frames = frames
        self.frame_index = 0
        self.state = 'idle'
        self.entity = entity
        self.fonts = fonts
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)

        self.main_rect = pg.FRect((0, 0), (MAIN_RECT_WIDTH, MAIN_RECT_HEIGHT))
        self.main_rect.center = pos

    def frame_length(self) -> int:
        return len(self.frames[self.state])

    def animate(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt

        if self.frame_index > self.frame_length():
            self.frame_index = 0

    def draw_name(self) -> pg.FRect:
        # draw name
        name_surf = self.fonts['regular'].render(
            self.monster.name, False, COLORS['dark']
        )
        name_bg_rect = pg.FRect(
            (self.main_rect.topleft), (MAIN_RECT_WIDTH, name_surf.height + 3)
        )
        name_rect = name_surf.get_rect(center=name_bg_rect.center)

        pg.draw.rect(
            self.screen, COLORS['battle'], name_bg_rect,
            border_top_left_radius=5, border_top_right_radius=5
        )
        self.screen.blit(name_surf, name_rect)

        return name_bg_rect

    def draw_level(self, name_bg_rect: pg.FRect) -> None:
        # draw level
        level_surf = self.fonts['regular'].render(
            f'Level: {self.monster.level}', False, COLORS['dark']
        )
        level_bg_rect = pg.FRect(
            (name_bg_rect.bottomleft), (MAIN_RECT_WIDTH, level_surf.height + 8)
        )
        level_rect = level_surf.get_rect(
            midleft=level_bg_rect.midleft + vector(8, 0)
        )

        pg.draw.rect(
            self.screen, COLORS['battle'], level_bg_rect,
            border_bottom_left_radius=5, border_bottom_right_radius=5
        )
        self.screen.blit(level_surf, level_rect)

    def draw_stats(self, frame_rect: pg.FRect) -> None:
        stats_height = self.main_rect.bottom - frame_rect.bottom - 1
        stats_bg_rect = pg.FRect(
            (0, 0), (MAIN_RECT_WIDTH, stats_height)
        )
        stats_bg_rect.bottomleft = self.main_rect.bottomleft
        pg.draw.rect(
            self.screen, COLORS['battle'], stats_bg_rect, border_radius=5
        )

        border_rect = stats_bg_rect.copy()
        pg.draw.rect(
            self.screen, COLORS['dark'], border_rect, BORDER_WIDTH, 5
        )

    def draw(self) -> None:
        name_bg_rect = self.draw_name()
        self.draw_level(name_bg_rect)

        # name & level divider
        pg.draw.line(
            self.screen, COLORS['light'], name_bg_rect.bottomleft, name_bg_rect.bottomright
        )

        # draw frame
        frame = self.frames[self.state][int(self.frame_index)]
        frame_rect = frame.get_frect(center=self.main_rect.center)

        self.screen.blit(frame, frame_rect)

        self.draw_stats(frame_rect)

    def update(self, dt: float) -> None:
        self.animate(dt)
