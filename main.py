from maze import all_levels
from tank_data import tank_data
from datetime import datetime
from random import randint
import math
import pygame
pygame.init()

W, H = 800, 600
b_size, b_x, b_y = 64, 0, 0
low_fps = False
i = 0
score = 0
obstacles = []
tiles = []
bullets = []
turrets = []
spawners = []
map_width, map_height = len(all_levels[0][0]) * b_size, len(all_levels[0]) * b_size
window = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

pygame.display.set_caption("Battle City Remake")
pygame.display.set_icon(pygame.image.load("images/Tanks/Player.png"))

pygame.mixer.music.load("sounds/menu_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

class Sprite:
    def __init__(self , x , y , w , h, img):
        self.original_img = img.convert_alpha()
        self.img = pygame.transform.scale(self.original_img , (w, h))
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        surface.blit(self.img, self.rect)

class Button(Sprite):
    def __init__(self, x, y, w, h, img, onclick):
        super().__init__(x, y, w, h, img)
        self.onclick = onclick
        self.t = 0
        
        self.base_w = w
        self.base_h = h

    def update(self):
        self.t += 0.01
        
        scale_offset = math.sin(self.t) * 5
        
        new_w = int(self.base_w + scale_offset)
        new_h = int(self.base_h + scale_offset)
        
        self.rect.w = new_w
        self.rect.h = new_h
        
        self.img = pygame.transform.scale(
            self.original_img, 
            (new_w, new_h)
        )
        
    
class ShopTile(Sprite):
    def __init__(self, x, y, w, h, img, button_img, new_costume):
        super().__init__(x, y, w, h, img)
        self.new_costume = new_costume
        self.button = Button(x+20, h-50+y, w-40, 40, button_img, self.on_button_click)
    
    def on_button_click(self):
        bought_costumes.add(self.new_costume)
        
class SlowTile(Sprite):
    def __init__(self, x, y, w, h, img1, img2, slowing_coof):
        super().__init__(x, y, w, h, img1)
        self.slowing_coof = slowing_coof
        self.t = 0
        self.img1 = img1
        self.img2 = img2
    
    def effect(self, player):
        player.speed = player.base_speed / self.slowing_coof
    
    def update(self):
        self.t += 1
        if self.t % 10 == 0 and not low_fps:
            self.img = self.img2 if self.img != self.img2 else self.img1
        
class FastTile(Sprite):
    def __init__(self, x, y, w, h, img1, img2, speeding_coof):
        super().__init__(x, y, w, h, img1)
        self.speeding_coof = speeding_coof
        self.t = 0
        self.img1 = img1
        self.img2 = img2
    
    def effect(self, player):
        player.speed = player.base_speed * self.speeding_coof
        
    def update(self):
        self.t += 1
        if self.t % 10 == 0 and not low_fps:
            self.img = self.img2 if self.img != self.img2 else self.img1
    
class MoveTile(Sprite):
    def __init__(self, x, y, w, h, img1, img2, direction):
        super().__init__(x, y, w, h, img1)
        self.direction = direction
        self.t = 0
        self.img1 = img1
        self.img2 = img2
    
    def effect(self, player):
        if self.direction == "up":
            player.rect.y -= 3
        if self.direction == "down":
            player.rect.y += 3
        if self.direction == "left":
            player.rect.x -= 3
        if self.direction == "right":
            player.rect.x += 3
    
    def update(self):
        self.t += 1
        if self.t % 10 == 0 and not low_fps:
            self.img = self.img2 if self.img != self.img2 else self.img1

class Player(Sprite):
    def __init__(self, x, y, img, speed, scale=64, patrons=30, hp=5):
        self.r_img = pygame.transform.scale(img, (scale, scale))
        self.l_img = pygame.transform.rotate(self.r_img, 180)
        self.u_img = pygame.transform.rotate(self.r_img, 90)
        self.d_img = pygame.transform.rotate(self.r_img, 270)
        super().__init__(x, y, scale, scale, self.r_img)
        
        self.base_speed = speed
        self.speed = self.base_speed
        self.shooting_pos_x, self.shooting_pos_y = self.rect.centerx + 20, self.rect.centery - 4
        self.direction = "up"
        self.max_patrons = patrons
        self.patrons = self.max_patrons
        self.max_wait = 170
        self.wait = 0
        self.shooting_cd = 10
        self.t = 0
        self.hp = hp
        self.max_hp = hp

    def update(self, obstacles):
        global lose, score
        
        old_x, old_y = self.rect.x, self.rect.y
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            self.img = self.l_img
            self.shooting_pos_x, self.shooting_pos_y = self.rect.centerx - 20, self.rect.centery - 4
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            self.img = self.r_img
            self.shooting_pos_x, self.shooting_pos_y = self.rect.centerx + 20, self.rect.centery - 4
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.direction = "up"
            self.img = self.u_img
            self.shooting_pos_x, self.shooting_pos_y = self.rect.centerx + 4, self.rect.centery - 20
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            self.direction = "down"
            self.img = self.d_img
            self.shooting_pos_x, self.shooting_pos_y = self.rect.centerx - 4, self.rect.centery + 20
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.rect.x, self.rect.y = old_x, old_y
                break
        self.wait += 1
        self.t += 1
        if self.wait >= self.max_wait and self.patrons < self.max_patrons:
            self.wait = 0
            self.patrons += min(self.max_patrons-self.patrons, 5)
        
        if self.hp <= 0:
            set_score(score)
            lose = True
        
    def fire(self, view_x, view_y):
        if self.patrons > 0 and self.t >= self.shooting_cd:
            self.t = 0
            self.patrons -= 1
            mouse_pos = pygame.mouse.get_pos()
            world_mouse = (
                mouse_pos[0] / camera.zoom + view_x,
                mouse_pos[1] / camera.zoom + view_y
            )

            bullets.append(Bullet(
                self.shooting_pos_x,
                self.shooting_pos_y,
                10, 10,
                bullet_img,
                8,
                world_mouse
            ))
                
class Bullet(Sprite):
    def __init__(self, x, y, w, h, image, speed, target_pos, type="good"):
        super().__init__(x, y, w, h, image)

        self.speed = speed
        self.pos = pygame.Vector2(self.rect.center)

        direction = pygame.Vector2(target_pos) - self.pos

        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)

        self.direction = direction.normalize()

        self.alive = True  # 👈 флаг життя
        self.type = type

    def move(self, player):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        if (
            self.rect.right < 0 or
            self.rect.left > W + player.rect.x or
            self.rect.bottom < 0 or
            self.rect.top > H + player.rect.y or
            any(self.rect.colliderect(o) for o in obstacles)
        ): self.alive = False

