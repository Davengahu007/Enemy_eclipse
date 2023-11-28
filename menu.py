import pygame
import os


class Menu:
    def __init__(self, screen, game):

        self.game = game
        self.screen = screen
        self.menu_font_large = pygame.font.Font(None, 48)
        self.music_on = True

        # Load background image
        background_path = os.path.join('data', 'images', 'background.png')
        self.background = pygame.image.load(background_path)
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        # Load icon image
        icon_path = os.path.join('data', 'images', 'start.png')
        self.icon = pygame.image.load(icon_path).convert_alpha()
        white = (255, 255, 255)
        self.icon.set_colorkey(white)
        self.icon_rect = self.icon.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))

        # Load the music icon
        self.music_icon = self.load_and_make_circular('data/images/music.png')
        self.mute_icon = self.load_and_make_circular('data/images/mute.png')
        self.music_icon_rect = self.music_icon.get_rect(midtop=(self.icon_rect.centerx, self.icon_rect.bottom + 10))

    def load_and_make_circular(self, image_path):
        # Load the image
        image = pygame.image.load(image_path).convert_alpha()

        # Create a circular mask
        mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (image.get_width() // 2, image.get_height() // 2),
                           min(image.get_width(), image.get_height()) // 2)

        # Apply the mask to the image
        mask.blit(image, (0, 0), None, pygame.BLEND_RGBA_MIN)
        return mask

    def display(self):
        self.screen.blit(self.background, (0, 0))

        game_name_text = "Enemy Eclipse"
        game_name_surface = self.menu_font_large.render(game_name_text, True, (0, 0, 0))
        game_name_rect = game_name_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(game_name_surface, game_name_rect)

        self.screen.blit(self.icon, self.icon_rect.topleft)

        # Display the icon
        if self.music_on:
            self.screen.blit(self.music_icon, self.music_icon_rect)
        else:
            self.screen.blit(self.mute_icon, self.music_icon_rect)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.icon_rect.collidepoint(mouse_pos):
                    # Start the game or some other action
                    return True
                elif self.music_icon_rect.collidepoint(mouse_pos):
                    # Toggle the music state
                    self.music_on = not self.music_on
                    if self.music_on:
                        pygame.mixer.music.play(-1)  # Play music in a loop
                    else:
                        pygame.mixer.music.stop()  # Stop the music
        return False
