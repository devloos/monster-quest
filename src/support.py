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


def import_tilemap(cols, rows, *path):
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
