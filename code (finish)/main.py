from settings import *
from pygame_compat import install_pygame_compat
# instalar compatibilidade imediatamente para que módulos importados em seguida
install_pygame_compat()
from itertools import combinations
from os.path import join
from random import choice, randint
from math import pi, sin
import sys

# ... (imports mantidos como no original) ...
from battle import Battle
from support import *
from monster import Monster
from start_screen import StartScreen
from select_screen import SelectScreen
from victory_menu import VictoryMenuScreen
from tutorialScreen import TutorialScreen
from platform_screen import PlatformScreen


def pointer_event(event):
    """Converte o início de um toque em evento de clique nas coordenadas do jogo."""
    if event.type == pygame.FINGERDOWN:
        width, height = pygame.display.get_surface().get_size()
        return pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': (int(event.x * width), int(event.y * height)), 'button': 1},
        )
    return event


def pointer_events(events):
    """Evita processar duas vezes o mesmo toque quando SDL também emula um clique."""
    has_touch = any(event.type == pygame.FINGERDOWN for event in events)
    for event in events:
        if has_touch and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            continue
        yield event


class Game:
    """Coordena as telas e transições da demo de batalha."""

    def __init__(self):
        """Inicializa a janela, os recursos do jogo e o time usado na demo."""
        if sys.platform == 'win32':
            import ctypes

            set_app_id = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
            set_app_id.argtypes = [ctypes.c_wchar_p]
            set_app_id.restype = ctypes.c_long
            result = set_app_id('br.com.pedagobattle.PedagoBattle')
            if result != 0:
                raise OSError(
                    f'Could not set the Windows taskbar app identity '
                    f'(HRESULT 0x{result & 0xFFFFFFFF:08X})'
                )

        pygame.init()
        self.display_surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.FULLSCREEN | pygame.SCALED,
        )
        if sys.platform != 'android':
            pygame.display.set_icon(
                pygame.image.load(resolve_path('graphics', 'ui', 'Logo.png')).convert_alpha()
            )
        self.cursor_image = pygame.image.load(
        resolve_path('graphics', 'ui', 'cursor.png')
        ).convert_alpha()
        pygame.mouse.set_visible(True)
        pygame.display.set_caption('PedagoBattle')
        self.clock = pygame.time.Clock()

        # As três opções da seleção usam os monstros deste time de demonstração.
        self.player_monsters = {0: Monster('Jabu', 15), 1: Monster('Equonci', 15), 2: Monster('Prezen', 16), 3: Monster('Rosial', 15), 4: Monster('Triátomo', 15), 5: Monster('Palhetin', 15)}
        for monster in self.player_monsters.values(): monster.xp += randint(0, monster.level * 100)
        self.import_assets()
        self.battle = None

        # --- Tela inicial ---
        self.game_state = 'platform'
        self.screen_transition_from = None
        self.screen_transition_started = 0
        self.screen_transition_style = 'dissolve'
        self.screen_transition_duration = 700
        self.SCREEN_TRANSITION_DURATION = 700
        self.battle_loading_started = 0
        self.BATTLE_LOADING_DURATION = 1_500
        self.battle_close_started = None
        self.BATTLE_CLOSE_DURATION = 700
        self.battle_reveal_started = None
        self.BATTLE_REVEAL_DURATION = 700
        self.pending_battle_pair = None
        self.last_opponent_pair = None
        self.opponent_pair_history = set()
        self.platform = None
        self.platform_screen = PlatformScreen(self.display_surface, self.fonts)
        self.start_screen = StartScreen(self.display_surface, self.fonts)
        self.tutorial_screen = TutorialScreen(self.display_surface, self.fonts)
        self.select_screen = SelectScreen(self.display_surface, self.fonts, self.monster_frames)
        self.victory_menu = VictoryMenuScreen(self.display_surface, self.fonts)

    # Preparação dos recursos da demo.
    def import_assets(self):
        """Carrega sprites, fontes, cenários e sons usados pela demo de batalha."""
        self.monster_frames = {'icons': import_folder_dict('graphics', 'icons'), 'monsters': monster_importer(4,2,'graphics', 'monsters'), 'ui': import_folder_dict('graphics', 'ui'), 'attacks': attack_importer('graphics', 'attacks')}
        loading_sheet = self.monster_frames['ui']['loading']
        frame_count = 4
        source_frame_width = loading_sheet.get_width() // frame_count
        frame_height = loading_sheet.get_height()
        self.loading_frames = [
            pygame.transform.scale(
                loading_sheet.subsurface(
                    (
                        index * source_frame_width,
                        0,
                        source_frame_width,
                        loading_sheet.get_height(),
                    )
                ).copy(),
                (source_frame_width * 3, frame_height * 3),
            )
            for index in range(frame_count)
        ]
        self.monster_frames['outlines'] = outline_creator(self.monster_frames['monsters'], 4)
        self.fonts = {'dialog': pygame.font.Font(resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 30), 'regular': pygame.font.Font(resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 18), 'small': pygame.font.Font(resolve_path('graphics', 'fonts', 'PixeloidSans.ttf'), 14), 'bold': pygame.font.Font(resolve_path('graphics', 'fonts', 'dogicapixelbold.otf'), 20)}
        self.bg_frames = import_folder_dict('graphics', 'backgrounds')
        self.audio = audio_importer('audio')

    def return_to_start_menu(self):
        """Encerra a batalha demo, restaura o time e volta ao menu inicial."""
        self.end_battle()
        for monster in self.player_monsters.values():
            monster.health = monster.get_stat('max_health')
            monster.energy = monster.get_stat('max_energy')
            monster.initiative = 0
        self.transition_to_screen('start')

    def end_battle(self, character=None):
        """Desliga a batalha demo e interrompe sua trilha sonora."""
        self.battle = None
        if 'battle' in self.audio:
            self.audio['battle'].stop()

    def draw_cursor(self):
        if self.platform == 'pc':
            self.display_surface.blit(self.cursor_image, pygame.mouse.get_pos())

    def transition_to_screen(self, game_state):
        """Troca entre telas de menu com uma dissolução da imagem anterior."""
        menu_states = {'platform', 'start', 'tutorial', 'select', 'victory_menu', 'playing'}
        transition_pair = (self.game_state, game_state)
        supported_transition = (
            self.game_state in menu_states
            and game_state in menu_states
        )
        if supported_transition:
            if game_state == 'start':
                self.screen_transition_from = None
                self.battle_reveal_started = pygame.time.get_ticks()
            else:
                self.screen_transition_from = self.display_surface.copy()
                self.screen_transition_started = pygame.time.get_ticks()
            if transition_pair == ('tutorial', 'select'):
                self.screen_transition_style = 'chalk'
                self.screen_transition_duration = 1_000
                self.screen_transition_from = pygame.Surface(
                    (WINDOW_WIDTH, WINDOW_HEIGHT),
                    pygame.SRCALPHA,
                )
                self.screen_transition_from.fill((0, 0, 0, 0))
                source_screen = {
                    'platform': self.platform_screen,
                    'tutorial': self.tutorial_screen,
                    'select': self.select_screen,
                }[self.game_state]
                source_screen.draw_transition_items(self.screen_transition_from)
            else:
                self.screen_transition_style = 'dissolve'
                self.screen_transition_duration = self.SCREEN_TRANSITION_DURATION
        else:
            self.screen_transition_from = None
        self.game_state = game_state

    def draw_screen_transition(self):
        """Sobrepõe a tela anterior com o efeito configurado para a transição."""
        if self.screen_transition_from is None:
            return
        elapsed = pygame.time.get_ticks() - self.screen_transition_started
        if elapsed >= self.screen_transition_duration:
            self.screen_transition_from = None
            return

        if self.screen_transition_style == 'chalk':
            self.draw_chalk_transition(elapsed)
            return

        alpha = int(255 * (1 - elapsed / self.screen_transition_duration))
        self.screen_transition_from.set_alpha(alpha)
        self.display_surface.blit(self.screen_transition_from, (0, 0))

    def draw_chalk_transition(self, elapsed):
        """Apaga a tela anterior com uma borda irregular de giz."""
        progress = min(1, elapsed / self.screen_transition_duration)
        eased_progress = progress * progress * (3 - 2 * progress)
        wipe_edge = int(WINDOW_WIDTH * eased_progress)
        wave_strength = sin(progress * pi) * 8

        for y in range(0, WINDOW_HEIGHT, 4):
            wave = int(sin(y * 0.045 + elapsed * 0.012) * wave_strength)
            edge_x = max(0, min(WINDOW_WIDTH, wipe_edge + wave))
            row_height = min(4, WINDOW_HEIGHT - y)
            if edge_x < WINDOW_WIDTH:
                source_rect = pygame.Rect(edge_x, y, WINDOW_WIDTH - edge_x, row_height)
                self.display_surface.blit(
                    self.screen_transition_from,
                    (edge_x, y),
                    source_rect,
                )

            if 0 < edge_x < WINDOW_WIDTH and (y // 4 + int(elapsed // 45)) % 4 != 0:
                chalk_color = '#e6eee8' if y % 3 else COLORS['pure white']
                pygame.draw.line(
                    self.display_surface,
                    chalk_color,
                    (edge_x, y),
                    (min(WINDOW_WIDTH - 1, edge_x + 2), min(WINDOW_HEIGHT - 1, y + 2)),
                    2,
                )

        eraser_surface = pygame.Surface((42, 26), pygame.SRCALPHA)
        pygame.draw.rect(
            eraser_surface,
            '#f4a6a6',
            (1, 1, 40, 24),
            border_radius=5,
        )
        pygame.draw.rect(
            eraser_surface,
            COLORS['dark'],
            (1, 1, 40, 24),
            width=2,
            border_radius=5,
        )
        pygame.draw.line(
            eraser_surface,
            COLORS['pure white'],
            (7, 7),
            (35, 7),
            3,
        )
        rotated_eraser = pygame.transform.rotate(eraser_surface, -18)
        eraser_rect = rotated_eraser.get_rect(
            center=(max(0, min(WINDOW_WIDTH, wipe_edge)), WINDOW_HEIGHT // 2),
        )
        self.display_surface.blit(rotated_eraser, eraser_rect)

    def draw_battle_reveal(self):
        """Puxa duas cortinas para as bordas e revela a tela da batalha."""
        if self.battle_reveal_started is None:
            return

        elapsed = pygame.time.get_ticks() - self.battle_reveal_started
        if elapsed >= self.BATTLE_REVEAL_DURATION:
            self.battle_reveal_started = None
            return

        progress = max(0, elapsed / self.BATTLE_REVEAL_DURATION)
        eased_progress = progress * progress * (3 - 2 * progress)
        cover_height = int((WINDOW_HEIGHT / 2) * (1 - eased_progress))
        if cover_height <= 0:
            return

        pygame.draw.rect(
            self.display_surface,
            COLORS['black'],
            (0, 0, WINDOW_WIDTH, cover_height),
        )
        pygame.draw.rect(
            self.display_surface,
            COLORS['black'],
            (0, WINDOW_HEIGHT - cover_height, WINDOW_WIDTH, cover_height),
        )
        pygame.draw.line(
            self.display_surface,
            COLORS['blue'],
            (0, cover_height),
            (WINDOW_WIDTH, cover_height),
            2,
        )
        pygame.draw.line(
            self.display_surface,
            COLORS['blue'],
            (0, WINDOW_HEIGHT - cover_height),
            (WINDOW_WIDTH, WINDOW_HEIGHT - cover_height),
            2,
        )

    def draw_battle_close(self):
        """Fecha as cortinas sobre a seleção antes de iniciar o carregamento."""
        if self.battle_close_started is None:
            return

        elapsed = pygame.time.get_ticks() - self.battle_close_started
        progress = min(1, max(0, elapsed / self.BATTLE_CLOSE_DURATION))
        eased_progress = progress * progress * (3 - 2 * progress)
        cover_height = int((WINDOW_HEIGHT / 2) * eased_progress)

        pygame.draw.rect(
            self.display_surface,
            COLORS['black'],
            (0, 0, WINDOW_WIDTH, cover_height),
        )
        pygame.draw.rect(
            self.display_surface,
            COLORS['black'],
            (0, WINDOW_HEIGHT - cover_height, WINDOW_WIDTH, cover_height),
        )
        if 0 < cover_height < WINDOW_HEIGHT // 2:
            pygame.draw.line(
                self.display_surface,
                COLORS['blue'],
                (0, cover_height),
                (WINDOW_WIDTH, cover_height),
                2,
            )
            pygame.draw.line(
                self.display_surface,
                COLORS['blue'],
                (0, WINDOW_HEIGHT - cover_height),
                (WINDOW_WIDTH, WINDOW_HEIGHT - cover_height),
                2,
            )

        if elapsed >= self.BATTLE_CLOSE_DURATION:
            self.battle_close_started = None

    def draw_battle_loading(self):
        """Desenha uma tela preta com um símbolo retrô de carregamento animado."""
        self.display_surface.fill(COLORS['black'])
        elapsed = pygame.time.get_ticks() - self.battle_loading_started
        frame_index = int(elapsed // 110) % len(self.loading_frames)
        loading_frame = self.loading_frames[frame_index]
        self.display_surface.blit(
            loading_frame,
            loading_frame.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)),
        )
        label = self.fonts['small'].render('CARREGANDO', False, COLORS['white'])
        self.display_surface.blit(
            label,
            label.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150)),
        )

    def handle_battle_finished(self, result):
        """Restaura o time e escolhe a próxima tela conforme vitória ou derrota."""
        # chamado pela Battle quando a tela de vitoria/derrota termina.
        # vitoria -> mostra a tela de 'parabens' com o menu; derrota -> volta direto pro menu inicial
        # cura o time antes de voltar, para a demo poder ser jogada de novo em ambos os casos
        for monster in self.player_monsters.values():
            monster.health = monster.get_stat('max_health')
            monster.energy = monster.get_stat('max_energy')
        if result == 'victory':
            self.transition_to_screen('victory_menu')
        else:
            self.transition_to_screen('start')


    # --- Demo: inicia uma batalha com a dupla escolhida ---
    def start_demo_battle(self, selected_pair):
        """Registra a dupla selecionada e cria uma dupla adversária cadastrada."""
        if selected_pair not in self.select_screen.available_pairings:
            raise ValueError(f'Dupla de Pedagos indisponível: {selected_pair!r}')

        player_monsters_by_name = {
            monster.name: monster for monster in self.player_monsters.values()
        }
        if any(name not in player_monsters_by_name for name in selected_pair):
            raise ValueError(f'Pedago selecionado não existe no time do jogador: {selected_pair!r}')

        selected_monsters = [player_monsters_by_name[name] for name in selected_pair]
        selected_player_monsters = dict(enumerate(selected_monsters))

        # Os monstros elegíveis são validados pela tela de seleção, mas o oponente
        # pode combinar qualquer dois deles, sem depender das duplas do jogador.
        available_monsters = tuple(dict.fromkeys(
            name
            for pair in self.select_screen.available_pairings
            for name in pair
        ))
        available_pairings = tuple(combinations(available_monsters, 2))
        opponent_pair_history = getattr(self, 'opponent_pair_history', set())
        opponent_choices = tuple(
            pair for pair in available_pairings
            if pair not in opponent_pair_history
        )
        if not opponent_choices:
            opponent_pair_history.clear()
            opponent_choices = available_pairings
        opponent_pair = choice(opponent_choices)
        opponent_pair_history.add(opponent_pair)
        self.opponent_pair_history = opponent_pair_history
        self.last_opponent_pair = opponent_pair
        opponent_team = [Monster(name, 15) for name in opponent_pair]
        opponent_monsters = dict(enumerate(opponent_team))
        bg = self.bg_frames.get('forest')
        if bg is None:
            bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            bg.fill(COLORS['white'])
        if 'battle' in self.audio:
            self.audio['battle'].play(-1)
        self.battle = Battle(
            player_monsters=selected_player_monsters,
            opponent_monsters=opponent_monsters,
            monster_frames=self.monster_frames,
            bg_surf=bg,
            fonts=self.fonts,
            end_battle=self.end_battle,
            character=None,
            sounds=self.audio,
            on_battle_finished=self.handle_battle_finished,
            on_return_to_menu=self.return_to_start_menu)
        self.battle.next_turn = 'opponent' if randint(0, 3) == 0 else 'player'
        
    def run(self):
        """Mantém o loop principal e encaminha eventos à tela que está ativa."""
        while True:
            dt = self.clock.tick(60) / 1000.0

            if self.game_state == 'platform':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    selected_platform = self.platform_screen.handle_event(pointer_event(event))
                    if selected_platform:
                        self.platform = selected_platform
                        pygame.mouse.set_visible(False)
                        self.transition_to_screen('start')
                self.platform_screen.update(dt)
                self.platform_screen.draw()
                self.draw_screen_transition()
                self.draw_cursor()
                pygame.display.flip()
                continue

            # --- Tela inicial: captura eventos separadamente e não roda o jogo ainda ---
            if self.game_state == 'start':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    action = self.start_screen.handle_event(pointer_event(event))
                    if action == 'exit':
                        pygame.quit()
                        sys.exit()
                    if action == 'start':
                        self.transition_to_screen('tutorial')
                self.start_screen.update(dt)
                self.start_screen.draw()
                self.draw_screen_transition()
                self.draw_battle_reveal()
                self.draw_cursor()
                pygame.display.flip()
                continue

            # --- Tutorial antes da escolha do pedago ---
            if self.game_state == 'tutorial':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if self.tutorial_screen.handle_event(pointer_event(event)):
                        self.transition_to_screen('select')
                self.tutorial_screen.update(dt)
                self.tutorial_screen.draw()
                self.draw_screen_transition()
                self.draw_cursor()
                pygame.display.flip()
                continue

            # --- Tela de escolha do pedago: também não roda o jogo ainda ---
            if self.game_state == 'select':
                # A escolha devolve o nome do monstro; só então a demo começa.
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    selected_pair = self.select_screen.handle_event(pointer_event(event))
                    if selected_pair:
                        self.pending_battle_pair = selected_pair
                        self.screen_transition_from = None
                        self.battle_reveal_started = None
                        self.battle_close_started = pygame.time.get_ticks()
                        self.game_state = 'battle_closing'
                self.select_screen.update(dt)
                self.select_screen.draw()
                self.draw_cursor()
                pygame.display.flip()
                continue

            if self.game_state == 'battle_closing':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.select_screen.draw()
                self.draw_battle_close()
                self.draw_cursor()
                pygame.display.flip()

                if (
                    self.battle_close_started is None
                    or pygame.time.get_ticks() - self.battle_close_started >= self.BATTLE_CLOSE_DURATION
                ):
                    self.battle_loading_started = pygame.time.get_ticks()
                    self.game_state = 'battle_loading'
                continue

            if self.game_state == 'battle_loading':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.draw_battle_loading()
                self.draw_screen_transition()
                self.draw_battle_reveal()
                pygame.display.flip()

                if self.pending_battle_pair:
                    selected_pair = self.pending_battle_pair
                    self.pending_battle_pair = None
                    self.start_demo_battle(selected_pair)
                    self.battle_loading_started = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.battle_loading_started >= self.BATTLE_LOADING_DURATION:
                    self.game_state = 'playing'
                    self.battle_reveal_started = pygame.time.get_ticks()
                    if self.battle:
                        self.battle.battle_transition_start = pygame.time.get_ticks()
                continue

            # --- Tela de 'parabens' pos-vitoria: menu com as opcoes (so 'voltar' funciona) ---
            if self.game_state == 'victory_menu':
                for event in pointer_events(pygame.event.get()):
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if self.victory_menu.handle_event(pointer_event(event)) == 'menu':
                        self.transition_to_screen('start')
                self.victory_menu.update(dt)
                self.victory_menu.draw()
                self.draw_screen_transition()
                self.draw_cursor()
                pygame.display.flip()
                continue

            for event in pointer_events(pygame.event.get()):
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.FINGERDOWN and self.battle:
                    width, height = self.display_surface.get_size()
                    self.battle.handle_touch(
                        (int(event.x * width), int(event.y * height))
                    )
            # Atualiza e desenha a batalha ativa.
            if self.battle:
                # Battle controla seu próprio turno e renderiza diretamente na janela.
                try:
                    self.battle.update(dt)
                    if self.game_state == 'playing':
                        self.draw_battle_reveal()
                    self.draw_cursor()
                    pygame.display.flip()  # Apresenta o quadro recém-desenhado da batalha.
                except Exception:
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                self.transition_to_screen('start')

if __name__ == '__main__':
    game = Game(); game.run()
