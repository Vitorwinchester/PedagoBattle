from settings import * 
from random import uniform
from math import sin
from support import draw_bar
from timer import Timer
from support import get_surface_rect

# battle sprites 
class MonsterSprite(pygame.sprite.Sprite):
	def __init__(self, pos, frames, groups, monster, index, pos_index, entity, apply_attack, create_monster):
		# data
		self.index = index 
		self.pos_index = pos_index
		self.entity = entity
		self.monster = monster
		self.frame_index, self.frames, self.state = 0, frames, 'idle'
		self.adjusted_frame_index = 0
		self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
		self.z = BATTLE_LAYERS['monster']
		self.highlight = False
		self.returning_to_book = False
		self.target_sprite = None
		self.current_attack = None
		self.apply_attack = apply_attack
		self.create_monster = create_monster

		# sprite setup
		super().__init__(groups)
		self.image = self.frames[self.state][self.frame_index]
		self.rect = get_surface_rect(self.image, center = pos)

		# timers 
		self.timers = {
			'remove highlight': Timer(350, func = lambda: self.set_highlight(False)),
			'kill': Timer(750, func = self.destroy),
			'shake': Timer(220),
		}

		# posicao de descanso usada para o efeito de 'sacudida' ao levar dano
		self.rest_center = vector(self.rect.center)

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		if self.state == 'attack' and self.frame_index >= len(self.frames['attack']):
			self.apply_attack(
				self,
				self.target_sprite,
				self.current_attack,
				self.monster.get_base_damage(self.current_attack),
			)
			self.state = 'idle'

		self.adjusted_frame_index = int(self.frame_index % len(self.frames[self.state]))
		self.image = self.frames[self.state][self.adjusted_frame_index]

		if self.highlight:
			white_surf = pygame.mask.from_surface(self.image).to_surface()
			white_surf.set_colorkey('black')
			self.image = white_surf

	def set_highlight(self, value):
		self.highlight = value
		if value: 
			self.timers['remove highlight'].activate()

	def take_hit(self):
		# dispara a sacudida visual usada quando o monstro sofre dano (batalha mais dinamica)
		self.timers['shake'].activate()

	def apply_shake(self):
		if self.timers['shake'].active:
			elapsed = pygame.time.get_ticks() - self.timers['shake'].start_time
			fade = max(0, 1 - elapsed / self.timers['shake'].duration)
			offset = vector(uniform(-8, 8), uniform(-5, 5)) * fade
			self.rect.center = self.rest_center + offset
		else:
			self.rect.center = self.rest_center

	def activate_attack(self, target_sprite, attack):
		self.state = 'attack'
		self.frame_index = 0
		self.target_sprite = target_sprite
		self.current_attack = attack
		self.monster.reduce_energy(attack)

	def delayed_kill(self, new_monster):
		if not self.timers['kill'].active:
			self.next_monster_data = new_monster
			self.timers['kill'].activate()

	def destroy(self):
		if self.next_monster_data:
			self.create_monster(*self.next_monster_data)
		self.kill()

	def update(self, dt):
		for timer in self.timers.values():
			timer.update()
		self.animate(dt)
		self.apply_shake()
		self.monster.update(dt)

class MonsterOutlineSprite(pygame.sprite.Sprite):
	def __init__(self, monster_sprite, groups, frames):
		super().__init__(groups)
		self.z = BATTLE_LAYERS['outline']
		self.monster_sprite = monster_sprite
		self.frames = frames

		self.image = self.frames[self.monster_sprite.state][self.monster_sprite.frame_index]
		self.rect = get_surface_rect(self.image, center = self.monster_sprite.rect.center)

	def update(self, _):
		self.image = self.frames[self.monster_sprite.state][self.monster_sprite.adjusted_frame_index]
		if not self.monster_sprite.groups():
			self.kill()

