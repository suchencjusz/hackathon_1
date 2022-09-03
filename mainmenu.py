import pygame_menu
import pygame


class MainMenu():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.start_menu()


MainMenu()
