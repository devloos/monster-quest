from settings import *
from random import uniform
from monster import Monster
from util.draw import draw_bar
from util.timer import Timer
from util.imports import import_image

MAIN_RECT_WIDTH = 200
MAIN_RECT_HEIGHT = 320
BORDER_WIDTH = 2


class BattleMonster(pg.sprite.Sprite):
    def __init__(
        self, id: int, pos: tuple[float, float], monster: Monster,
        frames: dict[str, list[pg.Surface]], attack_frames: dict[str, list[pg.Surface]],
        outlines: dict[str, list[pg.Surface]], entity: str, fonts: dict[str, pg.Font], groups
    ) -> None:
        super().__init__(groups)

        self.screen = pg.display.get_surface()
        self.id = id
        self.monster = monster
        self.outlines = outlines
        self.frames = frames
        self.frame_index = 0
        self.state = 'idle'
        self.entity = entity
        self.fonts = fonts
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)

        self.main_rect = pg.FRect((0, 0), (MAIN_RECT_WIDTH, MAIN_RECT_HEIGHT))
        self.main_rect.center = pos

        self.attacked = False
        self.attack_frames = attack_frames
        self.attack_animation = ''
        self.attacked_frame_index = 0

        self.highlight = False
        self.shine = False

        self.missed_catch_frame = import_image('graphics', 'ui', 'cross')
        self.missed_catch = False

        self.timers = {
            'remove_shine': Timer(250, False, False, self.remove_shine),
            'remove_missed_catch': Timer(600, False, False, lambda: self.set_missed_catch(False))
        }

    def set_highlight(self, value: bool, shine: bool = True) -> None:
        self.highlight = value

        if value and shine:
            self.shine = True
            self.timers['remove_shine'].activate()

    def remove_shine(self) -> None:
        self.shine = False

    def frame_length(self) -> int:
        return len(self.frames[self.state])

    def animate_attack(self) -> None:
        self.state = 'attack'
        self.frame_index = 0

    def animate_attacked(self, attack_animation) -> None:
        self.attack_animation = attack_animation
        self.attacked = True
        self.attacked_frame_index = 0

    def set_missed_catch(self, value: bool) -> None:
        self.missed_catch = value

        if self.missed_catch:
            self.timers['remove_missed_catch'].activate()

    def animate(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt

        # only animate attack for one frame cycle
        if self.state == 'attack' and self.frame_index >= self.frame_length():
            self.state = 'idle'

        if self.frame_index > self.frame_length():
            self.frame_index = 0

        if self.attacked:
            self.attacked_frame_index += self.animation_speed * dt

            if self.attacked_frame_index > len(self.attack_frames[self.attack_animation]):
                self.attacked = False

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

    def draw_level(self, name_bg_rect: pg.FRect) -> pg.FRect:
        # draw level
        level_surf = self.fonts['small'].render(
            f'Level: {self.monster.level}', False, COLORS['dark']
        )
        level_bg_rect = pg.FRect(
            (name_bg_rect.bottomleft), (MAIN_RECT_WIDTH, level_surf.height + 8)
        )

        level_rect = level_surf.get_rect(midleft=level_bg_rect.midleft + vector(8, 0))

        pg.draw.rect(
            self.screen, COLORS['battle'], level_bg_rect,
            border_bottom_left_radius=5, border_bottom_right_radius=5
        )

        draw_bar(
            self.screen, level_bg_rect, self.monster.xp,
            self.monster.level_up, COLORS['battle'], COLORS['battle-light'],
            border_bottom_left_radius=5, border_bottom_right_radius=5
        )
        self.screen.blit(level_surf, level_rect)

        return level_bg_rect

    def draw_health(self, stats_bg_rect: pg.FRect) -> pg.FRect:
        health_text = self.fonts['small'].render(
            f'hp: {int(self.monster.health)}/{self.monster.get_stat('max_health')}',
            False, COLORS['dark']
        )
        health_text_rect = health_text.get_frect(
            topleft=stats_bg_rect.topleft + vector(8, 5)
        )
        self.screen.blit(health_text, health_text_rect)

        health_bar_width = stats_bg_rect.right - health_text_rect.left - 8
        health_bar_rect = pg.FRect(
            (health_text_rect.bottomleft + vector(0, 2)), (health_bar_width, 5)
        )
        draw_bar(
            self.screen, health_bar_rect, self.monster.health,
            self.monster.get_stat('max_health'), COLORS['black'],
            COLORS['red'], border_radius=5
        )

        return health_bar_rect

    def draw_energy(self, health_bar_rect: pg.FRect, stats_bg_rect: pg.FRect) -> pg.FRect:
        energy_text = self.fonts['small'].render(
            f'ep: {int(self.monster.energy)}/{self.monster.get_stat('max_energy')}',
            False, COLORS['dark']
        )
        energy_text_rect = energy_text.get_frect(
            topleft=health_bar_rect.bottomleft + vector(0, 5)
        )
        self.screen.blit(energy_text, energy_text_rect)

        energy_bar_width = stats_bg_rect.right - energy_text_rect.left - 8
        energy_bar_rect = pg.FRect(
            (energy_text_rect.bottomleft + vector(0, 2)), (energy_bar_width, 5)
        )
        draw_bar(
            self.screen, energy_bar_rect, self.monster.energy,
            self.monster.get_stat('max_energy'), COLORS['black'],
            COLORS['blue'], border_radius=5
        )

        return energy_bar_rect

    def draw_stats(self, frame_rect: pg.FRect) -> None:
        # stat rect
        stats_height = self.main_rect.bottom - frame_rect.bottom
        stats_bg_rect = pg.FRect((0, 0), (MAIN_RECT_WIDTH, stats_height))
        stats_bg_rect.bottomleft = self.main_rect.bottomleft
        pg.draw.rect(self.screen, COLORS['battle'], stats_bg_rect, border_radius=5)

        border_rect = stats_bg_rect.copy()
        pg.draw.rect(
            self.screen, COLORS['dark'], border_rect, BORDER_WIDTH, 5
        )

        health_bar_rect = self.draw_health(stats_bg_rect)
        energy_bar_rect = self.draw_energy(health_bar_rect, stats_bg_rect)

        recharge_bar_width = stats_bg_rect.right - energy_bar_rect.left - 8
        recharge_bar_rect = pg.FRect(
            (energy_bar_rect.bottomleft + vector(0, 3)), (recharge_bar_width, 5)
        )
        draw_bar(
            self.screen, recharge_bar_rect, self.monster.recharge, MAX_RECHARGE,
            COLORS['white'], COLORS['dark'], border_radius=5
        )

    def draw(self) -> None:
        name_bg_rect = self.draw_name()
        level_bg_rect = self.draw_level(name_bg_rect)

        # name & level divider
        pg.draw.line(
            self.screen, COLORS['light'], name_bg_rect.bottomleft, name_bg_rect.bottomright
        )

        # draw frame
        frame = self.frames[self.state][int(self.frame_index)]
        frame_rect = frame.get_frect(midtop=level_bg_rect.midbottom + vector(0, 2))

        if self.highlight:
            outline = self.outlines[self.state][int(self.frame_index)]
            outline_rect = outline.get_frect(
                center=frame_rect.center
            )

            self.screen.blit(outline, outline_rect)

        if not self.shine:
            self.screen.blit(frame, frame_rect)

        if self.attacked:
            index = int(self.attacked_frame_index)
            attack_frame = self.attack_frames[self.attack_animation][index]
            attack_frame_rect = attack_frame.get_rect(center=frame_rect.center)
            self.screen.blit(attack_frame, attack_frame_rect)

        if self.missed_catch:
            missed_catch_rect = self.missed_catch_frame.get_rect(center=frame_rect.center)
            self.screen.blit(self.missed_catch_frame, missed_catch_rect)

        self.draw_stats(frame_rect)

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def update(self, dt: float) -> None:
        self.update_timers()
        self.monster.update(dt)
        self.animate(dt)
