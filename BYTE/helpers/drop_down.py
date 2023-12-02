import pygame

class Dropdown:
    def __init__(self, screen, options, pos):
        self.screen = screen
        self.options = options
        self.pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], 150, 30)  # Pravimo okvir za dropdown listu
        self.is_open = False
        self.selected_option = None

    def draw(self):
        pygame.draw.rect(self.screen, (200, 200, 200), self.rect)  # Crta okvir
        pygame.draw.line(self.screen, (0, 0, 0), (self.rect.x, self.rect.y), (self.rect.x + self.rect.width, self.rect.y), 2)  # Linija za oznaku
        font = pygame.font.Font(None, 24)
        text = font.render("Select", True, (0, 0, 0))  # Tekst za trenutno odabrani element
        self.screen.blit(text, (self.rect.x + 10, self.rect.y + 5))

        if self.is_open:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(self.screen, (200, 200, 200), rect)  # Pravi okvir za opcije
                text = font.render(option, True, (0, 0, 0))  # Tekst za opciju
                self.screen.blit(text, (self.rect.x + 10, self.rect.y + self.rect.height + i * self.rect.height + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, _ in enumerate(self.options):
                    rect = pygame.Rect(
                        self.rect.x, self.rect.y + self.rect.height + i * self.rect.height, self.rect.width, self.rect.height
                    )
                    if rect.collidepoint(event.pos):
                        self.selected_option = self.options[i]
                        self.is_open = False
                        return self.selected_option
        return None

