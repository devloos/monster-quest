from settings import *
from os.path import join
from os import walk

# imports


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


def import_folder_dict(*path):
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
            cutout_rect = pg.Rect(
                col * cell_width, row * cell_height, cell_width, cell_height)
            cutout_surf = pg.Surface((cell_width, cell_height))
            cutout_surf.fill('green')
            cutout_surf.set_colorkey('green')
            cutout_surf.blit(surf, (0, 0), cutout_rect)
            frames[(col, row)] = cutout_surf

    return frames


def import_characters_helper(cols, rows, *path) -> dict:
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
            frames = import_characters_helper(cols, rows, *path, name)
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
