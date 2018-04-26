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

        self.screen = None
        self.map = None
        self.render_surface = None
        self.player = None
        self.scaling = None

    def initialize(self):
        self.screen = self.game.render_context["screen"]
        self.map = self.load_map()
        self.render_surface = pygame.Surface((self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight))
        self.scaling = [x/y for x, y in zip(self.screen.get_size(), self.render_surface.get_size())]
        self.player = self.load_player()

    def render(self):
        pygame.display.flip()
        self.render_layers()
        self.render_player()

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_clicks(event)
            if event.type == pygame.KEYDOWN:
                self.handle_keybord_input(event)

    def load_map(self):
        return pytmx.util_pygame.load_pygame(resources.get_map_asset('mymap.tmx'))

    def get_layers(self):
        for layer in self.map:
            if isinstance(layer, pytmx.TiledTileLayer):
                yield layer

    def render_layers(self):
        for layer in self.get_layers():
            self.render_layer(layer)
        self.screen.blit(pygame.transform.scale(self.render_surface, self.screen.get_size()).convert(), (0, 0))

    def render_layer(self, layer):
        for x, y, tile in layer.tiles():
            self.render_surface.blit(tile, (x * tile.get_width(), y * tile.get_height()))

    def can_walk_to_position(self, position):
        scaled_position = self.get_scaled_position(position)
        for obj in self.get_object_group("Walls"):
            obj = self.convert_object_to_rect(obj)
            if obj.collidepoint(scaled_position):
                return True
        return False

    def get_object_group(self, name):
        for og in self.map.objectgroups:
            if og.name == name:
                return og

    def get_scaled_position(self, pos):
        return pos[0] / self.scaling[0], pos[1] / self.scaling[1]

    @staticmethod
    def convert_object_to_rect(obj):
        return pygame.Rect(obj.x, obj.y, obj.width, obj.height)

    def load_player(self):
        tile = self.get_object_group("Player")[0]
        pos = int(tile.x*self.scaling[0]), int(tile.y*self.scaling[1])
        size = int(tile.width*self.scaling[0]), int(tile.height*self.scaling[1])
        return player.Player(pos, size)

    # only for debugging, get's removed eventually
    def handle_mouse_clicks(self, event):
        if self.can_walk_to_position(event.pos):
            print("collision")

    def render_player(self):
        self.player.render(self.screen)

    def handle_keybord_input(self, event):
        if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
            self.player.move(event.key)







