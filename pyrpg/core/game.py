import logging

import pygame
import taz.game as taz
import core.resources as resources
import core.ui as ui
import pytmx

logger = logging.getLogger(__name__)


class LevelScene(taz.Scene):
    def __init__(self, identifier, level_name):
        super(LevelScene, self).__init__(identifier)

        self.key_held = False
        self.screen = None
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
        self.screen = self.game.render_context["SCREEN"]

        self.load_map("{}.tmx".format(self.level_name))
        self.player = self.game.update_context["PLAYER"]
        self.player.spawn(self.game, self.game.update_context["PLAYER_SPAWN"])
        self.ui = ui.HUD(self.screen.get_size())

    def load_map(self, level_name):
        m = pytmx.util_pygame.load_pygame(resources.get_map_asset(level_name))
        self.game.update_context["MAP_OBJECTS"] = list(m.objectgroups)
        self.game.update_context["MAP_LAYERS"] = list(m.layers)

        self.low_layers_render_surface = pygame.Surface(
            (m.width * m.tilewidth, m.height * m.tileheight))
        self.top_layer_render_surface = pygame.Surface(
            (m.width * m.tilewidth, m.height * m.tileheight), pygame.SRCALPHA)

        self.game.update_context["MAP_SCALING"] = [x / y for x, y in zip(self.screen.get_size(), self.low_layers_render_surface.get_size())]

        self.build_layer_surfaces()

    def build_layer_surfaces(self):
        for layer in self.get_layers():
            if layer.name == "Tops":
                self.render_layer(layer, self.top_layer_render_surface)
            else:
                self.render_layer(layer, self.low_layers_render_surface)

    def get_layers(self):
        for layer in self.game.update_context["MAP_LAYERS"]:
            if isinstance(layer, pytmx.TiledTileLayer):
                yield layer

    @staticmethod
    def render_layer(layer, surface):
        for x, y, tile in layer.tiles():
            surface.blit(tile, (x * tile.get_width(), y * tile.get_height()))

    def update(self):
        pygame.display.set_caption("FPS: {}".format(int(self.game.update_context["CLOCK"].get_fps())))
        delta = self.game.update_context["CLOCK"].tick(self.game.update_context["UPDATE_FREQUENCY"])
        self.delta_accumulator += delta

        self.handle_inputs(delta)
        self.check_for_collision()
        if not self.ui.is_hud_open():
            self.player.update(pygame.key.get_pressed(), delta)

    def check_for_collision(self):
        for obj in self.get_object_group("Trigger"):
            if self.player.collides_trigger(obj):
                if self.player.meet_requisites(obj.properties):
                    if "spawn_pos" in obj.properties:
                        self.game.update_context["PLAYER_SPAWN"] = obj.properties["spawn_pos"]
                    if obj.properties["scene"] == "push":
                        self.game.push_scene_on_stack(obj.properties["level"])
                    elif obj.properties["scene"] == "pop":
                        self.game.pop_scene_from_stack()
                else:
                    hint = obj.properties["hint"]
                    if hint is not None:
                        self.ui.draw_text(hint)
                    self.player.move_player_to_pos(self.player.previous_pos)

    def get_object_group(self, name):
        for og in self.game.update_context["MAP_OBJECTS"]:
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
            if event.type == pygame.MOUSEMOTION:
                if self.ui.is_inventory_open():
                    self.ui.show_inventory_hint(event.pos)

    def handle_keybord_input(self, event, delta):
        if not self.ui.is_hud_open():
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

        if event.key == pygame.K_i:
            self.ui.draw_inventory(self.player.inventory) if not self.ui.is_inventory_open() else self.ui.clear_inventory()

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
        self.load_map("{}.tmx".format(self.level_name))
        self.player.spawn(self.game, self.game.update_context["PLAYER_SPAWN"])

        self.game.update_context["PLAYER_SPAWN"] = None

    def tear_down(self):
        pass
