from base import Base
import pygame


class Circle(Base):
    def __init__(self, coords: tuple, radius: int, color: tuple):
        super().__init__()
        self.x, self.y = coords
        self.radius = radius
        self.color = color

    def draw(self, screen, offsets):
        ox, oy = offsets
        pygame.draw.circle(screen, self.color, (self.x - ox, self.y - oy), self.radius)

    def set_color(self, color: tuple):
        self.color = color


class Rectangle(Base):
    def __init__(self, dimensions: tuple, color: tuple):
        super().__init__()
        self.x, self.width, self.y, self.height = dimensions[0], dimensions[1], dimensions[2], dimensions[3]
        self.color = color
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill(self.color)
        self.collide = True

    def draw(self, screen, offsets: tuple):
        """Gets called every frame to draw the image."""
        ox, oy = offsets
        screen.blit(self.surf, (self.x - ox, self.y - oy))

    def set_color(self, color: tuple):
        self.color = color
        self.surf.fill(self.color)

    def within(self, other):
        within_x = self.x + self.width >= other.x and other.x + other.width >= self.x
        within_y = self.y + self.height >= other.y and other.y + other.height >= self.y
        return within_x and within_y


class Line(Base):
    def __init__(self, first_point: tuple, destination_point: tuple, color: tuple=(0, 0, 0), width: int=5):
        super().__init__()
        self.start = first_point
        self.dest = destination_point
        self.color = color
        self.width = width
        self.hide = False

    def draw(self, screen, offsets: tuple):
        if not self.hide:
            start = self.start[0] - offsets[0], self.start[1] - offsets[1]
            end = self.dest[0] - offsets[0], self.dest[1] - offsets[1]
            pygame.draw.line(screen, self.color, start, end, self.width)

    def set_color(self, color: tuple):
        self.color = color

    def reset_points(self, p1: tuple, p2: tuple):
        self.start = p1
        self.dest = p2


class Text(Base):
    """Text. Used with UIElement."""
    def __init__(self, coords: tuple, color: tuple, text: str, font, *, centered: bool=True, update=False):
        super().__init__()
        self.x, self.y = coords
        self.color = color
        self.text = text
        self.centered = centered
        self.font = font
        self.update = update
        self.hide = False

    def __repr__(self):
        return f'{self.text}'

    def draw(self, screen, offsets):
        if self.hide is False:
            text = self.font.render(self.text, True, self.color)
            x, y = self.x + offsets[0], self.y + offsets[1]
            if self.centered:
                center = text.get_rect(center=(x, y))
                screen.blit(text, center)
            else:
                screen.blit(text, (x, y))

    def set_text(self, text: str):
        self.text = text
