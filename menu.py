import pygame
import os

class Menu:
    def __init__(self, screen, high_score=0):
        self.screen = screen
        self.high_score = high_score
        self.menu_font_large = pygame.font.Font(None, 48)

        # Load background image
        background_path = os.path.join('data', 'images', 'background.png')
        self.background = pygame.image.load(background_path)
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        # Load icon image
        icon_path = os.path.join('data', 'images', 'start.png')  # Update with the correct path to your icon
        self.icon = pygame.image.load(icon_path)
        white = (255, 255, 255)
        self.icon.set_colorkey(white)
        self.icon_rect = self.icon.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))

    def display(self):
        self.screen.blit(self.background, (0, 0))

        game_name_text = "Enemy Eclipse"
        game_name_surface = self.menu_font_large.render(game_name_text, True, (0, 0, 0))
        game_name_rect = game_name_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(game_name_surface, game_name_rect)

        # Display the icon
        self.screen.blit(self.icon, self.icon_rect.topleft)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.icon_rect.collidepoint(mouse_pos):
                    return True
        return False
