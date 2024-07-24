from settings import *
from entities import Player, Character
from groups import RenderGroup


class DialogTree:
    def __init__(self, player: Player, character: Character, render_group: RenderGroup, font: pg.Font) -> None:
        self.player = player
        self.character = character
        self.render_group = render_group
        self.font = font

        print(self.character.get_dialog())
