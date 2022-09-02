import sys
import pygame
from pygame.locals import *
import math
from datetime import datetime, timedelta


class AirPlane():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = 1
        self.acceleration = 1
        self.angle = 30
        self.turn = 1  # -1: left, 1: right
        self.leftBullet = 10
        self.reloadTime = 1
        self.bullets = []
        self.last_reload = None
        self.is_reloading = False

    def update(self, dt):
        if self.leftBullet == 0:

            if not self.is_reloading:
                self.last_reload = datetime.now()
                self.is_reloading = True

            if self.last_reload + timedelta(seconds=1) < datetime.now() and self.is_reloading:
                self.leftBullet = 10
                self.is_reloading = False

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

    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)

    def draw_reload_progress(self, screen):
        if self.is_reloading:
            reload_progress = (
                datetime.now() - self.last_reload).total_seconds() / self.reloadTime
            pygame.draw.rect(screen, (255, 255, 255),
                             (self.x - 20, self.y - 50, 40*reload_progress, 10))
            pygame.draw.rect(screen, (0, 0, 0),
                             (self.x - 20, self.y - 50, 40, 10), 1)

    def draw(self, screen):
        radians = math.radians(self.angle)

        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 30)

        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y),
                         (self.x + 45*math.sin(radians), self.y + 45*math.cos(radians)), 2)

        self.draw_bullets(screen)
        self.draw_reload_progress(screen)

    def fire(self):
        if self.leftBullet != 0:
            self.leftBullet -= 1
            self.bullets.append(Bullet(self.x, self.y, self.angle))

    def controls(self, event):
        if event.key == pygame.K_a:
            self.turn = -1
        elif event.key == pygame.K_d:
            self.turn = 1
        elif event.key == pygame.K_w:
            if self.velocity < 20:
                self.velocity += self.acceleration
        elif event.key == pygame.K_s:
            if self.velocity > 1:
                self.velocity -= self.acceleration
        elif event.key == pygame.K_SPACE:
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


class GameEngine():

    def __init__(self):
        pygame.init()
        self.gameObjects = []
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.main()

    def update(self, dt):
        """
        Update game. Called once per frame.
        dt is the amount of time passed since last frame.
        If you want to have constant apparent movement no matter your framerate,
        what you can do is something like

        x += v * dt

        and this will scale your velocity based on time. Extend as necessary."""

        for gameObject in self.gameObjects:
            gameObject.update(dt)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                for gameObject in self.gameObjects:
                    gameObject.controls(event)

    def fps_counter(self, screen):
        fps = str(int(self.clock.get_fps()))
        fps_t = self.font.render(fps, 1, pygame.Color("RED"))
        screen.blit(fps_t, (0, 0))

    def draw(self, screen):
        """
        Draw things to the window. Called once per frame.
        """

        screen.fill((0, 150, 255))

        for gameObject in self.gameObjects:
            gameObject.draw(screen)

        self.fps_counter(screen)

        pygame.display.flip()

    def main(self):
        self.gameObjects.append(AirPlane(700, 300, 40, 40))

        fps = 60.0
        width, height = 1280, 720
        screen = pygame.display.set_mode((width, height))

        dt = 1/fps
        while True:
            self.update(dt)
            self.draw(screen)

            dt = self.clock.tick(fps)


if __name__ == '__main__':
    GameEngine()
