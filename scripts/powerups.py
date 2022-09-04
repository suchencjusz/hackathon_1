import pygame


class Heal():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        print(x, y)

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), 5)
