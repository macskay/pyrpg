import pygame
import core.resources as resources
import animation as ani
import logging
import yaml
from ast import literal_eval as make_tuple

logger = logging.getLogger(__name__)

SPRITE_STANDING_DOWN = 4
SPRITE_STANDING_LEFT = 5
SPRITE_STANDING_RIGHT = 6
SPRITE_STANDING_UP = 7

SPRITE_WALKING_RIGHT_LEFT_FOOT = 2
SPRITE_WALKING_RIGHT_RIGHT_FOOT = 10
SPRITE_WALKING_LEFT_LEFT_FOOT = 9
SPRITE_WALKING_LEFT_RIGHT_FOOT = 1
SPRITE_WALKING_UP_LEFT_FOOT = 3
SPRITE_WALKING_UP_RIGHT_FOOT = 11
SPRITE_WALKING_DOWN_LEFT_FOOT = 0
SPRITE_WALKING_DOWN_RIGHT_FOOT = 8

TILE_SIZE = 16


class Inventory(object):
    MAX_SIZE = 10

    def __init__(self):
        self.storage = []

    def add(self, item):
        self.storage.append(item)

    def remove(self, item):
        self.storage.remove(item)

    def size(self):
        return len(self.storage)

    def __str__(self):
        return "Bag {}/10: {}".format(len(self.storage), self.storage)

    def __iter__(self):
        for item in self.storage:
            yield item


