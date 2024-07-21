from settings import *


class AllSpriteGroup(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = vector()

    def draw(self, player_center: vector):
        # we want the player always in the center, if the player moves right
        # all other sprites move left by -x amount
        self.offset.x = -(player_center.x - WINDOW_WIDTH / 2)
        self.offset.y = -(player_center.y - WINDOW_HEIGHT / 2)

        sprite: pg.sprite.Sprite
        for sprite in self:
            self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)
