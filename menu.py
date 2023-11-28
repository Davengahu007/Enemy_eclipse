import pygame
import os

class Menu:
    def __init__(self, screen, high_score=0):
        self.screen = screen
        self.high_score = high_score
        self.menu_font_large = pygame.font.Font(None, 48)  # Large font
        self.menu_font_medium = pygame.font.Font(None, 36)  # Medium font
        logo_path = os.path.join('data', 'images', 'logo.jpeg')
        self.logo_original = pygame.image.load(logo_path)
        self.logo_max_height = 100  # Set the maximum height for the logo
        self.logo = pygame.transform.scale(self.logo_original, (int(self.logo_max_height * self.logo_original.get_width() / self.logo_original.get_height()), self.logo_max_height))  # Scale the logo

    def display(self):
        self.screen.fill((255, 255, 255))  # White background

        # Display logo in the center
        logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))  # Centered
        self.screen.blit(self.logo, logo_rect)

        # Display game name (Enemy Eclipse) below the logo
        game_name_text = "Enemy Eclipse"
        game_name_surface = self.menu_font_large.render(game_name_text, True, (0, 0, 0))  # Black text
        game_name_rect = game_name_surface.get_rect(center=(self.screen.get_width() // 2, logo_rect.bottom + 20))  # Below logo
        self.screen.blit(game_name_surface, game_name_rect)

        # Display play prompt beneath the high score
        prompt_text = "Press Enter to Play"
        prompt_surface = self.menu_font_medium.render(prompt_text, True, (0, 0, 0))  # Black text
        prompt_rect = prompt_surface.get_rect(center=(self.screen.get_width() // 2, game_name_rect.bottom + 20))  # Below high score
        self.screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
        return False
