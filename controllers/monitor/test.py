import os, pygame, time

def setSDLVariables(driver):
    print("Setting SDL variables...")
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_VIDEODRIVER"] = driver
    print("...done") 

def printSDLVariables():
    print("Checking current env variables...")
    print("SDL_VIDEODRIVER = {0}".format(os.getenv("SDL_VIDEODRIVER")))
    print("SDL_FBDEV = {0}".format(os.getenv("SDL_FBDEV")))

setSDLVariables('fbcon')
printSDLVariables()

try:
    pygame.init()
except pygame.error:
    print("Driver '{0}' failed!".format(driver))
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Detected screen size: {0}".format(size))


screen = pygame.display.set_mode(size )
clock = pygame.time.Clock()

for x in range(20):
    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(1)
    screen.fill((200, 200, 0))
    pygame.display.flip()
    clock.tick(1)
