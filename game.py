from datetime import datetime, timedelta
from re import I
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


class AirPlane(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle: float, playerid: int, name: str, color: tuple):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity = 1
        self.acceleration = 0.5
        self.angle = angle
        self.turn = 1  # -1: left, 1: right
        self.bullets = []
        self.playerid = playerid
        self.leftBullet = 10
        self.reloadTime = 1
        self.last_reload = None
        self.is_reloading = False
        self.name = name
        self.color = color
        self.max_velocity = 12

    def get_position(self) -> str:
        return f"move {round(self.x,1)} {round(self.y,1)} {round(self.angle,1)}"

    def update(self, dt):
        self.angle += self.turn * 0.2 * dt
        self.x -= self.velocity * \
            math.sin(math.radians(self.angle)) * dt * 0.05
        self.y -= self.velocity * \
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

        if self.leftBullet == 0:

            if not self.is_reloading:
                self.last_reload = datetime.now()
                self.is_reloading = True

            if self.last_reload + timedelta(seconds=1) < datetime.now() and self.is_reloading:
                self.leftBullet = 10
                self.is_reloading = False

    def draw_name(self, screen):

        font = pygame.font.SysFont('arial', 16)
        text = font.render(f"{self.name}", True, (255, 255, 255))
        screen.blit(
            text, text.get_rect(center=(self.x, self.y - 40)))

    def draw_reload_progress(self, screen):
        if self.is_reloading:
            reload_progress = (
                datetime.now() - self.last_reload).total_seconds() / self.reloadTime
            pygame.draw.rect(screen, (255, 255, 255),
                             (self.x - 20, self.y + 40, 40*reload_progress, 10))
            pygame.draw.rect(screen, (0, 0, 0),
                             (self.x - 20, self.y + 40, 40, 10), 1)

    def draw_debug_lines(self, screen):
        radians = math.radians(self.angle)
        pygame.draw.circle(screen, self.color, (self.x, self.y), 25)

        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y),
                         (self.x + 45*math.sin(radians), self.y + 45*math.cos(radians)), 3)

    def draw_airplane(self, screen):
        img = pygame.image.load('img/airplane1.png')
        img = pygame.transform.rotate(img, self.angle)
        screen.blit(img, img.get_rect(center=(self.x, self.y)))

    def draw(self, screen):

        for bullet in self.bullets:
            bullet.draw(screen)

        self.draw_name(screen)
        self.draw_airplane(screen)
        self.draw_reload_progress(screen)

    def fire(self):
        if self.leftBullet > 0:
            self.leftBullet -= 1
            self.bullets.append(
                Bullet(self.x, self.y, self.angle, self.color))

    def controls(self, key):
        if key == pygame.K_a:
            self.turn = -1
        elif key == pygame.K_d:
            self.turn = 1
        elif key == pygame.K_w:
            if self.velocity < self.max_velocity:
                self.velocity += self.acceleration
        elif key == pygame.K_s:
            if self.velocity > 1:
                self.velocity -= self.acceleration
        elif key == pygame.K_SPACE:
            self.fire()


class Bullet():
    def __init__(self, x: float, y: float, angle: float, color: tuple) -> None:
        self.x = x
        self.y = y
        self.velocity = 8
        self.angle = angle
        self.is_alive = False
        self.color = color

    def update(self, dt):
        self.x -= self.velocity * math.sin(math.radians(self.angle)) * dt * 0.1
        self.y -= self.velocity * math.cos(math.radians(self.angle)) * dt * 0.1

        if self.x < 0 or self.x > 1280 or self.y < 0 or self.y > 720:
            self.is_alive = False

    def draw(self, screen):
        radians = math.radians(self.angle)
        pygame.draw.line(screen, (155, 155, 155), (self.x + 25*math.sin(radians), self.y + 25*math.cos(radians)), (self.x + 35*math.sin(
            radians), self.y + 35*math.cos(radians)), 3)


class GameEngineArek():
    def __init__(self):
        pygame.init()
        self.bg = pygame.image.load('img/bg.png')
        self.bg = pygame.transform.scale(self.bg, (1280, 720))
        self.sprites = pygame.sprite.Group()
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
        self.screen.blit(self.bg, (0, 0))
        for gameObject in self.gameObjects.values():
            gameObject.draw(self.screen)

        pygame.display.flip()

    def main(self):
        client = Network()
        server_data = client.connect(self.name)

        self.my_id = server_data['id']
        self.gameObjects[self.my_id] = AirPlane(
            server_data["x"], server_data["y"], server_data["angle"], server_data["id"], self.name, server_data["color"])

        fps = 60.0
        fpsClock = pygame.time.Clock()

        dt = 1/fps
        while True:
            for k in self.gameObjects.copy().keys():
                if k != self.my_id:
                    del self.gameObjects[k]

            players = client.send(self.gameObjects[self.my_id].get_position())
            # print(players.values())
            for player_id, player_data in players.items():
                if player_id != self.my_id:
                    self.gameObjects[player_id] = AirPlane(
                        player_data["x"], player_data["y"], player_data["angle"], player_id, player_data["name"], player_data["color"])

            self.update(dt)
            self.draw()

            dt = fpsClock.tick(fps)


if __name__ == '__main__':
    GameEngineArek()
