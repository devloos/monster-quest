from settings import *
from typing import Callable


class Transition:
    def __init__(self) -> None:
        self.screen = pg.display.get_surface()
        self.tint = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.in_transition = False
        self.tint_mode: str | None = None
        self.tint_progress = 0
        self.tint_complete = False
        self.callback: Callable | None = None
        pass

    def start(self, callback: Callable) -> None:
        self.in_transition = True
        self.tint_progress = 0
        self.tint_mode = 'tint'
        self.callback = callback

    def update(self, dt) -> None:
        if not self.in_transition or self.tint_mode == None:
            return

        speed = 600

        if self.tint_mode == 'tint':
            self.tint_progress += speed * dt
        else:
            self.tint_progress -= speed * dt

        self.tint_progress = max(0, min(255, self.tint_progress))

        if self.tint_progress == 255:
            if self.callback:
                self.callback()

            self.tint_mode = 'untint'
            self.tint_complete = True

        # transition complete
        if self.tint_complete and self.tint_progress == 0:
            self.in_transition = False
            self.tint_mode = None
            self.callback = None
            self.tint_complete = False

        # keep tint progress between 0 and 255
        self.tint.set_alpha(self.tint_progress)
        self.screen.blit(self.tint, self.tint.get_rect())
