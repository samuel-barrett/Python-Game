import pygame

pygame.init()

BLACK=  (0,0,0)
WHITE=  (255,255,255)
GREEN=  (0,255,0)
RED=    (255,0,0)

# Opens a new window
windows_size = (800, 800)
screen = pygame.display.set_mode(windows_size)
pygame.display.set_caption("Pong")

exit_game = False

clock = pygame.time.Clock()

while not exit_game:
    #Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game = True
            
            
    screen.fill(WHITE)
    
    #Draw some shapes
    pygame.draw.rect(screen, RED, [0,0,0,0], 0)

    #Update screen
    pygame.display.flip()
    
    #Set framerate to 60 frames per second
    clock.tick(60)
    
pygame.quit()

