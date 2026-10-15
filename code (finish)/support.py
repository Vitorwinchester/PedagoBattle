from settings import *
from os.path import abspath, dirname, join
from os import walk

PROJECT_ROOT = abspath(join(dirname(__file__), '..'))

ASSET_NAME_ALIASES = {'Triatomo': 'Triátomo'}


def resolve_path(*path):
	return join(PROJECT_ROOT, *path)


def asset_name_to_game_name(name):
	return ASSET_NAME_ALIASES.get(name, name)


def _asset_name_priority(file_name):
	name = file_name.rsplit('.', 1)[0]
	return (name not in ASSET_NAME_ALIASES, file_name.casefold())


# import functions
def import_image(*path, alpha = True, format = 'png'):
	full_path = resolve_path(*path) + f'.{format}'
	if not pygame.get_init():
		pygame.init()
	surf = pygame.image.load(full_path)
	try:
		return surf.convert_alpha() if alpha else surf.convert()
	except pygame.error:
		return surf

def import_folder(*path):
	frames = []
	for folder_path, sub_folders, image_names in walk(resolve_path(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames.append(surf)
	return frames

def import_folder_dict(*path):
	frames = {}
	for folder_path, sub_folders, image_names in walk(resolve_path(*path)):
		for image_name in sorted(image_names, key = _asset_name_priority):
			game_name = asset_name_to_game_name(image_name.split('.')[0])
			if game_name in frames:
				continue
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames[game_name] = surf
	return frames

def import_tilemap(cols, rows, *path):
	frames = {}
	surf = import_image(*path)
	cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
	for col in range(cols):
		for row in range(rows):
			cutout_rect = pygame.Rect(col * cell_width, row * cell_height,cell_width,cell_height)
			cutout_surf = pygame.Surface((cell_width, cell_height))
			cutout_surf.fill('green')
			cutout_surf.set_colorkey('green')
			cutout_surf.blit(surf, (0,0), cutout_rect)
			frames[(col, row)] = cutout_surf
	return frames


def get_surface_rect(surface, **kwargs):
	if hasattr(surface, 'get_frect'):
		return surface.get_frect(**kwargs)
	return surface.get_rect(**kwargs)

def monster_importer(cols, rows, *path):
	monster_dict = {}
	for folder_path, sub_folders, image_names in walk(resolve_path(*path)):
		for image in sorted(image_names, key = _asset_name_priority):
			image_name = image.split('.')[0]
			game_name = asset_name_to_game_name(image_name)
			if game_name in monster_dict:
				continue
			monster_dict[game_name] = {}
			frame_dict = import_tilemap(cols, rows, folder_path, image_name)
			for row, key in enumerate(('idle', 'attack')):
				monster_dict[game_name][key] = [frame_dict[(col,row)] for col in range(cols)]
	return monster_dict

def outline_creator(frame_dict, width):
	outline_frame_dict = {}
	for monster, monster_frames in frame_dict.items():
		outline_frame_dict[monster] = {}
		for state, frames in monster_frames.items():
			outline_frame_dict[monster][state] = []
			for frame in frames:
				new_surf = pygame.Surface(vector(frame.get_size()) + vector(width * 2), pygame.SRCALPHA)
				new_surf.fill((0,0,0,0))
				white_frame = pygame.mask.from_surface(frame).to_surface()
				white_frame.set_colorkey('black')

				new_surf.blit(white_frame, (0,0))
				new_surf.blit(white_frame, (width,0))
				new_surf.blit(white_frame, (width * 2,0))
				new_surf.blit(white_frame, (width * 2,width))
				new_surf.blit(white_frame, (width * 2,width * 2))
				new_surf.blit(white_frame, (width,width * 2))
				new_surf.blit(white_frame, (0,width * 2))
				new_surf.blit(white_frame, (0,width))
				outline_frame_dict[monster][state].append(new_surf)
	return outline_frame_dict

def attack_importer(*path):
	attack_dict = {}
	for folder_path, _, image_names in walk(resolve_path(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			attack_dict[image_name] = list(import_tilemap(4,1,folder_path, image_name).values())
	return attack_dict

def audio_importer(*path):
	files = {}
	for folder_path, _, file_names in walk(resolve_path(*path)):
		for file_name in file_names:
			full_path = join(folder_path, file_name)
			files[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
	return files

# game functions
def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
	ratio = rect.width / max_value
	bg_rect = rect.copy()
	progress = max(0, min(rect.width,value * ratio))
	progress_rect = pygame.FRect(rect.topleft, (progress,rect.height))
	pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
	pygame.draw.rect(surface, color, progress_rect, 0, radius)
