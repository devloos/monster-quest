from src.settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame


def import_image(*path, alpha=True, format='png') -> pg.Surface:
    full_path = join(*path) + f'.{format}'

    if (alpha):
        surf = pg.image.load(full_path).convert_alpha()
    else:
        surf = pg.image.load(full_path).convert()

    return surf


def import_folder(*path):
    frames = []
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            surf = pg.image.load(full_path).convert_alpha()
            frames.append(surf)

    return frames


def import_folder_dict(*path) -> dict[str, pg.Surface]:
    frames = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surf = pg.image.load(full_path).convert_alpha()
            frames[image_name.split('.')[0]] = surf

    return frames


def import_sub_folders(*path):
    frames = {}
    for _, sub_folders, __ in walk(join(*path)):
        if not sub_folders:
            continue

        for sub_folder in sub_folders:
            frames[sub_folder] = import_folder(*path, sub_folder)

    return frames


def import_tilemap(cols, rows, *path) -> dict:
    frames = {}
    surf = import_image(*path)

    cell_width = surf.get_width() / cols
    cell_height = surf.get_height() / rows

    for col in range(cols):
        for row in range(rows):
            cutout_rect = pg.FRect(
                col * cell_width, row * cell_height, cell_width, cell_height
            )
            cutout_surf = pg.Surface((cell_width, cell_height)).convert_alpha()
            # fill bg with color we dont use
            cutout_surf.fill('green')
            # ignore that color
            cutout_surf.set_colorkey('green')
            cutout_surf.blit(surf, (0, 0), cutout_rect)
            frames[(col, row)] = cutout_surf

    return frames


def import_attacks(cols, rows, *path) -> dict[str, list[pg.Surface]]:
    normalized_frames = {}

    for _, __, image_names in walk(join(*path)):
        image_name: str
        for image_name in image_names:
            name = image_name.split('.')[0]
            frames = list(import_tilemap(cols, rows, *path, name).values())
            normalized_frames[name] = frames

    return normalized_frames


def import_character_helper(cols, rows, *path) -> dict:
    # frames[(0, 0)] = Surface
    frames = import_tilemap(cols, rows, *path)
    directions = ['down', 'left', 'right', 'up']
    normalized_frames = {}

    for index, direction in enumerate(directions):
        normalized_frames[direction] = []
        normalized_frames[f'{direction}_idle'] = [frames[(0, index)]]

        for col in range(cols):
            normalized_frames[direction].append(frames[(col, index)])

    return normalized_frames


def import_characters(cols, rows, *path) -> dict:
    # each character will have its corresponding side
    # e.g. normalized_frames['player'] = {'down': [surfaces]}
    normalized_frames = {}

    for _, __, image_names in walk(join(*path)):
        image_name: str
        for image_name in image_names:
            name = image_name.split('.')[0]
            frames = import_character_helper(cols, rows, *path, name)
            normalized_frames[name] = frames

    return normalized_frames


def import_coast(cols, rows, *path) -> dict:
    STEP = 3
    frames = import_tilemap(cols, rows, *path)
    normalized_frames = {}
    terrains = [
        'grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i'
    ]

    sides = {
        'topleft': (0, 0), 'top': (1, 0), 'topright': (2, 0),
        'left': (0, 1), 'right': (2, 1),
        'bottomleft': (0, 2), 'bottom': (1, 2), 'bottomright': (2, 2),
    }

    for terrain_index, terrain in enumerate(terrains):
        # each terrain will have its corresponding sides
        # e.g. normalized_frames['grass'] = {'top': [surfaces]}
        normalized_frames[terrain] = {}
        for side, pos in sides.items():
            normalized_frames[terrain][side] = []

            # for each terrain move down using current row and store frame
            # into what ever side we are doing this for
            for row in range(0, rows, STEP):
                frame = frames[(pos[0] + terrain_index * STEP, pos[1] + row)]
                normalized_frames[terrain][side].append(frame)

    return normalized_frames


def import_tmx_maps(*path) -> dict:
    tmx_dict = {}

    for folder_path, _, file_names in walk(join(*path)):
        file_name: str
        for file_name in file_names:
            tmx_dict[file_name.split('.')[0]] = load_pygame(
                join(folder_path, file_name)
            )

    return tmx_dict


def import_monster_frames(cols, rows, *path) -> dict:
    monster_frames = {}

    for _, _, image_names in walk(join(*path)):
        image_name: str

        for image_name in image_names:
            image_name = image_name.split('.')[0]
            frame_dict = import_tilemap(cols, rows, *path, image_name)
            monster_frames[image_name] = {}

            for row, state in enumerate(('idle', 'attack')):
                monster_frames[image_name][state] = []
                for col in range(cols):
                    monster_frames[image_name][state].append(
                        frame_dict[(col, row)]
                    )

    return monster_frames


def import_audio(*path) -> dict[str, pg.mixer.Sound]:
    audio: dict[str, pg.mixer.Sound] = {}

    for _, _, audio_names in walk(join(*path)):
        audio_name: str

        for audio_name in audio_names:
            normalized_name = audio_name.split('.')[0]
            audio[normalized_name] = pg.mixer.Sound(join(*path, 'battle.ogg'))

            volume = 0.1 if DEBUG else 0.4
            audio[normalized_name].set_volume(volume)

    return audio
