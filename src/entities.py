from settings import *
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


class Character(Entity):
    def __init__(self, pos, frames: dict, state: str, groups) -> None:
        super().__init__(pos, frames, state, groups)


class Player(Entity):
    def __init__(self, pos, frames: dict, state: str, collision_group: list[pg.sprite.Sprite], groups) -> None:
        super().__init__(pos, frames, state, groups)

        self.collision_group = collision_group

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
        self._input()
        self.animate(dt)
        self.move(dt)

    def get_center_pos(self) -> vector:
        x = self.rect.center[0]
        y = self.rect.center[1]

        return vector(x, y)