class Turret(Sprite):
    def __init__(self, x, y, w, h, img, cooldown, bullet_img, bullet_speed, direction):
        super().__init__(x, y, w, h, img)
        self.cd = cooldown
        self.bullet_img = bullet_img
        self.t = 0
        self.bullets = []
        self.bullet_speed = bullet_speed
        self.dir = direction
    
    def update(self):
        self.t += 1
        if self.t % self.cd == 0:
            self.bullets.append(Sprite(self.rect.centerx, self.rect.centery, 10, 10, self.bullet_img))
        
        for b in self.bullets:
            b.draw(world_surface)
            if self.dir > 0:
                b.rect.x += self.bullet_speed
            else:
                b.rect.x -= self.bullet_speed
            if b.rect.x > map_width or b.rect.x < 0 or any(b.rect.colliderect(o.rect) for o in obstacles):
                self.bullets.remove(b)
            if player.rect.colliderect(b.rect): 
                player.hp -= 1
                self.bullets.remove(b)

class Enemy(Sprite):
    def __init__(self, x, y, w, h, img, cooldown, bullet_img, range, speed, see_distance, hp):
        super().__init__(x, y, w, h, img)
        self.cooldown = cooldown
        self.bullet_img = bullet_img
        self.range = range
        self.original_img = img
        self.bullets = []
        self.t = 0
        self.speed = speed
        self.see_distance = see_distance
        self.hp = hp
        self.alive = True

    def shoot(self, player):
        pos = (
            player.rect.x + randint(-self.range, self.range),
            player.rect.y + randint(-self.range, self.range)
        )

        print(pos)

        self.bullets.append(
            Bullet(
                self.rect.centerx,
                self.rect.centery,
                10, 10,
                self.bullet_img,
                4,
                pos,
                "bad"
            )
        )

    def move(self, player):
        self.original = self.rect.copy()
        
        dh = self.rect.x - player.rect.x
        dv = self.rect.y - player.rect.y

        if abs(dh) > abs(dv):
            if dh > 0:
                self.rect.x -= self.speed
                self.img = pygame.transform.rotate(self.original_img, 180)
            elif dh < 0:
                self.rect.x += self.speed
                self.img = self.original_img
        else:
            if dv > 0:
                self.rect.y -= self.speed
                self.img = pygame.transform.rotate(self.original_img, 90)
            elif dv < 0:
                self.rect.y += self.speed
                self.img = pygame.transform.rotate(self.original_img, 270)
        
        self.img = pygame.transform.scale(self.img, (self.rect.w, self.rect.h))
        
        if any(self.rect.colliderect(o) for o in obstacles):
            self.rect = self.original
        
    def update(self):
        global score
        self.t += 1
        
        for b in self.bullets:
            b.draw(world_surface)
            b.move(player)
        
        if abs(self.rect.x-player.rect.x) < self.see_distance and abs(self.rect.y-player.rect.y) < self.see_distance:
            self.move(player)
            if self.t % self.cooldown == 0:
                self.shoot(player)
        
        for b in bullets:
            if self.rect.colliderect(b):
                self.hp -= 1
                score += 1
                bullets.remove(b)
        
        if any(self.rect.colliderect(o) for o in obstacles):
            self.rect.y += 1
        if self.hp <= 0: self.alive = False
            
        self.bullets[:] = [b for b in self.bullets if b.alive]

