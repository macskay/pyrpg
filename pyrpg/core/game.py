import logging

import core
import pygame
import taz.game as taz
import core.resources as resources
import core.player as player
import core.ui as ui
import pytmx
import yaml

logger = logging.getLogger(__name__)


class LevelScene(taz.Scene):
    def __init__(self, identifier, level_name):
        super(LevelScene, self).__init__(identifier)

        self.key_held = False
        self.screen = None
        self.map = None
        self.low_layers_render_surface = None
        self.top_layer_render_surface = None
        self.top_layer = None
        self.player = None
        self.level_context = None
        self.ui = None
        self.scaling = None
        self.exit_pos = None
        self.level_name = level_name
        self.delta_accumulator = 0.0

    def initialize(self):
        self.screen = self.game.render_context["screen"]

        self.load_map("{}.tmx".format(self.level_name))
        self.player = self.load_player()
        self.ui = ui.HUD(self.screen.get_size())

    def load_map(self, level_name):
        self.map = pytmx.util_pygame.load_pygame(resources.get_map_asset(level_name))
        self.low_layers_render_surface = pygame.Surface(
            (self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight))
        self.top_layer_render_surface = pygame.Surface(
            (self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight), pygame.SRCALPHA)
        self.scaling = [x / y for x, y in zip(self.screen.get_size(), self.low_layers_render_surface.get_size())]
        self.build_layer_surfaces()

    def load_player(self):
        return player.Player(list(self.map.objectgroups), self.scaling, self.game)

    def build_layer_surfaces(self):
        for layer in self.get_layers():
            if layer.name == "Tops":
                self.render_layer(layer, self.top_layer_render_surface)
            else:
                self.render_layer(layer, self.low_layers_render_surface)

    def get_layers(self):
        for layer in self.map:
            if isinstance(layer, pytmx.TiledTileLayer):
                yield layer

    @staticmethod
    def render_layer(layer, surface):
        for x, y, tile in layer.tiles():
            surface.blit(tile, (x * tile.get_width(), y * tile.get_height()))

    def update(self):
        pygame.display.set_caption("FPS: {}".format(int(self.game.update_context["clock"].get_fps())))
        delta = self.game.update_context["clock"].tick(self.game.update_context["UPDATE_FREQUENCY"])
        self.delta_accumulator += delta

        self.handle_inputs(delta)
        self.check_for_collision()
        if self.ui.text_box is None:
            self.player.update(pygame.key.get_pressed(), delta)

    def check_for_collision(self):
        for obj in self.get_object_group("Trigger"):
            if self.player.collides_trigger(obj):
                new_level = obj.properties["level"]
                if "LAST_MAP_NAME" in self.game.update_context and self.game.update_context["LAST_MAP_NAME"] == new_level:
                    self.player.start_animiation(*self.game.update_context["LAST_MAP_EXIT_POS"], relative=False, duration=1)
                    self.player.update_sprite(self.game.update_context["LAST_MAP_FACING_DIRECTION"])
                else:
                    self.game.update_context["LAST_MAP_EXIT_POS"] = self.player.previous_pos
                    self.game.update_context["LAST_MAP_NAME"] = self.level_name
                    self.game.update_context["LAST_MAP_FACING_DIRECTION"] = self.player.sprite_group.sprite.active_sprite

                self.level_name = obj.properties["level"]
                self.load_map("{}.tmx".format(self.level_name))

    def get_object_group(self, name):
        for og in self.map.objectgroups:
            if og.name == name:
                return og

    def handle_inputs(self, delta):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise taz.Game.GameExitException
            if event.type == pygame.KEYDOWN:
                self.handle_keybord_input(event, delta)
            if event.type == pygame.KEYUP:
                self.game.render_context["key_held"] = False

    def handle_keybord_input(self, event, delta):
        if self.ui.text_box is None:
            if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                self.game.render_context["key_held"] = True
                if not self.player.animation_running:
                    self.player.update(pygame.key.get_pressed(), delta)
            if event.key == pygame.K_SPACE:
                hint = self.player.use()
                if hint is not None:
                    self.ui.draw_text(hint)
        else:
            if event.key == pygame.K_SPACE:
                self.ui.clear_text()

    def render(self):
        if self.delta_accumulator >= self.game.render_context["RENDER_FREQUENCY"]:
            pygame.display.flip()

            self.render_low_layers()
            self.render_player()
            self.render_top_layer()
            self.ui.render(self.screen)

            self.delta_accumulator = 0.0

    def render_low_layers(self):
        self.screen.blit(pygame.transform.scale(self.low_layers_render_surface, self.screen.get_size()), (0, 0))

    def render_player(self):
        self.player.render(self.screen)

    def render_top_layer(self):
        self.screen.blit(pygame.transform.scale(self.top_layer_render_surface, self.screen.get_size()), (0, 0))

    def pause(self):
        pass

    def resume(self):
        if self.game.update_context["EXITING_BUILDING"]:
            self.player.exit_building()

    def tear_down(self):
        pass
