import pygame
import yaml
from core import resources


class HUD(object):
    def __init__(self, size):
        self.text_render = pygame.Surface(size)
        self.inventory_render = pygame.Surface(size)

        self.set_color_keys()

        self.text_box = None
        self.inventory_ui = InventoryUI(self.inventory_render)

    def render(self, surface):
        if self.text_box is not None:
            surface.blit(self.text_render, (0, 0))
        if self.inventory_ui.is_open:
            self.inventory_ui.render(surface)

    def draw_text(self, text):
        self.text_box = TextBox(self.text_render, text)
        self.text_box.draw()

    def clear_text(self):
        self.text_box = None

    def draw_inventory(self, inv):
        self.inventory_ui.is_open = True
        self.inventory_ui.draw(inv)

    def clear_inventory(self):
        self.inventory_ui.is_open = False

    def set_color_keys(self):
        self.text_render.set_colorkey(pygame.Color("MAGENTA"))
        self.inventory_render.set_colorkey(pygame.Color("MAGENTA"))

    def is_hud_open(self):
        return self.inventory_ui.is_open or self.text_box is not None

    def is_inventory_open(self):
        return self.inventory_ui.is_open

    def show_inventory_hint(self, pos):
        self.inventory_ui.show_hint(pos)


class InventoryUI(object):
    START_POS = (446, 208)
    GAP = 8
    ICON_SIZE = 32
    ROWS = 10
    COLS = 10

    def __init__(self, inventory_surface):
        self.hud = inventory_surface
        self.hud.fill(pygame.Color("MAGENTA"))
        self.inventory_bg = pygame.image.load(resources.get_image_asset("inventory-slots.png"))
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

        self.item_info = self.load_item_info()
        self.items = self.load_items()

        self.inventory_slots = pygame.sprite.Group()

        self.is_open = False
        self.hint = None

    def draw(self, inv):
        self.hud.blit(self.inventory_bg, (0, 0))

        if inv.size() > 0:
            y = InventoryUI.START_POS[1]
            for i, item in enumerate(inv):
                x = InventoryUI.START_POS[0] + (i % InventoryUI.ROWS)*(InventoryUI.ICON_SIZE+InventoryUI.GAP)
                if i % InventoryUI.COLS == 0 and i != 0:
                    y += InventoryUI.ICON_SIZE+InventoryUI.GAP
                self.inventory_slots.add(Item(self.items[item], item, (x, y)))

    def load_items(self):
        items = {}
        for item in resources.list_item_assets():
            if item not in ["__init__.py", "__pycache__"]:
                icon = pygame.image.load(resources.get_item_asset(item))
                items[item.replace(".png", "")] = pygame.transform.scale(icon, (InventoryUI.ICON_SIZE, InventoryUI.ICON_SIZE)).convert_alpha()
        return items

    def load_item_info(self):
        with open(resources.get_data_asset("items.yaml"), "r") as fob:
            return yaml.load(fob)["ITEMS"]

    def render(self, surface):
        x = self.hud.get_width() // 2 - self.inventory_bg.get_width() // 2
        y = self.hud.get_height() // 2 - self.inventory_bg.get_height() // 2
        surface.blit(self.inventory_bg, (x, y))
        self.inventory_slots.draw(surface)
        if self.hint is not None:
            surface.blit(self.hint, (self.hud.get_width() // 2 - self.hint.get_width() // 2, y + 10))

    def show_hint(self, pos):
        for item in self.inventory_slots:
            if item.rect.collidepoint(pos):
                self.hint = self.font.render(self.item_info[item.name]["hint"], 1, pygame.Color("WHITE"))
            else:
                self.hint = None


class Item(pygame.sprite.Sprite):
    def __init__(self, icon, name, pos, *groups):
        super().__init__(*groups)
        self.name = name
        self.image = icon
        self.rect = pygame.Rect(pos, (32, 32))


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