class EnemySpawner:
    def __init__(self, x, y, cooldown, max_enemies):
        self.x = x
        self.y = y
        self.cooldown = cooldown
        self.max_enemies = max_enemies
        self.enemies = []
        self.t = 0
    
    def spawn(self):
        self.enemies.append(Enemy(self.x+randint(-100, 100), self.y+randint(-100, 100), 
                                  50, 50, pygame.image.load("images/Tanks/Enemy.png"), 
                                  70, pygame.image.load("images/Bullets/BadBullet.png"), 
                                  150, 1, 300, 5))
    
    def update(self):
        self.t += 1
        
        for e in self.enemies:
            e.draw(world_surface)
            e.update()
        
        if self.t % self.cooldown == 0 and len(self.enemies) < self.max_enemies:
            self.spawn()
            

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0  # 👈 рівень зуму

    def update(self, player):
        self.x = -player.rect.centerx * self.zoom + W // 2
        self.y = -player.rect.centery * self.zoom + H // 2

def write_info(path, info):
    now = datetime.now()
    formatted = f"[{now.strftime('%d.%m.%Y')}] [{now.strftime('%H:%M')}]"
    with open(path, "a", encoding="utf-8") as file:
        file.write(f"{formatted} {info}\n")
        print("AAA")

def update_player_costume():
    global bullet_img
    img = pygame.image.load(f"images/Tanks/{costume}.png").convert_alpha()
    bullet_img = pygame.image.load(f"images/Bullets/{costume}Bullet.png").convert_alpha()

    player.r_img = pygame.transform.scale(img, (50, 50))
    player.l_img = pygame.transform.rotate(player.r_img, 180)
    player.u_img = pygame.transform.rotate(player.r_img, 90)
    player.d_img = pygame.transform.rotate(player.r_img, 270)

    player.img = player.r_img

    # 🔥 Зберігаємо відсоток HP
    hp_percent = player.hp / player.max_hp

    # Нові характеристики
    player.max_hp = tank_data[costume]["HP"]
    player.base_speed = tank_data[costume]["Speed"]
    player.speed = player.base_speed

    # Перераховуємо HP
    player.hp = max(1, round(player.max_hp * hp_percent)) if hp_percent > 0 else 0


