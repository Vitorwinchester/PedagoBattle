"""Camada de compatibilidade para rodar este jogo (escrito originalmente
para o pygame-ce) no pygame "normal" (python-pygame).

Só existem dois recursos do pygame-ce que o código realmente usa e que
faltam no pygame normal:

1. `pygame.FRect` / `.get_frect()` -> resolvido pela classe FRect abaixo.
   Obs: `get_surface_rect()` (em support.py) já tem um fallback
   pra `.get_rect()` quando `get_frect` não existe, então NÃO precisamos
   substituir pygame.Surface nem pygame.font.Font globalmente (isso é o
   que causava as caixas de texto pretas: reconstruir toda superfície
   manualmente em attach_surface_compat() perdia canal alpha/colorkey
   em certos casos).

2. `pygame.key.get_just_pressed()` / `get_just_released()` -> resolvido
   guardando o estado do teclado do frame anterior e comparando com o
   estado atual.
"""

import pygame


class FRect(pygame.Rect):
	"""Shim mínimo para o FRect do pygame-ce (aqui só precisa ser um Rect
	com o método .move_to(), que o pygame normal não tem)."""

	def __init__(self, *args, **kwargs):
		if len(args) == 1 and isinstance(args[0], pygame.Rect):
			super().__init__(args[0])
		else:
			super().__init__(*args, **kwargs)

	def move_to(self, **kwargs):
		rect = self.copy()
		for key, value in kwargs.items():
			setattr(rect, key, value)
		return FRect(rect)

	def copy(self):
		return FRect(self)


# --- shim de get_just_pressed / get_just_released ---------------------
# O pygame normal não tem essas funções. Elas dependem de saber o estado
# do teclado do frame anterior, então precisamos "amostrar" get_pressed()
# uma vez por frame. O ponto mais confiável pra isso é logo depois de
# pygame.display.flip(), que é chamado exatamente uma vez por frame tanto
# na batalha (main.py e evolution.py).

_previous_keys = None
_original_flip = None


class _JustKeysWrapper:
	"""Permite fazer keys[pygame.K_SPACE] igual ao retorno real do
	pygame-ce, comparando o estado atual com o anterior."""
	__slots__ = ('_now', '_before')

	def __init__(self, now, before):
		self._now = now
		self._before = before

	def __getitem__(self, key):
		return bool(self._now[key]) and not bool(self._before[key])


def _snapshot_keys():
	global _previous_keys
	_previous_keys = pygame.key.get_pressed()


def _compat_flip(*args, **kwargs):
	result = _original_flip(*args, **kwargs)
	_snapshot_keys()
	return result


def compat_get_just_pressed():
	current = pygame.key.get_pressed()
	previous = _previous_keys if _previous_keys is not None else current
	return _JustKeysWrapper(current, previous)


def compat_get_just_released():
	current = pygame.key.get_pressed()
	previous = _previous_keys if _previous_keys is not None else current
	return _JustKeysWrapper(previous, current)


def compat_grayscale(surface):
	grayscale = surface.copy()
	for x in range(surface.get_width()):
		for y in range(surface.get_height()):
			color = surface.get_at((x, y))
			value = (299 * color.r + 587 * color.g + 114 * color.b + 500) // 1000
			grayscale.set_at((x, y), (value, value, value, color.a))
	color_key = surface.get_colorkey()
	if color_key is not None:
		value = (299 * color_key.r + 587 * color_key.g + 114 * color_key.b + 500) // 1000
		grayscale.set_colorkey((value, value, value))
	return grayscale


def install_pygame_compat():
	# FRect
	if not hasattr(pygame, 'FRect'):
		pygame.FRect = FRect

	if not hasattr(pygame.transform, 'grayscale'):
		pygame.transform.grayscale = compat_grayscale

	# get_just_pressed / get_just_released
	if not hasattr(pygame.key, 'get_just_pressed'):
		global _original_flip
		if _original_flip is None:
			_original_flip = pygame.display.flip
			pygame.display.flip = _compat_flip
		pygame.key.get_just_pressed = compat_get_just_pressed
		pygame.key.get_just_released = compat_get_just_released


install_pygame_compat()
