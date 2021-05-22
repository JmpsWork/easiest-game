"""File to run the game"""
print('Loading...')

import pygame
import os
import json
from base import *
from player import Player
from level import Wall, Enemy, Level, Coin, Tile, Key
from shapes import Text
from ui import UIElement, SpriteButton, Button
from sprite_loader import get_images


# FIRST INIT

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
display = pygame.display.set_mode(size)
screen = pygame.Surface(size, pygame.SRCALPHA)

pygame.display.set_mode(size)
pygame.display.set_caption(caption)

bg_color = 180, 180, 180, 255
gradient_color = 180, 180, 220, 255
cam_x, cam_y = 0, 0

player = Player((0, 0))
player.speed = 2
player_dying = False
add_to_drawn('collides', player)

for image_name, image_path in get_images().items():
    images[image_name] = pygame.image.load(image_path).convert_alpha()

# FONTS
def_font = pygame.font.Font('data/apple_kid.ttf', 50)
lvl_font = pygame.font.Font('data/apple_kid.ttf', 80)
font_blurb = pygame.font.Font(pygame.font.match_font('impact'), 100)

# LEVEL LOADING VARIABLES
level_loading_delay = -1
next_level = 'editor_level'
level = Level(next_level, def_font, (200, 200), True)
level.end = True  # Start level loading immediately

# SOUNDS
sound_coin = pygame.mixer.Sound('sfx/coin_collect.wav')
sound_death = pygame.mixer.Sound('sfx/death.wav')
sound_win = pygame.mixer.Sound('sfx/completed.wav')
sound_key = pygame.mixer.Sound('sfx/key_collect.wav')

