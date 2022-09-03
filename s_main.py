import sys
import pygame
from pygame.locals import *
import math

import pickle
import select
import socket

BUFFERSIZE = 2048
playerid = 0
serverAddr = '127.0.0.1'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4126))

class AirPlane():
    def __init__(self, x, y, width, height, velocity, angle, acceleration, playerid):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.acceleration = acceleration
        self.angle = angle
        self.turn = 1  # -1: left, 1: right
        self.bullets = []
        self.playerid = playerid

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
        self.gameObjects = []
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
                    gameObject.controls(event.key)

    def draw(self, screen):
        """
        Draw things to the window. Called once per frame.
        """

        screen.fill((0, 150, 255))

        for gameObject in self.gameObjects:
            gameObject.draw(screen)

        pygame.display.flip()

    def main(self):
        self.gameObjects.append(AirPlane(50, 50, 40, 40, 1,30,1,0))

        

        pygame.init()
        fps = 60.0
        fpsClock = pygame.time.Clock()

        width, height = 1280, 720
        screen = pygame.display.set_mode((width, height))

        dt = 1/fps
        while True:
            self.update(dt)
            self.draw(screen)

            dt = fpsClock.tick(fps)

            ins, outs, ex = select.select([s], [], [], 0)
            for inm in ins:
                gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
                if gameEvent[0] == 'id update':
                    playerid = gameEvent[1]
                    print(playerid)
                if gameEvent[0] == 'player locations':
                    gameEvent.pop(0)
                    minions = []
                    for minion in gameEvent:
                        if minion[0] != playerid:
                            minions.append(AirPlane(minion[1], minion[2],40,40,1,30,1,minion[0]))    
            ge = ['position update', playerid, self.gameObjects[0].x, self.gameObjects[0].y, self.gameObjects[0].angle, self.gameObjects[0].turn, self.gameObjects[0].velocity, self.gameObjects[0].acceleration, self.gameObjects[0].bullets]
            s.send(pickle.dumps(ge))

if __name__ == '__main__':
    GameEngineArek()
