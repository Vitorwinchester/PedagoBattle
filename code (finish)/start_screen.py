"""
Tela inicial (menu principal) do jogo.

Mostra o nome "PEDAGOBATTLE" como logo, um fundo colorido e os botões para
iniciar ou encerrar o jogo.
"""

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
from support import resolve_path


class Button:
	def __init__(self, rect, text, font):
		self.rect = rect
		self.text = text
		self.font = font
		self.hovered = False

	def draw(self, surface):
		# cor muda um pouco quando o mouse está em cima (feedback visual simples)
		base_color = pygame.Color(COLORS['chalk green'])
		if self.hovered:
			base_color = pygame.Color(COLORS['chalk hover'])

		pygame.draw.rect(surface, base_color, self.rect, border_radius=12)
		pygame.draw.rect(surface, COLORS['chalk white'], self.rect, width=3, border_radius=12)

		text_surf = self.font.render(self.text, True, COLORS['chalk white'])
		text_rect = text_surf.get_rect(center=self.rect.center)
		surface.blit(text_surf, text_rect)

	def update_hover(self, mouse_pos):
		self.hovered = self.rect.collidepoint(mouse_pos)

	def is_clicked(self, event):
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.rect.collidepoint(event.pos)
		)


class StartScreen:
	def __init__(self, display_surface, fonts):
		self.display_surface = display_surface
		self.fonts = fonts

		# fontes próprias para o menu (maiores que as usadas no resto do jogo)
		try:
			self.title_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'dogicapixelbold.otf'), 64)
			self.subtitle_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 22)
			self.button_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 32)
		except Exception:
			# fallback caso as fontes não sejam encontradas por algum motivo
			self.title_font = pygame.font.SysFont('arial', 64, bold=True)
			self.subtitle_font = pygame.font.SysFont('arial', 22)
			self.button_font = pygame.font.SysFont('arial', 32)

		button_width, button_height = 280, 70
		button_rect = pygame.Rect(0, 0, button_width, button_height)
		button_rect.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.68))
		self.start_button = Button(button_rect, 'INICIAR', self.button_font)
		exit_rect = pygame.Rect(0, 0, button_width, 60)
		exit_rect.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.84))
		self.exit_button = Button(exit_rect, 'SAIR DO JOGO', self.button_font)

		# Carrega a arte da lousa uma vez para reutilizá-la em cada quadro.
		self.background = self._build_background()

		# pequena animação de "flutuação" no título
		self.time_elapsed = 0

	def _build_background(self):
		background = pygame.image.load(
			resolve_path('graphics', 'backgrounds', 'tela-lousa.png')
		).convert()
		return pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

	def update(self, dt):
		self.time_elapsed += dt
		mouse_pos = pygame.mouse.get_pos()
		self.start_button.update_hover(mouse_pos)
		self.exit_button.update_hover(mouse_pos)

	def draw(self):
		self.display_surface.blit(self.background, (0, 0))

		# logo com leve efeito de "sombra" e flutuação vertical
		float_offset = int(6 * pygame.math.Vector2(0, 1).y) if False else 0
		import math
		float_offset = int(math.sin(self.time_elapsed * 2) * 6)

		title_text = 'PEDAGOBATTLE'
		title_surf = self.title_font.render(title_text, True, COLORS['chalk white'])

		title_center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.32) + float_offset)
		title_rect = title_surf.get_rect(center=title_center)

		self.display_surface.blit(title_surf, title_rect)

		subtitle_surf = self.subtitle_font.render(
			'Aperte ENTER ou clique em Iniciar', True, COLORS['chalk white'])
		subtitle_rect = subtitle_surf.get_rect(
			center=(WINDOW_WIDTH // 2, title_rect.bottom + 40))
		self.display_surface.blit(subtitle_surf, subtitle_rect)

		self.start_button.draw(self.display_surface)
		self.exit_button.draw(self.display_surface)

	def handle_event(self, event):
		"""Retorna a ação escolhida no menu inicial, se houver."""
		if self.exit_button.is_clicked(event):
			return 'exit'
		if self.start_button.is_clicked(event):
			return 'start'
		if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
			return 'start'
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			return 'exit'
		return None
