
from __future__ import annotations
from settings import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sprites.entity import Entity


def check_connection(radius: float, entity: Entity, character: Entity, tolerance: float = 30):
    relation = vector(entity.rect.center) - vector(character.rect.center)

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
