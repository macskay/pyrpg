import logging
import pygame
import taz.game as taz
import core.resources as resources
import pytmx

logger = logging.getLogger(__name__)


class LevelScene(taz.Scene):
    def __init__(self, identifier):
        super(LevelScene, self).__init__(identifier)

        self.screen = None
        self.map = None

    def initialize(self):
        self.screen = self.game.render_context["screen"]
        self.load_map()

    def render(self):
        pygame.display.flip()
        # self.screen.fill(pygame.Color("red"))
        self.render_layers()

    def update(self):
        self.handle_inputs()

    def pause(self):
        pass

    def resume(self):
        pass

    def tear_down(self):
        pass

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise taz.Game.GameExitException

    def load_map(self):
        self.map = pytmx.util_pygame.load_pygame(resources.get_map_asset('mymap.tmx'))

    def get_layers(self):
        for layer in self.map:
            if isinstance(layer, pytmx.TiledTileLayer):
                yield layer

    def render_layers(self):
        for layer in self.get_layers():
            self.render_layer(layer)

    def render_layer(self, layer):
        s = pygame.Surface((512, 320))
        for x, y, tile in layer.tiles():
            s.blit(tile, (x * tile.get_width(), y * tile.get_height()))
        # s = pygame.transform.scale(s, self.screen.get_size())
        self.screen.blit(s, (0, 0))

    # def render_layer(self, layer):
    #     for x, y, tile in layer.tiles():
    #         self.screen.blit(tile, (x * tile.get_width(), y * tile.get_width()))





