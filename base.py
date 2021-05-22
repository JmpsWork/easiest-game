"""Base file containing all the base variables."""
import pygame

size = 1650, 1050  # Window size
size_mult = 1650 / size[0], 1050 / size[1]
caption = 'World\'s Easiest Game'  # Window name
closed = False  # Set this to true to close the game
FPS = 60  # Ticks per second
elapsed = 0  # Elapsed time, in milliseconds
game_speed = 1000 / FPS  # Game speed, 1000 milliseconds / game speed, in FPS
drawn = {'bg': [],  # Things in bg don't do collide checks
         'collides': [],  # Anything with the name collide will do collision checks
         'tg': [],  # Same as bg, except it gets drawn on top of collides and bg
         'ui': []}  # UI won't offset based on camera position

images = {}

BLACK = 0, 0, 0
WHITE_BASIC = 220, 220, 220
BLUE_BASIC = 160, 160, 220
BLUE_ENEMY = 50, 50, 230

mousedown = False
rightmousedown = False
mouse_pos = 0, 0


dict_keymap = {
    pygame.K_a: 'a',  # Integer key connects to correct string representing character
    pygame.K_b: 'b',
    pygame.K_c: 'c',
    pygame.K_d: 'd',
    pygame.K_e: 'e',
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_h: 'h',
    pygame.K_i: 'i',
    pygame.K_j: 'j',
    pygame.K_k: 'k',
    pygame.K_l: 'l',
    pygame.K_m: 'm',
    pygame.K_n: 'n',
    pygame.K_o: 'o',
    pygame.K_p: 'p',
    pygame.K_q: 'q',
    pygame.K_r: 'r',
    pygame.K_s: 's',
    pygame.K_t: 't',
    pygame.K_u: 'u',
    pygame.K_v: 'v',
    pygame.K_w: 'w',
    pygame.K_x: 'x',
    pygame.K_y: 'y',
    pygame.K_z: 'z',
    pygame.K_SPACE: ' ',
    # Numbers
    pygame.K_0: '0',
    pygame.K_1: '1',
    pygame.K_2: '2',
    pygame.K_3: '3',
    pygame.K_4: '4',
    pygame.K_5: '5',
    pygame.K_6: '6',
    pygame.K_7: '7',
    pygame.K_8: '8',
    pygame.K_9: '9',
    # Symbols
    pygame.K_PERIOD: '.',
    pygame.K_SLASH: '/',
    pygame.K_MINUS: '-',
    pygame.K_QUOTE: '\'',
    pygame.K_COMMA: ',',
    pygame.K_SEMICOLON: ';',
    pygame.K_RIGHTBRACKET: '[',
    pygame.K_LEFTBRACKET: ']',
    pygame.K_EQUALS: '=',
    pygame.K_BACKQUOTE: '`',
    pygame.K_BACKSLASH: '\\',
    # Boolean keys (backspace, enter, etc.)
    pygame.K_BACKSPACE: 'BACKSPACE',
    pygame.K_RSHIFT: 'RSHIFT',
    pygame.K_LSHIFT: 'LSHIFT',
    pygame.K_CAPSLOCK: 'CAPSLOCK',
    pygame.K_KP_ENTER: 'ENTER'
}

dict_keymap_alt = {
    # Number alts
    pygame.K_0: ')',  # Any keys that have an alternate key when holding shift
    pygame.K_1: '!',
    pygame.K_2: '@',
    pygame.K_3: '#',
    pygame.K_4: '$',
    pygame.K_5: '%',
    pygame.K_6: '^',
    pygame.K_7: '&',
    pygame.K_8: '*',
    pygame.K_9: '(',
    # Symbols alts
    pygame.K_PERIOD: '>',
    pygame.K_SLASH: '?',
    pygame.K_MINUS: '_',
    pygame.K_QUOTE: '\"',
    pygame.K_COMMA: '<',
    pygame.K_SEMICOLON: ':',
    pygame.K_RIGHTBRACKET: '}',
    pygame.K_LEFTBRACKET: '{',
    pygame.K_EQUALS: '+',
    pygame.K_BACKQUOTE: '~',
    pygame.K_BACKSLASH: '|',
}


class Base:
    """Base class for everything."""
    def __init__(self):
        self.die = False  # Engine checks for things with die, removes them if found

    def __repr__(self) -> str:
        return f'Base({self.die})'

    def draw(self, screen, offsets: tuple):
        """Draw something to a surface. The offset is a x and y tuple which offsets the final position."""
        pass

    def tick(self):
        """Gets called 60 times a second."""
        pass


def add_to_drawn(section: str, thing: Base, index: int=None):
    """Add a thing to a specific section. Leaving out index will append it,
    otherwise will insert at specific index."""
    if index is None:
        drawn[section].append(thing)
    else:
        drawn[section].insert(index, thing)


def remove_from_drawn(section: str, index: int):
    """Remove a thing from a specific section using a specific index."""
    del drawn[section][index]
