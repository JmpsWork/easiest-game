"""Level editor for easiestgame"""


print('Loading...')

# import pygame
import json
import jsbeautifier  # Isn't necessary, just cleans up the json output of excess newlines
from base import *
from shapes import Rectangle, Line, Text
from ui import UIElement
from level import Wall, Enemy
from sprite_loader import get_images


# FIRST INIT

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
display = pygame.display.set_mode(size)
screen = pygame.Surface(size, pygame.SRCALPHA)

pygame.display.set_mode(size)
pygame.display.set_caption(f'{caption} LEVEL EDITOR')

bg_color = 80, 80, 80, 255
gradient_color = 180, 180, 220, 255
cam_x, cam_y = 0, 0
cam_vx, cam_vy = 0, 0
g_mousepos_x, g_mousepos_y = 0, 0
MODE = 1  # 1 for placing and remove tiles, 2 for walls, 3 for enemies, 4 for coins

tile_override_existing = False  # Ignores the check for existing tiles

centered = False  # Center the position to the tile
wall_starting = True  # Either create a point using ws or we
wsx, wsy = 0, 0  # Wall start x, wall start y
wex, wey = 0, 0  # Wall end x, wall end y
temp_line = Line((wsx, wsy), (wex, wey), width=6)
temp_line.hide = True
fixup = True  # Fix vertical walls so players don't get stuck on corners

enemy_starting = True
esx, esy = 0, 0  # Enemy start x, enemy start y
eex, eey = 0, 0
temp_enemy_line = Line((esx, esy), (eex, eey), width=4, color=(200, 40, 40))
temp_enemy_line.hide = True
enemy_paths = []  # List of enemy travel points
enemy_lines = []  # Visual list of enemy path

spawn_x, spawn_y = 0, 0

for image_name, image_path in get_images().items():
    images[image_name] = pygame.image.load(image_path).convert_alpha()

with open(f'data/tiletemplates.json') as tile_template_data:  # Load tile templates and level data
    tile_templates = json.loads(tile_template_data.read())

print(tile_templates)
tile_template_index = 0
tile_template_names = []
for k, v in tile_templates.items():
    tile_template_names.append(k)
using_tile = tile_template_names[tile_template_index]
print(tile_template_names)


class Tile(Rectangle):
    def __init__(self, grid_x, grid_y, color: tuple):
        super().__init__((grid_x * 50, 50, grid_y * 50, 50), color)
        self.gx = grid_x
        self.gy = grid_y
        self.end = False
        self.checkpoint = False
        self.hide = False
        self.nil = False
        self.warp = False, 0, 0  # Does warp, warp X. warp Y
        self.reset_point = 0, 0
        self.template = ''

    def __repr__(self):
        return f'Tile({self.gx, self.gy}, {self.color})'

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            super().draw(screen, offsets)

    def set_position(self, gx: int, gy: int):
        self.gx, self.gy = gx, gy
        self.x, self.y = gx * 50, gy * 50


