from settings import *
from entities import Entity
from support import import_image


class AllSpriteGroup(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = vector()
        self.shadow = import_image('graphics', 'other', 'shadow')

    def draw(self, player_center: vector):
        # we want the player always in the center, if the player moves right
        # all other sprites move left by -x amount
        self.offset.x = -(player_center.x - WINDOW_WIDTH / 2)
        self.offset.y = -(player_center.y - WINDOW_HEIGHT / 2)

        sprite: pg.sprite.Sprite

        bg_sprites = filter(lambda sprite: sprite.z < WorldLayer.main, self)
        main_sprites = filter(lambda sprite: sprite.z == WorldLayer.main, self)
        main_sprites = sorted(
            main_sprites, key=lambda sprite: sprite.get_y_sort()
        )
        fg_sprites = filter(lambda sprite: sprite.z > WorldLayer.main, self)

        for sprites in [bg_sprites, main_sprites, fg_sprites]:
            for sprite in sprites:
                if isinstance(sprite, Entity):
                    self.screen.blit(
                        self.shadow, sprite.rect.topleft +
                        self.offset + vector(40, 110)
                    )

                self.screen.blit(
                    sprite.image, sprite.rect.topleft + self.offset
                )
