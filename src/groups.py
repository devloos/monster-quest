from __future__ import annotations
from src.settings import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # <-try this,
    from src.sprites.entity import Entity
    from src.textures.texture import Texture
    from src.overlays.dialog import DialogSprite


class RenderGroup(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = vector()

    def draw(self, player_center: vector):
        # we want the player always in the center, if the player moves right
        # all other sprites move left by -x amount
        self.offset.x = -(player_center.x - WINDOW_WIDTH / 2)
        self.offset.y = -(player_center.y - WINDOW_HEIGHT / 2)

        bg_sprites = filter(lambda sprite: sprite.z < WorldLayer.main, self)
        main_sprites = filter(lambda sprite: sprite.z == WorldLayer.main, self)
        main_sprites = sorted(
            main_sprites, key=lambda sprite: sprite.get_y_sort()
        )
        fg_sprites = filter(lambda sprite: sprite.z > WorldLayer.main, self)

        sprite: Entity | Texture | DialogSprite

        for sprites in [bg_sprites, main_sprites, fg_sprites]:
            for sprite in sprites:
                sprite.draw(self.offset)
