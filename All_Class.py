import pygame
import random

MY_PLANE_SPEED = 10                     # 我机速度
FRAME_RATE = 60                         # 帧率
SMALL_BLOOD = 1                         # 小型机血量
MID_BLOOD = 8                           # 中型机血量
BIG_BLOOD = 18                          # 大型机血量
HERO_FIRE_EVENT = pygame.USEREVENT      # 装填子弹事件
SUPPLY_TIME = pygame.USEREVENT+1        # 发射补给时间
SUPER_BULLET = pygame.USEREVENT+2       # 超级子弹持续事件
INVINCIBLE_TIME = pygame.USEREVENT+3    # 接触无敌状态

SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 90, 90)
RED = (255, 0, 0)
DARK_GRAY = (105, 105, 105)
WHITE = (255, 255, 255)
GRAY = (68, 139, 139)

COLOR = (BLACK, GRAY, GREEN, RED, WHITE, BROWN, DARK_GRAY)


# 我方飞机类
class MyPlane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.destroy = []
        self.image1 = pygame.image.load('./images/me1.png').convert_alpha()
        self.image2 = pygame.image.load('./images/me2.png').convert_alpha()
        self.destroy.extend([pygame.image.load('./images/me_destroy_1.png').convert_alpha(),
                             pygame.image.load('./images/me_destroy_2.png').convert_alpha(),
                             pygame.image.load('./images/me_destroy_3.png').convert_alpha(),
                             pygame.image.load('./images/me_destroy_4.png').convert_alpha()])
        self.life_image = pygame.image.load('./images/life.png').convert_alpha()
        self.life_rect = self.life_image.get_rect()
        self.down_sound = pygame.mixer.Sound('./sound/me_down.wav')
        self.down_sound.set_volume(0.2)
        self.rect = self.image1.get_rect()
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 60
        self.mask = pygame.mask.from_surface(self.image1)
        self.bullets = pygame.sprite.Group()
        self.invincible = False
        self.survival = True
        self.life = 3
        self.dx = 0
        self.dy = 0

    # 刷新位置
    def update(self):
        self.rect.x += self.dx
        self.rect.y -= self.dy
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right >= SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        if self.rect.y <= 60:
            self.rect.y = 60
        elif self.rect.bottom >= SCREEN_RECT.bottom - 60:
            self.rect.bottom = SCREEN_RECT.bottom - 60

    # 移动
    def move(self, type_str=' '):
        if type_str == 'right':
            self.dx = MY_PLANE_SPEED
        elif type_str == 'left':
            self.dx = -MY_PLANE_SPEED
        elif type_str == 'up':
            self.dy = MY_PLANE_SPEED
        elif type_str == 'down':
            self.dy = -MY_PLANE_SPEED
        else:
            self.dx = self.dy = 0

    # 开火
    def fire(self, super_bullet=False):
        if super_bullet:
            bullet1 = Super_Bullet()
            bullet2 = Super_Bullet()
            bullet1.rect.x = self.rect.x + self.rect.width/3 - 10
            bullet2.rect.x = self.rect.x + self.rect.width*2/3 + 10
            bullet1.rect.y = bullet2.rect.y = self.rect.y
            self.bullets.add(bullet1, bullet2)
        else:
            bullet = Bullets()
            bullet.rect.midtop = self.rect.midtop
            self.bullets.add(bullet)

    # 重生
    def reset(self):
        self.survival = True
        self.invincible = True
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 60


# 敌机类（父类）
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, range1, range2, speed=1):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, self.max_x)
        self.rect.bottom = random.randint(range1, range2)
        self.r1 = range1
        self.r2 = range2
        self.speed = speed
        self.hit = False
        self.survival = True
        self.index = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_RECT.height:
            self.reset()

    def reset(self):
        self.survival = True
        self.rect.x = random.randint(0, self.max_x)
        self.rect.bottom = random.randint(self.r1, self.r2)

    # 绘制血条
    def draw_blood(self, screen, initial_blood):
        pygame.draw.line(screen, BLACK, (self.rect.left, self.rect.top-5),
                         (self.rect.right, self.rect.top-5), 2)
        blood_remain = self.blood / initial_blood
        if blood_remain > 0.3:
            blood_color = GREEN
        else:
            blood_color = RED
        pygame.draw.line(screen, blood_color, (self.rect.left, self.rect.top-5),
                         (self.rect.left+self.rect.width*blood_remain, self.rect.top-5), 2)


class SmallEnemy(Enemy):
    def __init__(self, speed=2):
        super().__init__("./images/enemy1.png", -5 * SCREEN_RECT.height, 0, speed)
        self.destroy_images = []
        self.destroy_images.extend([pygame.image.load('./images/enemy1_down1.png').convert_alpha(),
                                    pygame.image.load('./images/enemy1_down2.png').convert_alpha(),
                                    pygame.image.load('./images/enemy1_down3.png').convert_alpha(),
                                    pygame.image.load('./images/enemy1_down4.png').convert_alpha()])
        self.down_sound = pygame.mixer.Sound('./sound/enemy1_down.wav')
        self.down_sound.set_volume(0.3)
        self.blood = SMALL_BLOOD

    def reset(self):
        super().reset()
        self.blood = SMALL_BLOOD


