import pygame
import core.game
import taz.game

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()

    render_context = {
        "screen": pygame.display.set_mode((1280, 800)),
        "RENDER_FREQUENCY": 1000.0 / 60.0
    }

    update_context = {
        "UPDATE_FREQUENCY": 300,
        "clock": pygame.time.Clock()
    }


    game = taz.game.Game(update_context, render_context)
    red_scene = core.game.LevelScene("Level")
    
    game.register_new_scene(red_scene)
    game.push_scene_on_stack("Level")
    game.enter_mainloop()
