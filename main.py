import os
import sys
from All_Class import *

pygame.init()

screen = pygame.display.set_mode(SCREEN_RECT.size)
pygame.display.set_caption("Plane Game -- Joseph Tong")

pygame.mixer.music.load("./sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)

upgrade_sound = pygame.mixer.Sound("./sound/upgrade.wav")
upgrade_sound.set_volume(0.2)

level_font = pygame.font.Font('./Font/font.ttf', 28)
score_font = pygame.font.Font('./Font/font.ttf', 39)
joke_font = pygame.font.Font('./Font/font.ttf', 39)
over_font = pygame.font.Font('./Font/font.ttf', 52)


def joke_part(i):
    i %= 7
    joke_text1 = joke_font.render("HaHaHaHaHa...", True, COLOR[i])
    joke_text2 = joke_font.render("HeHeHeHeHeHeHeHe...", True, COLOR[i])
    screen.blit(joke_text1, (116, SCREEN_RECT.height / 3))
    screen.blit(joke_text2, (76, SCREEN_RECT.height * 1.5 / 3))


class MainGame(object):

    # 初始化，各种所需参数
    def __init__(self):

        self.record_path = "./data/record.txt"
        self.shoot_sound = pygame.mixer.Sound('./sound/bullet.wav')
        self.shoot_sound.set_volume(0.2)

        self.clock = pygame.time.Clock()

    # 创建规定数量的敌机
    def add_enemies(self, g1, g2, num, size):
        for i in range(num):
            if size == 1:
                emy = SmallEnemy(self.small_speed)
            elif size == 2:
                emy = MidEnemy(self.mid_speed)
            elif size == 3:
                emy = BigEnemy(self.big_speed)
            g1.add(emy)
            g2.add(emy)

    def add_more_enemies(self, small=0, mid=0, big=0):
        self.add_enemies(self.small_enemies, self.enemies, small, 1)
        self.add_enemies(self.mid_enemies, self.enemies, mid, 2)
        self.add_enemies(self.big_enemies, self.enemies, big, 3)

    # 加速
    def promote_speed(self, small=False, mid=False, big=False):
        if small:
            self.small_speed += 1
            for each in self.small_enemies:
                each.speed = self.small_speed
        if mid:
            self.mid_speed += 1
            for each in self.mid_enemies:
                each.speed = self.mid_speed
        if big:
            self.big_speed += 1
            for each in self.big_enemies:
                each.speed = self.big_speed

    # 控制单个动画帧率
    def control_frame_rate(self):
        if not (self.delay % 5):
            self.switch_image = not self.switch_image

        self.delay -= 1
        if not self.delay:
            self.delay = 100

    # 控制游戏难度
    def control_level(self):
        if self.level == 1 and self.score >= 5000:
            self.level = 2
            upgrade_sound.play()
            self.add_more_enemies(1, 1, 0)
            self.promote_speed(True, True)
        elif self.level == 2 and self.score >= 20000:
            self.level = 3
            upgrade_sound.play()
            self.add_more_enemies(2, 1, 1)
            self.promote_speed(True)
        elif self.level == 3 and self.score >= 40000:
            self.level = 4
            upgrade_sound.play()
            self.add_more_enemies(3, 2, 1)
        elif self.level == 4 and self.score >= 62000:
            self.level = 5
            upgrade_sound.play()
            self.add_more_enemies(3, 2, 2)
            self.promote_speed(True, True)
        elif self.level == 5 and self.score >= 88000:
            self.level = 6
            upgrade_sound.play()
            self.add_more_enemies(3, 2, 2)
            self.promote_speed(True, True, True)

    # 创建各种变量
    def __create_variables(self):

        self.switch_image = True
        self.delay = 100
        self.level = 1

        # 中弹索引
        self.big_down_index = 0
        self.mid_down_index = 0
        self.small_down_index = 0
        self.my_plane_index = 0

        self.small_speed = 2
        self.mid_speed = 1
        self.big_speed = 1

        self.score = 0
        self.super_bullet = False

        pygame.time.set_timer(HERO_FIRE_EVENT, 190)
        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)

        bg1 = Background()
        bg2 = Background(True)
        self.bg_group = pygame.sprite.Group(bg1, bg2)

        self.my_plane = MyPlane()

        self.enemies = pygame.sprite.Group()

        self.small_enemies = pygame.sprite.Group()
        self.add_enemies(self.small_enemies, self.enemies, 15, 1)

        self.mid_enemies = pygame.sprite.Group()
        self.add_enemies(self.mid_enemies, self.enemies, 5, 2)

        self.big_enemies = pygame.sprite.Group()
        self.add_enemies(self.big_enemies, self.enemies, 1, 3)

        self.bomb_supply = Supply('images/bomb_supply.png', 'sound/get_bomb.wav')
        self.bullet_supply = Supply('images/bullet_supply.png', 'sound/get_bullet.wav')

        self.pause = Control_Pause()

        self.tools = Bomb()

        self.over = pygame.image.load('./images/gameover.png')
        self.over_rect = self.over.get_rect()
        self.over_rect.centerx = SCREEN_RECT.centerx

        self.again = pygame.image.load('./images/again.png')
        self.again_rect = self.again.get_rect()
        self.again_rect.centerx = SCREEN_RECT.centerx

    # 绘制
    def draw_picture(self):

        # 大型敌机
        for each in self.big_enemies:
            if each.survival:
                each.update()
                if each.hit:
                    screen.blit(each.hit_image, each.rect)
                    each.hit = False
                else:
                    if self.switch_image:
                        screen.blit(each.image, each.rect)
                    else:
                        screen.blit(each.image2, each.rect)
                if each.rect.bottom == -30:
                    each.fly_sound.play(-1)

                # 绘制血槽
                each.draw_blood(screen, BIG_BLOOD)

            # 击毁
            else:
                if not (self.delay % 3):
                    screen.blit(each.destroy_images[self.big_down_index], each.rect)
                    self.big_down_index = (self.big_down_index + 1) % 6
                    if self.big_down_index == 0:
                        each.fly_sound.stop()
                        each.down_sound.play()
                        self.score += 1000
                        each.reset()

        # 中型敌机
        for each in self.mid_enemies:
            if each.survival:
                each.update()
                if each.hit:
                    screen.blit(each.hit_image, each.rect)
                    each.hit = False
                else:
                    screen.blit(each.image, each.rect)

                # 绘制血槽
                each.draw_blood(screen, MID_BLOOD)

            # 击毁
            else:
                if not (self.delay % 3):
                    screen.blit(each.destroy_images[self.mid_down_index], each.rect)
                    self.mid_down_index = (self.mid_down_index + 1) % 4
                    if self.mid_down_index == 0:
                        each.down_sound.play()
                        self.score += 500
                        each.reset()

        # 小型敌机
        for each in self.small_enemies:
            if each.survival:
                each.update()
                screen.blit(each.image, each.rect)

            # 击毁
            else:
                if not (self.delay % 3):
                    screen.blit(each.destroy_images[self.small_down_index], each.rect)
                    self.small_down_index = (self.small_down_index + 1) % 4
                    if self.small_down_index == 0:
                        each.down_sound.play()
                        self.score += 100
                        each.reset()

        # 绘制我机
        if self.my_plane.survival:
            if self.switch_image:
                screen.blit(self.my_plane.image1, self.my_plane.rect)
            else:
                screen.blit(self.my_plane.image2, self.my_plane.rect)
        else:
            self.my_plane.down_sound.play()
            if not (self.delay % 3):
                screen.blit(self.my_plane.destroy[self.my_plane_index], self.my_plane.rect)
                self.my_plane_index = (self.my_plane_index + 1) % 4
                if self.my_plane_index == 0:
                    self.my_plane.bullets.empty()
                    self.my_plane.life -= 1
                    self.my_plane.reset()
                    pygame.time.set_timer(INVINCIBLE_TIME, 3 * 1000)

        self.my_plane.update()

        # 绘制子弹
        self.my_plane.bullets.update()
        self.my_plane.bullets.draw(screen)

        # 绘制补给
        if self.bomb_supply.survival:
            self.bomb_supply.update()
            screen.blit(self.bomb_supply.image, self.bomb_supply.rect)
        if self.bullet_supply.survival:
            self.bullet_supply.update()
            screen.blit(self.bullet_supply.image, self.bullet_supply.rect)

        # 全屏炸弹图标
        self.tools.bomb_str = self.tools.bomb_font.render('x ' + str(self.tools.bomb_num),
                                                          True, BROWN)
        screen.blit(self.tools.bomb, self.tools.bomb_rect)
        screen.blit(self.tools.bomb_str, (self.tools.bomb_rect.right + 10,
                                          self.tools.bomb_rect.top - 5))

        # 绘制生命数
        for i in range(self.my_plane.life):
            screen.blit(self.my_plane.life_image,
                        (SCREEN_RECT.width - 10 - 2 * i - (i + 1) * self.my_plane.life_rect.width,
                         SCREEN_RECT.height - 5 - self.my_plane.life_rect.height))

        # 得分
        score_image = score_font.render("Score: " + str(self.score), True, GRAY)
        screen.blit(score_image, (10, 5))

        level_image = level_font.render("Level: " + str(self.level), True, DARK_GRAY)
        screen.blit(level_image, (15, 55))

    # 游戏结束/重新开始画面
    def choice_restart(self):
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        pygame.time.set_timer(SUPPLY_TIME, 0)
        pygame.time.set_timer(HERO_FIRE_EVENT, 0)

        self.bg_group.update()
        self.bg_group.draw(screen)

        with open(self.record_path, "r") as file:
            record_score = int(file.read())
        if self.score > record_score:
            with open(self.record_path, "w") as file:
                file.write(str(self.score))

        record_text = score_font.render("Best: " + str(record_score), True, GRAY)
        screen.blit(record_text, (50, 50))

        over_text1 = over_font.render("Your Score ", True, GRAY)
        over_rect1 = over_text1.get_rect()
        over_rect1.centerx = SCREEN_RECT.centerx
        over_rect1.top = SCREEN_RECT.height // 2
        over_text2 = over_font.render(str(self.score), True, GRAY)
        over_rect2 = over_text2.get_rect()
        over_rect2.centerx = SCREEN_RECT.centerx
        over_rect2.top = over_rect1.bottom + 10
        screen.blit(over_text1, over_rect1)
        screen.blit(over_text2, over_rect2)

        self.again_rect.top = over_rect2.bottom + 50
        self.over_rect.top = self.again_rect.bottom + 10
        screen.blit(self.again, self.again_rect)
        screen.blit(self.over, self.over_rect)

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if self.again_rect.left < pos[0] < self.again_rect.right and \
                    self.again_rect.top < pos[1] < self.again_rect.bottom:
                self.start_game()
            elif self.over_rect.left < pos[0] < self.over_rect.right and \
                    self.over_rect.top < pos[1] < self.over_rect.bottom:
                self.game_over()

    # 事件监听
    def event_handler(self):

        for event in pygame.event.get():

            # 关闭游戏
            if event.type == pygame.QUIT:
                self.game_over()

            # 释放全屏炸弹
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.tools.bomb_num:
                        self.tools.bomb_num -= 1
                        self.tools.bomb_sound.play()
                        for each in self.enemies:
                            if each.rect.bottom > 0:
                                each.survival = False

            # 装填子弹
            elif event.type == HERO_FIRE_EVENT:
                if self.pause.judge:
                    if not self.super_bullet:
                        self.my_plane.fire()
                    else:
                        self.my_plane.fire(True)
                    self.shoot_sound.play()

            # 补给
            elif event.type == SUPPLY_TIME:
                self.bomb_supply.sound.play()
                if random.choice([True, False]):
                    self.bomb_supply.reset()
                else:
                    self.bullet_supply.reset()

            elif event.type == SUPER_BULLET:
                self.super_bullet = False
                pygame.time.set_timer(SUPER_BULLET, 0)

            elif event.type == INVINCIBLE_TIME:
                self.my_plane.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)

            # 判断暂停
            else:
                self.pause.update(event)

        # 控制飞机移动
        key_press = pygame.key.get_pressed()
        if key_press[pygame.K_RIGHT] or key_press[pygame.K_d]:
            self.my_plane.move('right')
        elif key_press[pygame.K_LEFT] or key_press[pygame.K_a]:
            self.my_plane.move('left')
        elif key_press[pygame.K_UP] or key_press[pygame.K_w]:
            self.my_plane.move('up')
        elif key_press[pygame.K_DOWN] or key_press[pygame.K_s]:
            self.my_plane.move('down')
        else:
            self.my_plane.move()

    # 碰撞检测
    def collide_check(self):
        # 子弹与敌机碰撞检测
        for each in self.my_plane.bullets:
            enemies_hit = pygame.sprite.spritecollide(each, self.enemies, False, pygame.sprite.collide_mask)
            if enemies_hit:
                each.kill()
                for e in enemies_hit:
                    e.blood -= 1
                    e.hit = True
                    if e.blood == 0:
                        e.survival = False

        # 我机与敌机碰撞检测
        enemies_down = pygame.sprite.spritecollide(self.my_plane, self.enemies, False, pygame.sprite.collide_mask)
        if enemies_down and not self.my_plane.invincible:
            self.my_plane.survival = False
            for each in enemies_down:
                each.survival = False

        # 我机与补给碰撞检测
        if self.bomb_supply.survival:
            if pygame.sprite.collide_mask(self.bomb_supply, self.my_plane):
                self.bomb_supply.get_supply.play()
                if self.tools.bomb_num < 3:
                    self.tools.bomb_num += 1
                self.bomb_supply.survival = False
        if self.bullet_supply.survival:
            if pygame.sprite.collide_mask(self.bullet_supply, self.my_plane):
                pygame.time.set_timer(SUPER_BULLET, 18 * 1000)
                self.bullet_supply.get_supply.play()
                self.bullet_supply.survival = False
                self.super_bullet = True

    # 游戏结束
    @staticmethod
    def game_over():
        pygame.quit()
        sys.exit()

    def start_game(self):

        pygame.mixer.music.play(-1)

        self.__create_variables()

        # 游戏循环
        while True:

            # 背景(滚动)
            self.bg_group.update()
            self.bg_group.draw(screen)

            self.event_handler()

            if self.pause.judge and self.my_plane.life:
                self.collide_check()
                self.draw_picture()
                self.control_level()
            elif self.my_plane.life == 0:
                self.choice_restart()
            else:
                joke_part(self.pause.num)

            # 绘制暂停按钮
            screen.blit(self.pause.image, self.pause.rect)

            self.control_frame_rate()

            pygame.display.update()
            self.clock.tick(FRAME_RATE)


if __name__ == '__main__':
    player = MainGame()
    player.start_game()
    player.game_over()

