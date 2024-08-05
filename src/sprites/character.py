from __future__ import annotations

from settings import *
from sprites.player import Player
from sprites.entity import Entity
from util.support import check_connection
from typing import TYPE_CHECKING
from random import choice
from util.timer import Timer
from time import time
from monster import Monster

if TYPE_CHECKING:
    from overlays.dialog import DialogTree


class Character(Entity):
    def __init__(
        self, pos, frames: dict, state: str, character_data: dict,
        radius: float, player: Player, dialog_tree: DialogTree,
        font: pg.Font, shadow: pg.Surface, alert: pg.Surface,
        collision_group: pg.sprite.Group, notice_sound: pg.mixer.Sound, groups
    ) -> None:
        super().__init__(pos, frames, state, shadow, alert, groups, 'character')

        self.character_data = character_data
        self.radius = radius
        self.player = player
        self.dialog_tree = dialog_tree
        self.font = font
        self.has_moved = False
        self.is_nurse = self.character_data['is_nurse']
        self.can_alert_player = self.character_data['can_alert_player']
        self.biome = self.character_data['biome']
        self.notice_sound = notice_sound

        self.monsters: list[Monster] = []

        for (monster_name, level) in self.character_data['monsters'].values():
            self.monsters.append(Monster(monster_name, level))

        self.timers = {
            'look_around': Timer(
                2000, True, True, self.choose_random_state
            ),
        }

        self.collision_group = pg.sprite.Group()

        for sprite in collision_group:
            if not sprite == self:
                self.collision_group.add(sprite)

    def get_dialog(self) -> list:
        if self.character_data['defeated']:
            return self.character_data['dialog']['defeated']

        return self.character_data['dialog']['default']

    def start_move(self) -> None:
        relation = (
            vector(self.player.rect.center) - vector(self.rect.center)
        ).normalize()

        self.direction = vector(round(relation.x), round(relation.y))

    def raycast(self) -> None:
        if not self.can_alert_player:
            return

        if self.dialog_tree.in_dialog:
            return

        if check_connection(self.radius, self, self.player) and self.has_line_of_sight() and not self.has_moved:
            self.notice_sound.play()
            self.player.face_target_pos(self.rect.center)
            self.player.block()
            self.block()

            self.dialog_tree.block()
            self.dialog_tree.in_dialog = True
            self.player.alerted = True

            self.start_move()

    def move(self, dt: float) -> None:
        if self.has_moved:
            return

        speed = 200

        if self.hitbox.inflate(10, 10).colliderect(self.player.hitbox):
            self.has_moved = True
            self.player.alerted = False
            self.direction = vector()
            self.dialog_tree.setup(self.player, self, self.font)
        else:
            self.rect.center += self.direction * speed * dt
            self.hitbox.center = self.rect.center

    def has_line_of_sight(self) -> bool:
        if vector(self.rect.center).distance_to(self.player.rect.center) >= self.radius:
            return False

        sprite: pg.sprite.Sprite

        for sprite in self.collision_group:
            # does the sprite collide with a line from character to player
            # e.g. character ----------- sprite ------------ player -> TRUE
            if sprite.rect.clipline(self.rect.center, self.player.rect.center):
                return False

        return True

    def choose_random_state(self) -> None:
        if not self.blocked:
            self.state = choice(self.character_data['directions'])

    def update_timers(self) -> None:
        timer: Timer

        for timer in self.timers.values():
            timer.update()

    def draw(self, offset: vector) -> None:
        self.screen.blit(
            self.shadow, self.rect.topleft + offset + vector(40, 110)
        )

        self.screen.blit(
            self.image, self.rect.topleft + offset
        )

    def update(self, dt) -> None:
        self.update_timers()
        self.raycast()
        self.move(dt)
        self.animate(dt)
