import pygame
from core import resources


class HUD(object):
    def __init__(self, size):
        self.text_render = pygame.Surface(size)
        self.text_render.set_colorkey(pygame.Color("MAGENTA"))
        self.text_box = None

    def render(self, surface):
        if self.text_box is not None:
            surface.blit(self.text_render, (0, 0))

    def draw_text(self, text):
        self.text_box = TextBox(self.text_render, text)
        self.text_box.draw()

    def clear_text(self):
        self.text_box = None


class TextBox(object):
    def __init__(self, hud_surface, text):
        self.hud = hud_surface
        self.text_box_image = pygame.image.load(resources.get_image_asset("text_box.png")).convert()
        self.font = pygame.font.SysFont("monospace", 20, bold=True)
        self.text = text

    def draw(self):
        label = self.font.render(self.text, 1, pygame.Color("BLACK"))

        self.hud.blit(self.text_box_image, (0, 0))
        self.hud.blit(label, (25, 625))





