import pygame
import math
from datetime import datetime, timedelta

# bullets = {}


class Airplane(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle: float, playerid: int, name: str, color: tuple):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity = 1
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

    def create_bullet(self, x, y, angle, owner_id):
        self.bullets.append(Bullet(x, y, angle, owner_id))

    def get_position(self) -> dict:
        bullet_data = ""
        for bullet in self.bullets:
            bullet_data += bullet.get_position()
        return f'move {round(self.x, 1)} {round(self.y, 1)} {round(self.angle, 1)} {bullet_data}'

    def update(self, dt):
        self.angle += self.turn * 0.2 * dt
        self.x -= self.velocity * \
            math.sin(math.radians(self.angle)) * dt * 0.03
        self.y -= self.velocity * \
            math.cos(math.radians(self.angle)) * dt * 0.03

        for bullet in self.bullets:
            bullet.update(dt)
            if not bullet.is_alive:
                del self.bullets[self.bullets.index(bullet)]

        if self.x < 0:
            self.x = 1280
        elif self.x > 1280:
            self.x = 0
        if self.y < 0:
            self.y = 720
        elif self.y > 720:
            self.y = 0

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

        self.draw_name(screen)
        self.draw_airplane(screen)
        self.draw_reload_progress(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

    def fire(self):
        if self.leftBullet > 0:
            self.leftBullet -= 1
            self.bullets.append(
                Bullet(self.x, self.y, self.angle, self.playerid))

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
    def __init__(self, x: float, y: float, angle: float,  owner_id: int) -> None:
        self.x = x
        self.y = y
        self.velocity = 8
        self.angle = angle
        self.is_alive = True
        self.owner_id = owner_id

    def update(self, dt):
        self.x -= self.velocity * math.sin(math.radians(self.angle)) * dt * 0.1
        self.y -= self.velocity * math.cos(math.radians(self.angle)) * dt * 0.1

        if self.x < 0 or self.x > 1280 or self.y < 0 or self.y > 720:
            self.is_alive = False

    def draw(self, screen):
        radians = math.radians(self.angle)
        pygame.draw.line(screen, (155, 155, 155), (self.x + 25*math.sin(radians), self.y + 25*math.cos(radians)), (self.x + 35*math.sin(
            radians), self.y + 35*math.cos(radians)), 3)

    def get_position(self):
        return f'{round(self.x, 1)},{round(self.y, 1)},{round(self.angle, 1)} '
