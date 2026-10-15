from settings import * 

class BattleSprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()

	def draw(self, current_monster_sprite, side, mode, target_index, player_sprites, opponent_sprites):
		# Identifica as posições válidas
		sprite_group = opponent_sprites if side == 'opponent' else player_sprites
		sprites = {sprite.pos_index: sprite for sprite in sprite_group}
		
		monster_sprite = None
		if sprites:
			chaves_disponiveis = list(sprites.keys())
			# Evita erros de índice se a lista mudar durante a animação
			if target_index < len(chaves_disponiveis):
				monster_sprite = sprites[chaves_disponiveis[target_index]]

		for sprite in sorted(self, key = lambda sprite: sprite.z):
			monster_sprite = getattr(sprite, 'monster_sprite', sprite)
			if getattr(monster_sprite, 'returning_to_book', False):
				continue

			if sprite.z == BATTLE_LAYERS['outline']:
				# Verificar se deve mostrar outline
				outline_is_current = (
					sprite.monster_sprite == current_monster_sprite 
					and not (mode == 'target' and side == 'player')
				)
				outline_is_target = (
					sprite.monster_sprite == monster_sprite 
					and sprite.monster_sprite.entity == side 
					and mode == 'target'
				)
				if outline_is_current or outline_is_target:
					self.display_surface.blit(sprite.image, sprite.rect)
			else:
				self.display_surface.blit(sprite.image, sprite.rect)
