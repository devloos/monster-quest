
from __future__ import annotations
from src.settings import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sprites.entity import Entity


def check_connection(radius: float, entity: Entity, target: Entity, tolerance: float = 30):
    relation = vector(entity.rect.center) - vector(target.rect.center)

    if relation.length() > radius:
        return False

    state = entity.state

    # check if on the right side and facing left
    if state == 'left' and relation.x > 0 and abs(relation.y) < tolerance:
        return True

    # check if on the left side and facing right
    if state == 'right' and relation.x < 0 and abs(relation.y) < tolerance:
        return True

    # check if on the bottom side and facing up
    if state == 'up' and relation.y > 0 and abs(relation.x) < tolerance:
        return True

    # check if on top side and facing down
    if state == 'down' and relation.y < 0 and abs(relation.x) < tolerance:
        return True

    return False


def calculate_monster_outlines(
    monster_frames: dict[str, dict[str, list[pg.Surface]]], width: int
) -> dict[str, dict[str, list[pg.Surface]]]:
    outline_frames: dict[str, dict[str, list[pg.Surface]]] = {}

    for monster, state_frames in monster_frames.items():
        outline_frames[monster] = {}

        for state, frames in state_frames.items():
            outline_frames[monster][state] = []

            for frame in frames:
                new_surf = pg.Surface(
                    vector(frame.get_size()) + vector(width * 2), pg.SRCALPHA
                )
                new_surf.fill((0, 0, 0, 0))

                white_frame = pg.mask.from_surface(frame).to_surface()
                white_frame.set_colorkey('black')

                # create an outline frame for each side
                new_surf.blit(white_frame, (0, 0))
                new_surf.blit(white_frame, (width, 0))
                new_surf.blit(white_frame, (width * 2, 0))
                new_surf.blit(white_frame, (width * 2, width))
                new_surf.blit(white_frame, (width * 2, width * 2))
                new_surf.blit(white_frame, (width, width * 2))
                new_surf.blit(white_frame, (0, width * 2))
                new_surf.blit(white_frame, (0, width))

                outline_frames[monster][state].append(new_surf)

    return outline_frames


def flip_surfaces(surfaces: list[pg.Surface], horizontal: bool, vertical: bool) -> list[pg.Surface]:
    surfs: list[pg.Surface] = []

    for surf in surfaces:
        surfs.append(pg.transform.flip(surf, horizontal, vertical))

    return surfs
