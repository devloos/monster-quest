from settings import *
from util.imports import *
from util.support import check_connection
from pytmx import TiledMap, TiledObject
from os.path import join
from textures.texture import Texture
from textures.animated_texture import AnimatedTexture
from textures.monster_patch_texture import MonsterPatchTexture
from textures.collidable_texture import CollidableTexture
from textures.world_texture import WorldTransition
from sprites.player import Player
from sprites.character import Character
from groups import RenderGroup
from game_data import *
from overlays.dialog import DialogTree
from overlays.monster_index import MonsterIndex
from overlays.battle import Battle
from overlays.transition import Transition
from overlays.evolution import Evolution
from monster import Monster


class World:
    def __init__(self, name: str, player_start_pos: str) -> None:
        self.name = name
        self.player_start_pos = player_start_pos


class Game:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        pg.display.set_caption('Monster Quest')
        self.clock = pg.time.Clock()

        # transitions
        self.transition = Transition(self.block_player, self.unblock_player)
        self.world = World('world', 'house')

        # import all assets
        self.import_assets()

        # groups
        self.render_group = RenderGroup()
        self.collision_group = pg.sprite.Group()
        self.character_group = pg.sprite.Group()
        self.world_transitions = pg.sprite.Group()

        self.player_monsters = [
            Monster('Friolera', 30),
            Monster('Larvea', 1),
            Monster('Jacana', 12),
            Monster('Pouch', 4),
            # Monster('Charmadillo', 30),
            # Monster('Finsta', 16),
            # Monster('Draem', 23),
            # Monster('Cleaf', 20),
            # Monster('Cindrill', 14)
        ]

        # overlay
        self.monster_index = MonsterIndex(
            self.player_monsters, self.monster_frames, self.ui_icons, self.fonts
        )

        self.battle = Battle(
            self.monster_frames, self.transition, self.ui_icons, self.attack_frames,
            self.battle_backgrounds, self.audio, self.fonts
        )

        self.dialog_tree = DialogTree(self.battle, self.transition, self.render_group)
        self.evolution = Evolution(
            self.monster_frames, self.star_frames, self.audio['evolution'], self.fonts['dialog']
        )

        # essentially start game
        self.setup(self.tmx_maps[self.world.name], self.world.player_start_pos)

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

        self.ui_icons = import_folder_dict('graphics', 'ui')

        self.battle_backgrounds = import_folder_dict('graphics', 'backgrounds')

        self.attack_frames = import_attacks(4, 1,  'graphics', 'attacks')

        self.star_frames = import_folder('graphics', 'other', 'star-animation')

        self.audio = import_audio('audio')

    def setup(self, tmx_map: TiledMap, player_start_pos) -> None:
        # todo: correct player position after world change
        self.render_group.empty()
        self.collision_group.empty()
        self.character_group.empty()
        self.world_transitions.empty()

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

        # Worlds
        for obj in tmx_map.get_layer_by_name('Transition'):
            pos = (obj.x, obj.y)
            size = (obj.width, obj.height)
            target = (obj.properties['target'], obj.properties['pos'])
            WorldTransition(pos, size, target, self.world_transitions)

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
                    self.player_monsters,
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
                    self.audio['notice'],
                    groups
                )

        # Monsters
        for obj in tmx_map.get_layer_by_name('Monsters'):
            z = WorldLayer.main
            biome = obj.properties['biome']
            monster_names = str(obj.properties['monsters']).split(',')
            level = obj.properties['level']

            if biome == 'sand':
                z = WorldLayer.bg

            MonsterPatchTexture(
                (obj.x, obj.y), obj.image, z, biome, self.player,
                monster_names, level, self.battle,
                self.transition, self.render_group
            )

        self.audio['overworld'].play(-1)

    def block_player(self) -> None:
        self.player.block()

    def unblock_player(self) -> None:
        self.player.unblock()

    def input(self):
        if self.dialog_tree.in_dialog or self.battle.in_progress:
            return

        keys = pg.key.get_just_pressed()

        if keys[pg.K_SPACE]:
            character: Character

            for character in self.character_group:
                if check_connection(200, self.player, character):
                    self.dialog_tree.setup(
                        self.player, character, self.fonts['dialog']
                    )

        if keys[pg.K_TAB]:
            self.monster_index.opened = not self.monster_index.opened
            self.player.blocked = not self.player.blocked

        if keys[pg.K_ESCAPE]:
            self.monster_index.opened = False
            self.player.blocked = False

    def check_world_change(self) -> None:
        world: WorldTransition

        for world in self.world_transitions:
            if self.player.hitbox.colliderect(world.rect) and not self.transition.in_transition:
                self.world = World(world.target[0], world.target[1])

                self.transition.start(
                    lambda: self.setup(
                        self.tmx_maps[self.world.name], self.world.player_start_pos
                    )
                )

    def end_evolution(self, monster: Monster) -> None:
        monster_evolution = Monster(monster.evolution['name'], monster.evolution['level'])
        index = self.player_monsters.index(monster)
        self.player_monsters[index] = monster_evolution
        self.player.unblock()
        self.audio['overworld'].play(-1)

    def check_evolution(self) -> None:
        if self.evolution.in_evolution:
            return

        for monster in self.player_monsters:
            if monster.should_evolve():
                self.audio['overworld'].stop()
                self.player.block()
                self.evolution.setup(monster, self.end_evolution)

    def run(self) -> None:
        while True:
            dt = self.clock.tick() / 1000
            # handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            # handle game input
            self.check_world_change()

            if not self.transition.in_transition and \
               not self.battle.in_progress and \
               not self.dialog_tree.in_dialog:
                self.check_evolution()

            self.input()

            # handle game logic
            self.render_group.update(dt)
            self.screen.fill((0, 0, 0))
            self.render_group.draw(self.player.get_center_pos())

            if self.dialog_tree.in_dialog:
                self.dialog_tree.update()

            if self.monster_index.opened:
                self.monster_index.update(dt)

            if self.battle.in_progress:
                self.battle.update(dt)

            if self.evolution.in_evolution and \
               not self.transition.in_transition and \
               not self.dialog_tree.in_dialog and \
               not self.battle.in_progress:

                self.evolution.update(dt)

            if self.transition.in_transition:
                self.transition.update(dt)

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
