from src.settings import *
from src.monster import Monster
from typing import Callable
from src.util.timer import Timer


class Evolution:
    def __init__(
        self, monster_frames: dict[str, dict[str, list[pg.Surface]]],
        star_frames: list[pg.Surface], evolution_sound: pg.mixer.Sound, font: pg.Font
    ) -> None:
        self.screen = pg.display.get_surface()
        self.monster_frames = monster_frames
        self.star_frames = star_frames
        self.font = font
        self.in_evolution = False
        self.evolution_sound = evolution_sound

        self.monster: Monster | None
        self.monster_evolution = {
            'name': '',
            'level': 0
        }
        self.callback: Callable | None
        self.monster_frame: pg.Surface | None
        self.monster_frame_rect: pg.FRect | None
        self.monster_evolution_frame: pg.Surface | None
        self.monster_evolution_frame_rect: pg.FRect | None

        self.monster_mask_frame: pg.Surface | None = None
        self.monster_mask_alpha = 0

        self.star_frame_index = 0

        self.timers = {
            'start': Timer(2000, False, False, self.start_finish_timer),
            'finish': Timer(2300, False, False, self.end_evolution)
        }

        self.bg_tint_surf = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg_tint_surf.set_alpha(200)

    def setup(self, monster: Monster, callback: Callable) -> None:
        self.in_evolution = True
        self.monster = monster
        self.monster_evolution = monster.evolution
        self.callback = callback

        self.monster_frame = self.monster_frames[self.monster.name]['idle'][0]
        self.monster_frame = pg.transform.scale2x(self.monster_frame)

        self.monster_mask_frame = pg.mask.from_surface(self.monster_frame).to_surface()
        self.monster_mask_frame.set_colorkey('black')
        self.monster_mask_frame.set_alpha(0)

        self.monster_frame_rect = self.monster_frame.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        )

        self.monster_mask_alpha = 0

        self.monster_evolution_frame = self.monster_frames[self.monster_evolution['name']]['idle'][0]
        self.monster_evolution_frame = pg.transform.scale2x(self.monster_evolution_frame)
        self.monster_evolution_frame_rect = self.monster_evolution_frame.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        )

        self.timers['start'].activate()
        self.evolution_sound.play()

    def start_finish_timer(self) -> None:
        self.timers['finish'].activate()

    def end_evolution(self) -> None:
        if self.callback != None:
            self.callback(self.monster)

        self.in_evolution = False
        self.monster = None
        self.monster_frame_rect = None
        self.monster_evolution = None
        self.monster_evolution_frame_rect = None
        self.callback = None

        self.monster_mask_frame = None
        self.monster_mask_alpha = 0

        self.monster_frame = None
        self.monster_evolution_frame = None
        self.evolution_sound.stop()

    def draw_star_animation(self, dt: float) -> None:
        self.star_frame_index += 24 * dt

        if self.star_frame_index > len(self.star_frames):
            return

        star_frame = pg.transform.scale2x(self.star_frames[int(self.star_frame_index)])
        star_frame_rect = star_frame.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        )
        self.screen.blit(star_frame, star_frame_rect)

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def update(self, dt: float) -> None:
        self.update_timers()

        self.screen.blit(self.bg_tint_surf, (0, 0))

        if self.timers['start'].active:
            self.screen.blit(self.monster_frame, self.monster_frame_rect)
            self.screen.blit(self.monster_mask_frame, self.monster_frame_rect)

            text_surf = self.font.render(
                f'{self.monster.name} is evolving', False, COLORS['black']
            )
            bg_rect = text_surf.get_rect().inflate(75, 15)
            bg_rect.midtop = self.monster_frame_rect.midbottom + vector(0, 10)
            text_rect = text_surf.get_rect(center=bg_rect.center)

            pg.draw.rect(self.screen, COLORS['white'], bg_rect, border_radius=5)
            self.screen.blit(text_surf, text_rect)

            self.monster_mask_alpha += 100 * dt
            self.monster_mask_frame.set_alpha(self.monster_mask_alpha)

        if self.timers['finish'].active:
            self.screen.blit(
                self.monster_evolution_frame, self.monster_evolution_frame_rect
            )

            text_surf = self.font.render(
                f'{self.monster.name} evolved into {self.monster_evolution['name']}',
                False, COLORS['black']
            )
            bg_rect = text_surf.get_rect().inflate(75, 15)
            bg_rect.midtop = self.monster_evolution_frame_rect.midbottom + vector(0, 10)
            text_rect = text_surf.get_rect(center=bg_rect.center)

            pg.draw.rect(self.screen, COLORS['white'], bg_rect, border_radius=5)
            self.screen.blit(text_surf, text_rect)

            self.draw_star_animation(dt)
