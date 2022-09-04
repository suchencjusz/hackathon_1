import math
import random
import time
import datetime


class Bot():
    last_update = 0
    last_update_speed = 0

    def __init__(self, x: float, y: float, angle: float, playerid: int, name: str, color: tuple, health: int, score: int = 0):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity = 9
        self.acceleration = 0.5
        self.angle = angle
        self.turn = 1  # -1: left, 1: right
        self.playerid = playerid
        self.leftBullet = 10
        self.reloadTime = 1
        self.last_reload = None
        self.is_reloading = False
        self.name = name
        self.color = color
        self.max_velocity = 12
        self.bullets = []
        self.health = health
        self.score = score

    def update(self):
        dt = 1/2

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

        if datetime.datetime.now().timestamp() - self.last_update_speed > 1:
            rand = random.randint(1, 10)
            if rand > 5:
                if self.velocity < self.max_velocity:
                    self.velocity += self.acceleration
            else:
                if self.velocity > 1:
                    self.velocity -= self.acceleration

            self.last_update_speed = datetime.datetime.now().timestamp()

        if datetime.datetime.now().timestamp() - self.last_update > 2:
            self.turn = random.choice([-1, 1])
            self.last_update = datetime.datetime.now().timestamp()

        time.sleep(0.001)
