import pygame as pg
from abc import ABC, abstractmethod


class IHitbox(ABC):

    @abstractmethod
    def get_hitbox(self) -> pg.FRect:
        pass
