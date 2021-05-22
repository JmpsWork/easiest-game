"""Level geometry and objects"""
from base import *
from shapes import Rectangle, Line, Circle, Text
from sprites import Sprite, AnimSprite
import json
import pygame
import math


class Tile(Rectangle):
    def __init__(self, grid_x, grid_y, color: tuple, level):
        super().__init__((grid_x * 50, 50, grid_y * 50, 50), color)
        self.gx = grid_x
        self.gy = grid_y
        self.end = False
        self.checkpoint = False
        self.hide = False
        self.nil = False
        self.warp = False, 0, 0  # Does warp, warp X. warp Y
        self.level = level
        self.reset_point = 0, 0

    def __repr__(self):
        return f'Tile({self.gx, self.gy}, {self.color})'

    def draw(self, screen, offsets: tuple):
        if self.nil is False and self.hide is False:
            super().draw(screen, offsets)

    def execute_flag(self, player):
        """Gets called when the player interacts with this tile."""
        if self.checkpoint:
            self.level.player_spawn = self.reset_point
            for coin in self.level.coins:
                if coin.collected:
                    coin.perm_collected = True
        if self.end:
            if self.level.coins_collected >= self.level.coins_needed:
                self.level.end = True
                if self.level.next is False:
                    self.level.final_end = True

        if self.warp[0]:
            player.teleport(self.warp[1], self.warp[2])


class Wall(Line):
    def __init__(self, start: tuple, end: tuple, color: tuple=BLACK, width=6, axis: str='xy', associate: int=None):
        self.cstart = start  # Points for collision, obsolete
        self.cdest = end
        self.axis = axis
        self.hide = False
        self.collide = True
        self.id = associate
        super().__init__(start, end, color, width)

        half_width = self.width / 2
        start = start[0] - half_width, start[1] - half_width
        end = end[0] + half_width, end[1] + half_width
        width, height = end[0] - start[0], end[1] - start[1]
        if width < 0:  # The start point is the end point
            start = start[0] + width, start[1]
            width = math.fabs(width)
        if height < 0:
            start = start[0], start[1] + height
            height = math.fabs(height)
        self.crect = Rectangle((start[0], width, start[1], height), color)

    def __repr__(self):
        return f'Wall({self.start}, {self.dest})'

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            self.crect.draw(screen, offsets)

    def nearest_point(self, relative: tuple):
        """Returns the nearest point relative to another point."""
        dist1 = math.sqrt((relative[0] - self.cstart[0])**2 + (relative[1] - self.cstart[1])**2)
        dist2 = math.sqrt((relative[0] - self.cdest[0])**2 + (relative[1] - self.cdest[1])**2)
        if dist1 < dist2:
            return self.cstart
        else:
            return self.cdest

    def on_key_collect(self, key):
        if self.id == key.id:
            self.collide = False
            self.crect.collide = False
            self.crect.surf.set_alpha(70)

    def intersect(self, o_line: Line):
        """Checks if 2 lines intersects. If true, returns the intersection point"""
        p0_x, p0_y = self.cstart
        p1_x, p1_y = self.cdest
        p2_x, p2_y = o_line.start
        p3_x, p3_y = o_line.dest

        s1_x = p1_x - p0_x
        s1_y = p1_y - p0_y
        s2_x = p3_x - p2_x
        s2_y = p3_y - p2_y

        s1 = -s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)
        s2 = -s2_x * s1_y + s1_x * s2_y
        if s1 == 0 or s2 == 0:  # Avoid division by zero
            return False

        s = s1 / s2
        t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

        if (s >= 0 and s <= 1) and (t >= 0 and t <= 1):
            i_x = p0_x + (t * s1_x)
            i_y = p0_y + t * s1_y
            return i_x, i_y
        return False

    def set_position(self, x: int, y: int, ex: int, ey: int):
        start = min(x, ex), min(y, ey)
        end = max(x, ex), max(y, ey)

        half_width = self.width / 2
        start = start[0] - half_width, start[1] - half_width
        end = end[0] + half_width, end[1] + half_width
        width, height = end[0] - start[0], end[1] - start[1]
        if width < 0:  # The start point is the end point
            start = start[0] + width, start[1]
            width = math.fabs(width)
        if height < 0:
            start = start[0], start[1] + height
            height = math.fabs(height)
        self.crect = Rectangle((start[0], width, start[1], height), self.color)

    def within(self, other: Rectangle):
        if self.collide:
            within_x = self.crect.x + self.crect.width >= other.x and other.x + other.width >= self.crect.x
            within_y = self.crect.y + self.crect.height >= other.y and other.y + other.height >= self.crect.y
            return within_x and within_y
        return False


