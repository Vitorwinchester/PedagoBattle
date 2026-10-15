MONSTER_DATA = {
	'Equonci': {
		'stats': {'element': 'Matemática', 'max_health': 15, 'max_energy': 17, 'attack': 4, 'defense': 8, 'recovery': 1, 'speed': 1},
		'abilities': {0: 'splash', 5: 'spark', 10: 'battlecry'},
		'evolve': ('Ivieron', 15)},
	'Ivieron': {
		'stats': {'element': 'plant', 'max_health': 18, 'max_energy': 20, 'attack': 5, 'defense': 10, 'recovery': 1.2, 'speed': 1.2},
		'abilities': {0: 'scratch', 5: 'spark'},
		'evolve': ('Pluma', 32)},
	'Pluma': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 26, 'attack': 6, 'defense': 12, 'recovery': 1.8, 'speed': 1.8},
		'abilities': {0: 'scratch', 5: 'spark'},
		'evolve': None},
	'Jabu': {
		'stats': {'element': 'Linguagem', 'max_health': 15, 'max_energy': 7, 'attack': 3, 'defense': 8, 'recovery': 1.1, 'speed': 1},
		'abilities': {0: 'scratch', 5: 'fire', 15: 'battlecry', 26:'explosion'},
		'evolve': ('Cindrill', 15)},
	'Cindrill': {
		'stats': {'element': 'fire', 'max_health': 18, 'max_energy': 10, 'attack': 3.5, 'defense': 10, 'recovery': 1.2, 'speed': 1.1},
		'abilities': {0: 'scratch', 5: 'fire', 15: 'battlecry', 26:'explosion'},
		'evolve': ('Palhetin', 33)},
	'Palhetin': {
		'stats': {'element': 'Artes', 'max_health': 29, 'max_energy': 12, 'attack': 4, 'defense': 17, 'recovery': 1.35, 'speed': 1.1},
		'abilities': {0: 'scratch', 5: 'battlecry', 15: 'explosion'},
		'ability_costs': {'explosion': 70},
		'evolve': None},
	'Finsta': {
		'stats': {'element': 'water', 'max_health': 13, 'max_energy': 17, 'attack': 2, 'defense': 8, 'recovery': 1.5, 'speed': 1.8},
		'abilities': {0: 'scratch', 5: 'spark', 15: 'splash', 20: 'ice', 25: 'heal'},
		'evolve': ('Gulfin', 34)},
	'Gulfin': {
		'stats': {'element': 'water', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 1.8, 'speed': 2},
		'abilities': {0: 'scratch', 5: 'spark', 15: 'splash', 20: 'ice', 25: 'heal'},
		'evolve': ('Finiette', 45)},
	'Finiette': {
		'stats': {'element': 'water', 'max_health': 27, 'max_energy': 23, 'attack': 4, 'defense': 17, 'recovery': 2, 'speed': 2.5},
		'abilities': {0: 'scratch', 5: 'spark', 15: 'splash', 20: 'ice', 25: 'heal'},
		'evolve': None},
	'Atrox': {
		'stats': {'element': 'fire', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 1.3, 'speed': 1.9},
		'abilities': {0: 'scratch', 5: 'spark', 30: 'fire'},
		'evolve': None},
	'Pouch': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 25, 'attack': 4, 'defense': 12, 'recovery': 1, 'speed': 1.5},
		'abilities': {0: 'scratch', 5: 'spark', 25: 'heal'},
		'evolve': None},
	'Draem': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 25, 'attack': 4, 'defense': 12, 'recovery': 1.2, 'speed': 1.4},
		'abilities': {0: 'scratch', 5: 'heal', 20: 'explosion', 25: 'splash'},
		'evolve': None},
	'Rosial': {
		'stats': {'element': 'Geografia', 'max_health': 15, 'max_energy': 17, 'attack': 2, 'defense': 8, 'recovery': 1, 'speed': 1},
		'abilities': {0: 'scratch', 5: 'spark', 10: 'heal'},
		'evolve': ('Cleaf', 4)},
	'Prezen': {
		'stats': {'element': 'Filosofia', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 1.7, 'speed': 1.6},
		'abilities': {0: 'ice', 5: 'battlecry', 10: 'spark', 25: 'heal'},
		'evolve': None},
	'Triátomo': {
		'stats': {'element': 'Química', 'max_health': 12, 'max_energy': 19, 'attack': 3, 'defense': 10, 'recovery': 2.1, 'speed': 2.6},
		'abilities': {0: 'heal', 5: 'spark', 15: 'burn'},
		'evolve': None},
	'Friolera': {
		'stats': {'element': 'water', 'max_health': 13, 'max_energy': 20, 'attack': 4, 'defense': 6, 'recovery': 1.3, 'speed': 2},
		'abilities': {0: 'scratch', 5: 'spark', 15: 'splash', 20: 'ice', 25: 'heal'},
		'evolve': None},
}

