"""
Tela de "parabéns" mostrada depois que o jogador vence a batalha demo.

Mostra a mensagem de parabéns e um menu com 3 opções:
- "Ver Pokémons Futuros"  -> clicável, mas ainda não leva a lugar nenhum (placeholder)
- "Conhecer História"     -> clicável, mas ainda não leva a lugar nenhum (placeholder)
- "Voltar para o Início"  -> única opção funcional, volta para a tela inicial (menu)

Segue o mesmo estilo visual de start_screen.py / select_screen.py.
"""

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
from support import resolve_path


class VictoryButton:
	def __init__(self, rect, text, font, functional):
		self.rect = rect
		self.text = text
		self.font = font
		self.functional = functional   # False = clicavel, mas nao faz nada (placeholder)
		self.hovered = False
		self.clicked_flash = 0         # pequeno feedback visual ao clicar numa opcao "morta"

	def draw(self, surface):
		if self.functional:
			base_color = pygame.Color('#ffe066') if self.hovered else pygame.Color(COLORS['gold'])
			border_color = COLORS['dark']
			text_color = COLORS['dark']
		else:
			# opcoes ainda nao disponiveis: visual mais apagado, deixando claro que
			# sao clicaveis mas "em breve" (nao levam a lugar nenhum por enquanto)
			base_color = pygame.Color(COLORS['light-gray']) if self.hovered else pygame.Color(COLORS['gray'])
			border_color = COLORS['light']
			text_color = COLORS['light']

		if self.clicked_flash > 0:
			base_color = pygame.Color(COLORS['white'])

		pygame.draw.rect(surface, base_color, self.rect, border_radius=12)
		pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=12)

		text_surf = self.font.render(self.text, True, text_color)
		text_rect = text_surf.get_rect(center=self.rect.center)
		surface.blit(text_surf, text_rect)

		if not self.functional:
			tag_surf = pygame.font.Font(None, 18).render('em breve', True, COLORS['light'])
			tag_rect = tag_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 4))
			surface.blit(tag_surf, tag_rect)

	def update(self, dt, mouse_pos):
		self.hovered = self.rect.collidepoint(mouse_pos)
		if self.clicked_flash > 0:
			self.clicked_flash = max(0, self.clicked_flash - dt)

	def is_clicked(self, event):
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.rect.collidepoint(event.pos)
		)


class VictoryMenuScreen:
	def __init__(self, display_surface, fonts):
		self.display_surface = display_surface
		self.fonts = fonts
		self.time_elapsed = 0

		try:
			self.title_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'dogicapixelbold.otf'), 40)
			self.subtitle_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 22)
			self.button_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 24)
		except Exception:
			self.title_font = pygame.font.SysFont('arial', 40, bold=True)
			self.subtitle_font = pygame.font.SysFont('arial', 22)
			self.button_font = pygame.font.SysFont('arial', 24)

		self.background = self._build_background()

		button_width, button_height = 340, 64
		gap = 22
		start_y = int(WINDOW_HEIGHT * 0.45)

		labels = [
			('Ver Pokemons Futuros', False),
			('Conhecer Historia', False),
			('Voltar para o Inicio', True),
		]

		self.buttons = []
		for i, (label, functional) in enumerate(labels):
			rect = pygame.Rect(0, 0, button_width, button_height)
			rect.center = (WINDOW_WIDTH // 2, start_y + i * (button_height + gap))
			self.buttons.append(VictoryButton(rect, label, self.button_font, functional))

	def _build_background(self):
		bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		top_color = pygame.Color(COLORS['gold'])
		bottom_color = pygame.Color(COLORS['dark'])
		for y in range(WINDOW_HEIGHT):
			t = y / WINDOW_HEIGHT
			color = top_color.lerp(bottom_color, t)
			pygame.draw.line(bg, color, (0, y), (WINDOW_WIDTH, y))
		return bg

	def update(self, dt):
		self.time_elapsed += dt
		mouse_pos = pygame.mouse.get_pos()
		for button in self.buttons:
			button.update(dt, mouse_pos)

	def draw(self):
		self.display_surface.blit(self.background, (0, 0))

		import math
		float_offset = int(math.sin(self.time_elapsed * 2) * 5)

		title_text = 'PARABENS!'
		shadow_surf = self.title_font.render(title_text, True, COLORS['dark'])
		title_surf = self.title_font.render(title_text, True, COLORS['white'])
		title_center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.18) + float_offset)
		shadow_rect = shadow_surf.get_rect(center=(title_center[0] + 3, title_center[1] + 3))
		title_rect = title_surf.get_rect(center=title_center)
		self.display_surface.blit(shadow_surf, shadow_rect)
		self.display_surface.blit(title_surf, title_rect)

		subtitle_surf = self.subtitle_font.render(
			'Voce terminou a batalha demo!', True, COLORS['white'])
		subtitle_rect = subtitle_surf.get_rect(center=(WINDOW_WIDTH // 2, title_rect.bottom + 36))
		self.display_surface.blit(subtitle_surf, subtitle_rect)

		for button in self.buttons:
			button.draw(self.display_surface)

	def handle_event(self, event):
		"""Retorna 'menu' quando a opcao funcional (voltar) e clicada; None caso contrario.
		Opcoes nao-funcionais dao um pequeno feedback visual mas nao retornam nada."""
		for button in self.buttons:
			if button.is_clicked(event):
				if button.functional:
					return 'menu'
				else:
					button.clicked_flash = 0.15
					return None
		return None
