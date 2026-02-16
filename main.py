from maze import maze
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

class Sprite:
    def __init__(self , x , y , w , h, img):
        self.img = img
        self.rect = pygame.Rect(x, y, w, h)
        self.img = pygame.transform.scale(self.img , (w, h))
    
    def draw(self):
        scaled_img = pygame.transform.scale(
            self.img,
            (
                int(self.rect.w * camera.zoom),
                int(self.rect.h * camera.zoom)
            )
        )

        draw_x = self.rect.x * camera.zoom + camera.x
        draw_y = self.rect.y * camera.zoom + camera.y
        
        if player.rect.x + W > draw_x or player.rect.y + H > draw_y:
            window.blit(scaled_img, (draw_x, draw_y))

class SlowTile(Sprite):
    def __init__(self, x, y, w, h, img, slowing_coof):
        super().__init__(x, y, w, h, img)
        self.slowing_coof = slowing_coof
    
    def effect(self, player):
        player.speed = player.base_speed / self.slowing_coof
        
class FastTile(Sprite):
    def __init__(self, x, y, w, h, img, speeding_coof):
        super().__init__(x, y, w, h, img)
        self.speeding_coof = speeding_coof
    
    def effect(self, player):
        player.speed = player.base_speed * self.speeding_coof

class MoveTile(Sprite):
    def __init__(self, x, y, w, h, img, direction):
        super().__init__(x, y, w, h, img)
        self.direction = direction
    
    def effect(self, player):
        if self.direction == "up":
            player.rect.y -= 3
        if self.direction == "down":
            player.rect.y += 3
        if self.direction == "left":
            player.rect.x -= 3
        if self.direction == "right":
            player.rect.x += 3

class Player(Sprite):
    def __init__(self, x, y, img, speed, scale=64, patrons=30):
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

def update_player_image():
    player.r_img = pygame.image.load(f"images/{costume}.png")
    player.l_img = pygame.transform.rotate(player.r_img, 180)
    player.u_img = pygame.transform.rotate(player.r_img, 90)
    player.d_img = pygame.transform.rotate(player.r_img, 270)

font = pygame.font.SysFont("Century Gothic", 20, True)
version_txt = font.render("V0.8", True, (0, 0, 0))

bullet_img = pygame.image.load("images/Bullet.png")
menu_bg = Sprite(-W/2, -H/2, 2*W, 2*H, pygame.image.load("images/BG.png"))
game_bg = Sprite(0, 0, map_width, map_height, pygame.image.load("images/GameBG.png"))
play_button = Sprite(W/2-85, H/2-35, 170, 70, pygame.image.load("images/Play.png"))
exit_button = Sprite(W/2-85, H/2+55, 170, 70, pygame.image.load("images/Exit.png"))
shop_button = Sprite(W/2-85, H/2+145, 170, 70, pygame.image.load("images/Shop.png"))
close_shop_button = Sprite(0, 0, 50, 50, pygame.image.load("images/Close.png"))
buy_slow = Sprite(100, 100, 100, 140, pygame.image.load("images/BuySlow.png"))
buy_slow_button = Sprite(110, 190, 80, 40, pygame.image.load("images/Buy.png"))
player = Player(100, 100, pygame.image.load("images/Player.png"), 5, 50)
camera = Camera()
obstacles = []
tiles = []
bullets = []

for row in maze:
    for char in row:
        if char == "1":
            obstacles.append(Sprite(b_x, b_y, b_size, b_size, pygame.image.load("images/Wall.png")))
        if char == "2":
            tiles.append(SlowTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Slow.png"), 1.7))
        if char == "3":
            tiles.append(FastTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Fast.png"), 2))
        if char == "4":
            tiles.append(MoveTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Tiles/Down.png"), "down"))
        b_x += b_size
    b_y += b_size
    b_x = 0

running = True
menu = True
shop = False
costume = "Player"
bought_costumes = {"Player"}

while running:
    i += 1
    update_player_image()
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
            if buy_slow_button.rect.collidepoint(x, y):
                bought_costumes.add("Slow")
                print("!!")
        if keys[pygame.K_SPACE]:
            player.fire()
        if keys[pygame.K_1]:
            costume = "Player"
        elif keys[pygame.K_2] and "Slow" in bought_costumes:
            costume = "Slow"
        if event.type == pygame.MOUSEWHEEL:
            camera.zoom += event.y * 0.1

            # Обмеження
            if camera.zoom < 0.5:
                camera.zoom = 0.5
            if camera.zoom > 2:
                camera.zoom = 2

    if menu:
        menu_bg.draw()
        play_button.draw()
        exit_button.draw()
        shop_button.draw()
        window.blit(version_txt, (0, 0))
        
        menu_bg.rect.x += (pygame.mouse.get_pos()[0] - last_mouse_x) / 10
        menu_bg.rect.y += (pygame.mouse.get_pos()[1] - last_mouse_y) / 10
    elif shop:
        menu_bg.draw()
        close_shop_button.draw()
        buy_slow.draw()
        if "Slow" not in bought_costumes:
            buy_slow_button.draw()
    else:
        game_bg.draw()
    
        for obstacle in obstacles:
            obstacle.draw()
            
        for tile in tiles:
            tile.draw()
            if player.rect.colliderect(tile.rect):
                tile.effect(player)
        
        for bullet in bullets:
            bullet.draw()
            bullet.move(player)

        # 🔥 Очищення після руху
        bullets = [b for b in bullets if b.alive]

        fps = clock.get_fps()
        fps_txt = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        window.blit(fps_txt, (0, 0))
        patrons_txt = font.render(f"Patrons: {player.patrons}", True, (255, 255, 255))
        window.blit(patrons_txt, (0, 20))
        if i % 10 == 0:
            write_info("log.txt", f"FPS: {fps}")
        
        player.update(obstacles)
        player.draw()
        player.speed = player.base_speed
        camera.update(player)
    
    pygame.display.update()
    clock.tick(60)
pygame.quit()