def go_to_menu():
    global lose, menu
    lose = False
    menu = True

def fade_in(screen, width, height):
    fade_s = pygame.Surface((width, height)).convert()
    fade_s.fill((0, 0, 0))

    for a in range(0, 256, 5):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        fade_s.set_alpha(a)
        screen.blit(fade_s, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)


def fade_out(screen, width, height):
    fade_s = pygame.Surface((width, height)).convert()
    fade_s.fill((0, 0, 0))

    for a in range(255, -1, -5):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        fade_s.set_alpha(a)
        screen.blit(fade_s, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

def get_previous_score():
    with open("score.txt", "r", encoding="utf-8") as file: 
        return int(file.read())

def set_score(score):
    with open("score.txt", "w", encoding="utf-8") as file: 
        file.write(str(score))

def load_level(index):
    global map_width, map_height, b_x, b_y
    level = all_levels[index]
    map_width, map_height = len(level[0]) * b_size, len(level) * b_size
    obstacles.clear()
    tiles.clear()
    bullets.clear()
    turrets.clear()
    spawners.clear()
    for row in level:
        for char in row:
            if char == "1":
                obstacles.append(Sprite(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Wall.png")))
            if char == "2":
                tiles.append(SlowTile(b_x, b_y, b_size, b_size, 
                                    pygame.image.load("images/Tiles/Slow.png"),
                                    pygame.image.load("images/Tiles/Slow2.png"),1.7))
            if char == "3":
                tiles.append(FastTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Fast.png"), 
                                    pygame.image.load("images/Tiles/Fast2.png"), 2))
            if char == "4":
                tiles.append(MoveTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Down.png"),
                                    pygame.image.load("images/Tiles/Down2.png"), "down"))
            if char == "5":
                tiles.append(MoveTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Up.png"),
                                    pygame.image.load("images/Tiles/Up2.png"), "up"))
            if char == "6":
                tiles.append(MoveTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Right.png"),
                                    pygame.image.load("images/Tiles/Right2.png"), "right"))
            if char == "7":
                tiles.append(MoveTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Left.png"),
                                    pygame.image.load("images/Tiles/Left2.png"), "left"))
            if char == "8":
                turrets.append(Turret(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/TurretRight.png"),
                                    50, pygame.image.load("images/Bullets/BadBullet.png"), 2, -1))
            if char == "9":
                turrets.append(Turret(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/TurretLeft.png"),
                                    50, pygame.image.load("images/Bullets/BadBullet.png"), 2, 1))
            if char == "#":
                spawners.append(EnemySpawner(b_x, b_y, 150, 2))
            b_x += b_size
        b_y += b_size
        b_x = 0

def start_game():
    global menu
    menu = False

def exit_game():
    global running
    running = False

def open_shop():
    global shop, menu
    menu = False
    shop = True

font = pygame.font.SysFont("Century Gothic", 20, True)
version_txt = font.render("V1.5", True, (0, 0, 0))

bullet_img = pygame.image.load("images/Bullets/PlayerBullet.png")
menu_bg = Sprite(-W/2, -H/2, 2*W, 2*H, pygame.image.load("images/BG/BG.png"))
game_bg = Sprite(0, 0, map_width, map_height, pygame.image.load("images/BG/GameBG.png"))
lose_bg = Sprite(0, 0, W, H, pygame.image.load("images/BG/LoseBG.png"))
play_button = Button(W/2-85, H/2-35, 170, 70, pygame.image.load("images/Buttons/Play.png"), start_game)
exit_button = Button(W/2-85, H/2+55, 170, 70, pygame.image.load("images/Buttons/Exit.png"), exit_game)
shop_button = Button(W/2-85, H/2+145, 170, 70, pygame.image.load("images/Buttons/Shop.png"), open_shop)
close_shop_button = Sprite(0, 0, 50, 50, pygame.image.load("images/Buttons/Close.png"))
close_game_button = Sprite(W-50, 0, 50, 50, pygame.image.load("images/Buttons/Close.png"))