class EditorLevel(Base):
    def __init__(self):
        super().__init__()
        self.tiles = []  # This self.tiles is a list of all tiles, not a list of X rows
        self.walls = []
        self.enemies = []
        self.level_data = {}  # Raw level data

    def add_tile(self, g_pos: tuple, template: str='empty'):
        if not self.get_tile(*g_pos):
            print(f'tile added: {template}')
            new_tile = Tile(*g_pos, (0, 0, 0))
            template_info = tile_templates.get(template, False)
            if template_info:
                new_tile.set_color(template_info.get('color', (255, 0, 255)))
                new_tile.nil = template_info.get('nil', False)
                new_tile.checkpoint = template_info.get('checkpoint', False)
            if new_tile.nil:
                new_tile.set_color((50, 200, 120))
            add_to_drawn('bg', new_tile)
            self.tiles.append(new_tile)
            new_tile.template = template
        elif tile_override_existing:
            print(f'tile override: {template}')
            self.remove_tile(*g_pos)
            new_tile = Tile(*g_pos, (0, 0, 0))
            template_info = tile_templates.get(template, False)
            if template_info:
                new_tile.set_color(template_info.get('color', (255, 0, 255)))
                new_tile.nil = template_info.get('nil', False)
            if new_tile.nil:
                new_tile.set_color((50, 200, 120))
            add_to_drawn('bg', new_tile)
            self.tiles.append(new_tile)
            new_tile.template = template

    def add_wall(self, x: int, y: int, ex: int, ey: int):
        """Create a wall from start x and y to ending x and y."""
        if x == ex and fixup:
            y += 6
            ey -= 6
        new_wall = Wall((x, y), (ex, ey))
        self.walls.append(new_wall)
        add_to_drawn('tg', new_wall)

    def add_enemy(self, x: int, y: int, speed: int, path: list=[]):
        """Create an enemy with a path."""
        new_enemy = Enemy((x, y), speed, path)
        new_enemy.move = False
        self.enemies.append(new_enemy)
        add_to_drawn('tg', new_enemy)

    def enable_enemies(self):
        """Allow all enemies to move"""
        for enemy in self.enemies:
            enemy.move = True

    def export(self, name: str):
        """Export level info to a json file"""
        if self.tiles == []:  # Avoid crash
            return False

        xs = [tile.gx for tile in self.tiles]
        ys = [tile.gy for tile in self.tiles]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        size_x, size_y = max_x - min_x + 1, max_y - min_y + 1
        origin_x, origin_y = 0 - min_x, 0 - min_y  # Difference in tile x to origin x in grid space
        spawnx, spawny = spawn_x + origin_x * 50, spawn_y + origin_x * 50
        print(size_x, size_y, origin_x, origin_y)

        for tile in self.tiles:  # Center everything to the origin
            tile.set_position(tile.gx + origin_x, tile.gy + origin_y)
        new_walls = []  # Walls for json
        for wall in self.walls:
            start = wall.cstart[0] + origin_x * 50, wall.cstart[1] + origin_y * 50
            end = wall.cdest[0] + origin_x * 50, wall.cdest[1] + origin_y * 50
            wall.cstart, wall.cdest = start, end
            wall.set_position(start[0], start[1], end[0], end[1])
            info = {'sx': start[0], 'sy': start[1], 'ex': end[0], 'ey': end[1]}
            new_walls.append(info)
        new_enemies = []  # enemies for json
        for enemy in self.enemies:
            new_path = []
            for path_point in enemy.path:
                x, y = path_point
                new_path.append((x + origin_x * 50, y + origin_y * 50))
            enemy.path = new_path
            enemy.x += origin_x * 50
            enemy.y += origin_y * 50
            enemy.newx += origin_x * 50
            enemy.newy += origin_y * 50
            info = {'x': enemy.x, 'y': enemy.y, 'speed': enemy.speed, 'path': new_path}
            new_enemies.append(info)

        sorted_tiles = sorted(self.tiles, key=lambda tile: (tile.y, tile.x))  # arbitrarily sorted x first, then y
        new_tiles = []  # correctly sorted tiles for json.
        # print(sorted_tiles)
        for y in range(0, size_y):
            x_row = []
            for x in range(0, size_x):
                try:
                    real_tile = self.get_tile(x, y)
                    if real_tile:
                        selected_tile = sorted_tiles[x + y * size_x]
                        info = {"template": selected_tile.template}
                        if selected_tile.checkpoint:
                            info['newx'] = spawnx
                            info['newy'] = spawny
                        x_row.append(info)
                    else:
                        x_row.append({"template": "empty"})
                except IndexError:
                    x_row.append({"template": "empty"})
            new_tiles.append(x_row)
        for row in new_tiles:
            print(row)
        blurb = 'empty'
        level_centered = True
        next_level = False
        self.level_data['blurb'] = blurb
        self.level_data['next_level'] = next_level
        self.level_data['centered'] = level_centered
        self.level_data['spawnx'], self.level_data['spawny'] = spawnx, spawny
        self.level_data['tiles'] = new_tiles
        self.level_data['walls'] = new_walls
        self.level_data['enemies'] = new_enemies
        with open('data/editor_level.json', 'w') as empty_file:
            data = json.dumps(self.level_data, indent=2)
            options = jsbeautifier.default_options()
            options.indent_size = 2
            empty_file.write(jsbeautifier.beautify(data, options))

    def get_tile(self, gx: int, gy: int):
        """Gets a tile at the specified GX and GY. If none exist, returns None."""
        for tile in self.tiles:
            if tile.gx == gx and tile.gy == gy:
                return tile
        return None

    def remove_tile(self, gx: int, gy: int):
        for i, tile in enumerate(self.tiles):
            if tile.gx == gx and tile.gy == gy:
                tile = self.tiles.pop(i)
                tile.die = True

    def remove_wall(self):
        """Will only remove the wall at the top of the list. Essentially an undo function for walls."""
        if len(self.walls) > 0:
            wall = self.walls.pop(len(self.walls) - 1)
            wall.die = True

    def remove_enemy(self):
        if len(self.enemies) > 0:
            enemy = self.enemies.pop(len(self.enemies) - 1)
            enemy.die = True

    def reset(self):
        """Destroy a level."""
        for tile in self.tiles:
            tile.die = True
        for wall in self.walls:
            wall.die = True
        for enemy in self.enemies:
            enemy.die = True
        self.tiles = []
        self.walls = []
        self.enemies = []