class Enemy(Circle):
    """Enemy level object. Sends player back to the start when touched."""
    def __init__(self, position: tuple, speed: int=0, path: list=[], color: tuple=BLUE_ENEMY):
        super().__init__(position, 16, BLACK)
        self.scircle = Circle(position, 9, color)
        self.hide = False
        self.path = path  # Enemies can traverse between multiple points at a certain speed
        self.pivot = None  # Enemies can pivot around a point at speed degrees per second
        self.point_index = 0
        self.speed = speed
        self.vx = 0
        self.vy = 0
        self.steps = 0  # Until next point
        self.move = True

        self.newx, self.newy = self.x, self.y
        self.pivot_angle = 0
        if path != []:  # Calculate # of steps and velocity to next point from current position
            cx, cy = self.x, self.y
            self.next_point = self.path[self.point_index]
            nx, ny = self.next_point
            d = math.sqrt((cx - nx) ** 2 + (cy - ny) ** 2)
            self.steps = d / self.speed
            a = self.angle_to((nx, ny))
            self.vx = self.speed * math.cos(a)
            self.vy = self.speed * math.sin(a)

    def __repr__(self):
        return f'Enemy({self.x, self.y})'

    def angle_to(self, other) -> float:
        x = other[0] - self.x
        y = other[1] - self.y
        return math.atan2(y, x)

    def colliding(self, other: Rectangle):
        """Collision detection between player rectangle vs this circle."""
        if other.collide is False:
            return False
        nx = max(other.x, min(self.newx, other.x + other.width))  # Determine closest point
        ny = max(other.y, min(self.newy, other.y + other.height))

        dx = self.newx - nx
        dy = self.newy - ny
        dist = dx**2 + dy**2
        if dist <= self.radius ** 2:
            return True
        return False

    def draw(self, screen, offsets):
        if self.hide is False:
            ox, oy = offsets
            x, y = self.newx, self.newy
            pygame.draw.circle(screen, self.color, (round(x - ox), round(y - oy)), self.radius)
            new_pos = x, y
            self.scircle.x, self.scircle.y = round(new_pos[0]), round(new_pos[1])
            self.scircle.draw(screen, offsets)

    def pivot_around(self):
        """Called every tick for enemies with a pivot."""
        self.pivot_angle += self.speed / 60
        if self.pivot_angle > 360:
            self.pivot_angle -= 360
        elif self.pivot_angle < 360:
            self.pivot_angle += 360

        angle = math.radians(self.pivot_angle)
        x = self.x - self.pivot[0]
        y = self.y - self.pivot[1]

        newx = x * math.cos(angle) - y * math.sin(angle)
        newy = x * math.sin(angle) + y * math.cos(angle)

        self.newx = newx + self.pivot[0]
        self.newy = newy + self.pivot[1]

    def tick(self):
        super().tick()
        if self.hide is False and self.move:
            if self.path != []:
                self.travel()
            elif self.pivot:
                self.pivot_around()

    def travel(self):
        if self.steps > 0:
            self.x += self.vx
            self.y += self.vy
            self.newx, self.newy = self.x, self.y
            self.steps -= 1
        else:
            self.point_index += 1
            self.x, self.y = self.next_point
            if self.point_index > len(self.path) - 1:
                self.point_index = 0
            self.new_path()

    def new_path(self):
        cx, cy = self.next_point
        self.next_point = self.path[self.point_index]
        nx, ny = self.next_point
        d = math.sqrt((cx - nx)**2 + (cy - ny)**2)
        self.steps = d / self.speed
        a = self.angle_to((nx, ny))
        vx = self.speed * math.cos(a)
        vy = self.speed * math.sin(a)
        self.vx = vx
        self.vy = vy


