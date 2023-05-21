import pygame


def main():
    pygame.init()
    DISPLAY = pygame.display.set_mode((800,480),0,32)
    WHITE = (255,255,255)
    blue = (0,0,255)
    DISPLAY.fill(WHITE)
    pygame.mouse.set_visible(False)
    pygame.draw.rect(DISPLAY, blue,(280,200,50,250))
    pygame.display.update()
    pygame.mouse.set_pos(280, 200)
    while True:
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            pygame.draw.rect(DISPLAY, blue, (pos[0],pos[1], 50, 250))
            pygame.display. update()
            DISPLAY.fill(WHITE)
main()
