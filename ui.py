from base import *
from shapes import Rectangle, Line, Text
from sprites import Sprite


class Button(Rectangle):
    def __init__(self, dimensions: tuple, color: tuple, called=None, second_color: tuple=None, called_params=None, centered=False):
        super().__init__(dimensions, color)
        self.first_color = color
        if second_color is None:
            self.second_color = self.color[0] + 20, self.color[1] + 20, self.color[2] + 20
        else:
            self.second_color = second_color
        if centered:
            self.x -= self.width / 2
            self.y -= self.height / 2
        self.pressed = False  # Allows a button to be held down, but not repeatably pressed
        self.called = called
        if self.called is None:
            self.called = self.empty
        self.params = called_params
        self.hide = False

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            super().draw(screen, offsets)

    def empty(self, *params):
        """Buttons with no function will use this instead."""
        pass

    def is_pressed(self, mouse_pos: tuple) -> bool:
        point = mouse_pos
        within_x = self.x + self.width >= point[0] and point[0] >= self.x
        within_y = self.y + self.height >= point[1] and point[1] >= self.y
        return within_x and within_y

    def press(self, mouse_pos: tuple):
        if self.hide is False:
            if self.pressed is False and self.is_pressed(mouse_pos):
                self.set_color(self.second_color)
                self.pressed = True

    def unpress(self, mouse_pos: tuple):
        if self.hide is False:
            if self.pressed is True:
                self.set_color(self.first_color)
                self.pressed = False
                if self.is_pressed(mouse_pos):
                    if self.params is None:
                        self.called()
                    else:
                        self.called(*self.params)


class SpriteButton(Base):
    """Same as the Button class but uses 2 sprites instead of a rectangle."""
    def __init__(self, pos: tuple, first, second, called, called_params: tuple=None, centered: bool=False):
        super().__init__()
        self.first = Sprite(pos, first)
        self.second = Sprite(pos, second)
        self.display_first = True
        if centered:
            self.first.x -= self.first.size[0] / 2
            self.first.y -= self.first.size[1] / 2
            self.second.x -= self.second.size[0] / 2
            self.second.y -= self.second.size[1] / 2
        self.pressed = False  # Allows a button to be held down, but not repeatably pressed
        self.called = called
        if self.called is None:
            self.called = self.empty
        self.params = called_params
        self.hide = False

    def draw(self, screen, offsets: tuple):
        if self.hide is False:
            if self.display_first:
                self.first.draw(screen, offsets)
            else:
                self.second.draw(screen, offsets)

    def empty(self, *params):
        """Buttons with no function will use this instead."""
        pass

    def is_pressed(self, mouse_pos: tuple) -> bool:
        point = mouse_pos
        within_x = self.first.x + self.first.size[0] >= point[0] and point[0] >= self.first.x
        within_y = self.first.y + self.first.size[1] >= point[1] and point[1] >= self.first.y
        return within_x and within_y

    def press(self, mouse_pos: tuple):
        if self.hide is False:
            if self.pressed is False and self.is_pressed(mouse_pos):
                self.display_first = False
                self.pressed = True

    def set_image(self, first, second):
        pos = self.first.x, self.first.y
        self.first = Sprite(pos, first)
        self.second = Sprite(pos, second)

    def unpress(self, mouse_pos: tuple):
        if self.hide is False:
            if self.pressed is True:
                self.display_first = True
                self.pressed = False
                if self.is_pressed(mouse_pos):
                    if self.params is None:
                        self.called()
                    else:
                        self.called(*self.params)


