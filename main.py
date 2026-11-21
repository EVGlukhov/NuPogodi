import pygame
import config

pygame.init()

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption(config.TITLE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill(config.BACKGROUND_COLOR)
    pygame.display.flip()
    
pygame.quit()