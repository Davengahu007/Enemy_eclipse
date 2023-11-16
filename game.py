import sys
import pygame

class Game:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Enemy Eclipse')
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')

        self.img_pos = [160, 260]

    def run(self):
        while True:
            self.screen.blit(self.img, self.img_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)

Game().run()