buy_slow = ShopTile(100, 100, 150, 210, pygame.image.load("images/ShopTiles/BuySlow.png"), 
                    pygame.image.load("images/Buttons/Buy.png"), "Slow")
buy_fast = ShopTile(270, 100, 150, 210, pygame.image.load("images/ShopTiles/BuyFast.png"), 
                    pygame.image.load("images/Buttons/Buy.png"), "Fast")
buy_hyper = ShopTile(440, 100, 150, 210, pygame.image.load("images/ShopTiles/BuyHyper.png"), 
                    pygame.image.load("images/Buttons/Buy.png"), "Hyper")
to_menu = Button(W/2, H/2, 100, 40, pygame.image.load("images/Buttons/Menu.png"), go_to_menu)
player = Player(75, 75, pygame.image.load("images/Tanks/Player.png"), 5, 50)
camera = Camera()
world_surface = pygame.Surface((map_width, map_height)).convert()

running = True
menu = True
levels_menu = False
shop = False
lose = False
fade_alpha = 0
fading = False
fade_direction = 1  # 1 = затемнення, -1 = освітлення
fade_speed = 8
next_state = None
costume = "Player"
bought_costumes = {"Player"}
score = get_previous_score()
load_level(0)

while running:
    i += 1
    window.fill((0, 0, 0))
    last_mouse_x, last_mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if menu:
                if play_button.rect.collidepoint(x, y):
                    fading = True
                    fade_direction = 1
                    fade_alpha = 0
                    next_state = "game"

                elif shop_button.rect.collidepoint(x, y):
                    fading = True
                    fade_direction = 1
                    fade_alpha = 0
                    next_state = "shop"

                elif exit_button.rect.collidepoint(x, y):
                    running = False

            elif shop:
                if close_shop_button.rect.collidepoint(x, y):
                    fading = True
                    fade_direction = 1
                    fade_alpha = 0
                    next_state = "menu"

                elif buy_slow.button.rect.collidepoint(x, y) and score >= 10:
                    buy_slow.button.onclick()
                    score -= 10

                elif buy_fast.button.rect.collidepoint(x, y) and score >= 10:
                    buy_fast.button.onclick()
                    score -= 10
                
                elif buy_hyper.button.rect.collidepoint(x, y) and score >= 60:
                    buy_hyper.button.onclick()
                    score -= 60

            elif lose:
                if to_menu.rect.collidepoint(x, y):
                    to_menu.onclick()
                    player.hp = player.max_hp
            
            else:
                if close_game_button.rect.collidepoint(x, y):
                    set_score(score)
                    fading = True
                    fade_direction = 1
                    fade_alpha = 0
                    next_state = "menu"

        if keys[pygame.K_SPACE]:
            player.fire(view_x, view_y)
            
        if keys[pygame.K_LSHIFT] and keys[pygame.K_TAB] and keys[pygame.K_w]:
            score += 1000000
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and "Player" in bought_costumes:
                costume = "Player"
                update_player_costume()

            elif event.key == pygame.K_2 and "Slow" in bought_costumes:
                costume = "Slow"
                update_player_costume()

            elif event.key == pygame.K_3 and "Fast" in bought_costumes:
                costume = "Fast"
                update_player_costume()
            
            elif event.key == pygame.K_4 and "Hyper" in bought_costumes:
                costume = "Hyper"
                update_player_costume()
                
        if event.type == pygame.MOUSEWHEEL:
            camera.zoom += event.y * 0.1

            # Обмеження
            if camera.zoom < 0.5:
                camera.zoom = 0.5
            if camera.zoom > 2:
                camera.zoom = 2

    if menu:
        menu_bg.draw(world_surface)
        play_button.draw(world_surface)
        exit_button.draw(world_surface)
        shop_button.draw(world_surface)
        window.blit(version_txt, (0, 0))
        
        play_button.update()
        exit_button.update()
        shop_button.update()
        
        menu_bg.rect.x += (pygame.mouse.get_pos()[0] - last_mouse_x) / 10
        menu_bg.rect.y += (pygame.mouse.get_pos()[1] - last_mouse_y) / 10

        window.blit(world_surface, (0, 0))
        
    elif shop:
        menu_bg.draw(world_surface)
        close_shop_button.draw(world_surface)
        
        buy_slow.draw(world_surface)
        buy_fast.draw(world_surface)
        buy_hyper.draw(world_surface)
        
        if "Slow" not in bought_costumes:
            buy_slow.button.draw(world_surface)
        if "Fast" not in bought_costumes:
            buy_fast.button.draw(world_surface)
        if "Hyper" not in bought_costumes:
            buy_hyper.button.draw(world_surface)
        
        window.blit(world_surface, (0, 0))
        
    elif lose:
        world_surface.fill((0, 0, 0))
        lose_bg.draw(world_surface)
        to_menu.draw(world_surface)
        window.blit(world_surface, (0, 0))
        
    else:
        world_surface.fill((0, 0, 0))

        game_bg.draw(world_surface)

        for obstacle in obstacles:
            obstacle.draw(world_surface)

        player.speed = player.base_speed
        for tile in tiles:
            tile.update()
            tile.draw(world_surface)
            if player.rect.colliderect(tile.rect):
                tile.effect(player)

        for bullet in bullets:
            bullet.move(player)
            bullet.draw(world_surface)
        
        for spawner in spawners:
            spawner.update()
            for enemy in spawner.enemies:
                if enemy.alive:
                    enemy.draw(world_surface)
                    enemy.update()
                else:
                    spawner.enemies.remove(enemy)
                    
                for bullet in enemy.bullets:
                    if player.rect.colliderect(bullet.rect):
                        player.hp -= 1
                        bullet.alive = False
        
        for turret in turrets:
            turret.update()
            turret.draw(world_surface)

        bullets[:] = [b for b in bullets if b.alive]

        
        player.update(obstacles)
        player.draw(world_surface)

        camera.update(player)

        view_width = int(W / camera.zoom)
        view_height = int(H / camera.zoom)

        # Центруємо на гравці
        view_x = int(player.rect.centerx - view_width // 2)
        view_y = int(player.rect.centery - view_height // 2)

        # Обмежуємо межами карти
        view_x = max(0, min(map_width - view_width, view_x))
        view_y = max(0, min(map_height - view_height, view_y))

        view_rect = pygame.Rect(view_x, view_y, view_width, view_height)

        sub_surface = world_surface.subsurface(view_rect).copy()

        scaled_view = pygame.transform.scale(sub_surface, (W, H))

        window.blit(scaled_view, (0, 0))


        # UI
        close_game_button.draw(window)
        
        fps = clock.get_fps()
        fps_txt = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        window.blit(fps_txt, (0, 0))

        patrons_txt = font.render(f"Patrons: {player.patrons}", True, (255, 255, 255))
        window.blit(patrons_txt, (0, 20))

        hp_txt = font.render(f"HP: {player.hp}", True, (255, 255, 255))
        window.blit(hp_txt, (0, 40))

        score_txt = font.render(f"Score: {score}", True, (255, 255, 255))
        window.blit(score_txt, (0, 60))
    
    if fading:
        fade_surface = pygame.Surface((W, H))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        window.blit(fade_surface, (0, 0))

        fade_alpha += fade_speed * fade_direction

        # Коли повністю затемнилось
        if fade_alpha >= 255:
            fade_alpha = 255

            # 👇 тут міняємо стан
            if next_state == "game":
                menu = False
                shop = False
                write_info("log.txt", "CLOSED MENU")
            if next_state == "shop":
                menu = False
                shop = True
                write_info("log.txt", "OPENED SHOP")
            if next_state == "menu":
                menu = True
                shop = False
                write_info("log.txt", "OPENED MENU")

            fade_direction = -1  # починаємо освітлення

        # Коли повністю освітлилось
        if fade_alpha <= 0 and fade_direction == -1:
            fade_alpha = 0
            fading = False
            next_state = None

    write_info("log.txt", f"FPS: {round(clock.get_fps(), 2)}")
    
    pygame.display.update()
    clock.tick(60)
pygame.quit()