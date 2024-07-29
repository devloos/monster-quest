import pygame as pg
from pygame.math import Vector2 as vector
from sys import exit
from enum import IntEnum

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 64
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4
DEBUG = True

COLORS = {
    'white': '#f4fefa',
    'pure white': '#ffffff',
    'dark': '#2b292c',
    'light': '#c8c8c8',
    'gray': '#3a373b',
    'gold': '#bfa100',
    'light-gray': '#4b484d',
    'fire': '#f8a060',
    'water': '#50b0d8',
    'plant': '#64a990',
    'normal': '#ffffff',
    'black': '#000000',
    'red': '#f03131',
    'blue': '#66d7ee',
    'blue-700': '#1d4ed8'
}


class WorldLayer(IntEnum):
    water = 0,
    bg = 1,
    shadow = 2,
    main = 3,
    top = 4


BATTLE_POSITIONS = {
    'left': {
        'top': (360, 260),
        'center': (190, 400),
        'bottom': (410, 520)
    },
    'right': {
        'top': (900, 260),
        'center': (1110, 390),
        'bottom': (900, 550)
    }
}

BATTLE_LAYERS = {
    'outline': 0,
    'name': 1,
    'monster': 2,
    'effects': 3,
    'overlay': 4
}

BATTLE_CHOICES = {
    'full': {
        'fight':  {'pos': vector(30, -60), 'icon': 'sword'},
        'defend': {'pos': vector(40, -20), 'icon': 'shield'},
        'switch': {'pos': vector(40, 20), 'icon': 'arrows'},
        'catch':  {'pos': vector(30, 60), 'icon': 'hand'}
    },

    'limited': {
        'fight':  {'pos': vector(30, -40), 'icon': 'sword'},
        'defend': {'pos': vector(40, 0), 'icon': 'shield'},
        'switch': {'pos': vector(30, 40), 'icon': 'arrows'}
    }
}

MAX_STATS = {
    'health': 30,
    'energy': 28,
    'attack': 8,
    'defense': 20,
    'recovery': 10,
    'speed': 3
}
