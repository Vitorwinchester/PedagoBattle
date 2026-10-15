import pygame
from pygame.math import Vector2 as vector 
from sys import exit

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4

# --- ajustes de ritmo e dificuldade da batalha ---
BATTLE_PACE = 0.75          # <1 deixa a barra de iniciativa encher mais devagar (batalha mais lenta e tatica)
OPPONENT_TURN_DELAY = 850   # pequena reducao na pausa do inimigo antes de atacar
BOT_SMART_CHANCE = 0.92     # chance maior do bot escolher a melhor jogada e pressionar o jogador
MONSTER_HEALTH_MULTIPLIER = 1.1  # aumenta um pouco a vida maxima de todos os monstros
MONSTER_ENERGY_MULTIPLIER = 1.2  # amplia a reserva maxima de energia de todos os monstros
BATTLE_DAMAGE_MULTIPLIER = 0.55  # dano base mais baixo; o nível do monstro continua escalando o ataque naturalmente

COLORS = {
	'white': '#f4fefa', 
	'pure white': '#ffffff',
	'dark': '#2b292c',
	'light': '#c8c8c8',
	'gray': '#3a373b',
	'green': '#31c96b',
	'gold': '#ffd700',
	'light-gray': '#4b484d',
	'fire':'#f8a060',
	'water':'#50b0d8',
	'plant': '#64a990', 
    'História':"#f68b3f",
	'Matemática':"#0091ff",
	'Biologia': "#97ff3c", 
    'Linguagem':"#C800FF",
    'Química':"#04ff00",
	'Física': "#ff0000", 
    'Filosofia':"#00ffee",
	'Ed. Física':"#00ffbf",
    'Geografia': "#00ff4c",
    'Artes':"#ff5ce9",
	'black': '#000000', 
	'red': '#f03131',
	'blue': '#66d7ee',
	'normal': '#ffffff',
	'dark white': '#f0f0f0',
	'chalk white': '#f5f5e8',
	'chalk green': '#258659',
	'chalk hover': '#31966d'
}

BATTLE_POSITIONS = {
	'left': {'top': (360, 260), 'center': (420, 400), 'bottom': (410, 520)},
	'right': {'top': (900, 260), 'center': (860, 390), 'bottom': (900, 550)}
}

BATTLE_LAYERS =  {
	'outline': 0,
	'name': 1,
	'monster': 2,
	'effects': 3,
	'overlay': 4
}

BATTLE_CHOICES = {
	'full': {
		'fight':  {'pos' : vector(30, -60), 'icon': 'sword'},
		'defend': {'pos' : vector(40, -20), 'icon': 'shield'},
		'switch': {'pos' : vector(40, 20), 'icon': 'arrows'},
		'catch':  {'pos' : vector(30, 60), 'icon': 'hand'}},
	
	'limited': {
		'fight':  {'pos' : vector(30, -40), 'icon': 'sword'},
		'defend': {'pos' : vector(40, 0), 'icon': 'shield'},
		'switch': {'pos' : vector(30, 40), 'icon': 'arrows'}}
}