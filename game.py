from datetime import datetime, timedelta
from re import I
import sys
import pygame
from pygame.locals import *
import pygame_menu
from client import Network
from airplane import Airplane

BULLETS = {}


class GameEngineArek():
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont('arial', 16)
        self.bg = pygame.image.load('img/bg.png')
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        self.sprites = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.gameObjects = {}
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.menu()

        self.main()

    def update(self, dt):
        """
        Update game. Called once per frame.
        dt is the amount of time passed since last frame.
        If you want to have constant apparent movement no matter your framerate,
        what you can do is something like

        x += v * dt

        and this will scale your velocity based on time. Extend as necessary."""

        self.gameObjects[self.my_id].update(dt)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.gameObjects[self.my_id].controls(event.key)

    def get_name(self, name):
        self.name = name

    def menu(self):
        menu = pygame_menu.Menu('Welcome', 1280, 720,
                                theme=pygame_menu.themes.THEME_BLUE)

        menu.add.text_input('Name :', default="Insert nick",
                            onchange=self.get_name)
        menu.add.button('Play', self.main)
        menu.add.button('Quit', pygame_menu.events.EXIT)

        menu.mainloop(self.screen)

    def fps_counter(self):
        fps = str(int(self.clock.get_fps()))
        fps_t = self.font.render(fps, 1, pygame.Color("RED"))
        self.screen.blit(fps_t, (0, 0))

    def draw(self):
        """
        Draw things to the window. Called once per frame.
        """

        self.screen.blit(self.bg, (0, 0))
        self.fps_counter()
        for gameObject in self.gameObjects.values():
            gameObject.draw(self.screen)

        pygame.display.flip()

    def main(self):
        client = Network()
        server_data = client.connect(self.name)
        max_fps = 60.0

        self.my_id = server_data['id']
        self.gameObjects[self.my_id] = Airplane(
            server_data["x"], server_data["y"], server_data["angle"], server_data["id"], self.name, server_data["color"])

        dt = 1/max_fps
        while True:
            for k in self.gameObjects.copy().keys():
                if k != self.my_id:
                    del self.gameObjects[k]

            players = client.send(
                self.gameObjects[self.my_id].get_position())
            for player_id, player_data in players.items():
                if player_id != self.my_id:
                    self.gameObjects[player_id] = Airplane(
                        player_data["x"], player_data["y"], player_data["angle"], player_id, player_data["name"], player_data["color"])

                    # print(player_data['bullets'])
                    for bullet in player_data['bullets']:
                        self.gameObjects[player_id].create_bullet(
                            bullet['x'], bullet['y'], bullet['angle'], player_id)

            self.update(dt)
            self.draw()

            dt = self.clock.tick(max_fps)


if __name__ == '__main__':
    GameEngineArek()
