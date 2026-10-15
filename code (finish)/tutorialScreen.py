# tutorial_screen.py
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
from support import resolve_path


class TutorialScreen:
    def __init__(self, display_surface, fonts):
        self.display_surface = display_surface
        self.fonts = fonts
        self.current_step = 0

        self.steps = [
            {
                'title': 'Comece a partida',
                'lines': ['Escolha Computador ou Celular.', 'No menu, selecione INICIAR.'],
                'keys': ['CLIQUE / TOQUE'],
            },
            {
                'title': 'Escolha sua dupla',
                'lines': [
                    'Escolha um Pedago disponível: o cartão',
                    'define sua dupla oficial.',
                    'O rival receberá outra dupla.',
                ],
                'keys': ['CLIQUE / TOQUE NO PEDAGO'],
            },
            {
                'title': 'Jogue no seu turno',
                'lines': [
                    'Escolha um ataque na parte inferior.',
                    'Com pouca energia, tente recuperá-la.',
                ],
                'keys': ['CLIQUE / TOQUE NA OPÇÃO'],
            },
            {
                'title': 'Responda ao quiz',
                'lines': [
                    'Escolha uma resposta antes do tempo acabar.',
                    'Acertar fortalece o ataque; errar causa dano normal.',
                    'Se o tempo acabar, o turno termina sem dano.',
                    'Recuperar energia exige resposta correta.',
                ],
                'keys': ['CLIQUE / TOQUE NA RESPOSTA'],
            },
        ]

        self.title_font = fonts['dialog']
        self.step_font = fonts['bold']
        self.body_font = fonts['regular']
        self.small_font = fonts['small']

        self.panel_rect = pygame.Rect(
            int(WINDOW_WIDTH * 0.11),
            int(WINDOW_HEIGHT * 0.27),
            int(WINDOW_WIDTH * 0.78),
            int(WINDOW_HEIGHT * 0.42),
        )

        button_y = int(WINDOW_HEIGHT * 0.78)
        self.previous_rect = pygame.Rect(0, 0, 180, 54)
        self.previous_rect.center = (WINDOW_WIDTH // 2 - 120, button_y)

        self.next_rect = pygame.Rect(0, 0, 180, 54)
        self.next_rect.center = (WINDOW_WIDTH // 2 + 120, button_y)

        self.skip_rect = pygame.Rect(0, 0, 220, 36)
        self.skip_rect.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.89))

        self.background = self.build_background()

    def build_background(self):
        background = pygame.image.load(
            resolve_path('graphics', 'backgrounds', 'tela-lousa.png')
        ).convert()
        return pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw_button(self, rect, text, hovered=False):
        color = pygame.Color(COLORS['chalk hover']) if hovered else pygame.Color(COLORS['chalk green'])
        self.draw_translucent_rect(rect, color, 105, 12)
        pygame.draw.rect(
            self.display_surface,
            COLORS['chalk white'],
            rect,
            width=3,
            border_radius=12,
        )

        text_surface = self.body_font.render(text, True, COLORS['chalk white'])
        self.display_surface.blit(text_surface, text_surface.get_rect(center=rect.center))

    def draw_translucent_rect(self, rect, color, alpha, border_radius):
        fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        fill_color = (*pygame.Color(color)[:3], alpha)
        pygame.draw.rect(fill_surface, fill_color, fill_surface.get_rect(), border_radius=border_radius)
        self.display_surface.blit(fill_surface, rect.topleft)

    def draw_keys(self, labels, center_y):
        gap = 12
        widths = [max(54, self.small_font.size(label)[0] + 28) for label in labels]
        total_width = sum(widths) + gap * (len(widths) - 1)
        x = (WINDOW_WIDTH - total_width) // 2

        for label, width in zip(labels, widths):
            key_rect = pygame.Rect(x, center_y - 24, width, 48)
            self.draw_translucent_rect(key_rect, COLORS['chalk green'], 105, 8)
            pygame.draw.rect(
                self.display_surface,
                COLORS['chalk white'],
                key_rect,
                width=3,
                border_radius=8,
            )

            text = self.small_font.render(label, True, COLORS['chalk white'])
            self.display_surface.blit(text, text.get_rect(center=key_rect.center))
            x += width + gap

    def draw(self):
        self.display_surface.blit(self.background, (0, 0))
        self.draw_items()

    def draw_transition_items(self, surface):
        """Desenha a interface do tutorial sem copiar o fundo para a transição."""
        previous_surface = self.display_surface
        self.display_surface = surface
        try:
            self.draw_items()
        finally:
            self.display_surface = previous_surface

    def draw_items(self):

        title = self.title_font.render('COMO JOGAR', True, COLORS['chalk white'])
        self.display_surface.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.13))),
        )

        step = self.steps[self.current_step]
        counter = f'{self.current_step + 1} / {len(self.steps)}'
        counter_surface = self.small_font.render(counter, True, COLORS['chalk white'])
        self.display_surface.blit(
            counter_surface,
            counter_surface.get_rect(
                center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.22))
            ),
        )

        self.draw_translucent_rect(self.panel_rect, COLORS['chalk green'], 72, 16)
        pygame.draw.rect(
            self.display_surface,
            COLORS['chalk white'],
            self.panel_rect,
            width=3,
            border_radius=16,
        )

        step_title = self.step_font.render(step['title'], True, COLORS['chalk white'])
        self.display_surface.blit(
            step_title,
            step_title.get_rect(
                center=(WINDOW_WIDTH // 2, self.panel_rect.top + 55)
            ),
        )

        for index, line in enumerate(step['lines']):
            body = self.body_font.render(line, True, COLORS['chalk white'])
            self.display_surface.blit(
                body,
                body.get_rect(
                    center=(
                        WINDOW_WIDTH // 2,
                        self.panel_rect.top + 115 + index * 32,
                    )
                ),
            )

        self.draw_keys(step['keys'], self.panel_rect.bottom - 48)

        self.draw_button(
            self.previous_rect,
            'VOLTAR',
            self.current_step == 0,
        )
        next_text = 'COMEÇAR' if self.current_step == len(self.steps) - 1 else 'CONTINUAR'
        self.draw_button(self.next_rect, next_text)

        self.draw_button(self.skip_rect, 'PULAR TUTORIAL')

    def advance(self):
        if self.current_step == len(self.steps) - 1:
            return True

        self.current_step += 1
        return False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.skip_rect.collidepoint(event.pos):
                return True
            if self.previous_rect.collidepoint(event.pos):
                self.current_step = max(0, self.current_step - 1)

            if self.next_rect.collidepoint(event.pos):
                return self.advance()

        return False

    def update(self, dt):
        pass