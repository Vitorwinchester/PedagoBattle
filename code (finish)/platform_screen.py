"""Tela inicial para selecionar os controles de computador ou celular."""

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS


class PlatformScreen:
    def __init__(self, display_surface, fonts):
        self.display_surface = display_surface
        self.fonts = fonts
        self.title_font = fonts['dialog']
        self.body_font = fonts['regular']
        self.button_font = fonts['bold']
        self.background = self._build_background()

        button_width, button_height = 300, 110
        gap = 50
        first_x = (WINDOW_WIDTH - (button_width * 2 + gap)) // 2
        button_y = int(WINDOW_HEIGHT * 0.52)
        self.options = [
            ('pc', 'COMPUTADOR', pygame.Rect(first_x, button_y, button_width, button_height)),
            (
                'mobile',
                'CELULAR',
                pygame.Rect(first_x + button_width + gap, button_y, button_width, button_height),
            ),
        ]
        self.hovered = None

    def _build_background(self):
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background.fill(COLORS['black'])
        return background

    def update(self, _dt):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = next(
            (platform for platform, _, rect in self.options if rect.collidepoint(mouse_pos)),
            None,
        )

    def draw(self):
        self.display_surface.blit(self.background, (0, 0))
        self.draw_transition_items(self.display_surface)

    def draw_transition_items(self, surface):
        """Desenha apenas os elementos de interface, sem incluir o fundo."""
        title = self.title_font.render('COMO VOCE VAI JOGAR?', True, COLORS['gold'])
        surface.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.25))),
        )
        subtitle = self.body_font.render(
            'Escolha a plataforma para configurar os controles',
            True,
            COLORS['white'],
        )
        surface.blit(
            subtitle,
            subtitle.get_rect(center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.36))),
        )

        for platform, label, rect in self.options:
            color = '#ffe066' if platform == self.hovered else COLORS['gold']
            pygame.draw.rect(surface, color, rect, border_radius=16)
            pygame.draw.rect(surface, COLORS['dark'], rect, 4, border_radius=16)
            text = self.button_font.render(label, True, COLORS['dark'])
            surface.blit(text, text.get_rect(center=rect.center))

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        return next(
            (platform for platform, _, rect in self.options if rect.collidepoint(event.pos)),
            None,
        )
