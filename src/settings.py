import pygame as pg
from pygame.math import Vector2 as vector
from sys import exit
from enum import IntEnum
from pprint import pprint

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 64
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4
DEBUG = False

PLAYER = 'player'
ENEMY = 'enemy'

MAX_RECHARGE = 100

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
    'blue-700': '#1d4ed8',
    'battle': '#F9F0DE',
    'battle-light': '#dbd4c5'
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

NEW_BATTLE_POSITIONS = {
    'player': [
        (430, 215),
        (160, 360),
        (430, 540)
    ],
    'enemy': [
        (850, 215),
        (1125, 360),
        (850, 540)
    ]
}

BATTLE_LAYERS = {
    'outline': 0,
    'name': 1,
    'monster': 2,
    'effects': 3,
    'overlay': 4
}

MAX_STATS = {
    'health': 30,
    'energy': 28,
    'attack': 8,
    'defense': 20,
    'recovery': 10,
    'speed': 3
}
