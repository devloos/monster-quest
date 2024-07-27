from __future__ import annotations

from settings import *
from util.support import check_connection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dialog import DialogTree
    from sprites import Sprite


class Entity(pg.sprite.Sprite):
    def __init__(self, pos, frames: dict[str, list[pg.Surface]], state: str, groups) -> None:
        super().__init__(groups)

        self.frame_index = 0
        self.frames = frames

        self.state = state
        self.direction = vector()

        self.image = self.frames[self.get_state()][self.frame_index]
        self.rect = self.image.get_frect(center=pos)

        self.z = WorldLayer.main
        self.hitbox = self.rect.inflate(-(self.rect.width / 2), -60)

    def get_state(self):
        moving = bool(self.direction)

        if not moving:
            return f'{self.state}_idle'

        return self.state

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt

        state = self.get_state()
        if self.frame_index > len(self.frames[state]):
            self.frame_index = 0

        index = int(self.frame_index) % len(self.frames[state])
        self.image = self.frames[state][index]

    def get_y_sort(self) -> float:
        return self.rect.centery

    def face_target_pos(self, target_pos: tuple[float, float]) -> None:
        relation = vector(target_pos) - vector(self.rect.center)

        # this is using the rect since a y less than 30 means player is either
        # left or right. this is true since the rect is taller but its width
        # is shorter
        if abs(relation.y) < 30:
            self.state = 'right' if relation.x > 0 else 'left'
        else:
            self.state = 'down' if relation.y > 0 else 'up'


class Player(Entity):
    def __init__(self, pos, frames: dict, state: str, collision_group: list[pg.sprite.Sprite], groups) -> None:
        super().__init__(pos, frames, state, groups)

        self.collision_group = collision_group
        self.blocked = False

    def _input(self):
        keys = pg.key.get_pressed()
        input_vector = vector()

        if keys[pg.K_UP]:
            self.state = 'up'
            input_vector.y -= 1

        if keys[pg.K_DOWN]:
            self.state = 'down'
            input_vector.y += 1

        if keys[pg.K_LEFT]:
            self.state = 'left'
            input_vector.x -= 1

        if keys[pg.K_RIGHT]:
            self.state = 'right'
            input_vector.x += 1

        if input_vector:
            self.direction = input_vector.normalize()
        else:
            self.direction = input_vector

    def move(self, dt: float):
        speed = 250

        if DEBUG:
            keys = pg.key.get_pressed()

            if keys[pg.K_LSHIFT]:
                speed = 800

        self.rect.centerx += self.direction.x * speed * dt
        self.hitbox.centerx = self.rect.centerx
        self.horizontal_collision()

        self.rect.centery += self.direction.y * speed * dt
        self.hitbox.centery = self.rect.centery
        self.vertical_collision()

    def horizontal_collision(self) -> bool:
        sprite: Sprite | Entity

        for sprite in self.collision_group:
            if sprite.hitbox.colliderect(self.hitbox):
                if self.direction.x > 0:
                    self.hitbox.right = sprite.hitbox.left

                if self.direction.x < 0:
                    self.hitbox.left = sprite.hitbox.right

                self.rect.centerx = self.hitbox.centerx

    def vertical_collision(self) -> bool:
        sprite: Sprite | Entity

        for sprite in self.collision_group:
            if sprite.hitbox.colliderect(self.hitbox):
                if self.direction.y > 0:
                    self.hitbox.bottom = sprite.hitbox.top

                if self.direction.y < 0:
                    self.hitbox.top = sprite.hitbox.bottom

                self.rect.centery = self.hitbox.centery

    def update(self, dt: float) -> None:
        if not self.blocked:
            self._input()
            self.move(dt)

        self.animate(dt)

    def get_center_pos(self) -> vector:
        x = self.rect.center[0]
        y = self.rect.center[1]

        return vector(x, y)

    def block(self) -> None:
        self.blocked = True
        self.direction = vector()

    def unblock(self) -> None:
        self.blocked = False


class Character(Entity):
    def __init__(
        self, pos, frames: dict, state: str, character_data: dict,
        radius: float, player: Player, dialog_tree: DialogTree,
        font: pg.Font, collision_group: pg.sprite.Group, groups
    ) -> None:
        super().__init__(pos, frames, state, groups)

        self.character_data = character_data
        self.radius = radius
        self.player = player
        self.dialog_tree = dialog_tree
        self.font = font
        self.has_moved = False

        self.collision_group = pg.sprite.Group()

        for sprite in collision_group:
            if not sprite == self:
                self.collision_group.add(sprite)

    def get_dialog(self) -> list:
        if self.character_data['defeated']:
            return self.character_data['dialog']['defeated']

        return self.character_data['dialog']['default']

    def raycast(self) -> None:
        if self.dialog_tree.in_dialog:
            return

        if check_connection(self.radius, self, self.player) and self.has_line_of_sight() and not self.has_moved:
            self.player.face_target_pos(self.rect.center)
            self.player.block()

            relation = (
                vector(self.player.rect.center) - vector(self.rect.center)
            ).normalize()

            self.direction = vector(round(relation.x), round(relation.y))

    def move(self, dt: float) -> None:
        if self.has_moved:
            return

        speed = 400

        if not self.hitbox.inflate(10, 10).colliderect(self.player.hitbox):
            self.rect.center += self.direction * speed * dt
            self.hitbox.center = self.rect.center
        else:
            self.has_moved = True
            self.direction = vector()
            self.dialog_tree.setup(self.player, self, self.font)

    def has_line_of_sight(self) -> bool:
        if vector(self.rect.center).distance_to(self.player.rect.center) >= self.radius:
            return

        sprite: pg.sprite.Sprite

        for sprite in self.collision_group:
            # does the sprite collide with a line from character to player
            # e.g. character ----------- sprite ------------ player -> TRUE
            if sprite.rect.clipline(self.rect.center, self.player.rect.center):
                return False

        return True

    def update(self, dt) -> None:
        self.raycast()
        self.move(dt)
        self.animate(dt)