class SlideBar(Base):
    """A slide bar for inputs that need a value between 0 and 1. Only works on the X axis."""
    def __init__(self, bar: Rectangle, slide: Line):
        super().__init__()
        self.slide = slide
        self.bar = bar
        self.held = False
        self.dead = False

    def amount(self) -> float:
        """Returns a normalized value from 0-1 indicating the position of the bar on the slide."""
        start, end = self.slide.start[0] - self.bar.width / 2, self.slide.dest[0] - self.bar.width / 2
        bar_x_start = self.bar.x - start  # Get a start value of 0
        bar_x_end = end - start  # Get the end value from 0

        if bar_x_start <= 0:
            return 0.0
        elif bar_x_start / bar_x_end >= 1:
            return 1.0
        else:
            return bar_x_start / bar_x_end

    def draw(self, screen, offsets):
        if self.dead is False:
            self.slide.draw(screen, offsets)
            self.bar.draw(screen, offsets)

    def is_pressed(self) -> bool:
        if self.dead is False:
            point = mouse_pos
            within_x = self.bar.x + self.bar.width >= point[0] and point[0] >= self.bar.x - self.bar.width
            within_y = self.bar.y + self.bar.height >= point[1] and point[1] >= self.bar.y
            return within_x and within_y  # Only checks for X axis collision
        else:
            return False

    def hold(self):
        pressed = self.is_pressed()
        point = mouse_pos

        if pressed is True and mousedown is True:
            self.held = True
            # Stop bar at bar center, not bar edge
            start, end = self.slide.start[0], self.slide.dest[0]
            if point[0] > start and point[0] < end:
                self.bar.x = point[0] - self.bar.width / 2
        else:
            self.held = False

    def set_amount(self, amount: float):
        """Change the Bar's position on the slide using a number from 0-1."""
        start, end = self.slide.start[0] - self.bar.width / 2, self.slide.dest[0] - self.bar.width / 2
        bar_x_end = end - start
        new_pos = amount * bar_x_end + start
        self.bar.x = new_pos


class UIElement(Base):
    """Containerizes the Main Menu and certain other menus."""
    def __init__(self, bg: Rectangle, parented: list, buttons: list):
        super().__init__()
        self.bg = bg
        self.parented = parented
        self.buttons = buttons
        self.dead = False  # On-Off switch for disabling the menu from being drawn
        self.mousedown = False
        self.mouse_pos = 0, 0

    def add_child(self, rectangle):
        self.parented.append(rectangle)

    def add_button(self, button):
        self.buttons.append(button)

    def draw(self, screen, offsets):
        if self.dead is True:
            return
        if self.bg is not None:
            self.bg.draw(screen, offsets)
        for button in self.buttons:
            button.draw(screen, offsets)
            if self.mousedown:
                button.press(self.mouse_pos)
            else:
                button.unpress(self.mouse_pos)
        for parented in self.parented:
            parented.draw(screen, offsets)
            if isinstance(parented, SlideBar):
                parented.hold()


class TextBox(Base):
    """Displays keyboard inputs and manages key inputs for proper output.
    Exclusively used by editor.py"""
    def __init__(self, coords: tuple, color: tuple):
        super().__init__()
        self.text = Text(coords, color, '')
        self.current_pressed = {}  # Keyindex: [key, time pressed (frames)]
        self.upper = False
        self.invalid = ('CAPSLOCK', 'LSHIFT', 'RSHIFT', 'BACKSPACE')

    def draw(self, screen, offsets: tuple):
        self.text.draw(screen, offsets)

    def feed(self, keys: list, keymap):
        """Determines what keys to 'feed' in to the string to be displayed."""
        input_string = self.text.text

        is_caps = keymap[pygame.K_CAPSLOCK] == 1 or keymap[pygame.K_RSHIFT] == 1 or keymap[pygame.K_LSHIFT] == 1
        if is_caps is True:
            self.upper = True

        for key in keys:  # key being the key index for the dict_keymap
            letter = dict_keymap[key]
            if self.upper is True:
                variant = dict_keymap_alt.get(key)
                if variant is None:
                    letter = letter.upper()
                else:
                    letter = variant
            pressed = self.current_pressed.get(key)
            if pressed is None:  # Keep track of how long certain keys have been pressed for
                self.current_pressed[key] = [letter, 0]

            time = self.current_pressed[key][1]
            if time == 0:  # Determine when the pressed key can be sent to the string
                if letter == 'BACKSPACE':
                    input_string = input_string[:-1]
                elif letter not in self.invalid:  # Ignore keys which don't have letters
                    input_string += letter
            elif time % 5 == 0 and time > FPS / 2:
                if letter == 'BACKSPACE':
                    input_string = input_string[:-1]
                elif letter not in self.invalid:
                    input_string += letter

        for key in list(self.current_pressed):
            if key not in keys:
                self.current_pressed.pop(key)  # Delete unused keys to reset time

        self.text.set_text(input_string)
        self.upper = False

    def tick(self):
        for key, value in self.current_pressed.items():
            value[1] += 1  # Count how long keys have been pressed