class Coin(Circle):
    """Coin level object"""
    def __init__(self, position: tuple):
        super().__init__(position, 15, BLACK)
        self.scircle = Circle(position, 10, (220, 220, 40))
        self.hide = False
        self.collected = False
        self.perm_collected = False  # If a player hits a checkpoint and this coin is collected this switches to true

    def __repr__(self):
        return f'Coin({self.x, self.y})'

    def colliding(self, other: Rectangle):
        """Collision detection between player rectangle vs this circle."""
        if self.collected or other.collide is False:
            return False
        nx = max(other.x, min(self.x, other.x + other.width))  # Determine closest point
        ny = max(other.y, min(self.y, other.y + other.height))

        dx = self.x - nx
        dy = self.y - ny
        dist = dx**2 + dy**2
        if dist <= self.radius ** 2:
            return True
        return False

    def draw(self, screen, offsets):
        if not self.collected and self.hide is False:
            super().draw(screen, offsets)
            new_pos = self.x, self.y
            self.scircle.x, self.scircle.y = new_pos
            self.scircle.draw(screen, offsets)


class PowerUp(Circle):
    """PowerUps provide a bonus to the player."""
    def __init__(self, position: tuple, name: str):
        super().__init__(position, 14, BLACK)
        self.scircle = Circle(position, 9, (40, 230, 230))
        self.hide = False
        self.type = name
        self.collected = False

    def colliding(self, other: Rectangle):
        """Collision detection between player rectangle vs this circle."""
        if self.collected or other.collide is False:
            return False
        nx = max(other.x, min(self.x, other.x + other.width))  # Determine closest point
        ny = max(other.y, min(self.y, other.y + other.height))

        dx = self.x - nx
        dy = self.y - ny
        dist = dx**2 + dy**2
        if dist <= self.radius ** 2:
            return True
        return False

    def draw(self, screen, offsets):
        if not self.collected and self.hide is False:
            super().draw(screen, offsets)
            new_pos = self.x, self.y
            self.scircle.x, self.scircle.y = new_pos
            self.scircle.draw(screen, offsets)


class Key(Sprite):
    """Key level object."""
    def __init__(self, pos: tuple, associate: int, color: tuple=BLACK):
        super().__init__(pos, pygame.image.load('images/key.png').convert_alpha())
        self.x -= self.size[0] / 2
        self.y -= self.size[1] / 2
        self.id = associate  # Any walls with the same id will unlock when this key is grabbed
        self.color = color
        self.set_color(color)
        self.hide = False

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            super().draw(screen, offsets)

    def set_color(self, color: tuple):
        """Changes any pure white pixels of this key to a specific color."""
        r, g, b, = color
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                p_r, p_g, p_b, p_a = self.image.get_at((x, y))
                total = sum([p_r, p_g, p_b])
                if total == 765:
                    self.image.set_at((x, y), pygame.Color(r, g, b, p_a))

    def within(self, other: Rectangle):
        if self.collide:
            within_x = self.x + self.size[0] >= other.x and other.x + other.width >= self.x
            within_y = self.y + self.size[1] >= other.y and other.y + other.height >= self.y
            return within_x and within_y


class LevelObject(AnimSprite):
    """An animated sprite which can be placed in a level."""
    def __init__(self, coords, frames: list, delay: int, loop: bool=False):
        super().__init__(coords, frames, delay, loop)