class Player(object):
    def __init__(self):
        self.game = None
        self.standing_sprite = None
        self.previous_pos = ()
        self.sprite_group = None
        self.foot = True
        self.animations = pygame.sprite.Group()
        self.animation_running = False
        self.inventory = Inventory()

    def spawn(self, game, spawn_pos=None):
        self.game = game

        scaling = self.get_scaling()
        tile = self.get_object_group("Player")[0]

        pos = (int(tile.x*scaling[0]), int(tile.y*scaling[1])) if spawn_pos is None else make_tuple(spawn_pos)
        size = int(tile.width*scaling[0]), int(tile.height*scaling[1])
        self.sprite_group = self.load_sprites(pos, size)

    def move_player_to_pos(self, pos):
        sprite = self.sprite_group.sprite
        active = sprite.active_sprite
        self.sprite_group = self.load_sprites(pos, sprite.size, active)

    def get_object_group(self, name):
        for og in self.game.update_context["MAP_OBJECTS"]:
            if og.name == name:
                return og

    @staticmethod
    def load_sprites(pos, size, active=None):
        sprites = pygame.sprite.GroupSingle()
        sprites.add(PlayerSprite(pos, size, active))
        return sprites

    def update(self, key, delta):
        if not self.animation_running:
            self.move(key)
        self.animations.update(delta)

    def move(self, key):
        sprite = self.sprite_group.sprite
        if key[pygame.K_DOWN]:
            self.update_sprite(SPRITE_STANDING_DOWN)
            self.start_animiation(y=sprite.rect.height)
        elif key[pygame.K_LEFT]:
            self.update_sprite(SPRITE_STANDING_LEFT)
            self.start_animiation(x=-sprite.rect.width)
        elif key[pygame.K_RIGHT]:
            self.update_sprite(SPRITE_STANDING_RIGHT)
            self.start_animiation(x=sprite.rect.width)
        elif key[pygame.K_UP]:
            self.update_sprite(SPRITE_STANDING_UP)
            self.start_animiation(y=-sprite.rect.height)

    def update_sprite(self, index):
        if self.sprite_group.sprite.active_sprite != index:
            self.sprite_group.sprite.change_active_sprite(index)

    def start_animiation(self, x=0.0, y=0.0, relative=True, duration=250):
        sprite = self.sprite_group.sprite
        if self.can_walk_to_pos(sprite, x, y):
            logger.debug("Dest: {}".format((sprite.rect.left+x, sprite.rect.top+y)))
            self.previous_pos = sprite.rect.topleft
            a = ani.Animation(sprite.rect, x=int(x), y=int(y), duration=duration, relative=relative)
            a.schedule(self.clear_animations)
            self.update_walking_sprite(x, y)
            self.animation_running = True
            self.animations.add(a)

    def get_scaling(self):
        return self.game.update_context["MAP_SCALING"]

    def can_walk_to_pos(self, sprite, x, y):
        new_pos = self.get_scaled_position((sprite.rect.x+x, sprite.rect.y+y))
        for obj in self.get_object_group("Walls"):
            obj = self.convert_object_to_rect(obj)
            scaling = self.get_scaling()
            size = sprite.rect.width // scaling[0], sprite.rect.height // scaling[1]
            rect = pygame.Rect(new_pos, size)
            if obj.colliderect(rect):
                return False
        return True

    def get_scaled_position(self, pos):
        scaling = self.get_scaling()
        return pos[0] / scaling[0], pos[1] / scaling[1]

    def update_walking_sprite(self, x, y):
        walk = None
        if x < 0:
            walk = SPRITE_WALKING_LEFT_RIGHT_FOOT if self.foot else SPRITE_WALKING_LEFT_LEFT_FOOT
            self.standing_sprite = SPRITE_STANDING_LEFT
        elif x > 0:
            walk = SPRITE_WALKING_RIGHT_LEFT_FOOT if self.foot else SPRITE_WALKING_RIGHT_RIGHT_FOOT
            self.standing_sprite = SPRITE_STANDING_RIGHT
        elif y < 0:
            walk = SPRITE_WALKING_UP_LEFT_FOOT if self.foot else SPRITE_WALKING_UP_RIGHT_FOOT
            self.standing_sprite = SPRITE_STANDING_UP
        elif y > 0:
            walk = SPRITE_WALKING_DOWN_LEFT_FOOT if self.foot else SPRITE_WALKING_DOWN_RIGHT_FOOT
            self.standing_sprite = SPRITE_STANDING_DOWN

        self.update_sprite(walk)
        self.foot = False if self.foot else True

    def render(self, screen):
        self.sprite_group.draw(screen)

    def clear_animations(self):
        self.animations.empty()
        if not self.game.render_context["key_held"]:
            self.update_sprite(self.standing_sprite)
            self.standing_sprite = None
        self.animation_running = False

    @staticmethod
    def convert_object_to_rect(obj):
        return pygame.Rect(obj.x, obj.y, obj.width, obj.height)

    def use(self):
        player_facing = self.sprite_group.sprite.active_sprite
        is_facing, obj_props = self.facing_usable_object(player_facing)
        if is_facing:
            if "item" in obj_props:
                if obj_props["item"] not in self.inventory:
                    self.inventory.add(obj_props["item"])
                else:
                    return obj_props["collected"]
            return obj_props["hint"]
        return None

    def facing_usable_object(self, player_facing):
        sprite_rect = self.sprite_group.sprite.rect
        facing_pos = self.get_facing_pos(player_facing, sprite_rect)
        new_pos = self.get_scaled_position(facing_pos)
        for obj in self.get_object_group("Usables"):
            if (obj.x, obj.y) == new_pos:
                return True, obj.properties
        return False, None

    @staticmethod
    def get_facing_pos(player_facing, sprite_rect):
        facing_x = sprite_rect.left
        facing_y = sprite_rect.top
        if player_facing == SPRITE_STANDING_RIGHT:
            facing_x += sprite_rect.width
        elif player_facing == SPRITE_STANDING_LEFT:
            facing_x -= sprite_rect.width
        elif player_facing == SPRITE_STANDING_UP:
            facing_y -= sprite_rect.height
        elif player_facing == SPRITE_STANDING_DOWN:
            facing_y += sprite_rect.height
        return facing_x, facing_y

    def collides_trigger(self, obj):
        sprite_rect = self.sprite_group.sprite.rect
        new_pos = self.get_scaled_position(sprite_rect.topleft)

        return self.convert_object_to_rect(obj).collidepoint(*new_pos)

    def exit_building(self):
        dest = self.previous_pos
        self.start_animiation(x=dest[0], y=dest[1], relative=False)

    def meet_requisites(self, props):
        if "pre_req" in props:
            if props["pre_req"] in self.inventory:
                return True
            return False
        return True


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size, active=None):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = None
        self.active_sprite = SPRITE_STANDING_RIGHT if active is None else active

        self.sprite_set = self.load_tiles()
        self.change_active_sprite(self.active_sprite)

        self.rect = self.image.get_rect()
        self.move_sprite(pos)

    @staticmethod
    def load_tiles():
        tiles = []
        for i in range(3):
            for j in range(4):
                tile = resources.get_tile_from_tileset("vx_characters.png", (i, j))
                tiles.append(tile)
        return tiles

    def change_active_sprite(self, index):
        self.image = self.sprite_set[index]
        self.image = pygame.transform.scale(self.image, self.size).convert()
        self.image.set_colorkey(pygame.Color("MAGENTA"))

        self.active_sprite = index

    def update(self, pos):
        self.move_sprite(pos)

    def move_sprite(self, pos):
        self.rect.x, self.rect.y = pos
