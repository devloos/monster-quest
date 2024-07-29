from settings import *
from util.imports import *
from util.collisions import check_connection
from pytmx import TiledMap, TiledObject
from os.path import join
from textures.texture import Texture
from textures.animated_texture import AnimatedTexture
from textures.monster_patch_texture import MonsterPatchTexture
from textures.collidable_texture import CollidableTexture
from textures.transition_texture import TransitionTexture
from sprites.player import Player
from sprites.character import Character
from groups import RenderGroup
from game_data import *
from overlays.dialog import DialogTree
from overlays.monster_index import MonsterIndex
from monster import Monster


class Game:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        pg.display.set_caption('Monster Quest')
        self.clock = pg.time.Clock()

        # import all assets
        self.import_assets()

        # groups
        self.render_group = RenderGroup()
        self.collision_group = pg.sprite.Group()
        self.character_group = pg.sprite.Group()
        self.transition_group = pg.sprite.Group()

        # transitions / tint
        self.transition_map: str
        self.transition_pos: str
        self.tint = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0

        self.player_monsters = [
            Monster('Atrox', 16),
            Monster('Friolera', 4),
            Monster('Jacana', 39),
            Monster('Larvea', 23),
            Monster('Charmadillo', 30),
            Monster('Finsta', 16),
            Monster('Charmadillo', 30),
            Monster('Larvea', 23),
            Monster('Finsta', 16)
        ]

        # overlay
        self.dialog_tree = DialogTree(self.render_group)
        self.monster_index = MonsterIndex(
            self.player_monsters, self.monster_frames, self.fonts
        )

        # essentially start game
        self.setup(self.tmx_maps['world'], 'house')

    def import_assets(self) -> None:
        self.tmx_maps = import_tmx_maps('data', 'maps')

        self.overworld_frames = {
            'water': import_folder('graphics', 'tilesets', 'water'),
            'coast': import_coast(24, 12, 'graphics', 'tilesets', 'coast'),
            'characters': import_characters(4, 4, 'graphics', 'characters')
        }

        self.fonts = {
            'dialog': pg.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 30),
            'regular': pg.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 20),
            'small': pg.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 14),
            'bold': pg.Font(join('graphics', 'fonts', 'dogicapixelbold.otf'), 22),
        }

        self.monster_frames = import_monster_frames(
            4, 2, 'graphics', 'monsters'
        )

    def setup(self, tmx_map: TiledMap, player_start_pos) -> None:
        self.render_group.empty()
        self.collision_group.empty()
        self.character_group.empty()
        self.transition_group.empty()

        # Terrain
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Texture(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    WorldLayer.bg,
                    self.render_group
                )

        obj: TiledObject

        # Water
        for obj in tmx_map.get_layer_by_name('Water'):
            # this is not really a grid with row, col
            # just tiles that act as coords
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedTexture(
                        (x, y),
                        self.overworld_frames['water'],
                        WorldLayer.water,
                        self.render_group
                    )

        # Coast
        for obj in tmx_map.get_layer_by_name('Coast'):
            pos = (obj.x, obj.y)
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            frames = self.overworld_frames['coast'][terrain][side]
            AnimatedTexture(pos, frames, WorldLayer.water, self.render_group)

        # Objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            z = WorldLayer.main
            pos = (obj.x, obj.y)
            surf = obj.image

            if obj.name == 'top':
                z = WorldLayer.top
                Texture(pos, surf, z, self.render_group)
            else:
                CollidableTexture(
                    pos, surf, [self.render_group, self.collision_group]
                )

        # Collisions
        for obj in tmx_map.get_layer_by_name('Collisions'):
            Texture(
                (obj.x, obj.y),
                pg.Surface((obj.width, obj.height)),
                WorldLayer.main,
                self.collision_group
            )

        # Transitions
        for obj in tmx_map.get_layer_by_name('Transition'):
            pos = (obj.x, obj.y)
            size = (obj.width, obj.height)
            target = (obj.properties['target'], obj.properties['pos'])
            TransitionTexture(pos, size, target, self.transition_group)

        # Monsters
        for obj in tmx_map.get_layer_by_name('Monsters'):
            z = WorldLayer.main
            biome = obj.properties['biome']

            if biome == 'sand':
                z = WorldLayer.bg

            MonsterPatchTexture(
                (obj.x, obj.y), obj.image, z, biome, self.render_group
            )

        SHADOW = import_image('graphics', 'other', 'shadow')
        ALERT = import_image('graphics', 'ui', 'alert')
        # Entities
        for obj in tmx_map.get_layer_by_name('Entities'):
            frames = self.overworld_frames['characters'][obj.properties['graphic']]
            state = obj.properties['direction']

            # check for player and check starting pos
            if obj.name == 'Player' and obj.properties['pos'] == player_start_pos:
                self.player = Player(
                    (obj.x, obj.y),
                    frames,
                    state,
                    SHADOW,
                    ALERT,
                    self.collision_group,
                    self.render_group
                )
            elif obj.name == 'Character':
                groups = (
                    self.render_group, self.collision_group, self.character_group
                )
                character_data = TRAINER_DATA[obj.properties['character_id']]
                radius = obj.properties['radius']

                Character(
                    (obj.x, obj.y),
                    frames,
                    state,
                    character_data,
                    radius,
                    self.player,
                    self.dialog_tree,
                    self.fonts['dialog'],
                    SHADOW,
                    ALERT,
                    self.collision_group,
                    groups
                )

    def _input(self):
        if self.dialog_tree.in_dialog:
            return

        keys = pg.key.get_just_pressed()

        if keys[pg.K_SPACE]:
            character: Character

            for character in self.character_group:
                if check_connection(200, self.player, character):
                    self.player.block()
                    character.face_target_pos(self.player.rect.center)

                    self.dialog_tree.setup(
                        self.player, character, self.fonts['dialog']
                    )

        if keys[pg.K_TAB]:
            self.monster_index.opened = not self.monster_index.opened
            self.player.blocked = not self.player.blocked

        if keys[pg.K_ESCAPE]:
            self.monster_index.opened = False
            self.player.blocked = False

    def check_transitions(self) -> None:
        transition: TransitionTexture

        for transition in self.transition_group:
            if self.player.hitbox.colliderect(transition.rect):
                self.player.block()
                self.transition_map = transition.target[0]
                self.transition_pos = transition.target[1]
                self.tint_mode = 'tint'

    def tint_screen(self, dt) -> None:
        speed = 600

        if self.tint_mode == 'tint':
            self.tint_progress += speed * dt
        elif self.tint_mode == 'untint':
            self.tint_progress -= speed * dt

        self.tint_progress = max(0, min(255, self.tint_progress))

        if self.tint_progress == 255 and self.transition_map in self.tmx_maps:
            self.setup(self.tmx_maps[self.transition_map], self.transition_pos)
            self.tint_mode = 'untint'
            self.transition_map = None
            self.transition_pos = None

        # keep tint progress between 0 and 255
        self.tint.set_alpha(self.tint_progress)
        self.screen.blit(self.tint, self.tint.get_rect())

    def run(self) -> None:
        while True:
            dt = self.clock.tick() / 1000
            # handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            # handle game input
            self.check_transitions()
            self._input()

            # handle game logic
            self.render_group.update(dt)
            self.screen.fill((0, 0, 0))
            self.render_group.draw(self.player.get_center_pos())

            if self.dialog_tree.in_dialog:
                self.dialog_tree.update()

            if self.monster_index.opened:
                self.monster_index.update(dt)

            self.tint_screen(dt)

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
