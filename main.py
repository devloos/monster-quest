# /// script
# dependencies = [
#  "pygame-ce",
#  "pytmx",
# ]
# ///
import asyncio
import sys
import pygame as pg
from src.game import Game


async def main():
    game = Game()

    while game.is_running:
        game.update()
        await asyncio.sleep(0)  # do not forget that one, it must be called on every frame

    # Closing the game (not strictly required)
    pg.quit()
    sys.exit()


asyncio.run(main())