class MonsterNameSprite(pygame.sprite.Sprite):
	def __init__(self, pos, monster_sprite, groups, font):
		super().__init__(groups)
		self.monster_sprite = monster_sprite
		self.z = BATTLE_LAYERS['name']

		text_surf = font.render(monster_sprite.monster.name, False, COLORS['black'])
		padding = 10

		# Garante que o tamanho mínimo é válido
		text_width = max(text_surf.get_width(), 20)
		text_height = max(text_surf.get_height(), 10)
		self.image = pygame.Surface((text_width + 2 * padding, text_height + 2 * padding), pygame.SRCALPHA) 
		pygame.draw.rect(self.image, COLORS['white'], self.image.get_rect(), 0, 6)
		pygame.draw.rect(self.image, COLORS['dark'], self.image.get_rect(), 1, 6)
		self.image.blit(text_surf, (padding, padding))
		self.rect = get_surface_rect(self.image, midtop = pos)

	def update(self, _):
		if not self.monster_sprite.groups():
			self.kill()

class MonsterLevelSprite(pygame.sprite.Sprite):
	def __init__(self, entity, pos, monster_sprite, groups, font):
		super().__init__(groups)
		self.monster_sprite = monster_sprite
		self.font = font
		self.z = BATTLE_LAYERS['name']

		self.image = pygame.Surface((60,26), pygame.SRCALPHA)
		self.rect = get_surface_rect(self.image, topleft = pos) if entity == 'player' else get_surface_rect(self.image, topright = pos)
		self.xp_rect = pygame.FRect(0,self.rect.height - 2,self.rect.width,2)

	def update(self, _):
		self.image.fill((0, 0, 0, 0))
		pygame.draw.rect(self.image, COLORS['white'], self.image.get_rect(), 0, 6)
		pygame.draw.rect(self.image, COLORS['dark'], self.image.get_rect(), 1, 6)

		text_surf = self.font.render(f'Lvl {self.monster_sprite.monster.level}', False, COLORS['black'])
		text_rect = get_surface_rect(text_surf, center = (self.rect.width / 2, self.rect.height / 2))
		self.image.blit(text_surf, text_rect)

		draw_bar(self.image, self.xp_rect, self.monster_sprite.monster.xp, self.monster_sprite.monster.level_up, COLORS['black'], COLORS['white'], 0)

		if not self.monster_sprite.groups():
			self.kill()

class MonsterStatsSprite(pygame.sprite.Sprite):
	def __init__(self, pos, monster_sprite, size, groups, font, anchor = 'midbottom'):
		super().__init__(groups)
		self.monster_sprite = monster_sprite
		self.image = pygame.Surface(size, pygame.SRCALPHA) 
		self.rect = get_surface_rect(self.image, **{anchor: pos})
		self.font = font
		self.z = BATTLE_LAYERS['overlay']

	def update(self, _):
		self.image.fill((0, 0, 0, 0))
		pygame.draw.rect(self.image, COLORS['white'], self.image.get_rect(), 0, 6)
		pygame.draw.rect(self.image, COLORS['dark'], self.image.get_rect(), 1, 6)

		for index, (value, max_value) in enumerate(self.monster_sprite.monster.get_info()):
			color = (COLORS['red'], COLORS['blue'], COLORS['gray'])[index]
			if index < 2: # health and energy 
				text_surf = self.font.render(f'{int(value)}/{max_value}', False, COLORS['black'])
				text_rect = get_surface_rect(text_surf, topleft = (self.rect.width * 0.05,index * self.rect.height / 2))
				bar_rect = pygame.FRect(text_rect.bottomleft + vector(0,-2), (self.rect.width * 0.9, 4))

				self.image.blit(text_surf, text_rect)
				draw_bar(self.image, bar_rect, value, max_value, color, COLORS['black'], 2)
			else: # initiative
				init_rect = pygame.FRect((0, self.rect.height - 2), (self.rect.width, 2)) 
				draw_bar(self.image, init_rect, value, max_value, color, COLORS['white'], 0)

		if not self.monster_sprite.groups():
			self.kill()

