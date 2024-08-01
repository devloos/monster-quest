from __future__ import annotations

from settings import *
from sprites.entity import Entity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textures.texture import Texture


class Player(Entity):
    def __init__(
        self, pos, frames: dict, state: str,
        shadow: pg.Surface, alert: pg.Surface,
        collision_group: list[pg.sprite.Sprite], groups
    ) -> None:
        super().__init__(pos, frames, state, shadow, alert, groups)

        self.collision_group = collision_group
        self.blocked = False
        self.alerted = False

    def input(self):
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
        sprite: Texture | Entity

        for sprite in self.collision_group:
            if sprite.hitbox.colliderect(self.hitbox):
                if self.direction.x > 0:
                    self.hitbox.right = sprite.hitbox.left

                if self.direction.x < 0:
                    self.hitbox.left = sprite.hitbox.right

                self.rect.centerx = self.hitbox.centerx

    def vertical_collision(self) -> bool:
        sprite: Texture | Entity

        for sprite in self.collision_group:
            if sprite.hitbox.colliderect(self.hitbox):
                if self.direction.y > 0:
                    self.hitbox.bottom = sprite.hitbox.top

                if self.direction.y < 0:
                    self.hitbox.top = sprite.hitbox.bottom

                self.rect.centery = self.hitbox.centery

    def draw(self, offset: vector) -> None:
        if self.alerted:
            self.screen.blit(
                self.alert, self.rect.midtop + offset + vector(-50, -100)
            )

        self.screen.blit(
            self.shadow, self.rect.topleft + offset + vector(40, 110)
        )

        self.screen.blit(
            self.image, self.rect.topleft + offset
        )

        # todo: make monster patch better by overlaying leaf pedals

    def update(self, dt: float) -> None:
        if not self.blocked:
            self.input()
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
