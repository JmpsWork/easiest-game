"""Player character"""
from base import *
from shapes import Rectangle
from level import Tile
import math
import pygame


class Player(Base):
    def __init__(self, pos: tuple):
        super().__init__()
        self.x, self.y = pos
        self.vx, self.vy = 0, 0
        self.bg_rect = Rectangle((pos[0], 40, pos[1], 40), BLACK)
        self.center_rect = Rectangle((pos[0], 34, pos[1], 34), (230, 100, 0))
        self.mask = pygame.mask.from_surface(self.bg_rect.surf)
        self.bbox_size = self.bg_rect.surf.get_size()
        # self.debug_line = Line((0, 0), (0, 0), (255, 0, 0), 4)

        self.alpha = 255
        self.speed = 2
        self.hide = False
        self.can_move = True

    @property
    def velocity_direction(self) -> tuple:
        if self.vx < 0:
            x_dir = -1
        elif self.vx > 0:
            x_dir = 1
        else:
            x_dir = 0
        if self.vy < 0:
            y_dir = -1
        elif self.vy > 0:
            y_dir = 1
        else:
            y_dir = 0
        return x_dir, y_dir

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            self.bg_rect.draw(screen, offsets)
            div = (self.bg_rect.width - self.center_rect.width) / 2
            self.center_rect.x = self.bg_rect.x + div
            self.center_rect.y = self.bg_rect.y + div
            self.center_rect.draw(screen, offsets)
            # self.debug_line.draw(screen, offsets)

    def fadeout(self):
        if self.alpha > 0:
            self.alpha -= 6.375 / 2
            self.bg_rect.surf.set_alpha(round(self.alpha))
            self.center_rect.surf.set_alpha(round(self.alpha))

    def fadein(self):
        if self.alpha < 255:
            self.alpha += 6.375 / 2
            self.bg_rect.surf.set_alpha(round(self.alpha))
            self.center_rect.surf.set_alpha(round(self.alpha))

    @property
    def origin(self) -> tuple:
        return self.x + self.bg_rect.width / 2, self.y + self.bg_rect.height / 2

    def rect_intersect(self, rect: Rectangle):
        x, y = self.origin
        if rect.within(self.bg_rect) and rect.collide:
            nx = max(rect.x, min(x, rect.x + rect.width))  # Determine closest point
            ny = max(rect.y, min(y, rect.y + rect.height))

            # self.debug_line.start = nx, ny
            # self.debug_line.dest = x, y

            # Determine which axis to push on, based on which is closest
            if math.fabs(ny - y) > math.fabs(nx - x):
                if y < ny:  # Push up
                    self.y += ny - y - self.bg_rect.height / 2
                elif y > ny:  # Push down
                    self.y += ny - y + self.bg_rect.height / 2
            else:
                if x < nx:  # Push left
                    self.x += nx - x - self.bg_rect.width / 2
                elif x > nx:  # Push right
                    self.x += nx - x + self.bg_rect.width / 2

    def reset(self):
        """Resets changes back to their default."""
        self.set_speed(2)
        self.center_rect.color = 230, 100, 0

    def set_speed(self, speed: int):
        dir = self.velocity_direction
        self.vx = dir[0] * speed
        self.vy = dir[1] * speed
        self.speed = speed

    def teleport(self, x: int, y: int):
        """Sets the players origin to this x and y value."""
        self.x = x - self.bbox_size[0] / 2
        self.y = y - self.bbox_size[1] / 2

    def tick(self):
        if self.can_move or self.hide:
            self.x += self.vx
            self.y += self.vy
        else:
            self.vx = 0
            self.vy = 0
        self.bg_rect.x, self.bg_rect.y = self.x, self.y

    def tile_interact(self, tile: Tile):
        """Executes important tile flags when the player touches one of them."""
        if self.bg_rect.within(tile):
            tile.execute_flag(self)
