from settings import *
from entities import Player, Character
from groups import RenderGroup


class DialogSprite(pg.sprite.Sprite):
    def __init__(self, message: str, character: Character, font: pg.Font, groups) -> None:
        super().__init__(groups)

        self.z = WorldLayer.top

        font_surf = font.render(message, False, COLORS['black'])
        padding = 30

        width = max(30, font_surf.width + padding)
        height = font_surf.height + padding

        # plus 20 to support thought bubble
        surf = pg.Surface((width, height + 14), pg.SRCALPHA)

        # make surface invisible
        surf.fill((0, 0, 0, 0))

        # fill height minus 20 with pure white bg
        rect = pg.Rect(surf.get_rect())
        rect.height -= 14

        # add bubble thought
        pg.draw.rect(surf, COLORS['pure white'], rect, 0, 4)

        rect = pg.Rect()
        rect.midbottom = surf.get_rect().bottomleft + vector(width / 3, -10)
        rect = rect.inflate(15, 28)

        pg.draw.rect(surf, COLORS['pure white'], rect, 0, 20)

        center_rect = font_surf.get_frect(center=(width / 2, height / 2))
        surf.blit(font_surf, center_rect)

        self.image = surf
        self.rect = self.image.get_frect(midbottom=character.rect.midtop)

    def get_y_sort(self) -> float:
        return self.rect.centery


class DialogTree:
    def __init__(self) -> None:
        self.player: Player
        self.character: Character
        self.render_group: RenderGroup
        self.font: pg.Font

        self.dialog: list
        self.dialog_index: int

        self.dialog_sprite: DialogSprite = None
        self.in_dialog = False

    def setup(self, player: Player, character: Character, render_group: RenderGroup, font: pg.Font) -> None:
        self.player = player
        self.character = character
        self.render_group = render_group
        self.font = font

        self.dialog = self.character.get_dialog()
        self.dialog_index = -1
        self.in_dialog = True

    def move_dialog(self) -> None:
        if (self.dialog_sprite):
            self.dialog_sprite.kill()
            self.dialog_sprite = None

        self.dialog_index += 1

        if self.dialog_index >= len(self.dialog):
            self.in_dialog = False
            return

        self.dialog_sprite = DialogSprite(
            self.dialog[self.dialog_index], self.character, self.font, self.render_group
        )

    def _input(self) -> None:
        keys = pg.key.get_just_pressed()

        if keys[pg.K_SPACE]:
            self.move_dialog()

    def update(self) -> None:
        self._input()
