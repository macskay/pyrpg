import pygame
import core.game
import taz.game
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pygame.init()
    pygame.mixer.init()

    render_context = {
        "screen": pygame.display.set_mode((1280, 800)),
        "RENDER_FREQUENCY": 1000.0 / 60.0
    }

    update_context = {
        "UPDATE_FREQUENCY": 300,
        "clock": pygame.time.Clock(),
        "EXITING_BUILDING": False
    }

    game = taz.game.Game(update_context, render_context)
    red_scene = core.game.LevelScene("Level", "level_1")
    new_scene = core.game.LevelScene("players_house", "players_house")

    game.register_new_scene(new_scene)
    game.register_new_scene(red_scene)
    game.push_scene_on_stack("Level")
    game.enter_mainloop()
