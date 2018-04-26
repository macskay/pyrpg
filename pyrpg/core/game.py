import logging
import pygame
import taz.game as taz
import core.resources as resources
import core.player as player
import pytmx

logger = logging.getLogger(__name__)


class LevelScene(taz.Scene):
    def __init__(self, identifier):
        super(LevelScene, self).__init__(identifier)

        self.key_held = False
        self.screen = None
        self.map = None
        self.low_layers_render_surface = None
        self.top_layer_render_surface = None
        self.top_layer = None
        self.player = None
        self.scaling = None
        self.delta_accumulator = 0.0

    def initialize(self):
        self.screen = self.game.render_context["screen"]
        self.map = self.load_map()
        self.low_layers_render_surface = pygame.Surface((self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight))
        self.top_layer_render_surface = pygame.Surface((self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight), pygame.SRCALPHA)
        self.scaling = [x / y for x, y in zip(self.screen.get_size(), self.low_layers_render_surface.get_size())]
        self.player = self.load_player()

        self.build_layer_surfaces()

    def render(self):
        if self.delta_accumulator >= self.game.render_context["RENDER_FREQUENCY"]:
            pygame.display.flip()

            self.render_low_layers()
            self.render_player()
            self.render_top_layer()

            self.delta_accumulator = 0.0

    def update(self):
        pygame.display.set_caption("FPS: {}".format(int(self.game.update_context["clock"].get_fps())))
        delta = self.game.update_context["clock"].tick(self.game.update_context["UPDATE_FREQUENCY"])
        self.delta_accumulator += delta

        self.handle_inputs(delta)
        self.player.update(pygame.key.get_pressed(), delta)

    def pause(self):
        pass

    def resume(self):
        pass

    def tear_down(self):
        pass

    def handle_inputs(self, delta):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise taz.Game.GameExitException
            if event.type == pygame.KEYDOWN:
                self.handle_keybord_input(event, delta)
            if event.type == pygame.KEYUP:
                self.game.render_context["key_held"] = False

    def load_map(self):
        return pytmx.util_pygame.load_pygame(resources.get_map_asset('mymap.tmx'))

    def get_layers(self):
        for layer in self.map:
            if isinstance(layer, pytmx.TiledTileLayer):
                yield layer

    def render_low_layers(self):
        self.screen.blit(pygame.transform.scale(self.low_layers_render_surface, self.screen.get_size()), (0, 0))

    def render_top_layer(self):
        self.screen.blit(pygame.transform.scale(self.top_layer_render_surface, self.screen.get_size()), (0, 0))

    def render_layer(self, layer, surface):
        for x, y, tile in layer.tiles():
            surface.blit(tile, (x * tile.get_width(), y * tile.get_height()))

    def load_player(self):
        return player.Player(list(self.map.objectgroups), self.scaling, self.game)

    def render_player(self):
        self.player.render(self.screen)

    def handle_keybord_input(self, event, delta):
        if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
            self.game.render_context["key_held"] = True
            if not self.player.animation_running:
                self.player.update(pygame.key.get_pressed(), delta)

    def build_layer_surfaces(self):
        for layer in self.get_layers():
            if layer.name == "Tops":
                self.render_layer(layer, self.top_layer_render_surface)
            else:
                self.render_layer(layer, self.low_layers_render_surface)








