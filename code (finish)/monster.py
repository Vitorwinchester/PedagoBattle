from game_data import MONSTER_DATA, ATTACK_DATA
from settings import BATTLE_DAMAGE_MULTIPLIER, BATTLE_PACE, MONSTER_ENERGY_MULTIPLIER, MONSTER_HEALTH_MULTIPLIER
from random import randint

class Monster:
	"""Dados e regras individuais de um monstro usado na batalha."""

	def __init__(self, name, level):
		"""Carrega atributos e habilidades do catálogo para o nível inicial."""
		self.name, self.level = name, level
		self.paused = False

		# stats 
		self.element = MONSTER_DATA[name]['stats']['element']
		self.base_stats = MONSTER_DATA[name]['stats']
		self.health = self.get_stat('max_health')
		self.energy = self.get_stat('max_energy')
		self.initiative = 0
		self.abilities = MONSTER_DATA[name]['abilities']
		self.defending = False

		# experience
		self.xp = 0
		self.level_up = self.level * 150
		self.evolution = MONSTER_DATA[self.name]['evolve']

	def __repr__(self):
		return f'monster: {self.name}, lvl: {self.level}'

	def get_stat(self, stat):
		"""Calcula um atributo escalado pelo nível atual do monstro."""
		value = self.base_stats[stat] * self.level
		if stat == 'max_health':
			value *= MONSTER_HEALTH_MULTIPLIER
		elif stat == 'max_energy':
			value *= MONSTER_ENERGY_MULTIPLIER
		return value

	def get_stats(self):
		return {
			'health': self.get_stat('max_health'),
			'energy': self.get_stat('max_energy'),
			'attack': self.get_stat('attack'),
			'defense': self.get_stat('defense'),
			'speed': self.get_stat('speed'),
			'recovery': self.get_stat('recovery'),
		}

	def get_abilities(self, all  = True):
		"""Retorna golpes aprendidos; opcionalmente filtra os que custam energia demais."""
		if all:
			return [ability for lvl, ability in self.abilities.items() if self.level >= lvl]
		else:
			return [ability for lvl, ability in self.abilities.items() if self.level >= lvl and self.get_attack_cost(ability) <= self.energy]

	def get_attack_cost(self, attack):
		"""Retorna o custo individual do monstro ou o custo padrão do golpe."""
		overrides = MONSTER_DATA[self.name].get('ability_costs', {})
		return overrides.get(attack, ATTACK_DATA[attack]['cost'])

	def get_info(self):
		return (
			(self.health, self.get_stat('max_health')),
			(self.energy, self.get_stat('max_energy')),
			(self.initiative, 100)
			)

	def reduce_energy(self, attack):
		"""Desconta a energia configurada para o golpe após sua execução."""
		self.energy -= self.get_attack_cost(attack)

	def get_base_damage(self, attack):
		"""Calcula o efeito bruto do golpe antes de defesa e vantagem elemental."""
		amount = self.get_stat('attack') * ATTACK_DATA[attack]['amount']
		if amount > 0:
			amount *= BATTLE_DAMAGE_MULTIPLIER
		return amount

	def update_xp(self, amount):
		if self.level_up - self.xp > amount:
			self.xp += amount
		else:
			self.level += 1
			self.xp = amount - (self.level_up - self.xp)
			self.level_up = self.level * 150

	def stat_limiter(self):
		"""Mantém vida e energia dentro dos limites definidos pelos atributos."""
		self.health = max(0, min(self.health, self.get_stat('max_health')))
		self.energy = max(0, min(self.energy, self.get_stat('max_energy')))

	def update(self, dt):
		"""Atualiza iniciativa somente quando o monstro não está pausado."""
		self.stat_limiter()
		if not self.paused:
			# BATTLE_PACE deixa o preenchimento da iniciativa um pouco mais lento (batalha menos apressada)
			self.initiative += self.get_stat('speed') * dt * BATTLE_PACE