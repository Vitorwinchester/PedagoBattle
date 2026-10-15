"""Tela para escolher uma dupla oficial antes da batalha de demonstração."""

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
from support import resolve_path
from game_data import MONSTER_DATA, PAIRING_OPTIONS


class MonsterCard:
	"""Cartão clicável que mostra o ícone e o nome de um monstro."""

	def __init__(
		self,
		rect,
		name,
		icon_surf,
		enabled=True,
		partner_name=None,
		monster_surf=None,
		partner_surf=None,
	):
		self.rect = rect
		self.name = name
		self.icon_surf = icon_surf
		self.enabled = enabled
		self.hovered = False
		self.partner_name = partner_name
		self.monster_surf = monster_surf
		self.partner_surf = partner_surf

	def draw(self, surface, name_font, partner_font=None):
		"""Desenha o cartão e destaca visualmente quando o cursor está sobre ele."""
		color = pygame.Color(COLORS['chalk hover']) if self.hovered else pygame.Color(COLORS['chalk green'])
		pygame.draw.rect(surface, color, self.rect, border_radius=16)
		pygame.draw.rect(surface, COLORS['chalk white'], self.rect, width=3, border_radius=16)

		if self.partner_surf:
			partner_position = (self.rect.centerx + 54, self.rect.top + 166)
			partner_rect = self.partner_surf.get_rect(midbottom=partner_position)
			surface.blit(self.partner_surf, partner_rect)

		if self.monster_surf:
			monster_position = (self.rect.centerx - 50, self.rect.top + 174)
			monster_rect = self.monster_surf.get_rect(midbottom=monster_position)
			surface.blit(self.monster_surf, monster_rect)
		elif self.icon_surf:
			icon_rect = self.icon_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 24))
			surface.blit(self.icon_surf, icon_rect)

		name_surf = name_font.render(self.name, True, COLORS['chalk white'])
		name_bottom = self.rect.bottom - 38 if self.partner_name else self.rect.bottom - 20
		name_rect = name_surf.get_rect(midbottom=(self.rect.centerx, name_bottom))
		surface.blit(name_surf, name_rect)

		if self.partner_name and partner_font:
			partner_name_surf = partner_font.render(
				f'com {self.partner_name}', True, COLORS['chalk white'])
			partner_name_rect = partner_name_surf.get_rect(
				midbottom=(self.rect.centerx, self.rect.bottom - 12))
			surface.blit(partner_name_surf, partner_name_rect)

	def update_hover(self, mouse_pos):
		self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)

	def is_clicked(self, event):
		"""Confirma apenas cliques do botão esquerdo dentro do cartão."""
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.enabled
			and self.rect.collidepoint(event.pos)
		)


class SelectScreen:
	"""Monta a tela para escolher um Pedago e formar sua dupla oficial."""

	# A ordem e a disposição preservam os três cartões da tela original.
	MONSTER_NAMES = ['Jabu', 'Equonci', 'Prezen']

	def __init__(self, display_surface, fonts, monster_frames):
		"""Prepara cartões e recursos visuais reaproveitando os ícones do jogo."""
		self.display_surface = display_surface
		self.fonts = fonts

		try:
			self.title_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'dogicapixelbold.otf'), 44)
			self.name_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 24)
			self.partner_font = pygame.font.Font(
				resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 14)
		except Exception:
			self.title_font = pygame.font.SysFont('arial', 44, bold=True)
			self.name_font = pygame.font.SysFont('arial', 24)
			self.partner_font = pygame.font.SysFont('arial', 14)

		self.background = self._build_background()

		icons = monster_frames.get('icons', {}) if monster_frames else {}
		monsters = monster_frames.get('monsters', {}) if monster_frames else {}
		self.available_pairings = tuple(
			pair for pair in PAIRING_OPTIONS
			if all(
				name in MONSTER_DATA and name in icons and name in monsters
				for name in pair
			)
		)
		available_names = {name for pair in self.available_pairings for name in pair}
		card_width, card_height = 220, 260
		gap = 50
		total_width = card_width * 3 + gap * 2
		start_x = (WINDOW_WIDTH - total_width) // 2
		card_y = int(WINDOW_HEIGHT * 0.38)

		self.cards = []
		for i, name in enumerate(self.MONSTER_NAMES):
			pair = next((pair for pair in self.available_pairings if name in pair), ())
			partner_name = next((member for member in pair if member != name), None)
			rect = pygame.Rect(
				start_x + i * (card_width + gap),
				card_y,
				card_width,
				card_height,
			)
			icon_surf = icons.get(name)
			if icon_surf is not None:
				icon_surf = pygame.transform.scale(
					icon_surf,
					(icon_surf.get_width() * 3, icon_surf.get_height() * 3),
				)

			monster_surf = None
			partner_surf = None
			if name in monsters and partner_name in monsters:
				monster_frame = monsters[name]['idle'][0]
				partner_frame = monsters[partner_name]['idle'][0]
				monster_frame = monster_frame.subsurface(
					monster_frame.get_bounding_rect()).copy()
				partner_frame = partner_frame.subsurface(
					partner_frame.get_bounding_rect()).copy()
				monster_surf = self._fit_sprite(monster_frame, (116, 144))
				partner_surf = self._fit_sprite(partner_frame, (92, 116))

			self.cards.append(MonsterCard(
				rect,
				name,
				icon_surf,
				enabled=name in available_names,
				partner_name=partner_name,
				monster_surf=monster_surf,
				partner_surf=partner_surf,
			))

		self.selected_pair = None

	def _build_background(self):
		background = pygame.image.load(
			resolve_path('graphics', 'backgrounds', 'tela-lousa.png')
		).convert()
		return pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

	@staticmethod
	def _fit_sprite(sprite, max_size):
		scale = min(max_size[0] / sprite.get_width(), max_size[1] / sprite.get_height())
		size = (
			max(1, int(sprite.get_width() * scale)),
			max(1, int(sprite.get_height() * scale)),
		)
		return pygame.transform.scale(sprite, size)

	def update(self, dt):
		"""Atualiza o destaque dos cartões conforme a posição atual do mouse."""
		mouse_pos = pygame.mouse.get_pos()
		for card in self.cards:
			card.update_hover(mouse_pos)

	def draw(self):
		"""Desenha o fundo, o título e os Pedagos cadastrados."""
		self.display_surface.blit(self.background, (0, 0))
		self.draw_transition_items(self.display_surface)

	def draw_transition_items(self, surface):
		"""Desenha título e cartões sem incluir o fundo da seleção."""
		title_surf = self.title_font.render(
			'ESCOLHA SEU TIME PEDAGO', True, COLORS['chalk white'])
		title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.18)))
		surface.blit(title_surf, title_rect)

		for card in self.cards:
			card.draw(surface, self.name_font, self.partner_font)

	def handle_event(self, event):
		"""Retorna a dupla oficial do Pedago clicado."""
		for card in self.cards:
			if card.is_clicked(event):
				self.selected_pair = next(
					(pair for pair in PAIRING_OPTIONS if card.name in pair),
					None,
				)
				return self.selected_pair
		return None
