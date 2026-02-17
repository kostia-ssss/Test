from maze import maze
from tank_data import tank_data
from datetime import datetime
import pygame
pygame.init()

W, H = 800, 600
b_size, b_x, b_y = 64, 0, 0
i = 0
map_width, map_height = len(maze[0]) * b_size, len(maze) * b_size
window = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

pygame.display.set_caption("Battle City Remake")
pygame.display.set_icon(pygame.image.load("images/Player.png"))

pygame.mixer.music.load("sounds/menu_music.mp3")
# pygame.mixer.music.play(-1)
# pygame.mixer.music.set_volume(0.6)

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
        if self.t % 10 == 0:
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
        if self.t % 10 == 0:
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
        if self.t % 10 == 0:
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

    def update(self, obstacles):
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
        
    def fire(self):
        if self.patrons > 0 and self.t >= self.shooting_cd:
            self.t = 0
            self.patrons -= 1
            mouse_pos = pygame.mouse.get_pos()
            world_mouse = (
                (mouse_pos[0] - camera.x) / camera.zoom,
                (mouse_pos[1] - camera.y) / camera.zoom
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
    def __init__(self, x, y, w, h, image, speed, target_pos):
        super().__init__(x, y, w, h, image)

        self.speed = speed
        self.pos = pygame.Vector2(self.rect.center)

        direction = pygame.Vector2(target_pos) - self.pos

        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)

        self.direction = direction.normalize()

        self.alive = True  # 👈 флаг життя

    def move(self, player):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        if (
            self.rect.right < 0 or
            self.rect.left > W + player.rect.x or
            self.rect.bottom < 0 or
            self.rect.top > H + player.rect.y
        ):
            self.alive = False

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

def update_player_costume():
    img = pygame.image.load(f"images/{costume}.png").convert_alpha()

    player.r_img = pygame.transform.scale(img, (50, 50))
    player.l_img = pygame.transform.rotate(player.r_img, 180)
    player.u_img = pygame.transform.rotate(player.r_img, 90)
    player.d_img = pygame.transform.rotate(player.r_img, 270)

    player.img = player.r_img

    player.speed = tank_data[costume]["Speed"]
    player.hp = tank_data[costume]["HP"]
    player.base_speed = player.speed


font = pygame.font.SysFont("Century Gothic", 20, True)
version_txt = font.render("V1.0", True, (0, 0, 0))

bullet_img = pygame.image.load("images/Bullet.png")
menu_bg = Sprite(-W/2, -H/2, 2*W, 2*H, pygame.image.load("images/BG.png"))
game_bg = Sprite(0, 0, map_width, map_height, pygame.image.load("images/GameBG.png"))
play_button = Sprite(W/2-85, H/2-35, 170, 70, pygame.image.load("images/Play.png"))
exit_button = Sprite(W/2-85, H/2+55, 170, 70, pygame.image.load("images/Exit.png"))
shop_button = Sprite(W/2-85, H/2+145, 170, 70, pygame.image.load("images/Shop.png"))
close_shop_button = Sprite(0, 0, 50, 50, pygame.image.load("images/Close.png"))
buy_slow = ShopTile(100, 100, 150, 210, pygame.image.load("images/BuySlow.png"), 
                    pygame.image.load("images/Buy.png"), "Slow")
buy_fast = ShopTile(270, 100, 150, 210, pygame.image.load("images/BuyFast.png"), 
                    pygame.image.load("images/Buy.png"), "Fast")
player = Player(100, 100, pygame.image.load("images/Player.png"), 5, 50)
camera = Camera()
world_surface = pygame.Surface((map_width, map_height)).convert()
obstacles = []
tiles = []
bullets = []
turrets = []

for row in maze:
    for char in row:
        if char == "1":
            obstacles.append(Sprite(b_x, b_y, b_size, b_size, pygame.image.load("images/Wall.png")))
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
                                50, pygame.image.load("images/BadBullet.png"), 2, -1))
        if char == "9":
            turrets.append(Turret(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/TurretLeft.png"),
                                50, pygame.image.load("images/BadBullet.png"), 2, 1))
        b_x += b_size
    b_y += b_size
    b_x = 0

running = True
menu = True
shop = False
lose = False
costume = "Player"
bought_costumes = {"Player"}

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
            if play_button.rect.collidepoint(x, y):
                menu = False
                write_info("log.txt", "CLOSED MENU")
            if shop_button.rect.collidepoint(x, y):
                menu = False
                shop = True
                write_info("log.txt", "OPENED SETTINGS")
            if exit_button.rect.collidepoint(x, y):
                running = False
            if close_shop_button.rect.collidepoint(x, y):
                shop = False
                menu = True
            if buy_slow.button.rect.collidepoint(x, y):
                buy_slow.button.onclick()
            if buy_fast.button.rect.collidepoint(x, y):
                buy_fast.button.onclick()
        if keys[pygame.K_SPACE]:
            player.fire()
        if keys[pygame.K_1] and "Slow" in bought_costumes:
            costume = "Player"
            update_player_costume()
        elif keys[pygame.K_2] and "Slow" in bought_costumes:
            costume = "Slow"
            update_player_costume()
        elif keys[pygame.K_3] and "Fast" in bought_costumes:
            costume = "Fast"
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
        
        menu_bg.rect.x += (pygame.mouse.get_pos()[0] - last_mouse_x) / 10
        menu_bg.rect.y += (pygame.mouse.get_pos()[1] - last_mouse_y) / 10

        window.blit(world_surface, (0, 0))
    elif shop:
        menu_bg.draw(world_surface)
        close_shop_button.draw(world_surface)
        
        buy_slow.draw(world_surface)
        buy_fast.draw(world_surface)
        
        if "Slow" not in bought_costumes:
            buy_slow.button.draw(world_surface)
        if "Fast" not in bought_costumes:
            buy_fast.button.draw(world_surface)
        
        window.blit(world_surface, (0, 0))
    elif lose:
        pass
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
        fps = clock.get_fps()
        fps_txt = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        window.blit(fps_txt, (0, 0))

        patrons_txt = font.render(f"Patrons: {player.patrons}", True, (255, 255, 255))
        window.blit(patrons_txt, (0, 20))

        hp_txt = font.render(f"HP: {player.hp}", True, (255, 255, 255))
        window.blit(hp_txt, (0, 40))
    
    pygame.display.update()
    clock.tick()
pygame.quit()