pygame.mixer.music.load(f'sfx/music1.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.35)

# STATS
deaths = 0
time = 0
level_times = {}  # level name : completion time

# UI
blurb = Text((size[0] / 2, size[1] / 2), BLACK, '', font_blurb, centered=True)
blurb.hide = True
blurb.set_text(level.blurb)
add_to_drawn('ui', blurb)


class MainMenu(UIElement):
    def __init__(self):
        parented = []
        buttons = [SpriteButton((size[0] * 0.3, size[1] * 0.85), images['button_play1'], images['button_play2'], self.start_playing, centered=True),
                   SpriteButton((size[0] * 0.5, size[1] * 0.85), images['button_ls1'], images['button_ls2'], self.campaign_select, centered=True),
                   SpriteButton((size[0] * 0.7, size[1] * 0.85), images['button_exit1'], images['button_exit2'], self.exit_game, centered=True)]
        super().__init__(None, parented, buttons)
        self.playing = False
        self.dead = False

    def exit_game(self):
        """Exit button."""
        global closed
        self.dead = True
        closed = True

    def campaign_select(self):
        """Level Select button."""
        self.dead = True
        campaign_menu.dead = False
        player.hide = True
        level.hide()

    def start_playing(self):
        """Play button."""
        level.unhide()
        level.end = True
        player.can_move = True
        player.hide = False
        self.playing = True
        self.dead = True
        game_menu.dead = False

    def stop_playing(self):
        global deaths
        level.hide()
        player.can_move = False
        player.hide = True
        self.playing = False
        a = player.bg_rect.width / 2
        player.x, player.y = level.player_spawn[0] + level.ox - a, level.player_spawn[1] + level.oy - a
        deaths = 0
        self.dead = False
        game_menu.dead = True


class GameMenu(UIElement):
    def __init__(self):
        self.text_time = Text((size[0] * 0.05, size[1] * 0.075), BLUE_BASIC, '', def_font, centered=False)
        self.text_deaths = Text((size[0] * 0.05, size[1] * 0.125), (220, 160, 160), '', def_font, centered=False)
        parented = [self.text_time, self.text_deaths]
        buttons = []
        super().__init__(None, parented, buttons)
        self.dead = True

    def tick(self):
        self.text_time.set_text(f'Time: {round(time / 1000, 2)}')
        self.text_deaths.set_text(f'Deaths: {deaths}')


class FinalMenu(UIElement):
    """Menu once a campaign is completed."""
    def __init__(self):
        parented = []
        buttons = []
        super().__init__(None, parented, buttons)
        self.dead = True


class CampaignSelect(UIElement):
    """UI For level select button."""
    def __init__(self):
        self.campaign_text = [Text((size[0] * 0.2, size[1] * 0.3), WHITE_BASIC, 'A', def_font),
                              Text((size[0] * 0.5, size[1] * 0.3), WHITE_BASIC, 'B', def_font),
                              Text((size[0] * 0.8, size[1] * 0.3), WHITE_BASIC, 'C', def_font),
                              Text((size[0] * 0.2, size[1] * 0.6), WHITE_BASIC, 'D', def_font),
                              Text((size[0] * 0.5, size[1] * 0.6), WHITE_BASIC, 'E', def_font),
                              Text((size[0] * 0.8, size[1] * 0.6), WHITE_BASIC, 'F', def_font)]
        self.difficulty_text = [Text((size[0] * 0.2, size[1] * 0.3 + 60), WHITE_BASIC, 'A', def_font),
                                Text((size[0] * 0.5, size[1] * 0.3 + 60), WHITE_BASIC, 'B', def_font),
                                Text((size[0] * 0.8, size[1] * 0.3 + 60), WHITE_BASIC, 'C', def_font),
                                Text((size[0] * 0.2, size[1] * 0.6 + 60), WHITE_BASIC, 'D', def_font),
                                Text((size[0] * 0.5, size[1] * 0.6 + 60), WHITE_BASIC, 'E', def_font),
                                Text((size[0] * 0.8, size[1] * 0.6 + 60), WHITE_BASIC, 'F', def_font)]
        self.campaign_buttons = [Button((size[0] * 0.2, 300, size[1] * 0.3, 200), BLACK, self.campaign, called_params=(0,), centered=True),
                                 Button((size[0] * 0.5, 300, size[1] * 0.3, 200), BLACK, self.campaign, called_params=(1,), centered=True),
                                 Button((size[0] * 0.8, 300, size[1] * 0.3, 200), BLACK, self.campaign, called_params=(2,), centered=True),
                                 Button((size[0] * 0.2, 300, size[1] * 0.6, 200), BLACK, self.campaign, called_params=(3,), centered=True),
                                 Button((size[0] * 0.5, 300, size[1] * 0.6, 200), BLACK, self.campaign, called_params=(4,), centered=True),
                                 Button((size[0] * 0.8, 300, size[1] * 0.6, 200), BLACK, self.campaign, called_params=(5,), centered=True)]
        parented = [Text((size[0] * 0.5, size[1] * 0.9), WHITE_BASIC, 'BACK', def_font)]
        buttons = [Button((size[0] * 0.5, 360, size[1] * 0.9, 80), BLACK, self.back, centered=True)]
        for t in self.campaign_text:
            t.hide = True
            parented.append(t)
        for t2 in self.difficulty_text:
            t2.hide = True
            parented.append(t2)
        for b in self.campaign_buttons:
            b.hide = True
            buttons.append(b)
        super().__init__(None, parented, buttons)
        self.dead = True
        self.campaign_info = []  # All campaign info is stored as a list of dict
        self.campaign_amount = 0
        self.campaign_page = 1
        self.load_campaigns()
        self.readjust_ui()

    def back(self):
        """Return to main menu."""
        self.dead = True
        main_menu.dead = False
        player.hide = False
        level.unhide()

    def campaign(self, b_id: int):
        """Load campaign at specified button index."""
        self.dead = True
        level_menu.dead = False
        level_menu.levels = self.campaign_info[b_id * self.campaign_page]['levels']
        level_menu.level_page = 1
        level_menu.readjust_ui()
        level_menu.set_difficulty(self.campaign_info[b_id * self.campaign_page]['difficulty'])

    def load_campaigns(self):
        """Loads / reloads all campaign.json files"""
        for file in os.listdir('data'):
            if 'campaign' in file:
                with open(f'data/{file}') as data:
                    info = json.loads(data.read())
                    self.campaign_info.append(info)
        self.campaign_amount = len(self.campaign_info)

    def page_up(self):
        if self.campaign_page * 6 < self.campaign_amount:
            self.campaign_page += 1
            self.reset_ui()
            self.readjust_ui()

    def page_down(self):
        if self.campaign_page > 1:
            self.campaign_page -= 1
            self.reset_ui()
            self.readjust_ui()

    def readjust_ui(self):
        for i, campaign in enumerate(self.campaign_info):
            if i < self.campaign_page * 6 and i >= self.campaign_page * 6 - 6:
                index = i + self.campaign_page * 6 - 6
                text, text2, button = self.campaign_text[index], self.difficulty_text[index], self.campaign_buttons[index]
                text.hide = False
                text2.hide = False
                text.set_text(campaign['name'])
                button.hide = False
                dif = campaign['difficulty']
                if dif == -1:
                    text2.set_text('')
                elif dif == 0:
                    text2.set_text('Easy')
                    text2.color = 40, 40, 220
                elif dif == 1:
                    text2.set_text('Medium')
                    text2.color = 220, 220, 40
                elif dif == 2:
                    text2.set_text('Hard')
                    text2.color = 220, 40, 40
                elif dif == 3:
                    text2.set_text('Expert')
                    text2.color = 220, 40, 220
                elif dif == 4:
                    text2.set_text('Special')
                    text2.color = 40, 220, 220
                elif dif == 99:
                    text2.set_text('Testing')
                    text2.color = 120, 120, 120

    def reset_ui(self):
        for t in self.campaign_text:
            t.set_text('')
            t.hide = True
        for t2 in self.difficulty_text:
            t2.hide = True
            t2.set_text('')
        for b in self.campaign_buttons:
            b.hide = True


class LevelSelect(UIElement):
    def __init__(self):
        self.level_buttons = [SpriteButton((size[0] * 0.2, size[1] * 0.25), images['level_easy'], images['level_easy'], self.level, called_params=(0, ), centered=True),
                              SpriteButton((size[0] * 0.35, size[1] * 0.25), images['level_easy'], images['level_easy'], self.level, called_params=(1, ), centered=True),
                              SpriteButton((size[0] * 0.5, size[1] * 0.25), images['level_easy'], images['level_easy'], self.level, called_params=(2, ), centered=True),
                              SpriteButton((size[0] * 0.65, size[1] * 0.25), images['level_easy'], images['level_easy'], self.level, called_params=(3, ), centered=True),
                              SpriteButton((size[0] * 0.8, size[1] * 0.25), images['level_easy'], images['level_easy'], self.level, called_params=(4, ), centered=True),

                              SpriteButton((size[0] * 0.2, size[1] * 0.5), images['level_easy'], images['level_easy'], self.level, called_params=(5, ), centered=True),
                              SpriteButton((size[0] * 0.35, size[1] * 0.5), images['level_easy'], images['level_easy'], self.level, called_params=(6, ), centered=True),
                              SpriteButton((size[0] * 0.5, size[1] * 0.5), images['level_easy'], images['level_easy'], self.level, called_params=(7, ), centered=True),
                              SpriteButton((size[0] * 0.65, size[1] * 0.5), images['level_easy'], images['level_easy'], self.level, called_params=(8, ), centered=True),
                              SpriteButton((size[0] * 0.8, size[1] * 0.5), images['level_easy'], images['level_easy'], self.level, called_params=(9, ), centered=True),

                              SpriteButton((size[0] * 0.2, size[1] * 0.75), images['level_easy'], images['level_easy'], self.level, called_params=(10, ), centered=True),
                              SpriteButton((size[0] * 0.35, size[1] * 0.75), images['level_easy'], images['level_easy'], self.level, called_params=(11, ), centered=True),
                              SpriteButton((size[0] * 0.5, size[1] * 0.75), images['level_easy'], images['level_easy'], self.level, called_params=(12, ), centered=True),
                              SpriteButton((size[0] * 0.65, size[1] * 0.75), images['level_easy'], images['level_easy'], self.level, called_params=(13, ), centered=True),
                              SpriteButton((size[0] * 0.8, size[1] * 0.75), images['level_easy'], images['level_easy'], self.level, called_params=(14, ), centered=True)]

        self.level_text = [Text((size[0] * 0.2, size[1] * 0.25), BLACK, '1', lvl_font, centered=True),
                           Text((size[0] * 0.35, size[1] * 0.25), BLACK, '2', lvl_font, centered=True),
                           Text((size[0] * 0.5, size[1] * 0.25), BLACK, '3', lvl_font, centered=True),
                           Text((size[0] * 0.65, size[1] * 0.25), BLACK, '4', lvl_font, centered=True),
                           Text((size[0] * 0.8, size[1] * 0.25), BLACK, '5', lvl_font, centered=True),

                           Text((size[0] * 0.2, size[1] * 0.5), BLACK, '6', lvl_font, centered=True),
                           Text((size[0] * 0.35, size[1] * 0.5), BLACK, '7', lvl_font, centered=True),
                           Text((size[0] * 0.5, size[1] * 0.5), BLACK, '8', lvl_font, centered=True),
                           Text((size[0] * 0.65, size[1] * 0.5), BLACK, '9', lvl_font, centered=True),
                           Text((size[0] * 0.8, size[1] * 0.5), BLACK, '10', lvl_font, centered=True),

                           Text((size[0] * 0.2, size[1] * 0.75), BLACK, '11', lvl_font, centered=True),
                           Text((size[0] * 0.35, size[1] * 0.75), BLACK, '12', lvl_font, centered=True),
                           Text((size[0] * 0.5, size[1] * 0.75), BLACK, '13', lvl_font, centered=True),
                           Text((size[0] * 0.65, size[1] * 0.75), BLACK, '14', lvl_font, centered=True),
                           Text((size[0] * 0.8, size[1] * 0.75), BLACK, '15', lvl_font, centered=True)]

        self.button_page_up = SpriteButton((size[0] * 0.95, size[1] * 0.5), images['arrow'], images['arrow'], self.page_up, centered=True)
        self.button_page_down = SpriteButton((size[0] * 0.05, size[1] * 0.5), images['arrow_l'], images['arrow_l'], self.page_down, centered=True)

        parented = [Text((size[0] * 0.06, size[1] * 0.1), WHITE_BASIC, 'BACK', def_font, centered=True)]
        buttons = [Button((size[0] * 0.06, 120, size[1] * 0.1, 80), BLACK, self.back, centered=True),
                   self.button_page_up, self.button_page_down]
        for lb in self.level_buttons:
            buttons.append(lb)
        for lt in self.level_text:
            parented.append(lt)
        super().__init__(None, parented, buttons)
        self.level_page = 1
        self.dead = True
        self.levels = []

    def back(self):
        self.dead = True
        campaign_menu.dead = False

    def level(self, b_id: int):
        global next_level, level_loading_delay
        self.dead = True
        name = self.levels[b_id + (self.level_page - 1) * 15]
        next_level = name
        level.reset()
        level.end = True
        level.load(name, def_font)
        level_loading_delay = -1
        blurb.set_text(level.this_blurb)
        a = player.bg_rect.width / 2
        player.x, player.y = level.player_spawn[0] + level.ox - a, level.player_spawn[1] + level.oy - a
        main_menu.start_playing()

    def page_up(self):
        if self.level_page * 15 < len(self.levels) and not self.dead:
            self.level_page += 1
            self.readjust_ui()

    def page_down(self):
        if self.level_page > 1 and not self.dead:
            self.level_page -= 1
            self.readjust_ui()

    def readjust_ui(self):
        """Remove excess level buttons"""
        self.reset_ui()
        start, end = self.level_page * 15 - 15, self.level_page * 15 - 1
        for i, level in enumerate(self.levels):
            dif = (self.level_page - 1) * 15
            index = i + start
            if index < len(self.levels) and index < self.level_page * 15:  # 0-14, 15-29, 30-44...
                b, t = self.level_buttons[index - dif], self.level_text[index - dif]
                b.hide = False
                t.hide = False
                t.set_text(f'{index + 1}')
        if self.level_page > 1:
            self.button_page_down.hide = False
        if self.level_page * 15 < len(self.levels):
            self.button_page_up.hide = False

    def reset_ui(self):
        self.button_page_up.hide = True
        self.button_page_down.hide = True
        for lb in self.level_buttons:
            lb.hide = True
        for lt in self.level_text:
            lt.hide = True

    def set_difficulty(self, difficulty: int):
        """0: easy, 1: medium, 2: hard, 3: expert"""
        for lb in self.level_buttons:
            if difficulty == -1:
                lb.set_image(images['level_tut'], images['level_tut'])
            elif difficulty == 1:
                lb.set_image(images['level_medium'], images['level_medium'])
            elif difficulty == 2:
                lb.set_image(images['level_hard'], images['level_hard'])
            elif difficulty == 3:
                lb.set_image(images['level_exp'], images['level_exp'])
            elif difficulty == 4:
                lb.set_image(images['level_spec'], images['level_spec'])
            elif difficulty == 99:
                lb.set_image(images['level_test'], images['level_test'])
            else:
                lb.set_image(images['level_easy'], images['level_easy'])


# INIT

a = player.bg_rect.width / 2
player.x, player.y = level.player_spawn[0] + level.ox - a, level.player_spawn[1] + level.oy - a

main_menu = MainMenu()
# main_menu.stop_playing()
add_to_drawn('ui', main_menu)
game_menu = GameMenu()
add_to_drawn('ui', game_menu)
campaign_menu = CampaignSelect()
add_to_drawn('ui', campaign_menu)
level_menu = LevelSelect()
add_to_drawn('ui', level_menu)
level_menu.readjust_ui()
final_menu = FinalMenu()
add_to_drawn('ui', final_menu)

print('Done!')


while not closed:

    pygame.display.update()
    dt = clock.tick_busy_loop()
    elapsed += dt
    mouse_pos = pygame.mouse.get_pos()

    if elapsed >= game_speed:  # Do do once every tick for these in particular
        screen.fill(bg_color)
        if main_menu.playing:
            if level.hidden is False:
                time += 1000 / 60
            if level.end is True and level_loading_delay == -1:
                print(round(time / 1000, 1), level.next)
                player.reset()
                level.hide()
                level.reset()
                player.hide = True
                player.x, player.y = -100, -100
                player.bg_rect.x, player.bg_rect.y = -100, -100
                level_loading_delay = 140
                blurb.hide = False
                sound_win.play()
                if not next_level:  # Last level gets completed (has 'false' as next_level)
                    pass
            if level_loading_delay > 0:  # Keep showing blurb
                level_loading_delay -= 1
            elif level.end is True and level_loading_delay == 0:  # Start new level
                time = 0
                player.hide = False
                a = player.bg_rect.width / 2
                if next_level:  # Goto next level
                    level.load(next_level, def_font)
                    level.unhide()
                    next_level = level.next
                    player.x, player.y = level.player_spawn[0] + level.ox - a, level.player_spawn[1] + level.oy - a
                else:  # Goto main menu
                    main_menu.dead = False
                    game_menu.dead = True
                blurb.hide = True
                blurb.set_text(level.blurb)
                level_loading_delay = -1
                level.end = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closed = True
            pygame.quit()
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousedown = True
            elif event.button == 3:
                rightmousedown = True

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
            elif event.key == pygame.K_SPACE:
                if level_loading_delay > 0:
                    level_loading_delay = 1
            if player.can_move:
                if event.key == pygame.K_w:
                    player.vy -= player.speed
                elif event.key == pygame.K_s:
                    player.vy += player.speed
                elif event.key == pygame.K_d:
                    player.vx += player.speed
                elif event.key == pygame.K_a:
                    player.vx -= player.speed
                elif event.key == pygame.K_F2:
                    player.set_speed(4)

        elif event.type == pygame.KEYUP:
            if player.can_move:
                if event.key == pygame.K_w:
                    player.vy += player.speed
                elif event.key == pygame.K_s:
                    player.vy -= player.speed
                elif event.key == pygame.K_d:
                    player.vx -= player.speed
                elif event.key == pygame.K_a:
                    player.vx += player.speed

    for section, values in drawn.items():
        for i, entity in enumerate(values):
            if entity.die is True:
                remove_from_drawn(section, i)

            if elapsed >= game_speed:
                if section == 'collides':
                    for o_i, o_entity in enumerate(values):
                        if o_i != i:
                            if isinstance(entity, Player) and isinstance(o_entity, Wall):
                                player.rect_intersect(o_entity.crect)
                            elif isinstance(entity, Player) and isinstance(o_entity, Tile):
                                player.tile_interact(o_entity)
                            elif isinstance(entity, Player) and isinstance(o_entity, Enemy):
                                if o_entity.colliding(player.bg_rect):
                                    deaths += 1
                                    a = player.bg_rect.width / 2
                                    player.x, player.y = level.player_spawn[0] + level.ox - a, level.player_spawn[1] + level.oy - a
                                    sound_death.play()
                                    for coin in level.coins:
                                        if coin.collected and not coin.perm_collected:
                                            coin.collected = False
                                            level.coins_collected -= 1
                            elif isinstance(entity, Player) and isinstance(o_entity, Coin):
                                if o_entity.colliding(player.bg_rect):
                                    o_entity.collected = True
                                    level.coins_collected += 1
                                    sound_coin.play()
                            elif isinstance(entity, Player) and isinstance(o_entity, Key):
                                if o_entity.within(player.bg_rect):
                                    o_entity.die = True
                                    level.unlock(o_entity)
                                    sound_key.play()
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
