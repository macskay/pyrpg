import logging
import pygame
import pytmx
import taz.game

logger = logging.getLogger(__name__)

class RedScene(taz.game.Scene):
    def __init__(self, identifier):
        super(RedScene, self).__init__(identifier)

        self.screen = None

    def initialize(self):
        self.screen = self.game.render_context["screen"]

    def render(self):
        pygame.display.flip()
        self.screen.fill(pygame.Color("red"))

    def update(self):
        self.handle_inputs()

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise taz.game.Game.GameExitException

