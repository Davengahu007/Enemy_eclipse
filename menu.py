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

        logo_path = os.path.join('data', 'images', 'logo.png')  # Replace with your logo file path
        self.logo = self.load_and_make_circular(logo_path)
        self.logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))


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

        self.screen.blit(self.logo, self.logo_rect.topleft)

        self.screen.blit(self.icon, self.icon_rect.topleft)

        # Display the icon
        if self.music_on:
            self.screen.blit(self.music_icon, self.music_icon_rect)
        else:
            self.screen.blit(self.mute_icon, self.music_icon_rect)

        pygame.display.flip()

    def toggle_sounds(self):
        self.music_on = not self.music_on
        if self.music_on:
            pygame.mixer.music.set_volume(0.5)  # Set music volume back to normal
            for sound in self.game.sfx.values():
                sound.set_volume(1)  # Set SFX volume back to normal (or your default level)
        else:
            pygame.mixer.music.set_volume(0)  # Mute music
            for sound in self.game.sfx.values():
                sound.set_volume(0)  # Mute SFX

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
                    self.toggle_sounds()  # Toggle all sounds

        return False
