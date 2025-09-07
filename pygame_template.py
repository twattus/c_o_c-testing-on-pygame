import pygame,sys
from pygame.locals import QUIT

screen_x=0
screen_y=0

pygame.init()
screen=pygame.display.set_mode((screen_x,screen_y))
pygame.display.set_caption('')
while True:
    clock=pygame.time.Clock()



    clock.tick(60)
    for event in pygame.event.get():
       if event.type == QUIT:
           pygame.quit()
           sys.exit()
    pygame.display.update()
