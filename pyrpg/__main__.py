import pygame
import core.game
import taz.game
import logging

from core.player import Player

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pygame.init()
    pygame.mixer.init()

    player = Player()
    render_context = {
        "SCREEN": pygame.display.set_mode((1280, 800)),
        "RENDER_FREQUENCY": 1000.0 / 60.0
    }

    update_context = {
        "UPDATE_FREQUENCY": 300,
        "CLOCK": pygame.time.Clock(),
        "EXITING_BUILDING": False,
        "PLAYER": player,
        "PLAYER_SPAWN": None
    }

    game = taz.game.Game(update_context, render_context)
    level = core.game.LevelScene("Level", "level_1")
    level2 = core.game.LevelScene("BitcraftsHouse", "bitcrafts_house")
    level3 = core.game.LevelScene("WkmaniresHouse", "wkmanires_house")

    game.register_new_scene(level)
    game.register_new_scene(level2)
    game.register_new_scene(level3)
    game.push_scene_on_stack("Level")
    game.enter_mainloop()