class AttackSprite(pygame.sprite.Sprite):
	def __init__(self, start_pos, target_sprite, frames, groups, on_impact, duration=0.32):
		self.frames = frames
		self.frame_index = 0
		self.elapsed = 0
		self.duration = duration
		self.start_pos = vector(start_pos)
		self.target_sprite = target_sprite
		self.on_impact = on_impact
		self.z = BATTLE_LAYERS['overlay']
		super().__init__(groups)
		self.image = self.frames[0]
		self.rect = self.image.get_rect(center=start_pos)

	def update(self, dt):
		self.elapsed = min(self.duration, self.elapsed + dt)
		progress = self.elapsed / self.duration
		target_pos = vector(self.target_sprite.rect.center)
		self.rect.center = self.start_pos.lerp(target_pos, progress)

		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index) % len(self.frames)]

		if progress >= 1:
			self.kill()
			self.on_impact()

class TimedSprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, duration):
		super().__init__(groups)
		self.image = surf
		self.rect = get_surface_rect(surf, center=pos)
		self.z = BATTLE_LAYERS['overlay']
		self.death_timer = Timer(duration, autostart = True, func = self.kill)

	def update(self, _):
		self.death_timer.update()

class DamageTextSprite(pygame.sprite.Sprite):
	"""Numero flutuante de dano/cura mostrado sobre o monstro atingido (efeito visual, batalha mais dinamica)."""
	def __init__(self, pos, groups, text, color, font):
		super().__init__(groups)
		self.z = BATTLE_LAYERS['overlay']
		self.font = font
		self.color = color
		self.text = text
		self.pos = vector(pos)
		self.velocity = vector(uniform(-15, 15), -75)
		self.duration = 900
		self.age = 0

		self.base_image = self.font.render(self.text, False, self.color)
		self.image = self.base_image
		self.rect = self.image.get_rect(center = pos)

	def update(self, dt):
		self.age += dt * 1000
		self.velocity.y += 90 * dt
		self.pos += self.velocity * dt

		alpha = max(0, 255 - int(255 * (self.age / self.duration)))
		self.image = self.base_image.copy()
		self.image.set_alpha(alpha)
		self.rect = self.image.get_rect(center = self.pos)

		if self.age >= self.duration:
			self.kill()

class BattleCalloutSprite(pygame.sprite.Sprite):
	def __init__(self, pos, groups, text, color, font):
		super().__init__(groups)
		self.z = BATTLE_LAYERS['overlay']
		self.pos = vector(pos)
		self.age = 0
		self.duration = 900
		self.text = text

		text_surf = font.render(text, True, color)
		outline_surf = font.render(text, True, COLORS['dark'])
		self.base_image = pygame.Surface(
			(text_surf.get_width() + 6, text_surf.get_height() + 6),
			pygame.SRCALPHA,
		)
		for x_offset, y_offset in (
			(0, 2), (2, 0), (2, 4), (4, 2),
			(1, 1), (3, 1), (1, 3), (3, 3),
		):
			self.base_image.blit(outline_surf, (x_offset, y_offset))
		self.base_image.blit(text_surf, (3, 3))
		self.image = self.base_image
		self.rect = self.image.get_rect(center=pos)

	def update(self, dt):
		self.age += dt * 1000
		progress = min(1, self.age / self.duration)
		scale = 1.15 - 0.15 * min(1, self.age / 180) + 0.04 * sin(self.age / 75)
		size = (
			max(1, int(self.base_image.get_width() * scale)),
			max(1, int(self.base_image.get_height() * scale)),
		)
		self.image = pygame.transform.smoothscale(self.base_image, size)
		self.image.set_alpha(max(0, 255 - int(255 * progress)))
		self.pos.y -= 34 * dt
		self.rect = self.image.get_rect(center=self.pos)

		if self.age >= self.duration:
			self.kill()
