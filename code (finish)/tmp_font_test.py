import sys
sys.path.insert(0, '.')
import pygame
pygame.init()
print('pygame.font.Font class', pygame.font.Font)
print('callable', callable(pygame.font.Font))
print('type', type(pygame.font.Font))
print('dir sample', [name for name in dir(pygame.font.Font) if 'render' in name.lower()])

OrigFont = pygame.font.Font
class CompatFont:
    def __init__(self, *args, **kwargs):
        self._font = OrigFont(*args, **kwargs)
    def render(self, *args, **kwargs):
        surf = self._font.render(*args, **kwargs)
        print('render produced', type(surf), 'has get_frect', hasattr(surf, 'get_frect'))
        return surf
    def __getattr__(self, name):
        return getattr(self._font, name)

pygame.font.Font = CompatFont
print('replaced font class', pygame.font.Font)
print('font instance type', type(pygame.font.Font(None, 12)))
text = pygame.font.Font(None, 12).render('hi', False, (0,0,0))
print('text type', type(text), 'has get_frect', hasattr(text, 'get_frect'))