PAIRING_OPTIONS = [
	('Jabu', 'Rosial'),
	('Equonci', 'Triátomo'),
	('Prezen', 'Palhetin'),
]

# Dados consultados pelo jogador, pelo cálculo dos golpes e pela IA do adversário.
# "amount" multiplica o ataque do monstro; valores negativos representam cura.
ATTACK_DATA = {
	'burn':       {'target': 'opponent', 'amount': 2,    'cost': 25,  'element': 'fire',   'animation': 'fire'},
	'heal':       {'target': 'player',   'amount': -1.2, 'cost': 33,  'element': 'plant',  'animation': 'green'},
	'battlecry':  {'target': 'player',   'amount': -1.4, 'cost': 33,  'element': 'normal', 'animation': 'green'},
	'spark':      {'target': 'opponent', 'amount': 1.1,  'cost': 33,  'element': 'fire',   'animation': 'fire'},
	'scratch':    {'target': 'opponent', 'amount': 1.2,  'cost': 33,  'element': 'normal', 'animation': 'scratch'},
	'splash':     {'target': 'opponent', 'amount': 2,    'cost': 25,  'element': 'water',  'animation': 'splash'},
	'fire':       {'target': 'opponent', 'amount': 2,    'cost': 25,  'element': 'fire',   'animation': 'fire'},
	'explosion':  {'target': 'opponent', 'amount': 2,    'cost': 144, 'element': 'fire',   'animation': 'explosion'},
	'annihilate': {'target': 'opponent', 'amount': 3,    'cost': 15,  'element': 'fire',   'animation': 'explosion'},
	'ice':        {'target': 'opponent', 'amount': 2,    'cost': 25,  'element': 'water',  'animation': 'ice'},
}

ATTACK_NAME_CATEGORIES = {
	'Jabu': 'Linguagem',
	'Palhetin': 'Artes',
	'Equonci': 'Matemática',
	'Rosial': 'Geografia',
	'Prezen': 'Filosofia',
	'Triátomo': 'Química',
}

ATTACK_DISPLAY_NAMES = {
	'Linguagem': {
		'scratch': 'Ataque Verbal',
		'fire': 'Plural',
		'explosion': 'Plural',
		'battlecry': 'Ponto e Vírgula',
	},
	'Matemática': {
		'splash': 'Fração',
		'spark': 'Ao Quadrado',
		'battlecry': 'Resolução',
	},
	'Filosofia': {
		'ice': 'Só Sei Que Nada Sei',
		'spark': 'Reflexão Profunda',
		'battlecry': 'Parar Para Pensar',
	},
	'Química': {
		'spark': 'Impulso Elétrico',
		'burn': 'Reação Química',
		'heal': 'Equilíbrio Atômico',
	},
	'Geografia': {
		'scratch': 'Ventos da rosa',
		'spark': 'Oeste a Leste',
		'heal': 'Mapear'
	},
	'Artes': {
		'scratch': 'Aquarela',
		'explosion': 'Inspiração instantâneo',
		'battlecry': 'Reestoque de tintas'
	}
}


def get_attack_display_name(ability, monster_name):
	category = ATTACK_NAME_CATEGORIES.get(monster_name)
	if category is None:
		return None
	return ATTACK_DISPLAY_NAMES.get(category, {}).get(ability)