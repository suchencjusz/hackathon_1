from asyncio import events
from multiprocessing.connection import Client
import sys
import pygame
from pygame.locals import *
import math
import pygame_menu
from client import Network

# BUFFERSIZE = 2048
# playerid = 0
# serverAddr = '127.0.0.1'

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((serverAddr, 4126))


class AirPlane():
    def __init__(self, x, y, angle, playerid):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity = 1
        self.acceleration = 1
        self.angle = angle
        self.turn = 1  # -1: left, 1: right
        self.bullets = []
        self.playerid = playerid

    def get_position(self):
        return f"move {round(self.x,1)} {round(self.y,1)} {round(self.angle,1)}"

    def update(self, dt):
        self.angle += self.turn * 0.2 * dt
        self.x += self.velocity * \
            math.sin(math.radians(self.angle)) * dt * 0.05
        self.y += self.velocity * \
            math.cos(math.radians(self.angle)) * dt * 0.05

        if self.x < 0:
            self.x = 1280
        elif self.x > 1280:
            self.x = 0
        if self.y < 0:
            self.y = 720
        elif self.y > 720:
            self.y = 0

        for bullet in self.bullets:
            bullet.update(dt)

    def draw(self, screen):
        radians = math.radians(self.angle)

        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 30)

        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y),
                         (self.x + 45*math.sin(radians), self.y + 45*math.cos(radians)), 2)

        for bullet in self.bullets:
            bullet.draw(screen)

    def fire(self):
        self.bullets.append(Bullet(self.x, self.y, self.angle))

    def controls(self, key):
        if key == pygame.K_a:
            self.turn = -1
        elif key == pygame.K_d:
            self.turn = 1
        elif key == pygame.K_w:
            if self.velocity < 20:
                self.velocity += self.acceleration
        elif key == pygame.K_s:
            if self.velocity > 1:
                self.velocity -= self.acceleration
        elif key == pygame.K_SPACE:
            self.fire()


class Bullet():
    def __init__(self, x, y, angle) -> None:
        self.x = x
        self.y = y
        self.velocity = 4
        self.angle = angle
        self.is_alive = False

    def update(self, dt):
        self.x += self.velocity * \
            math.sin(math.radians(self.angle)) * dt * 0.1
        self.y += self.velocity * \
            math.cos(math.radians(self.angle)) * dt * 0.1

        if self.x < 0 or self.x > 1280 or self.y < 0 or self.y > 720:
            self.is_alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 5)


class GameEngineArek():
    def __init__(self):
        pygame.init()
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

    # def menu_event_loop(self):
    #     if self.menu.is_enabled():
    #         self.menu.update(events)
    #         self.menu.draw()

    def menu(self):
        menu = pygame_menu.Menu('Welcome', 1280, 720,
                                theme=pygame_menu.themes.THEME_BLUE)

        menu.add.text_input('Name :', default="Insert nick",
                            onchange=self.get_name)
        menu.add.button('Play', self.main)
        menu.add.button('Quit', pygame_menu.events.EXIT)

        menu.mainloop(self.screen)

    def draw(self):
        """
        Draw things to the window. Called once per frame.
        """

        self.screen.fill((0, 150, 255))

        # for gameObject in self.gameObjects:
        #     gameObject.draw(self.screen)
        for gameObject in self.gameObjects.values():
            gameObject.draw(self.screen)

        pygame.display.flip()

    def main(self):
        client = Network()
        self.my_id = client.connect(self.name)

        self.gameObjects[self.my_id] = AirPlane(
            50, 50, 90, self.my_id)

        fps = 60.0
        fpsClock = pygame.time.Clock()

        dt = 1/fps
        while True:
            players = client.send(self.gameObjects[self.my_id].get_position())
            # print(players.values())
            for player_id, player_data in players.items():
                if player_id != self.my_id:
                    self.gameObjects[player_id] = AirPlane(
                        player_data["x"], player_data["y"], player_data["angle"], player_id)

            self.update(dt)
            self.draw()

            dt = fpsClock.tick(fps)


if __name__ == '__main__':
    GameEngineArek()
