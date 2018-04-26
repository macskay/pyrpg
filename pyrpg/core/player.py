import pygame
import core.resources as resources


SPRITE_STANDING_DOWN = 4
SPRITE_STANDING_LEFT = 5
SPRITE_STANDING_RIGHT = 6
SPRITE_STANDING_UP = 7


class Player(object):
    def __init__(self, pos, size):
        self.sprite_group = self.load_sprites(pos, size)

    def render(self, screen):
        self.sprite_group.draw(screen)

    @staticmethod
    def load_sprites(pos, size):
        sprites = pygame.sprite.GroupSingle()
        sprites.add(PlayerSprite(pos, size))
        return sprites

    def move(self, key):
        if key == pygame.K_DOWN:
            self.update_sprite(SPRITE_STANDING_DOWN)
        elif key == pygame.K_LEFT:
            self.update_sprite(SPRITE_STANDING_LEFT)
        elif key == pygame.K_RIGHT:
            self.update_sprite(SPRITE_STANDING_RIGHT)
        elif key == pygame.K_UP:
            self.update_sprite(SPRITE_STANDING_UP)

    def update_sprite(self, index):
        if self.sprite_group.sprite.active_sprite != index:
            self.sprite_group.sprite.change_active_sprite(index)


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = None
        self.active_sprite = SPRITE_STANDING_RIGHT

        self.sprite_set = self.load_tiles()
        self.change_active_sprite(self.active_sprite)

        self.rect = self.image.get_rect()
        self.move_sprite(pos)

    def update(self, pos):
        self.move_sprite(pos)

    def change_active_sprite(self, index):
        self.image = self.sprite_set[index]
        self.image = pygame.transform.scale(self.image, self.size)
        self.image.set_colorkey(pygame.Color("PINK"))

        self.active_sprite = index

    def move_sprite(self, pos):
        self.rect.x, self.rect.y = pos

    @staticmethod
    def load_tiles():
        tiles = []
        for i in range(3):
            for j in range(4):
                tile = resources.get_tile_from_tileset("vx_characters.png", (i, j))
                tiles.append(tile)
        return tiles







