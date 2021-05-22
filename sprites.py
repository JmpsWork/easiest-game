"""Any classes which are image related go here."""
from base import Base, size
import pygame
import math


class Sprite(Base):
    """Class for drawing an image."""
    def __init__(self, coords: tuple, path, facing: int=0):
        super().__init__()
        self.x = coords[0]
        self.y = coords[1]
        self.facing = facing
        self.image = path
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.size = self.rect.size
        self.bbox_size = self.size  # Bounding box accounted for rotation
        self.collide = True
        self.die = False

    def __repr__(self):
        return f'(Sprite: ({self.x}, {self.y}), {self.facing})'

    def angle_to_point(self, point: tuple, o_point: tuple=None) -> float:
        if o_point is None:
            o_point = self.x, self.y
        x = point[0] - o_point[0]
        y = point[1] - o_point[1]
        return math.degrees(math.atan2(y, x))

    def bbox_intersect(self, other) -> bool:
        if self.x + self.bbox_size[0] >= other.x and other.x + other.bbox_size[0] >= self.x and \
           self.y + self.bbox_size[1] >= other.y and other.y + other.bbox_size[1] >= self.y:
            return True
        return False

    def accurate_collision(self, other) -> bool:
        """Uses masks to determine if 2 things collide."""
        if self.collide:
            if self.bbox_intersect(other):
                offset = round(self.x - other.x), \
                         round(self.y - other.y)
                if self.mask.overlap(other.mask, offset):  # Overlap returns None or 1 point
                    return True
            return False
        else:
            return False

    def draw(self, screen, offsets: tuple):
        if not self.oob():
            offx, offy = offsets
            if self.facing == 0:
                screen.blit(self.image, (self.x + offx, self.y + offy))
            else:
                w, h = self.size
                box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
                box_rotate = [p.rotate(self.facing) for p in box]

                min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
                max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

                pivot = pygame.math.Vector2(self.size[0] / 2, -self.size[1] / 2)
                pivot_rotate = pivot.rotate(self.facing)
                pivot_move = pivot_rotate - pivot

                origin = (self.x + offx + min_box[0] - pivot_move[0], self.y + offy - max_box[1] + pivot_move[1])

                rotated_image = pygame.transform.rotate(self.image, self.facing)
                self.bbox_size = rotated_image.get_rect().size
                self.mask = pygame.mask.from_surface(rotated_image)
                screen.blit(rotated_image, origin)

    def face(self, other):
        x = other.x - self.x
        y = other.y - self.y
        self.facing = math.degrees(math.atan2(y, x))

    def oob(self) -> bool:
        outside_x = self.x + self.bbox_size[0] < 0 and self.x - self.bbox_size[0] > size[0]
        outside_y = self.y + self.bbox_size[1] < 0 and self.y - self.bbox_size[1] > size[1]
        return outside_x and outside_y

    @property
    def origin(self) -> tuple:
        return self.x + self.size[0] / 2, self.y + self.size[1] / 2

    def rotate(self, amount: int):
        self.facing += amount
        if self.facing > 360:  # Clamp angles
            self.facing -= 360
        elif self.facing < 0:
            self.facing += 360

    def set_pos(self, x: int, y: int):
        self.x = x
        self.y = y

    @property
    def rounded_coords(self) -> tuple:
        return round(self.x), round(self.y)


class AnimSprite(Sprite):
    def __init__(self, coords: tuple, frames: list, delay: int=1, loop: bool=False):
        super().__init__(coords, frames[0])
        self.frames = frames
        self.frame_index = 0
        self.delay = delay
        self.delay_count = 1
        self.do_loop = loop
        self.loop_alt = 0  # If loop_alt = 1, then it will augment until last frame, then decrease to first frame
        self.loop_down = False  # Used with loop_alt when loop_alt == 1

    def get_frame(self, i: int):
        """Returns the frame with index integer value"""
        try:
            return self.frames[i]
        except IndexError:
            return None

    def set_frame(self, i: int):
        self.image = self.frames[i]
        self.frame_index = i

    def loop(self):
        """Loop between self.frames at a set delay."""
        if self.delay_count >= self.delay:
            if self.loop_alt == 0:
                self.frame_index += 1
            elif self.loop_alt == 1:
                if self.loop_down and self.frame_index > 0:
                    self.frame_index -= 1
                else:
                    self.frame_index += 1
                    self.loop_down = False
            if self.frame_index >= len(self.frames):  # Repeat frames
                if self.loop_alt == 0:
                    self.frame_index = 0
                elif self.loop_alt == 1:
                    self.loop_down = True
                    self.frame_index -= 2

            self.image = self.frames[self.frame_index]
            self.delay_count = 0
        else:
            self.delay_count += 1

    def tick(self):
        super().tick()
        if self.do_loop:
            self.loop()