# FONTS
def_font = pygame.font.Font('data/apple_kid.ttf', 50)
lvl_font = pygame.font.Font('data/apple_kid.ttf', 80)

# SOUNDS
# STATS

# UI


class EditorUI(UIElement):
    def __init__(self):
        self.text_x = Text((size[0] * 0.05, size[1] * 0.05), (120, 30, 30), 'X:', def_font, centered=False)
        self.text_y = Text((size[0] * 0.11, size[1] * 0.05), (30, 30, 120), 'Y:', def_font, centered=False)
        self.text_gx = Text((size[0] * 0.05, size[1] * 0.1), (120, 30, 30), 'GX:', def_font, centered=False)
        self.text_gy = Text((size[0] * 0.11, size[1] * 0.1), (30, 30, 120), 'GY:', def_font, centered=False)
        self.text_tile = Text((size[0] * 0.75, size[1] * 0.05), (160, 160, 30), 'Tile: ', def_font, centered=False)
        self.text_mode = Text((size[0] * 0.75, size[1] * 0.1), (160, 160, 30), 'Mode: ', def_font, centered=False)
        parented = [self.text_x, self.text_y, self.text_gx, self.text_gy, self.text_tile, self.text_mode]
        buttons = []
        super().__init__(None, parented, buttons)

    def draw(self, screen, offsets):
        self.text_x.set_text(f'X: {mouse_pos[0] + cam_x}')
        self.text_y.set_text(f'Y: {mouse_pos[1] + cam_y}')
        self.text_gx.set_text(f'GX: {g_mousepos_x}')
        self.text_gy.set_text(f'GY: {g_mousepos_y}')
        if MODE == 1:
            self.text_tile.set_text(f'Tile: {using_tile}')
        else:
            self.text_tile.set_text('')
        self.text_mode.set_text(f'Mode: {MODE}')
        super().draw(screen, offsets)


# INIT

origin_line_x = Line((0, 0), (50, 0), (255, 0, 0), 4)
origin_line_y = Line((0, 0), (0, 50), (0, 0, 255), 4)
add_to_drawn('tg', origin_line_x)
add_to_drawn('tg', origin_line_y)
editorui = EditorUI()
editorlevel = EditorLevel()
add_to_drawn('ui', editorui)
add_to_drawn('ui', editorlevel)
add_to_drawn('tg', temp_line)
add_to_drawn('tg', temp_enemy_line)

print('Done!')


