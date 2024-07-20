from settings import *
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap
from os.path import join
from sprites import Sprite
from entities import Player


class Game:
    def __init__(self) -> None:
        pg.init()
        self.display_surface = pg.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pg.display.set_caption('Monster Quest')

        self.all_sprites = pg.sprite.Group()

        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')

    def import_assets(self) -> None:
        self.tmx_maps = {
            'world': load_pygame(join('data', 'maps', 'world.tmx'))
        }

    def setup(self, tmx_map: TiledMap, player_start_pos) -> None:
        for x, y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
            sprite = Sprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                surf,
                self.all_sprites
            )

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player' and obj.properties['pos'] == player_start_pos:
                player = Player((obj.x, obj.y), self.all_sprites)

    def run(self) -> None:
        while True:
            # handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            # handle game logic
            self.all_sprites.draw(self.display_surface)

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
