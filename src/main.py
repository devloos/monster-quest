from settings import *
from support import *
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap, TiledObject
from os.path import join
from sprites import Sprite, AnimatedSprite
from entities import Player, Character
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
            'coast': import_coast(24, 12, 'graphics', 'tilesets', 'coast'),
            'characters': import_characters(4, 4, 'graphics', 'characters')
        }

    def setup(self, tmx_map: TiledMap, player_start_pos) -> None:
        # Terrain
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    WorldLayer.bg,
                    self.all_sprites
                )

        obj: TiledObject

        # Water
        for obj in tmx_map.get_layer_by_name('Water'):
            # this is not really a grid with row, col
            # just tiles that act as coords
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(
                        (x, y),
                        self.overworld_frames['water'],
                        WorldLayer.water,
                        self.all_sprites
                    )

        # Coast
        for obj in tmx_map.get_layer_by_name('Coast'):
            pos = (obj.x, obj.y)
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            frames = self.overworld_frames['coast'][terrain][side]
            AnimatedSprite(pos, frames, WorldLayer.water, self.all_sprites)

        # Objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            z = WorldLayer.main

            if obj.name == 'top':
                z = WorldLayer.top

            Sprite((obj.x, obj.y), obj.image, z, self.all_sprites)

        # Monsters
        for obj in tmx_map.get_layer_by_name('Monsters'):
            Sprite(
                (obj.x, obj.y), obj.image, WorldLayer.main, self.all_sprites
            )

        # Entities
        for obj in tmx_map.get_layer_by_name('Entities'):
            frames = self.overworld_frames['characters'][obj.properties['graphic']]
            state = obj.properties['direction']

            # check for player and check starting pos
            if obj.name == 'Player' and obj.properties['pos'] == player_start_pos:
                self.player = Player(
                    (obj.x, obj.y), frames, state, self.all_sprites
                )
            elif obj.name == 'Character':
                Character(
                    (obj.x, obj.y), frames, state, self.all_sprites
                )

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
