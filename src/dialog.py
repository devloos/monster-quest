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
        rect.midbottom = surf.get_rect().midbottom - vector(60, 10)
        rect = rect.inflate(15, 28)

        pg.draw.rect(surf, COLORS['pure white'], rect, 0, 20)

        center_rect = font_surf.get_frect(center=(width / 2, height / 2))
        surf.blit(font_surf, center_rect)

        self.image = surf
        self.rect = self.image.get_frect(midbottom=character.rect.midtop)

    def get_y_sort(self) -> float:
        return self.rect.centery


class DialogTree:
    def __init__(self, player: Player, character: Character, render_group: RenderGroup, font: pg.Font) -> None:
        self.player = player
        self.character = character
        self.render_group = render_group
        self.font = font

        self.dialog = self.character.get_dialog()
        self.dialog_index = 0

        self.dialog_sprite = DialogSprite(
            self.dialog[self.dialog_index], self.character, self.font, self.render_group
        )