class MidEnemy(Enemy):

    def __init__(self, speed=1):
        super().__init__("./images/enemy2.png", -5 * SCREEN_RECT.height, -SCREEN_RECT.height, speed)
        self.destroy_images = []
        self.destroy_images.extend([pygame.image.load('./images/enemy2_down1.png').convert_alpha(),
                                    pygame.image.load('./images/enemy2_down2.png').convert_alpha(),
                                    pygame.image.load('./images/enemy2_down3.png').convert_alpha(),
                                    pygame.image.load('./images/enemy2_down4.png').convert_alpha()])
        self.hit_image = pygame.image.load('./images/enemy2_hit.png').convert_alpha()
        self.down_sound = pygame.mixer.Sound('./sound/enemy2_down.wav')
        self.down_sound.set_volume(0.5)
        self.blood = MID_BLOOD

    def reset(self):
        super().reset()
        self.blood = MID_BLOOD


class BigEnemy(Enemy):

    def __init__(self, speed=1):
        super().__init__('./images/enemy3_n1.png', -12 * SCREEN_RECT.height, -5 * SCREEN_RECT.height, speed)
        self.image2 = pygame.image.load("./images/enemy3_n2.png").convert_alpha()
        self.destroy_images = []
        self.destroy_images.extend([pygame.image.load('./images/enemy3_down1.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down2.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down3.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down4.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down4.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down5.png').convert_alpha(),
                                    pygame.image.load('./images/enemy3_down6.png').convert_alpha()])
        self.hit_image = pygame.image.load('./images/enemy3_hit.png')
        self.fly_sound = pygame.mixer.Sound('./sound/enemy3_flying.wav')
        self.fly_sound.set_volume(0.2)
        self.down_sound = pygame.mixer.Sound('./sound/enemy3_down.wav')
        self.down_sound.set_volume(0.5)
        self.mask = pygame.mask.from_surface(self.image2)
        self.blood = BIG_BLOOD

    def reset(self):
        super().reset()
        self.blood = BIG_BLOOD


# 子弹类（父类）
class Bullets(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/bullet1.png").convert_alpha()
        self.speed = 12
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= 0:
            self.kill()


# 超级子弹
class Super_Bullet(Bullets):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/bullet2.png").convert_alpha()
        self.speed = 15


# 背景图片类
class Background(pygame.sprite.Sprite):
    def __init__(self, is_alt=False):
        super().__init__()

        self.image = pygame.image.load('./images/background.png')
        self.rect = self.image.get_rect()
        self.speed = 1

        if is_alt:
            self.rect.y = -self.rect.height

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -SCREEN_RECT.height


# 暂停类
class Control_Pause(object):
    def __init__(self):

        self.pause_image = pygame.image.load('./images/pause1.png').convert_alpha()
        self.pause_dark_image = pygame.image.load('./images/pause2.png').convert_alpha()
        self.resume_image = pygame.image.load('./images/resume1.png').convert_alpha()
        self.resume_dark_image = pygame.image.load('./images/resume2.png').convert_alpha()
        self.rect = self.pause_image.get_rect()
        self.rect.left = SCREEN_RECT.width - self.rect.width - 10
        self.rect.y = 10

        self.image = self.pause_image
        self.judge = True
        self.num = 0

    def update(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.judge:
                    self.image = self.pause_dark_image
                else:
                    self.image = self.resume_dark_image
            else:
                if self.judge:
                    self.image = self.pause_image
                else:
                    self.image = self.resume_image

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.num += 1
                self.judge = not self.judge
                if self.judge:
                    self.image = self.pause_image
                    pygame.mixer.unpause()
                    pygame.mixer.music.unpause()
                    pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                else:
                    self.image = self.resume_image
                    pygame.mixer.pause()
                    pygame.mixer.music.pause()
                    pygame.time.set_timer(SUPPLY_TIME, 0)


# 炸弹类
class Bomb(object):
    def __init__(self):
        self.bomb = pygame.image.load('./images/bomb.png')
        self.bomb_rect = self.bomb.get_rect()
        self.bomb_rect.bottom = SCREEN_RECT.height - 10
        self.bomb_rect.x = 10
        self.bomb_font = pygame.font.Font('./Font/font.ttf', 55)
        self.bomb_num = 3
        self.bomb_str = self.bomb_font.render('x '+str(self.bomb_num), True, BROWN)
        self.bomb_sound = pygame.mixer.Sound('./sound/use_bomb.wav')
        self.bomb_sound.set_volume(0.2)


# 补给类
class Supply(pygame.sprite.Sprite):
    def __init__(self, image_path, sound_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.sound = pygame.mixer.Sound('./sound/supply.wav')
        self.sound.set_volume(0.2)
        self.get_supply = pygame.mixer.Sound(sound_path)
        self.get_supply.set_volume(0.2)
        self.survival = False
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_RECT.height:
            self.survival = False

    def reset(self):
        self.survival = True
        self.rect.bottom = -100
        self.rect.x = random.randint(0, SCREEN_RECT.width - self.rect.width)


