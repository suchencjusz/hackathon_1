import pygame
import math
from datetime import datetime, timedelta


class Airplane(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle: float, playerid: int, name: str, color: tuple, health: int, score: int = 0, stats: dict = None):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity = 1
        self.acceleration = 0.5
        self.angle = angle
        self.turn = 1  # -1: left, 1: right
        self.playerid = playerid
        self.leftBullet = stats['ammo']
        self.max_bullets = stats['ammo']
        self.reloadTime = stats['reload']
        self.last_reload = None
        self.is_reloading = False
        self.name = name
        self.color = color
        self.max_velocity = stats['velocity']
        self.bullets = []
        self.max_health = stats['health']
        self.health = self.max_hp(health)
        self.score = score
        self.image_path = stats['img']
        self.class_name = stats['class']
        self.is_a_pressed = False
        self.is_d_pressed = False
        self.is_w_pressed = False
        self.is_s_pressed = False
        self.is_space_pressed = False

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_score(self, score):
        self.score = score

    def max_hp(self, health):
        if health > self.max_health:
            return self.max_health
        return health

    def set_health(self, health):
        if health > self.max_health:
            self.health = self.max_health
        else:
            self.health = health

    def create_bullet(self, x, y, angle, owner_id):
        self.bullets.append(Bullet(x, y, angle, owner_id))

    def get_position(self) -> dict:
        bullet_data = ""
        for bullet in self.bullets:
            bullet_data += bullet.get_position()
        return f'move {round(self.x, 1)} {round(self.y, 1)} {round(self.angle, 1)} {self.health} {self.class_name} {bullet_data}'

    def update(self, dt):
        if self.is_a_pressed:
            self.turn = 1
        elif self.is_d_pressed:
            self.turn = -1
        if self.is_w_pressed:
            if self.velocity < self.max_velocity:
                self.velocity += self.acceleration
        elif self.is_s_pressed:
            if self.velocity > 1:
                self.velocity -= self.acceleration
        if self.is_space_pressed:
            self.fire()

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

        if self.leftBullet == 0 and self.max_bullets > 0:

            if not self.is_reloading:
                self.last_reload = datetime.now()
                self.is_reloading = True

            if self.last_reload + timedelta(seconds=self.reloadTime) < datetime.now() and self.is_reloading:
                self.leftBullet = self.max_bullets
                self.is_reloading = False

    def draw_health_bar(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.x - 25, self.y - 50, 50, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 25,
                         self.y - 50, 50*(self.health/self.max_health), 5))

    def draw_name(self, screen):

        font = pygame.font.SysFont('arial', 18)
        text = font.render(f"{self.name}", True, (255, 255, 255))
        screen.blit(
            text, text.get_rect(center=(self.x, self.y - 60)))

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
        img = pygame.image.load(self.image_path)
        img = pygame.transform.rotate(img, self.angle)
        screen.blit(img, img.get_rect(center=(self.x, self.y)))

    def draw(self, screen):

        self.draw_health_bar(screen)
        self.draw_name(screen)
        self.draw_airplane(screen)
        self.draw_reload_progress(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

    def fire(self):
        if self.leftBullet > 0:
            pygame.mixer.Sound.play(pygame.mixer.Sound('sound/fire.mp3'))
            self.leftBullet -= 1
            self.bullets.append(
                Bullet(self.x, self.y, self.angle, self.playerid))

    def controls(self, event):
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_a):
                self.is_a_pressed = True
            if(event.key == pygame.K_d):
                self.is_d_pressed = True
            if(event.key == pygame.K_w):
                self.is_w_pressed = True
            if(event.key == pygame.K_s):
                self.is_s_pressed = True
            if(event.key == pygame.K_SPACE):
                self.is_space_pressed = True
        if(event.type == pygame.KEYUP):
            if(event.key == pygame.K_a):
                self.is_a_pressed = False
            if(event.key == pygame.K_d):
                self.is_d_pressed = False
            if(event.key == pygame.K_w):
                self.is_w_pressed = False
            if(event.key == pygame.K_s):
                self.is_s_pressed = False
            if(event.key == pygame.K_SPACE):
                self.is_space_pressed = False


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
