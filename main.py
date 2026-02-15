from maze import maze
import pygame
pygame.init()

W, H = 800, 600
b_size, b_x, b_y = 64, 0, 0
map_width, map_height = len(maze[0]) * b_size, len(maze) * b_size
window = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

pygame.display.set_caption("Battle City Remake")
pygame.display.set_icon(pygame.image.load("images/Player.png"))

pygame.mixer.music.load("sounds/menu_music.mp3")
pygame.mixer.music.play(-1)

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

class Player(Sprite):
    def __init__(self, x, y, w, h, img, speed):
        super().__init__(x, y, w, h, img)
        self.base_speed = speed
        self.speed = self.base_speed
        self.direction = "up"
    
    def update(self, obstacles):
        old_x, old_y = self.rect.x, self.rect.y
        keys = pygame.key.get_pressed()
    
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            self.direction = "down"
        
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.rect.x, self.rect.y = old_x, old_y
                break
            
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

    def move(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        if (
            self.rect.right < 0 or
            self.rect.left > map_width or
            self.rect.bottom < 0 or
            self.rect.top > map_height
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

font = pygame.font.SysFont("Century Gothic", 20, True)

bullet_img = pygame.image.load("images/Bullet.png")
menu_bg = Sprite(-W/2, -H/2, 2*W, 2*H, pygame.image.load("images/BG.png"))
game_bg = Sprite(0, 0, map_width, map_height, pygame.image.load("images/GameBG.png"))
play_button = Sprite(W/2-85, H/2-35, 170, 70, pygame.image.load("images/Play.png"))
exit_button = Sprite(W/2-85, H/2+55, 170, 70, pygame.image.load("images/Exit.png"))
player = Player(100, 100, 50, 50, pygame.image.load("images/Player.png"), 5)
camera = Camera()
obstacles = []
tiles = []
bullets = []

for row in maze:
    for char in row:
        if char == "1":
            obstacles.append(Sprite(b_x, b_y, b_size, b_size, pygame.image.load("images/Wall.png")))
        if char == "2":
            tiles.append(SlowTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Slow.png"), 1.7))
        if char == "3":
            tiles.append(FastTile(b_x, b_y, b_size, b_size, pygame.image.load("images/Fast.png"), 2))
        b_x += b_size
    b_y += b_size
    b_x = 0

running = True
menu = True
while running:
    window.fill((0, 0, 0))
    last_mouse_x, last_mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            print(x)
            print(y)
            if play_button.rect.collidepoint(x, y):
                menu = False
            if exit_button.rect.collidepoint(x, y):
                running = False
        if keys[pygame.K_SPACE]:
            mouse_pos = pygame.mouse.get_pos()
            world_mouse = (
                (mouse_pos[0] - camera.x) / camera.zoom,
                (mouse_pos[1] - camera.y) / camera.zoom
            )

            bullets.append(Bullet(
                player.rect.centerx,
                player.rect.centery,
                10, 10,
                bullet_img,
                8,
                world_mouse
            ))
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
        version_txt = font.render("V0.6", True, (0, 0, 0))
        window.blit(version_txt, (0, 0))
        
        menu_bg.rect.x += (pygame.mouse.get_pos()[0] - last_mouse_x) / 10
        menu_bg.rect.y += (pygame.mouse.get_pos()[1] - last_mouse_y) / 10
        
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
            bullet.move()

        # 🔥 Очищення після руху
        bullets = [b for b in bullets if b.alive]

        
        player.update(obstacles)
        player.draw()
        player.speed = player.base_speed
        camera.update(player)
    
    pygame.display.update()
    clock.tick(60)
pygame.quit()