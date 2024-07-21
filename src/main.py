from settings import *
from support import *
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap, TiledObject
from os.path import join
from sprites import Sprite, AnimatedSprite
from entities import Player
from groups import AllSpriteGroup


class Game:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pg.display.set_caption('Monster Quest')
        self.clock = pg.time.Clock()

        self.all_sprites = AllSpriteGroup()

        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')
        # self.setup(self.tmx_maps['hospital'], 'world')

    def import_assets(self) -> None:
        self.tmx_maps = {
            'world': load_pygame(join('data', 'maps', 'world.tmx')),
            'hospital': load_pygame(join('data', 'maps', 'hospital.tmx'))
        }

        self.overworld_frames = {
            'water': import_folder('graphics', 'tilesets', 'water'),
            'coast': coast_importer(24, 12, 'graphics', 'tilesets', 'coast')
        }

        print(self.overworld_frames['coast'])

    def setup(self, tmx_map: TiledMap, player_start_pos) -> None:
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    self.all_sprites
                )

        obj: TiledObject

        for obj in tmx_map.get_layer_by_name('Water'):
            # this is not really a grid with row, col
            # just tiles that act as coords
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(
                        (x, y),
                        self.overworld_frames['water'],
                        self.all_sprites
                    )

        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites)

        entity: TiledObject
        for entity in tmx_map.get_layer_by_name('Entities'):
            if entity.name == 'Player' and entity.properties['pos'] == player_start_pos:
                self.player = Player((entity.x, entity.y), self.all_sprites)

    def run(self) -> None:
        while True:
            dt = self.clock.tick() / 1000
            # handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            # handle game logic
            self.all_sprites.update(dt)
            self.screen.fill((0, 0, 0))
            self.all_sprites.draw(self.player.get_center_pos())

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