class Level(Base):
    """A level contains all tiles, walls, enemies, etc. needed for a level.
    Loads information from a json file for levels.
    Also contains real tile level information (coins, player spawn, etc.)"""
    def __init__(self, level_file: str, font, offset: tuple=(0, 0), first: bool=False):
        super().__init__()
        self.ox, self.oy = offset
        self.size_y = 0
        self.size_x = 0
        self.tiles = []  # Keep track of level info
        self.walls = []
        self.enemies = []
        self.coins = []
        self.important_tiles = []  # Any tile with player interacting features goes here
        self.keys = []
        self.text = None
        self.text_index = 0
        self.coins_needed = 0
        self.next = False
        self.this_blurb = ''  # Current level blurb
        self.blurb = ''  # Next level blurb
        self.load(level_file, font, first)

        self.coins_collected = 0
        self.player_tile = None
        self.end = False
        self.final = False
        self.hidden = False

    def get_tile(self, x: int, y: int) -> [Tile, None]:
        try:
            if x > self.size_x or x < 0:
                return None
            if y > self.size_y or y < 0:
                return None
            return self.tiles[y][x]
        except IndexError:
            return None

    def hide(self):
        """Hide all level objects from being drawn."""
        self.hidden = True
        for row_y in self.tiles:
            for tile in row_y:
                tile.hide = True
        for wall in self.walls:
            wall.hide = True
        for enemy in self.enemies:
            enemy.hide = True
        for coin in self.coins:
            coin.hide = True
        for key in self.keys:
            key.hide = True
        self.text.hide = True

    def unhide(self):
        """Reveal all level objects from being drawn."""
        self.hidden = False
        for row_y in self.tiles:
            for tile in row_y:
                tile.hide = False
        for wall in self.walls:
            wall.hide = False
        for enemy in self.enemies:
            enemy.hide = False
        for coin in self.coins:
            coin.hide = False
        for key in self.keys:
            key.hide = False
        self.text.hide = False

    def load(self, file: str, font, first: bool=False):
        """Converts json info in to level objects. Do not call more than once!"""
        with open(f'data/tiletemplates.json') as tile_template_data:  # Load tile templates and level data
            tile_templates = json.loads(tile_template_data.read())
        with open(f'data/{file}.json') as level_data:
            level_info = json.loads(level_data.read())
            self.player_spawn = level_info.get('spawnx', 50), level_info.get('spawny', 50)
            self.size_y = len(level_info['tiles'])
            self.size_x = len(level_info['tiles'][0])
            if level_info.get('centered', False):
                self.ox = size[0] / 2 - (self.size_x * 50) / 2
                self.oy = size[1] / 2 - (self.size_y * 50) / 2
            for y, row_y in enumerate(level_info["tiles"]):
                tiles_y = []
                for x, tile_data in enumerate(row_y):
                    template = tile_data.get('template', False)
                    if template:
                        template_data = tile_templates[template]  # Get tile data from tile itself or template
                    else:
                        template_data = tile_data
                    r, g, b = tile_data.get('color', template_data.get('color', BLUE_BASIC))
                    new_tile = Tile(x, y, (r, g, b), self)  # Create tile with data
                    new_tile.x += self.ox
                    new_tile.y += self.oy
                    new_tile.nil = template_data.get('nil', False)
                    new_tile.checkpoint = template_data.get('checkpoint', False)  # Set various flags
                    new_tile.end = template_data.get('end_level', False)
                    new_tile.reset_point = tile_data.get('newx', template_data.get('newx', 0)), tile_data.get('newy', template_data.get('newy', 0))
                    new_tile.warp = tile_data.get('warp', template_data.get('warp', False)), tile_data.get('warpx', template_data.get('warpx', 0)) + self.ox, tile_data.get('warpy', template_data.get('warpy', 0)) + self.oy
                    if new_tile.end or new_tile.checkpoint or new_tile.warp[0]:
                        self.important_tiles.append(new_tile)
                        add_to_drawn('collides', new_tile, 0)
                    else:
                        add_to_drawn('bg', new_tile)
                    tiles_y.append(new_tile)
                self.tiles.append(tiles_y)

            for wall in level_info['walls']:
                start = wall['sx'] + self.ox, wall['sy'] + self.oy  # start x and y to end x and y
                end = wall['ex'] + self.ox, wall['ey'] + self.oy
                color = wall.get('color', BLACK)
                wall = Wall(start, end, color, 6, wall.get('axis', 'xy'), associate=wall.get('id', None))
                add_to_drawn('collides', wall)
                self.walls.append(wall)
                if wall.id is not None:
                    wall.crect.surf.set_alpha(200)

            for coin in level_info.get('coins', []):
                new_coin = Coin((round(coin['x'] + self.ox), round(coin['y'] + self.oy)))
                add_to_drawn('collides', new_coin)
                self.coins.append(new_coin)
                self.coins_needed += 1

            for enemy in level_info.get('enemies', []):
                path = []
                for point in enemy.get('path', []):
                    x, y = point
                    x += self.ox
                    y += self.oy
                    path.append((x, y))
                new_enemy = Enemy((round(enemy['x'] + self.ox), round(enemy['y'] + self.oy)), enemy.get('speed', 0), path, enemy.get('color', BLUE_ENEMY))
                pivot = enemy.get('pivot', None)
                if pivot:
                    new_enemy.pivot = pivot[0] + self.ox, pivot[1] + self.oy
                    new_enemy.pivot_angle += enemy.get('angle', 0)
                add_to_drawn('collides', new_enemy)
                self.enemies.append(new_enemy)

            for key in level_info.get('keys', []):
                new_key = Key((key['x'] + self.ox, key['y'] + self.oy), key['id'], key.get('color', (255, 255, 255)))
                add_to_drawn('collides', new_key)
                self.keys.append(new_key)

            self.text = Text((size[0] / 2, 100), (20, 20, 20), level_info.get('tutorial_text'), font, centered=True)
            add_to_drawn('ui', self.text)
            self.player_spawn = level_info.get('spawnx', 100), level_info.get('spawny', 100)
            self.next = level_info.get('next_level', False)
            self.this_blurb = level_info.get('blurb', 'Sample Text')
            if first:
                self.blurb = level_info.get('blurb', 'Sample Text')
            elif self.next:
                with open(f'data/{self.next}.json') as level_data2:
                    level_info2 = json.loads(level_data2.read())
                    self.blurb = level_info2.get('blurb', 'Sample Text')
            else:  # Otherwise final level
                self.blurb = 'FINAL'
            if self.next is False:
                self.final = True
            self.hidden = False

    def neighbour(self, x: int, y: int) -> list:
        neighbours = [self.get_tile(x - 1, y - 1),
                      self.get_tile(x, y - 1),
                      self.get_tile(x + 1, y - 1),
                      self.get_tile(x - 1, y),
                      self.get_tile(x + 1, y),
                      self.get_tile(x - 1, y + 1),
                      self.get_tile(x, y + 1),
                      self.get_tile(x + 1, y + 1)]
        return neighbours

    def reset(self):
        """Removes and resets all walls, tiles, important values, etc. from existence."""
        for row_y in self.tiles:
            for tile in row_y:
                tile.die = True
        for wall in self.walls:
            wall.die = True
        for enemy in self.enemies:
            enemy.die = True
        for coin in self.coins:
            coin.die = True

        self.tiles = []
        self.walls = []
        self.enemies = []
        self.coins = []
        self.important_tiles = []
        self.text.die = True

        self.coins_collected = 0
        self.coins_needed = 0

    def unlock(self, key: Key):
        """Disabled collisions on walls with the same ID as this key"""
        for wall in self.walls:
            wall.on_key_collect(key)
