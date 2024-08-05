from settings import *
from monster import Monster
from typing import Callable
from util.timer import Timer


class Evolution:
    def __init__(self, monster_frames: dict[str, dict[str, list[pg.Surface]]], font: pg.Font) -> None:
        self.screen = pg.display.get_surface()
        self.monster_frames = monster_frames
        self.font = font
        self.in_evolution = False

        self.monster: Monster | None
        self.monster_evolution = dict | None
        self.callback: Callable | None
        self.monster_frame: pg.Surface | None
        self.monster_frame_rect: pg.FRect | None
        self.monster_evolution_frame: pg.Surface | None
        self.monster_evolution_frame_rect: pg.FRect | None

        self.timers = {
            'start': Timer(1200, False, False, self.start_finish_timer),
            'finish': Timer(1800, False, False, self.end_evolution)
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
        self.monster_frame_rect = self.monster_frame.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        )

        self.monster_evolution_frame = self.monster_frames[self.monster_evolution['name']]['idle'][0]
        self.monster_evolution_frame = pg.transform.scale2x(self.monster_evolution_frame)
        self.monster_evolution_frame_rect = self.monster_evolution_frame.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        )

        self.timers['start'].activate()

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

        self.monster_frame = None
        self.monster_evolution_frame = None

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def update(self, dt: float) -> None:
        self.update_timers()

        self.screen.blit(self.bg_tint_surf, (0, 0))

        if self.timers['start'].active:
            self.screen.blit(self.monster_frame, self.monster_frame_rect)

        if self.timers['finish'].active:
            self.screen.blit(
                self.monster_evolution_frame, self.monster_evolution_frame_rect
            )
