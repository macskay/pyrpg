import pygame
import core.game
import taz.game

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()

    render_context = {
            "screen" : pygame.display.set_mode((1280, 800))
    }

    game = taz.game.Game({}, render_context)
    red_scene = core.game.RedScene("Red")
    
    game.register_new_scene(red_scene)
    game.push_scene_on_stack("Red")
    game.enter_mainloop()
