import pygame
pygame.init()

W, H = 600, 600
window = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pygame.display.update()
    clock.tick(60)
pygame.quit()