while not closed:

    pygame.display.update()
    dt = clock.tick_busy_loop()
    elapsed += dt
    mouse_pos = pygame.mouse.get_pos()

    if elapsed >= game_speed:  # Do do once every tick for these in particular
        screen.fill(bg_color)
        cam_x += cam_vx
        cam_y += cam_vy
        g_mousepos_x, g_mousepos_y = round((mouse_pos[0] + cam_x) // 50), round((mouse_pos[1] + cam_y) // 50)
        if mousedown:
            if MODE == 1:
                editorlevel.add_tile((g_mousepos_x, g_mousepos_y), using_tile)
        elif rightmousedown:
            if MODE == 1:
                editorlevel.remove_tile(g_mousepos_x, g_mousepos_y)
        if not wall_starting and MODE == 2:
            temp_line.start = wsx, wsy
            temp_line.dest = g_mousepos_x * 50, g_mousepos_y * 50
            if centered:
                wex += 25
                wey += 25
        if not enemy_starting and MODE == 3:
            temp_enemy_line.start = esx, esy
            temp_enemy_line.dest = g_mousepos_x * 50, g_mousepos_y * 50
            if centered:
                eex += 25
                eey += 25

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closed = True
            pygame.quit()
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousedown = True
                if MODE == 1:
                    editorlevel.add_tile((g_mousepos_x, g_mousepos_y), using_tile)
                elif MODE == 2:
                    if wall_starting:
                        temp_line.hide = False
                        wsx, wsy = g_mousepos_x * 50, g_mousepos_y * 50
                        wall_starting = False
                        if centered:
                            wsx += 25
                            wsy += 25
                    else:
                        temp_line.hide = True
                        wex, wey = g_mousepos_x * 50, g_mousepos_y * 50
                        wall_starting = True
                        if centered:
                            wex += 25
                            wey += 25
                        editorlevel.add_wall(wsx, wsy, wex, wey)
                elif MODE == 3:
                    if enemy_starting:
                        temp_enemy_line.hide = False
                        esx, esy = g_mousepos_x * 50, g_mousepos_y * 50
                        enemy_starting = False
                        if centered:
                            esx += 25
                            esy += 25
                        enemy_paths.append((esx, esy))
                    else:
                        temp_enemy_line.hide = True
                        eex, eey = g_mousepos_x * 50, g_mousepos_y * 50
                        enemy_starting = True
                        if centered:
                            eex += 25
                            eey += 25
                        path_line = Line((esx, esy), (eex, eey), BLUE_ENEMY, 4)
                        enemy_lines.append(path_line)
                        add_to_drawn('tg', path_line)

            elif event.button == 3:
                rightmousedown = True
                if MODE == 1:
                    editorlevel.remove_tile(g_mousepos_x, g_mousepos_y)
                elif MODE == 2:
                    editorlevel.remove_wall()
                elif MODE == 3:
                    editorlevel.remove_enemy()
            elif event.button == 4:  # Scroll up
                tile_template_index += 1
                if tile_template_index >= len(tile_template_names) - 1:
                    tile_template_index = 0
                using_tile = tile_template_names[tile_template_index]
            elif event.button == 5:  # Scroll down
                tile_template_index -= 1
                if tile_template_index < 0:
                    tile_template_index = len(tile_template_names) - 1
                using_tile = tile_template_names[tile_template_index]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mousedown = False
            elif event.button == 3:
                rightmousedown = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                closed = True
                pygame.quit()
                quit()
            if event.key == pygame.K_w:
                cam_vy = -2
            elif event.key == pygame.K_s:
                cam_vy = 2
            elif event.key == pygame.K_d:
                cam_vx = 2
            elif event.key == pygame.K_a:
                cam_vx = -2
            elif event.key == pygame.K_1:
                MODE = 1
            elif event.key == pygame.K_2:
                MODE = 2
            elif event.key == pygame.K_3:
                MODE = 3
            elif event.key == pygame.K_DELETE:
                editorlevel.reset()
            elif event.key == pygame.K_KP_ENTER:  # Keypad Enter
                if MODE == 3:
                    temp_enemy_line.hide = True
                    enemy_paths.append((eex, eey))
                    editorlevel.add_enemy(enemy_paths[0][0], enemy_paths[0][1], 3, enemy_paths)
                    for line in enemy_lines:
                        line.die = True
                    enemy_paths = []
            elif event.key == pygame.K_KP0:
                editorlevel.enable_enemies()
            elif event.key == pygame.K_c:
                if centered:
                    centered = False
                else:
                    centered = True
            elif event.key == pygame.K_r:
                editorlevel.export('editor_level')
            elif event.key == pygame.K_o:
                if tile_override_existing:
                    tile_override_existing = False
                else:
                    tile_override_existing = True
            elif event.key == pygame.K_f:
                if fixup:
                    fixup = False
                else:
                    fixup = True
            elif event.key == pygame.K_p:
                spawn_x, spawn_y = g_mousepos_x * 50, g_mousepos_y * 50
                if centered:
                    spawn_x += 25
                    spawn_y += 25

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                cam_vy = 0
            elif event.key == pygame.K_s:
                cam_vy = 0
            elif event.key == pygame.K_d:
                cam_vx = 0
            elif event.key == pygame.K_a:
                cam_vx = 0

    for section, values in drawn.items():
        for i, entity in enumerate(values):
            if entity.die is True:
                remove_from_drawn(section, i)

            if elapsed >= game_speed:
                if section == 'collides':
                    pass
                entity.tick()

            if section != 'ui':
                entity.draw(screen, (cam_x, cam_y))
            else:
                if isinstance(entity, UIElement):
                    entity.mouse_pos = mouse_pos
                    entity.mousedown = mousedown
                entity.draw(screen, (0, 0))

    while elapsed >= game_speed:
        elapsed -= game_speed

    if size_mult[0] != 1 and size_mult[1] != 1:
        scaled = pygame.transform.scale(screen, (round(size[0] * size_mult[0]), round(size[1] * size_mult[1])))
        display.blit(scaled, (0, 0))
    else:
        display.blit(screen, (0, 0))

