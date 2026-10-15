from settings import * 
from sprites import MonsterSprite, MonsterOutlineSprite, AttackSprite, DamageTextSprite, BattleCalloutSprite
from groups import BattleSprites
from game_data import ATTACK_DATA, ATTACK_NAME_CATEGORIES, get_attack_display_name
from support import draw_bar, get_surface_rect
from timer import Timer
from random import choice, random, shuffle, uniform, randint
from math import sin
from quiz import QUIZ_QUESTIONS, QUIZ_EXATAS, QUIZ_HUMANAS, QUIZ_POR_MATERIA

class Battle:
    """Controla turnos, ataques, interface e resultado de uma batalha."""

    OPPONENT_DAMAGE_MULTIPLIER = 1.1

    def __init__(self, player_monsters, opponent_monsters, monster_frames, bg_surf, fonts, end_battle, character, sounds, on_battle_finished = None, on_return_to_menu = None):
        """Prepara o estado da luta e guarda os recursos compartilhados com o jogo."""
        # Recursos compartilhados e callbacks que ligam a batalha ao jogo.
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.monster_frames = monster_frames
        self.fainted_icon_cache = {}
        self.fonts = fonts
        self.monster_data = {'player': player_monsters, 'opponent': opponent_monsters}
        self.battle_over = False
        self.end_battle = end_battle
        self.character = character
        self.sounds = sounds
        self.on_battle_finished = on_battle_finished  # callback opcional: chamado com 'victory'/'defeat' ao fim
        self.on_return_to_menu = on_return_to_menu

        # Temporizadores da batalha.
        self.timers = {
            'opponent delay': Timer(OPPONENT_TURN_DELAY, func = self.opponent_attack)
        }

        # tela animada de vitoria/derrota
        self.result = None
        self.result_particles = []
        self.result_start_time = 0
        self.result_min_display = 1300   # tempo minimo (ms) exibindo a tela antes de poder avancar
        self.result_continue_rect = pygame.Rect(0, 0, 320, 42)
        self.result_continue_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110)
        self.battle_transition_start = pygame.time.get_ticks()
        self.BATTLE_INTRO_DURATION = 1_800
        self.battle_intro_overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        self.return_button_rect = pygame.Rect(0, 0, 80, 30)
        self.return_button_rect.midtop = (WINDOW_WIDTH // 2, 4)
        self.recover_energy_button_rect = pygame.Rect(0, 0, 188, 42)

        # animacao de abertura dos menus (deslizar + suavizar) e pulso do destaque
        self._last_ui_mode = None
        self._menu_anim_start = 0

        # Acertos geram golpes críticos; erros causam o dano normal e o tempo
        # esgotado encerra o turno sem aplicar dano.
        self.pending_quiz = None      # {'question':..., 'target':..., 'attack':...} enquanto o quiz esta na tela
        self.quiz_question_queue = []
        self.quiz_queue_category = None
        self.last_quiz_question = None
        self.quiz_option_rects = []
        self.quiz_feedback = None
        self.quiz_outcome = None      # resultado do quiz consumido pelo proximo apply_attack
        self.QUIZ_FEEDBACK_TIME = 1_100
        self.QUIZ_TIME_LIMITS = {'easy': 20_000, 'medium': 25_000, 'hard': 30_000}
        self.QUIZ_DAMAGE_MULTIPLIERS = {
            'easy': 1.35,
            'medium': 1.45,
            'hard': 1.55,
        }
        self.HEALING_MULTIPLIER = 0.75
        self.ENERGY_RECOVERY_THRESHOLD = 0.25
        self.BOT_ENERGY_RECOVERY_ACCURACY = 0.7
        self.BOT_RANDOM_ATTACK_CHANCE = 0.65
        self.BOT_HEAL_CHANCE = 0.25
        self.BOT_HEAL_HEALTH_THRESHOLD = 0.55

        # painel lateral com o time (1x1 em campo + banco). so o painel do JOGADOR e clicavel;
        # o do oponente e so visual (quem escolhe trocar do lado do bot e o proprio bot)
        self.team_panel_rects = {'player': [], 'opponent': []}
        self.hovered_panel_card = None
        self.panel_card_hover_started = 0
        self.mouse_was_pressed = False
        self.touch_handled_this_frame = False
        self.attack_button_rects = []
        self.attack_page_rects = {}
        self.defend_button_rect = None
        self.attack_page = 0
        self.RETURN_TO_BOOK_DURATION = 1_200
        self.SWITCH_TO_BOOK_DURATION = self.RETURN_TO_BOOK_DURATION
        self.player_return_animation = None
        self.pending_player_switch = None
        self.awaiting_player_switch = False
        self.player_switch_ready = False
        self.pending_player_pos_index = None
        self.forced_switch_rects = []

        # Grupos separam os efeitos visuais e os monstros de cada lado.
        self.battle_sprites   = BattleSprites()
        self.player_sprites   = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        # Estado necessário para decidir quem joga e qual menu deve aparecer.
        self.current_monster = None
        self.selection_mode  = None
        self.selected_attack = None
        self.selection_side  = 'player'
        self.next_turn = 'player'
        self.turn_in_progress = False
        self.indexes = {
            'general': 0,
            'monster': 0,
            'attacks': 0,
            'switch' : 0,
            'target' : 0,
        }

        self.setup()

    def setup(self):
        """Coloca em campo o primeiro monstro de cada time; os demais ficam no banco."""
        # 1x1: so o primeiro monstro (menor indice) de cada lado entra ativo em campo.
        # monster_data continua com TODOS os monstros (ativo + banco) dos dois lados --
        # quem esta ativo e determinado por quem tem sprite em player_sprites/opponent_sprites
        # (mesma logica de 'banco' que o menu de troca do jogador ja usava).
        for entity in ('player', 'opponent'):
            monster_dict = self.monster_data[entity]
            if monster_dict:
                first_index = min(monster_dict.keys())
                self.create_monster(monster_dict[first_index], first_index, 1, entity)  # pos_index 1 = 'center'

        if not self.opponent_sprites.sprites():
            print("AVISO: Nenhum monstro inimigo foi criado!")

    def create_monster(self, monster, index, pos_index, entity):
        """Cria os sprites do monstro e registra-os nos grupos do lado correspondente."""
        monster.paused = False
        frames = self.monster_frames['monsters'][monster.name]
        outline_frames = self.monster_frames['outlines'][monster.name]
        if entity == 'player':
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in outline_frames.items()}
        else:
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        monster_sprite = MonsterSprite(pos, frames, groups, monster, index, pos_index, entity, self.apply_attack, self.create_monster)
        MonsterOutlineSprite(monster_sprite, self.battle_sprites, outline_frames)

    def input(self):
        """Verifica o limite de tempo enquanto a tela do quiz está ativa."""
        # o quiz aceita respostas pelo mouse; aqui so e verificado o tempo limite.
        if self.selection_mode == 'quiz':
            self.handle_quiz_input()
            return
        if self.selection_mode == 'quiz_feedback':
            return

    def start_player_attack(self, attack):
        """Define o alvo do golpe e inicia o quiz que antecede o ataque do jogador."""
        if not self.current_monster or self.current_monster.monster.get_attack_cost(attack) > self.current_monster.monster.energy:
            return
        target_group = self.opponent_sprites if ATTACK_DATA[attack]['target'] == 'opponent' else self.player_sprites
        targets = [
            sprite for sprite in target_group.sprites()
            if sprite.monster.health > 0 and not sprite.timers['kill'].active
        ]
        if not targets:
            return
        self.selected_attack = attack
        self.selection_side = ATTACK_DATA[attack]['target']
        self.start_quiz(targets[0], attack)
        self.selection_mode = 'quiz'

    def start_energy_recovery(self):
        """Abre o quiz para recuperar energia e consumir o turno atual."""
        if not self.can_recover_energy():
            return
        self.selected_attack = 'recover_energy'
        self.selection_side = 'player'
        self.start_quiz(self.current_monster, 'recover_energy')
        self.selection_mode = 'quiz'

    def can_recover_energy(self):
        """Permite recuperar energia somente quando restar no máximo 25%."""
        if not self.current_monster or self.player_sprites not in self.current_monster.groups():
            return False
        monster = self.current_monster.monster
        return monster.energy <= monster.get_stat('max_energy') * self.ENERGY_RECOVERY_THRESHOLD

    def apply_energy_recovery(self, monster_sprite, answered_correctly):
        """Restaura energia apenas após acertar o quiz e encerra o turno."""
        monster = monster_sprite.monster
        if answered_correctly:
            max_energy = monster.get_stat('max_energy')
            energy_restored = min(
                max_energy - monster.energy,
                max(1, int(max_energy * 0.35)),
            )
            monster.energy += energy_restored
            try:
                DamageTextSprite(
                    monster_sprite.rect.midtop + vector(0, -10),
                    self.battle_sprites,
                    f'+{energy_restored} ENERGIA',
                    COLORS['blue'],
                    self.fonts['bold'],
                )
            except Exception as error:
                print('Aviso: falha ao mostrar energia recuperada:', error)
        self.update_all_monsters('resume')

    def player_defend(self):
        """Ativa a defesa do monstro do jogador e encerra a escolha daquele turno."""
        if not self.current_monster:
            return
        self.current_monster.monster.defending = True
        self.update_all_monsters('resume')

    def update_timers(self):
        """Avança temporizadores de batalha, incluindo a espera antes da jogada do bot."""
        for timer in self.timers.values():
            timer.update()


    # Fluxo de turnos.
    def check_active(self):
        """Escolhe quem joga em seguida e abre o menu do jogador ou agenda o bot."""
        if self.awaiting_player_switch or self.turn_in_progress:
            return

        sprite_group = self.player_sprites if self.next_turn == 'player' else self.opponent_sprites
        available_sprites = [
            sprite for sprite in sprite_group.sprites()
            if sprite.monster.health > 0 and not sprite.timers['kill'].active
        ]
        if not available_sprites:
            return

        monster_sprite = available_sprites[0]
        monster_sprite.monster.defending = False
        self.update_all_monsters('pause')
        monster_sprite.monster.initiative = 0
        monster_sprite.set_highlight(True)
        self.current_monster = monster_sprite
        self.turn_in_progress = True
        self.next_turn = 'opponent' if self.next_turn == 'player' else 'player'

        if self.player_sprites in monster_sprite.groups():
            self.selection_mode = 'attacks'
            self.attack_page = 0
            self.indexes['attacks'] = 0
        else:
            self.selection_mode = None
            self.timers['opponent delay'].activate()

    def update_all_monsters(self, option):
        """Pausa ou retoma os monstros e limpa o estado quando um turno termina."""
        for monster_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            monster_sprite.monster.paused = True if option == 'pause' else False
        if option == 'resume':
            self.turn_in_progress = False
            self.current_monster = None
            self.selection_mode = None
            self.selected_attack = None

# --- quiz de batalha ---
    def start_quiz(self, target_sprite, attack):
        """Guarda a pergunta, o alvo e o prazo para resolver o ataque escolhido."""
        quiz_question = self.next_quiz_question()
        self.pending_quiz = {
            'question': quiz_question,
            'target': target_sprite,
            'attack': attack,
            'deadline': pygame.time.get_ticks() + self.QUIZ_TIME_LIMITS.get(
                quiz_question.get('difficulty', 'medium'),
                self.QUIZ_TIME_LIMITS['medium'],
            ),
        }

    def next_quiz_question(self):
        """Sorteia perguntas no mesmo tema do monstro atacante."""
        if not self.current_monster:
            return None

        monster = self.current_monster.monster
        quiz_tipo = QUIZ_POR_MATERIA.get(monster.name)
        if quiz_tipo is None:
            monster_element = monster.element.strip().casefold()
            exact_sciences = {'matemática', 'química', 'física', 'biologia'}
            category = 'exatas' if monster_element in exact_sciences else 'humanas'
            quiz_tipo = QUIZ_EXATAS if category == 'exatas' else QUIZ_HUMANAS
            queue_category = category
        else:
            queue_category = monster.name

        if queue_category != self.quiz_queue_category:
            self.quiz_question_queue = []
            self.quiz_queue_category = queue_category

        if not self.quiz_question_queue:
            self.quiz_question_queue = list(quiz_tipo)
            shuffle(self.quiz_question_queue)
            if (
                len(self.quiz_question_queue) > 1
                and self.quiz_question_queue[-1] == self.last_quiz_question
            ):
                self.quiz_question_queue[0], self.quiz_question_queue[-1] = (
                    self.quiz_question_queue[-1],
                    self.quiz_question_queue[0],
                )

        question = dict(self.quiz_question_queue.pop())
        indexed_options = list(enumerate(question['options']))
        shuffle(indexed_options)
        question['options'] = [option for _, option in indexed_options]
        question['correct'] = next(
            index
            for index, (original_index, _) in enumerate(indexed_options)
            if original_index == question['correct']
        )
        self.last_quiz_question = question
        return question

    def handle_quiz_input(self):
        """Encerra o turno sem dano quando o tempo do quiz acaba."""
        if not self.pending_quiz:
            return
        if pygame.time.get_ticks() >= self.pending_quiz['deadline']:
            self.pending_quiz = None
            self.selected_attack = None
            self.quiz_outcome = None
            self.update_all_monsters('resume')

    def resolve_quiz(self, selected_index):
        """Registra acerto/erro e prepara a breve tela de feedback do quiz."""
        quiz = self.pending_quiz
        if not quiz:
            return
        question = quiz['question']
        is_correct = selected_index == question['correct']
        self.quiz_feedback = {
            'question': question,
            'selected_index': selected_index,
            'correct': is_correct,
            'target': quiz['target'],
            'attack': quiz['attack'],
            'attacker': self.current_monster,
            'started_at': pygame.time.get_ticks(),
        }
        self.pending_quiz = None
        self.selection_mode = 'quiz_feedback'

    def update_quiz_feedback(self):
        """Após o feedback, aplica o ataque ou libera o turno se o atacante saiu."""
        feedback = self.quiz_feedback
        if not feedback:
            return
        elapsed = pygame.time.get_ticks() - feedback['started_at']
        if elapsed < self.QUIZ_FEEDBACK_TIME:
            return

        self.quiz_feedback = None
        self.selected_attack = None
        attacker = feedback['attacker']
        if attacker and attacker.groups():
            if feedback['attack'] == 'recover_energy':
                self.apply_energy_recovery(attacker, feedback['correct'])
                return
            self.quiz_outcome = {
                'critical': feedback['correct'],
                'correct': feedback['correct'],
                'difficulty': feedback['question'].get('difficulty', 'medium'),
            }
            attacker.activate_attack(feedback['target'], feedback['attack'])
            self.selection_mode = None
            self.current_monster = None
        else:
            self.quiz_outcome = None
            self.update_all_monsters('resume')

    def apply_attack(self, attacker_sprite, target_sprite, attack, amount):
        # consome o resultado do quiz (se este ataque veio de uma pergunta respondida);
        # ataques do bot nao passam pelo quiz, entao quiz_outcome sera None para eles
        quiz_outcome = self.quiz_outcome
        self.quiz_outcome = None

        if attacker_sprite.entity == 'opponent':
            if amount > 0:
                amount *= self.OPPONENT_DAMAGE_MULTIPLIER
            elif amount < 0:
                amount *= 0.7

        frames = self.monster_frames['attacks'][ATTACK_DATA[attack]['animation']]
        AttackSprite(
            attacker_sprite.rect.center,
            target_sprite,
            frames,
            self.battle_sprites,
            lambda: self.resolve_attack(target_sprite, attack, amount, quiz_outcome),
        )
        self.sounds[ATTACK_DATA[attack]['animation']].play()

    def resolve_attack(self, target_sprite, attack, amount, quiz_outcome):
        # O tipo do ataque pode dobrar ou reduzir pela metade o efeito conforme o alvo.
        attack_element = ATTACK_DATA[attack]['element']
        target_element = target_sprite.monster.element

        # Vantagem elemental: fogo vence planta, água vence fogo e planta vence água.
        is_super_effective = False
        if attack_element == 'fire'  and target_element == 'plant' or \
           attack_element == 'water' and target_element == 'fire'  or \
           attack_element == 'plant' and target_element == 'water':
            amount *= 2
            is_super_effective = True

        # Desvantagem elemental: aplica o inverso da relação acima.
        if attack_element == 'fire'  and target_element == 'water' or \
           attack_element == 'water' and target_element == 'plant' or \
           attack_element == 'plant' and target_element == 'fire':
            amount *= 0.5

        # Respostas corretas são críticas; respostas erradas usam o dano normal.
        is_critical_hit = bool(quiz_outcome and quiz_outcome['critical'])
        if amount > 0 and quiz_outcome and quiz_outcome['correct']:
            difficulty = quiz_outcome.get('difficulty', 'medium')
            amount *= self.QUIZ_DAMAGE_MULTIPLIERS.get(difficulty, 1.2)
        elif amount < 0:
            amount *= self.HEALING_MULTIPLIER

        # Defesa reduz o efeito; defender no turno anterior aplica mais uma redução.
        target_defense = 1 - target_sprite.monster.get_stat('defense') / 2000
        if target_sprite.monster.defending:
            target_defense -= 0.2
        target_defense = max(0, min(1, target_defense))

        # amount negativo representa cura: subtraí-lo aumenta a vida do alvo.
        final_amount = amount * target_defense

        # O mesmo cálculo serve para remover vida ou aplicar cura.
        target_sprite.monster.health -= final_amount
        self.check_death()

        # feedback visual: numero flutuante de dano/cura + sacudida no alvo (batalha mais dinamica)
        # protegido por try/except: um efeito visual nunca pode travar o andamento da batalha
        try:
            self.show_damage_feedback(target_sprite, final_amount, is_super_effective, is_critical_hit)
        except Exception as e:
            print('Aviso: falha ao mostrar feedback de dano:', e)

        if quiz_outcome is not None:
            try:
                callout = 'CRÍTICO!' if quiz_outcome['critical'] else 'DANO NORMAL'
                callout_color = COLORS['gold'] if quiz_outcome['critical'] else COLORS['red']
                BattleCalloutSprite(
                    target_sprite.rect.midtop + vector(0, -34),
                    self.battle_sprites,
                    callout,
                    callout_color,
                    self.fonts['bold'],
                )
            except Exception as e:
                print('Aviso: falha ao mostrar elogio do ataque:', e)

        # Libera os monstros depois que o efeito do ataque foi resolvido.
        self.update_all_monsters('resume')

    def show_damage_feedback(self, target_sprite, final_amount, is_super_effective, is_critical_hit = False):
        """Mostra o número flutuante e a reação visual de dano ou cura."""
        if final_amount >= 0:
            text = f'-{int(final_amount)}' + (' CRIT!' if is_critical_hit else '')
            color = COLORS['gold'] if (is_super_effective or is_critical_hit) else COLORS['red']
            target_sprite.take_hit()
        else:
            text = f'+{int(-final_amount)}'
            color = COLORS['plant']

        DamageTextSprite(target_sprite.rect.midtop + vector(0, -10), self.battle_sprites, text, color, self.fonts['bold'])

    def get_bench(self, entity):
        # retorna {indice: monstro} de quem esta vivo e NAO esta ativo em campo nesse lado --
        # usado tanto para o menu de troca do jogador quanto para o bot escolher um substituto
        sprite_group = self.player_sprites if entity == 'player' else self.opponent_sprites
        active_pairs = [(sprite.index, sprite.monster) for sprite in sprite_group]
        return {index: monster for index, monster in self.monster_data[entity].items()
                if monster.health > 0 and (index, monster) not in active_pairs}

    # --- Painel lateral de troca (mouse) ---
    def handle_mouse(self):
        """Distribui cada novo clique para a interface apropriada, sem repeti-lo."""
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.touch_handled_this_frame:
            self.mouse_was_pressed = mouse_pressed
            self.touch_handled_this_frame = False
            return
        clicked = mouse_pressed and not self.mouse_was_pressed
        self.mouse_was_pressed = mouse_pressed
        if clicked:
            self.handle_pointer_click(pygame.mouse.get_pos())

    def handle_touch(self, pointer_pos):
        """Processa o toque e evita tratar a emulação de mouse do mesmo toque duas vezes."""
        self.touch_handled_this_frame = True
        self.handle_pointer_click(pointer_pos)

    def handle_pointer_click(self, pointer_pos):
        """Aplica um clique de mouse ou toque às mesmas áreas interativas."""
        intro_is_playing = (
            pygame.time.get_ticks() - self.battle_transition_start
            < self.BATTLE_INTRO_DURATION
        )
        if intro_is_playing and not (
            self.awaiting_player_switch and self.player_switch_ready
        ):
            return
        if self.return_button_rect.collidepoint(pointer_pos):
            if self.on_return_to_menu:
                self.on_return_to_menu()
            return
        if self.result:
            elapsed = pygame.time.get_ticks() - self.result_start_time
            if elapsed >= self.result_min_display and self.result_continue_rect.collidepoint(pointer_pos):
                self.finish_battle()
        elif self.awaiting_player_switch:
            if self.player_switch_ready:
                for rect, index, monster in self.forced_switch_rects:
                    if rect.collidepoint(pointer_pos):
                        self.select_forced_player_monster(index, monster)
                        return
        elif self.selection_mode == 'quiz':
            self.handle_quiz_click(pointer_pos)
        elif not self.handle_attack_click(pointer_pos):
            self.handle_panel_click(pointer_pos)

    def handle_quiz_click(self, mouse_pos):
        """Converte o clique em uma resposta apenas se ele atingir uma opção."""
        if self.selection_mode != 'quiz':
            return False
        for rect, option_index in self.quiz_option_rects:
            if rect.collidepoint(mouse_pos):
                self.resolve_quiz(option_index)
                return True
        return False

    def handle_attack_click(self, mouse_pos):
        """Trata páginas, golpes e defesa; retorna se o clique foi consumido."""
        if not (
            self.selection_mode == 'attacks'
            and self.current_monster
            and self.player_sprites in self.current_monster.groups()
        ):
            return False

        for direction, rect in self.attack_page_rects.items():
            if rect.collidepoint(mouse_pos):
                abilities = self.current_monster.monster.get_abilities(all = False)
                page_count = max(1, (len(abilities) + 2) // 3)
                self.attack_page = (self.attack_page + direction) % page_count
                self.indexes['attacks'] = self.attack_page * 3
                return True

        for index, (rect, attack) in enumerate(self.attack_button_rects):
            if rect.collidepoint(mouse_pos):
                self.indexes['attacks'] = self.attack_page * 3 + index
                self.start_player_attack(attack)
                return True

        if self.recover_energy_button_rect.collidepoint(mouse_pos):
            self.start_energy_recovery()
            return True

        if self.defend_button_rect and self.defend_button_rect.collidepoint(mouse_pos):
            self.player_defend()
            return True
        return False

    def handle_panel_click(self, mouse_pos):
        # so pode trocar de pokemon pelo painel durante a SUA vez (nao durante o quiz, nem
        # durante o turno do bot), e so os monstros do proprio jogador sao clicaveis
        if self.selection_mode in ('quiz', 'quiz_feedback'):
            return
        if not (self.current_monster and self.player_sprites in self.current_monster.groups()):
            return
        active_pairs = [(sprite.index, sprite.monster) for sprite in self.player_sprites]
        for rect, index, monster in self.team_panel_rects['player']:
            if rect.collidepoint(mouse_pos) and monster.health > 0 and (index, monster) not in active_pairs:
                self.switch_player_monster(index, monster)
                return

    def switch_player_monster(self, index, monster):
        """Anima o monstro ativo voltando ao livro antes de colocar o escolhido."""
        outgoing_sprite = self.current_monster
        pos_index = outgoing_sprite.pos_index
        start_x, start_y = outgoing_sprite.rect.center
        outgoing_sprite.returning_to_book = True
        self.player_return_animation = {
            'sprite': outgoing_sprite,
            'start_time': pygame.time.get_ticks(),
            'start_pos': (start_x, start_y),
            'book_pos': (max(80, start_x - 120), max(80, start_y - 120)),
            'duration': self.SWITCH_TO_BOOK_DURATION,
        }
        self.pending_player_switch = (index, monster, pos_index)
        self.pending_quiz = None
        self.selected_attack = None
        self.attack_page = 0
        self.current_monster = None
        self.selection_mode = 'returning'
        self.indexes = {k: 0 for k in self.indexes}
        self.update_all_monsters('pause')

    def select_forced_player_monster(self, index, monster):
        """Coloca em campo somente o monstro vivo que o jogador escolheu."""
        if not self.awaiting_player_switch or not self.player_switch_ready:
            return
        if self.monster_data['player'].get(index) is not monster or monster.health <= 0:
            return

        available_monsters = self.get_bench('player')
        if available_monsters.get(index) is not monster:
            return

        pos_index = self.pending_player_pos_index
        if pos_index is None:
            raise RuntimeError('A posição do monstro derrotado não foi registrada.')

        self.create_monster(monster, index, pos_index, 'player')
        self.pending_player_pos_index = None
        self.player_return_animation = None
        self.awaiting_player_switch = False
        self.player_switch_ready = False
        self.forced_switch_rects = []
        self.selection_mode = None
        self.current_monster = None
        self.next_turn = 'player'
        self.update_all_monsters('resume')

    def draw_team_panel(self, entity):
        """Desenha os monstros no banco e guarda áreas clicáveis para o time do jogador."""
        monsters = list(self.monster_data[entity].items())
        if not monsters:
            return
        sprite_group = self.player_sprites if entity == 'player' else self.opponent_sprites
        active_pairs = [(sprite.index, sprite.monster) for sprite in sprite_group]

        row_width, row_height, gap = 150, 50, 8
        x = 12 if entity == 'player' else WINDOW_WIDTH - row_width - 12
        y = 40
        mouse_pos = pygame.mouse.get_pos()

        if entity == 'player':
            self.team_panel_rects['player'] = []
        has_hovered_card = False

        for index, monster in monsters:
            is_active = (index, monster) in active_pairs
            if is_active:
                continue

            rect = pygame.Rect(x, y, row_width, row_height)
            is_fainted = monster.health <= 0
            can_click = entity == 'player' and not is_fainted
            hovered = can_click and rect.collidepoint(mouse_pos)

            jump_offset = 0
            if entity == 'player' and hovered:
                has_hovered_card = True
                card_key = (entity, index)
                if card_key != self.hovered_panel_card:
                    self.hovered_panel_card = card_key
                    self.panel_card_hover_started = pygame.time.get_ticks()
                elapsed = pygame.time.get_ticks() - self.panel_card_hover_started
                progress = min(1, elapsed / 180)
                jump_offset = round(8 * sin(progress * 3.14159))
            visual_rect = rect.move(0, -jump_offset)

            if is_fainted:
                border_color = COLORS['dark']
            else:
                border_color = COLORS['gold'] if hovered else COLORS['blue']
            bg_color = COLORS['dark white'] if hovered else COLORS['white']

            pygame.draw.rect(self.display_surface, bg_color, visual_rect, 0, 6)
            pygame.draw.rect(self.display_surface, border_color, visual_rect, 2, 6)

            icon_surf = self.monster_frames['icons'][monster.name]
            if is_fainted:
                if monster.name not in self.fainted_icon_cache:
                    self.fainted_icon_cache[monster.name] = pygame.transform.grayscale(icon_surf)
                icon_surf = self.fainted_icon_cache[monster.name]
            icon_rect = icon_surf.get_rect(midleft = (visual_rect.left + 6, visual_rect.centery))
            self.display_surface.blit(icon_surf, icon_rect)

            name_color = COLORS['light'] if is_fainted else COLORS['black']
            name_font = self.fonts['small']
            name_text = f'{monster.name} Nv{monster.level}'
            text_left = icon_rect.right + 6
            text_width = max(0, rect.right - 6 - text_left)
            if name_font.size(name_text)[0] > text_width:
                short_name = monster.name
                level_text = f'... Nv{monster.level}'
                while short_name and name_font.size(f'{short_name}{level_text}')[0] > text_width:
                    short_name = short_name[:-1]
                name_text = f'{short_name}{level_text}'
            name_surf = name_font.render(name_text, False, name_color)
            self.display_surface.blit(name_surf, (text_left, visual_rect.top + 6))

            bar_width = max(10, visual_rect.right - (icon_rect.right + 6) - 6)
            bar_rect = pygame.FRect((icon_rect.right + 6, visual_rect.top + 28), (bar_width, 6))
            draw_bar(self.display_surface, bar_rect, max(0, monster.health), monster.get_stat('max_health'), COLORS['black'], COLORS['light-gray'])

            if entity == 'player':
                self.team_panel_rects['player'].append((rect, index, monster))

            y += row_height + gap

        if entity == 'player' and not has_hovered_card:
            self.hovered_panel_card = None

    def check_death(self):
        """Remove derrotados, agenda a troca inimiga e distribui experiência."""
        for monster_sprite in self.opponent_sprites.sprites() + self.player_sprites.sprites():
            if monster_sprite.monster.health <= 0 and not monster_sprite.timers['kill'].active:
                entity = 'player' if self.player_sprites in monster_sprite.groups() else 'opponent'
                bench = self.get_bench(entity)
                if entity == 'player':
                    start_x, start_y = monster_sprite.rect.center
                    self.player_return_animation = {
                        'sprite': monster_sprite,
                        'start_time': pygame.time.get_ticks(),
                        'start_pos': (start_x, start_y),
                        'book_pos': (max(80, start_x - 120), max(80, start_y - 120)),
                    }
                    monster_sprite.returning_to_book = True
                    if bench:
                        self.awaiting_player_switch = True
                        self.player_switch_ready = False
                        self.pending_player_pos_index = monster_sprite.pos_index
                        self.current_monster = None
                        self.selection_mode = 'returning'
                        self.pending_quiz = None
                        self.quiz_feedback = None
                        self.selected_attack = None
                        self.turn_in_progress = False
                        self.timers['opponent delay'].deactivate()
                        self.update_all_monsters('pause')
                    new_monster_data = None
                elif bench:
                    index, monster = list(bench.items())[0]
                    new_monster_data = (monster, index, monster_sprite.pos_index, entity)
                else:
                    new_monster_data = None

                if entity == 'opponent':
                    # xp so eh dado quando um monstro do OPONENTE e derrotado
                    xp_recipients = [
                        player_sprite
                        for player_sprite in self.player_sprites
                        if player_sprite.monster.health > 0
                    ]
                    if xp_recipients:
                        xp_amount = monster_sprite.monster.level * 100 / len(xp_recipients)
                    else:
                        xp_amount = 0
                    for player_sprite in xp_recipients:
                        player_sprite.monster.update_xp(xp_amount)

                # zera a iniciativa do monstro derrotado para garantir que ele nunca 'receba' um
                # turno durante os instantes em que ainda esta sendo removido da batalha
                monster_sprite.monster.initiative = 0
                monster_sprite.delayed_kill(new_monster_data)

    def update_player_return_animation(self):
        """Abre a seleção obrigatória quando a animação de retorno ao livro termina."""
        animation = self.player_return_animation
        if not animation:
            return

        elapsed = pygame.time.get_ticks() - animation['start_time']
        duration = animation.get('duration', self.RETURN_TO_BOOK_DURATION)
        if elapsed < duration:
            return

        self.player_return_animation = None
        if self.awaiting_player_switch:
            self.player_switch_ready = True
            self.selection_mode = 'forced_switch'
            self.update_all_monsters('pause')
        elif self.pending_player_switch:
            index, monster, pos_index = self.pending_player_switch
            outgoing_sprite = animation['sprite']
            outgoing_sprite.kill()
            self.create_monster(monster, index, pos_index, 'player')
            self.pending_player_switch = None
            self.update_all_monsters('resume')

    def draw_player_return_animation(self):
        """Anima o monstro encolhendo e voltando para as páginas de um livro."""
        animation = self.player_return_animation
        if not animation:
            return

        elapsed = pygame.time.get_ticks() - animation['start_time']
        duration = animation.get('duration', self.RETURN_TO_BOOK_DURATION)
        progress = min(1.0, elapsed / duration)
        eased_progress = progress * progress * (3 - 2 * progress)
        book_x, book_y = animation['book_pos']
        start_x, start_y = animation['start_pos']
        center = (
            int(start_x + (book_x - start_x) * eased_progress),
            int(start_y + (book_y - start_y) * eased_progress),
        )

        if progress >= 0.15:
            self.draw_open_book((book_x, book_y), min(1.0, (progress - 0.15) / 0.45))

        sprite = animation['sprite']
        scale = max(0.04, 1.0 - eased_progress * 0.96)
        size = (
            max(1, int(sprite.image.get_width() * scale)),
            max(1, int(sprite.image.get_height() * scale)),
        )
        frame_with_alpha = pygame.Surface(sprite.image.get_size(), pygame.SRCALPHA)
        frame_with_alpha.blit(sprite.image, (0, 0))
        image = pygame.transform.smoothscale(frame_with_alpha, size)
        image.set_alpha(max(0, int(255 * (1 - eased_progress))))
        self.display_surface.blit(image, image.get_rect(center=center))

    def draw_open_book(self, center, opacity):
        """Desenha o livro aberto que recebe o monstro durante a animação."""
        book = pygame.Surface((116, 78), pygame.SRCALPHA)
        alpha = int(255 * max(0.0, min(1.0, opacity)))
        dark = pygame.Color(COLORS['dark'])
        dark.a = alpha
        pages = pygame.Color(COLORS['chalk white'])
        pages.a = alpha
        green = pygame.Color(COLORS['chalk green'])
        green.a = alpha

        pygame.draw.polygon(book, dark, ((5, 14), (55, 22), (55, 69), (5, 59)))
        pygame.draw.polygon(book, dark, ((111, 14), (61, 22), (61, 69), (111, 59)))
        pygame.draw.polygon(book, pages, ((10, 18), (53, 25), (53, 64), (10, 56)))
        pygame.draw.polygon(book, pages, ((106, 18), (63, 25), (63, 64), (106, 56)))
        pygame.draw.line(book, green, (58, 24), (58, 67), 3)
        for line_y in (32, 41, 50):
            pygame.draw.line(book, green, (17, line_y), (47, line_y + 5), 2)
            pygame.draw.line(book, green, (69, line_y + 5), (99, line_y), 2)

        book.set_alpha(alpha)
        self.display_surface.blit(book, book.get_rect(center=center))

    def draw_forced_switch(self):
        """Mostra os Pedagos vivos para o jogador escolher quem continua a batalha."""
        available_monsters = list(self.get_bench('player').items())
        if not available_monsters:
            self.forced_switch_rects = []
            return

        panel_width = 540
        row_height = 74
        panel_height = 118 + len(available_monsters) * row_height
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.display_surface.blit(overlay, (0, 0))
        self.draw_panel(panel_rect, COLORS['gold'])

        title = self.fonts['bold'].render('ESCOLHA QUEM VAI CONTINUAR', True, COLORS['dark'])
        self.display_surface.blit(title, title.get_rect(midtop=(panel_rect.centerx, panel_rect.top + 18)))
        subtitle = self.fonts['small'].render(
            'Seu Pedago voltou ao livro. Selecione o próximo.',
            True,
            COLORS['gray'],
        )
        self.display_surface.blit(
            subtitle,
            subtitle.get_rect(midtop=(panel_rect.centerx, panel_rect.top + 52)),
        )

        self.forced_switch_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for row, (index, monster) in enumerate(available_monsters):
            rect = pygame.Rect(
                panel_rect.left + 18,
                panel_rect.top + 86 + row * row_height,
                panel_width - 36,
                row_height - 8,
            )
            self.forced_switch_rects.append((rect, index, monster))
            hovered = rect.collidepoint(mouse_pos)
            pygame.draw.rect(
                self.display_surface,
                COLORS['chalk hover'] if hovered else COLORS['chalk white'],
                rect,
                border_radius=8,
            )
            pygame.draw.rect(self.display_surface, COLORS['chalk green'], rect, 2, border_radius=8)

            icon = self.monster_frames['icons'][monster.name]
            icon_rect = icon.get_rect(midleft=(rect.left + 38, rect.centery))
            self.display_surface.blit(icon, icon_rect)
            label = self.fonts['regular'].render(
                f'{monster.name} ({monster.level})',
                True,
                COLORS['dark'],
            )
            self.display_surface.blit(label, label.get_rect(midleft=(rect.left + 86, rect.centery)))

    def draw_forced_switch_prompt(self):
        if self.awaiting_player_switch and self.player_switch_ready:
            self.draw_forced_switch()

    def opponent_attack(self):
        # o bot pode decidir trocar de pokemon em vez de atacar (mesmo banco que o jogador usa) --
        # quem escolhe aqui e sempre o proprio bot, nunca o jogador
        if self.bot_should_switch(self.current_monster):
            self.bot_switch(self.current_monster)
            return

        monster = self.current_monster.monster
        abilities = monster.get_abilities(all = False)
        max_energy = monster.get_stat('max_energy')
        energy_is_low = monster.energy <= max_energy * self.ENERGY_RECOVERY_THRESHOLD

        if energy_is_low and (not abilities or random() < 0.45):
            self.bot_recover_energy(self.current_monster)
            return

        healing_abilities = [
            ability for ability in abilities
            if ATTACK_DATA[ability]['amount'] < 0
            and ATTACK_DATA[ability]['target'] == 'player'
        ]
        attack_abilities = [
            ability for ability in abilities
            if ATTACK_DATA[ability]['amount'] > 0
            and ATTACK_DATA[ability]['target'] == 'opponent'
        ]
        health_ratio = monster.health / max(1, monster.get_stat('max_health'))

        if (
            healing_abilities
            and health_ratio <= self.BOT_HEAL_HEALTH_THRESHOLD
            and random() < self.BOT_HEAL_CHANCE
        ):
            ability = choice(healing_abilities)
            self.current_monster.activate_attack(self.current_monster, ability)
            return

        if not attack_abilities:
            if healing_abilities and monster.health < monster.get_stat('max_health'):
                self.current_monster.activate_attack(
                    self.current_monster,
                    choice(healing_abilities),
                )
            else:
                monster.defending = True
                self.update_all_monsters('resume')
            return

        # a IA avalia todas as combinacoes de ataque/alvo possiveis e escolhe a melhor jogada
        best_score, best_choice = None, None
        for ability in attack_abilities:
            data = ATTACK_DATA[ability]
            target_group = self.player_sprites if data['target'] == 'opponent' else self.opponent_sprites
            valid_targets = [
                target for target in target_group.sprites()
                if target.monster.health > 0 and not target.timers['kill'].active
            ]
            for target in valid_targets:
                score = self.evaluate_bot_move(monster, ability, data, target)
                if best_score is None or score > best_score:
                    best_score, best_choice = score, (ability, target)

        if best_choice is None:
            # nao deveria acontecer, mas por seguranca evita deixar a batalha travada (pausada para sempre)
            self.update_all_monsters('resume')
            return

        if random() < self.BOT_RANDOM_ATTACK_CHANCE:
            ability = choice(attack_abilities)
            target_group = self.player_sprites if ATTACK_DATA[ability]['target'] == 'opponent' else self.opponent_sprites
            candidates = [
                target for target in target_group.sprites()
                if target.monster.health > 0 and not target.timers['kill'].active
            ]
            target = choice(candidates) if candidates else best_choice[1]
        else:
            ability, target = best_choice

        self.current_monster.activate_attack(target, ability)

    def bot_recover_energy(self, monster_sprite):
        """Consume o turno tentando recuperar energia; um erro não recupera nada."""
        monster = monster_sprite.monster
        max_energy = monster.get_stat('max_energy')
        if random() < self.BOT_ENERGY_RECOVERY_ACCURACY:
            energy_restored = min(
                max_energy - monster.energy,
                max(1, int(max_energy * 0.35)),
            )
            monster.energy += energy_restored
            message = f'+{energy_restored} ENERGIA'
            color = COLORS['blue']
        else:
            message = 'ERROU!'
            color = COLORS['red']

        DamageTextSprite(
            monster_sprite.rect.midtop + vector(0, -10),
            self.battle_sprites,
            message,
            color,
            self.fonts['bold'],
        )
        self.update_all_monsters('resume')

    def evaluate_bot_move(self, monster, ability, data, target):
        if data['target'] == 'opponent':
            # ataque contra o time do jogador: pontua pelo dano estimado, priorizando finalizar ou castigar alvos fracos
            base_damage = monster.get_stat('attack') * data['amount'] * BATTLE_DAMAGE_MULTIPLIER * BATTLE_DAMAGE_MULTIPLIER
            multiplier = 1
            if data['element'] == 'fire'  and target.monster.element == 'plant' or \
               data['element'] == 'water' and target.monster.element == 'fire'  or \
               data['element'] == 'plant' and target.monster.element == 'water':
                multiplier = 2
            elif data['element'] == 'fire'  and target.monster.element == 'water' or \
                 data['element'] == 'water' and target.monster.element == 'plant' or \
                 data['element'] == 'plant' and target.monster.element == 'fire':
                multiplier = 0.5

            target_defense = 1 - target.monster.get_stat('defense') / 2000
            if target.monster.defending:
                target_defense -= 0.2
            target_defense = max(0, min(1, target_defense))
            damage = max(0, base_damage * multiplier * target_defense)

            score = damage
            if target.monster.health <= damage:
                score += 500   # prioriza finalizar o monstro adversario
            elif target.monster.health / max(1, target.monster.get_stat('max_health')) < 0.35:
                score += 150   # mira em quem ja esta fraco
            return score
        else:
            # cura/buff no proprio time: so vale a pena se o alvo estiver ferido
            missing_health = target.monster.get_stat('max_health') - target.monster.health
            return missing_health * 0.6 if data['amount'] < 0 else -1

    def bot_should_switch(self, monster_sprite):
        # o bot so considera trocar quando o proprio monstro esta bem fraco, e mesmo assim
        # so troca metade das vezes (pra nao ficar 100% previsivel)
        monster = monster_sprite.monster
        health_ratio = monster.health / max(1, monster.get_stat('max_health'))
        if health_ratio > 0.25:
            return False
        return bool(self.get_bench('opponent')) and random() < 0.5

    def bot_switch(self, monster_sprite):
        """Troca o monstro do bot pelo primeiro escolhido aleatoriamente do banco."""
        bench = self.get_bench('opponent')
        if not bench:
            self.update_all_monsters('resume')
            return
        index, new_monster = choice(list(bench.items()))
        pos_index = monster_sprite.pos_index
        monster_sprite.kill()
        self.create_monster(new_monster, index, pos_index, 'opponent')
        self.update_all_monsters('resume')

    def check_end_battle(self):
        if self.result:
            return

        # protegido por try/except: se a tela animada falhar por qualquer motivo, a batalha
        # ainda assim precisa terminar (em vez de travar silenciosamente sem nenhuma tela)
        try:
            # Sem sprites adversários restantes, o jogador venceu a batalha.
            if len(self.opponent_sprites) == 0 and not self.battle_over:
                self.battle_over = True
                for monster in self.monster_data['player'].values():
                    monster.initiative = 0
                self.start_result_screen('victory')

            # Sem sprites do jogador restantes, a batalha termina em derrota.
            elif not any(
                monster.health > 0
                for monster in self.monster_data['player'].values()
            ) and not self.battle_over and not self.player_return_animation:
                self.battle_over = True
                self.start_result_screen('defeat')
        except Exception as e:
            print('Aviso: falha ao iniciar a tela de resultado:', e)
            if not self.result:
                self.result = 'victory' if len(self.opponent_sprites) == 0 else 'defeat'
            self.result_start_time = pygame.time.get_ticks()
            self.result_particles = []
            self.selection_mode = None
            self.current_monster = None


    # ui 
    def menu_open_offset(self):
        # deslocamento (px) que comeca alto e suaviza ate 0 quando um menu acaba de abrir,
        # dando a sensacao do painel 'deslizar' ate a posicao final (batalha mais animada)
        if self.selection_mode != self._last_ui_mode:
            self._menu_anim_start = pygame.time.get_ticks()
            self._last_ui_mode = self.selection_mode
        elapsed = pygame.time.get_ticks() - self._menu_anim_start
        t = min(1.0, elapsed / 180)
        eased = 1 - (1 - t) ** 3
        return (1 - eased) * 16

    def draw_panel(self, rect, border_color):
        # painel com sombra e borda colorida (visual mais bonito que o retangulo branco liso original)
        shadow_rect = rect.move(4, 4)
        pygame.draw.rect(self.display_surface, COLORS['dark'], shadow_rect, 0, 8)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 8)
        pygame.draw.rect(self.display_surface, border_color, rect, 2, 8)

    def draw_monster_hud(self):
        """Desenha nome, nível e barra de vida dos monstros atualmente em campo."""
        status_width = 300
        status_height = 70
        left_edge = 176

        for entity, group in (('player', self.player_sprites), ('opponent', self.opponent_sprites)):
            for slot, sprite in enumerate(group.sprites()):
                monster = sprite.monster
                max_health = monster.get_stat('max_health')
                health = max(0, monster.health)
                top = 42 + slot * (status_height + 8)
                is_player = entity == 'player'
                left = left_edge if is_player else WINDOW_WIDTH - left_edge - status_width
                status_rect = pygame.Rect(left, top, status_width, status_height)
                border_color = COLORS['gold'] if is_player else COLORS['blue']
                pygame.draw.rect(self.display_surface, COLORS['white'], status_rect, 0, 7)
                pygame.draw.rect(self.display_surface, border_color, status_rect, 2, 7)

                icon_surf = self.monster_frames['icons'][monster.name]
                icon_rect = icon_surf.get_rect(midleft=(status_rect.left + 6, status_rect.centery))
                self.display_surface.blit(icon_surf, icon_rect)

                name_font = self.fonts['small']
                name_text = f'{monster.name}  Nv{monster.level}'
                element_color = COLORS.get(monster.element, COLORS['light-gray'])
                color = pygame.Color(element_color)
                text_color = (
                    COLORS['dark']
                    if 299 * color.r + 587 * color.g + 114 * color.b > 150_000
                    else COLORS['pure white']
                )
                element_surf = name_font.render(monster.element, True, text_color)
                badge_padding = 5
                badge_gap = 5
                badge_width = element_surf.get_width() + badge_padding * 2
                text_left = icon_rect.right + 6
                text_width = max(0, status_rect.right - 8 - text_left)
                show_element = True
                name_width = name_font.size(name_text)[0]
                if name_width + badge_gap + badge_width > text_width:
                    available_name_width = max(
                        0,
                        text_width - badge_gap - badge_width,
                    )
                    short_name = monster.name
                    level_text = f'... Nv{monster.level}'
                    while (
                        short_name
                        and name_font.size(f'{short_name}{level_text}')[0]
                        > available_name_width
                    ):
                        short_name = short_name[:-1]
                    shortened_name = f'{short_name}{level_text}'
                    if name_font.size(shortened_name)[0] <= available_name_width:
                        name_text = shortened_name
                    else:
                        show_element = False
                        if name_width > text_width:
                            short_name = monster.name
                            while (
                                short_name
                                and name_font.size(f'{short_name}{level_text}')[0]
                                > text_width
                            ):
                                short_name = short_name[:-1]
                            name_text = f'{short_name}{level_text}'
                name_surf = name_font.render(name_text, True, COLORS['black'])
                name_top = status_rect.top + 5
                self.display_surface.blit(name_surf, (text_left, name_top))
                if show_element:
                    badge_rect = pygame.Rect(
                        text_left + name_surf.get_width() + badge_gap,
                        name_top - 2,
                        badge_width,
                        element_surf.get_height() + 4,
                    )
                    pygame.draw.rect(
                        self.display_surface,
                        element_color,
                        badge_rect,
                        border_radius=5,
                    )
                    self.display_surface.blit(
                        element_surf,
                        (badge_rect.left + badge_padding, name_top),
                    )
                bar_rect = pygame.FRect(text_left, status_rect.top + 30, text_width, 8)
                draw_bar(self.display_surface, bar_rect, health, max_health, COLORS['green'], COLORS['light-gray'], 3)
                max_energy = monster.get_stat('max_energy')
                energy_text = self.fonts['small'].render(
                    f'EP {int(monster.energy)}/{int(max_energy)}',
                    False,
                    COLORS['dark'],
                )
                self.display_surface.blit(energy_text, (text_left, status_rect.top + 42))
                energy_rect = pygame.FRect(text_left, status_rect.top + 59, text_width, 6)
                draw_bar(
                    self.display_surface,
                    energy_rect,
                    monster.energy,
                    max_energy,
                    COLORS['blue'],
                    COLORS['light-gray'],
                    2,
                )

    def draw_ui(self):
        """Desenha quiz ou opções de ataque conforme o estado da batalha."""
        if self.awaiting_player_switch:
            self.draw_forced_switch_prompt()
            return
        if self.selection_mode in ('quiz', 'quiz_feedback'):
            self.draw_quiz()
            return
        if self.current_monster:
            if self.selection_mode == 'attacks':
                self.draw_attacks()
        else:
            self._last_ui_mode = None

    def wrap_text(self, text, font, max_width):
        # quebra de linha simples, so pra caber perguntas mais longas dentro do painel do quiz
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            test = f'{current} {word}'.strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def fit_text_surface(self, surface, max_width, max_height):
        """Reduz um texto renderizado para que caiba dentro do seu elemento."""
        if surface.get_width() <= max_width and surface.get_height() <= max_height:
            return surface
        scale = min(
            max_width / surface.get_width(),
            max_height / surface.get_height(),
        )
        size = (
            max(1, int(surface.get_width() * scale)),
            max(1, int(surface.get_height() * scale)),
        )
        return pygame.transform.smoothscale(surface.convert_alpha(), size)

    def draw_quiz(self):
        """Renderiza a pergunta, o cronômetro, as opções e o resultado da resposta."""
        quiz = self.pending_quiz
        feedback = self.quiz_feedback
        self.quiz_option_rects = []
        if not quiz and not feedback:
            return
        question = quiz['question'] if quiz else feedback['question']

        # fundo escurecido atras do quiz, pra destacar bem a pergunta
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.display_surface.blit(overlay, (0, 0))

        width, height = 560, 320
        rect = pygame.FRect((0, 0), (width, height))
        rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.draw_panel(rect, COLORS['blue'])

        if feedback:
            title = (
                'ACERTO CRÍTICO! RESPOSTA CORRETA:'
                if feedback['correct']
                else 'ERRO! RESPOSTA CORRETA:'
            )
            title_color = COLORS['green'] if feedback['correct'] else COLORS['red']
            cat_surf = self.fonts['small'].render(title, False, title_color)
        else:
            category_label = 'HUMANAS' if question['category'] == 'humanas' else 'EXATAS'
            cat_surf = self.fonts['small'].render(f'QUIZ - {category_label}', False, COLORS['blue'])
        self.display_surface.blit(cat_surf, (rect.left + 16, rect.top + 14))
        difficulty = question.get('difficulty', 'medium')
        difficulty_labels = {'easy': 'FÁCIL', 'medium': 'MÉDIA', 'hard': 'DIFÍCIL'}
        difficulty_colors = {
            'easy': COLORS['green'],
            'medium': COLORS['gold'],
            'hard': COLORS['red'],
        }
        difficulty_surf = self.fonts['small'].render(
            difficulty_labels.get(difficulty, 'MÉDIA'),
            False,
            difficulty_colors.get(difficulty, COLORS['gold']),
        )
        difficulty_rect = difficulty_surf.get_rect(
            midleft=(rect.left + 16 + cat_surf.get_width() + 10, rect.top + 24)
        )
        self.display_surface.blit(difficulty_surf, difficulty_rect)
        if quiz:
            remaining_ms = max(0, quiz['deadline'] - pygame.time.get_ticks())
            remaining_seconds = (remaining_ms + 999) // 1000
            timer_color = COLORS['red'] if remaining_seconds <= 5 else COLORS['dark']
            timer_surf = self.fonts['small'].render(f'Tempo: {remaining_seconds}s', False, timer_color)
            timer_rect = timer_surf.get_rect(topright = (rect.right - 16, rect.top + 14))
            self.display_surface.blit(timer_surf, timer_rect)

        y = rect.top + 44
        for line in self.wrap_text(question['question'], self.fonts['regular'], width - 32):
            line_surf = self.fonts['regular'].render(line, False, COLORS['black'])
            self.display_surface.blit(line_surf, (rect.left + 16, y))
            y += line_surf.get_height() + 6

        y += 12
        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(question['options']):
            option_rect = pygame.Rect(rect.left + 20, y, width - 40, 32)
            hovered = quiz is not None and option_rect.collidepoint(mouse_pos)
            fill_color = '#fff8e8'
            outline_color = '#9ac9a4'
            option_color = COLORS['dark']
            if feedback and i == question['correct']:
                fill_color = '#d9f7df'
                outline_color = COLORS['green']
                option_color = COLORS['green']
            elif feedback and i == feedback['selected_index']:
                fill_color = '#ffe0df'
                outline_color = COLORS['red']
                option_color = COLORS['red']
            elif hovered:
                fill_color = '#ffe066'
                outline_color = COLORS['gold']
            pygame.draw.rect(self.display_surface, fill_color, option_rect, border_radius=9)
            pygame.draw.rect(self.display_surface, outline_color, option_rect, 2, border_radius=9)
            option_surf = self.fonts['regular'].render(
                f'{chr(65 + i)}. {option}',
                False,
                option_color,
            )
            option_surf = self.fit_text_surface(
                option_surf,
                option_rect.width - 24,
                option_rect.height - 4,
            )
            option_rect_text = option_surf.get_rect(midleft=(option_rect.left + 12, option_rect.centery))
            self.display_surface.blit(option_surf, option_rect_text)
            if quiz:
                self.quiz_option_rects.append((option_rect, i))
            y += 36

        if feedback and feedback['attack'] == 'recover_energy':
            hint = 'Energia recuperada!' if feedback['correct'] else 'Resposta incorreta: energia não recuperada.'
        else:
            hint = 'Preparando o ataque...' if feedback else 'Clique em uma resposta para continuar'
        hint_color = COLORS['green'] if feedback and feedback['correct'] else COLORS['light']
        hint_surf = self.fonts['small'].render(hint, False, hint_color)
        hint_rect = hint_surf.get_rect(midbottom = (rect.centerx, rect.bottom - 10))
        self.display_surface.blit(hint_surf, hint_rect)

    def draw_attacks(self):
        """Desenha até três ataques por página e detalhes do ataque sob o cursor."""
        self.attack_button_rects = []
        self.attack_page_rects = {}
        self.defend_button_rect = None
        abilities = self.current_monster.monster.get_abilities(all = False)
        page_count = max(1, (len(abilities) + 2) // 3)
        self.attack_page %= page_count
        first_index = self.attack_page * 3
        visible_attacks = abilities[first_index:first_index + 3]

        card_width, card_height, gap = 230, 98, 12
        card_top = WINDOW_HEIGHT - card_height - 28
        first_left = 18
        self.recover_energy_button_rect.topleft = (first_left, card_top - 67)
        title = self.fonts['small'].render('ESCOLHA UM ATAQUE', False, COLORS['white'])
        self.display_surface.blit(title, (first_left, card_top - 20))

        if page_count > 1:
            page_text = self.fonts['small'].render(f'{self.attack_page + 1}/{page_count}', False, COLORS['white'])
            page_rect = page_text.get_rect(midright=(first_left + 3 * (card_width + gap) - gap - 54, card_top - 9))
            self.display_surface.blit(page_text, page_rect)
            for direction, label, left in (
                (-1, '<', first_left + 3 * (card_width + gap) - gap - 46),
                (1, '>', first_left + 3 * (card_width + gap) - gap - 20),
            ):
                rect = pygame.Rect(left, card_top - 20, 18, 18)
                pygame.draw.circle(self.display_surface, COLORS['dark'], rect.center, 11)
                pygame.draw.circle(self.display_surface, COLORS['white'], rect.center, 11, 1)
                label_surf = self.fonts['small'].render(label, False, COLORS['white'])
                self.display_surface.blit(label_surf, label_surf.get_rect(center=rect.center))
                self.attack_page_rects[direction] = rect

        mouse_pos = pygame.mouse.get_pos()
        hover_pulse = 0.5 + 0.5 * sin(pygame.time.get_ticks() / 110)
        hovered_ability = None
        for index, ability in enumerate(visible_attacks):
            card_rect = pygame.Rect(
                first_left + index * (card_width + gap),
                card_top,
                card_width,
                card_height,
            )
            element = ATTACK_DATA[ability]['element']
            accent = COLORS.get(element, COLORS['light-gray'])
            hovered = card_rect.collidepoint(mouse_pos)
            lift = 4 + int(hover_pulse * 2) if hovered else 0
            visual_rect = card_rect.move(0, -lift)
            radius = 16
            tail_left = visual_rect.left + 28
            tail_tip = (visual_rect.left + 18, visual_rect.bottom + 12)
            tail_right = visual_rect.left + 54
            tail_outline = [
                (tail_left, visual_rect.bottom - 3),
                tail_tip,
                (tail_right, visual_rect.bottom - 3),
            ]
            pygame.draw.polygon(
                self.display_surface,
                COLORS['dark'],
                [(tail_left + 2, visual_rect.bottom + 3), (tail_tip[0] + 2, tail_tip[1] + 3), (tail_right + 2, visual_rect.bottom + 3)],
            )
            pygame.draw.polygon(
                self.display_surface,
                '#fff8e8',
                [(tail_left, visual_rect.bottom - 4), tail_tip, (tail_right, visual_rect.bottom - 4)],
            )
            pygame.draw.lines(self.display_surface, accent, False, tail_outline, 3)
            pygame.draw.rect(
                self.display_surface,
                COLORS['dark'],
                visual_rect.move(2, 4),
                border_radius=radius,
            )
            pygame.draw.rect(
                self.display_surface,
                COLORS['gold'] if hovered else COLORS['dark'],
                visual_rect.inflate(4, 4),
                border_radius=radius + 2,
            )
            pygame.draw.rect(
                self.display_surface,
                '#fff8e8',
                visual_rect,
                border_radius=radius,
            )
            pygame.draw.rect(
                self.display_surface,
                accent,
                visual_rect,
                width=3,
                border_radius=radius,
            )
            pygame.draw.line(
                self.display_surface,
                '#ffffff',
                (visual_rect.left + 18, visual_rect.top + 7),
                (visual_rect.right - 22, visual_rect.top + 7),
                2,
            )

            attack_label = self.attack_name(ability)
            monster_name = self.current_monster.monster.name if self.current_monster else ''
            if not get_attack_display_name(ability, monster_name):
                attack_label = attack_label.upper()
            name_font = self.fonts['regular']
            if name_font.size(attack_label)[0] > visual_rect.width - 20:
                name_font = self.fonts['small']
            name_surf = name_font.render(attack_label, False, COLORS['dark'])
            name_surf = self.fit_text_surface(
                name_surf,
                visual_rect.width - 20,
                visual_rect.height - 16,
            )
            name_rect = name_surf.get_rect(center=visual_rect.center)
            self.display_surface.blit(name_surf, name_rect)

            if hovered:
                hovered_ability = ability
            self.attack_button_rects.append((card_rect, ability))

        if hovered_ability:
            attack_data = ATTACK_DATA[hovered_ability]
            details_left = first_left + 3 * (card_width + gap) - gap + 20
            details_width = WINDOW_WIDTH - details_left - first_left
            details_rect = pygame.Rect(
                details_left,
                card_top + card_height - 116,
                details_width,
                116,
            )
            accent = COLORS.get(attack_data['element'], COLORS['light-gray'])
            self.draw_panel(details_rect, accent)

            name_surf = self.fonts['regular'].render(
                self.attack_name(hovered_ability),
                False,
                COLORS['dark'],
            )
            name_surf = self.fit_text_surface(
                name_surf,
                details_width - 28,
                24,
            )
            self.display_surface.blit(name_surf, (details_rect.left + 14, details_rect.top + 8))

            description_y = details_rect.top + 34
            for line in self.wrap_text(
                self.attack_description(hovered_ability),
                self.fonts['small'],
                details_width - 28,
            )[:2]:
                line_surf = self.fonts['small'].render(line, False, COLORS['gray'])
                self.display_surface.blit(line_surf, (details_rect.left + 14, description_y))
                description_y += line_surf.get_height() + 2

            base_amount = int(abs(self.current_monster.monster.get_base_damage(hovered_ability)))
            amount_label = 'Cura base estimada' if attack_data['amount'] < 0 else 'Dano base estimado'
            attack_cost = self.current_monster.monster.get_attack_cost(hovered_ability)
            amount_surf = self.fonts['small'].render(
                f'{amount_label}: {base_amount}  |  Gasta: {attack_cost} EP',
                False,
                COLORS['dark'],
            )
            amount_surf = self.fit_text_surface(
                amount_surf,
                details_width - 28,
                18,
            )
            self.display_surface.blit(amount_surf, (details_rect.left + 14, details_rect.bottom - 36))

            note_surf = self.fonts['small'].render(
                'Dano varia conforme elemento, defesa e quiz.',
                False,
                COLORS['gray'],
            )
            note_surf = self.fit_text_surface(
                note_surf,
                details_width - 28,
                18,
            )
            self.display_surface.blit(note_surf, (details_rect.left + 14, details_rect.bottom - 18))

        recover_enabled = self.can_recover_energy()
        recover_hovered = (
            recover_enabled
            and self.recover_energy_button_rect.collidepoint(mouse_pos)
        )
        recover_fill = '#d9f4fb' if recover_enabled else COLORS['light-gray']
        if recover_hovered:
            recover_fill = '#ffe066'
        pygame.draw.rect(
            self.display_surface,
            COLORS['dark'],
            self.recover_energy_button_rect.move(2, 3),
            border_radius=10,
        )
        pygame.draw.rect(
            self.display_surface,
            recover_fill,
            self.recover_energy_button_rect,
            border_radius=10,
        )
        pygame.draw.rect(
            self.display_surface,
            COLORS['blue'] if recover_enabled else COLORS['gray'],
            self.recover_energy_button_rect,
            width=2,
            border_radius=10,
        )
        if recover_enabled:
            recover_surf = self.fonts['small'].render('RECUPERAR ENERGIA', False, COLORS['dark'])
            self.display_surface.blit(
                recover_surf,
                recover_surf.get_rect(center=self.recover_energy_button_rect.center),
            )
        else:
            recover_surf = self.fonts['small'].render('ENERGIA SUFICIENTE', False, COLORS['dark'])
            self.display_surface.blit(
                recover_surf,
                recover_surf.get_rect(center=self.recover_energy_button_rect.center),
            )

        if not abilities:
            self.defend_button_rect = pygame.Rect(first_left, card_top, card_width, card_height)
            pygame.draw.rect(self.display_surface, COLORS['dark'], self.defend_button_rect.move(2, 4), border_radius=16)
            pygame.draw.rect(self.display_surface, '#fff8e8', self.defend_button_rect, border_radius=16)
            pygame.draw.rect(self.display_surface, COLORS['green'], self.defend_button_rect, 3, border_radius=16)
            defend_surf = self.fonts['regular'].render('DEFENDER', False, COLORS['dark'])
            self.display_surface.blit(defend_surf, defend_surf.get_rect(center=self.defend_button_rect.center))
            hint_surf = self.fonts['small'].render('Sem energia para atacar', False, COLORS['white'])
            self.display_surface.blit(hint_surf, hint_surf.get_rect(midtop=(self.defend_button_rect.centerx, self.defend_button_rect.top + 58)))

    def attack_name(self, ability):
        """Converte a chave interna do ataque para o nome exibido em português."""
        monster_name = self.current_monster.monster.name if self.current_monster else ''
        display_name = get_attack_display_name(ability, monster_name)
        if display_name:
            return display_name

        names = {
            'annihilate': 'Ruptura Final',
            'battlecry': 'Rugido Vital',
            'burn': 'Brasas Ferozes',
            'explosion': 'Impacto Meteórico',
            'fire': 'Chama Elemental',
            'heal': 'Pulso Restaurador',
            'ice': 'Lança Glacial',
            'scratch': 'Garra Selvagem',
            'spark': 'Raio Faiscante',
            'splash': 'Maré Crescente',
        }
        return f'{names[ability]} · {monster_name}' if monster_name else names[ability]

    def attack_description(self, ability):
        """Retorna o texto de ajuda exibido ao apontar para um ataque."""
        default_descriptions = {
            'annihilate': 'Explosão colossal que causa dano devastador.',
            'battlecry': 'Uma pausa para respirar e recuperar vida.',
            'burn': 'Uma rajada ardente que queima o alvo.',
            'explosion': 'Uma explosão intensa de dano alto.',
            'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
            'heal': 'Recupera uma grande quantidade de vida.',
            'ice': 'Um disparo de gelo que causa dano.',
            'scratch': 'Um jogo de palavras que afetam o oponente.',
            'spark': 'Uma faísca elétrica certeira.',
            'splash': 'Uma onda poderosa atinge o alvo.',
        }
        element_descriptions = {
            'Linguagem': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Uma pausa para respirar e recuperar vida.',
                'burn': 'Uma rajada ardente que queima o alvo.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Recupera uma grande quantidade de vida.',
                'ice': 'Um disparo de gelo que causa dano.',
                'scratch': 'Um jogo de palavras que afetam o oponente.',
                'spark': 'Uma faísca elétrica certeira.',
                'splash': 'Uma onda poderosa atinge o alvo.',
            },
            'Matemática': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Resoluciona o problema e relaxa a cabeça, recuperando vida.',
                'burn': 'Uma rajada ardente que queima o alvo.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Recupera uma grande quantidade de vida.',
                'ice': 'Um disparo de gelo que causa dano.',
                'scratch': 'Um jogo de palavras que afetam o oponente.',
                'spark': 'Um ataque multiplicado por ele mesmo(seria muito forte, então não seria multiplicado por ele mesmo, mas por um número).',
                'splash': 'Um ataque de tirar uma fração da vida do oponente.',
            },
            'Filosofia': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Para para pensar e pausa para refletir, recuperando vida.',
                'burn': 'Uma rajada ardente que queima o alvo.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Recupera uma grande quantidade de vida.',
                'ice': 'Afirma que sabe de nada, mas sabe que não sabe ao oponente deixando o oponente confuso e atingido pelo raciocíinio.',
                'scratch': 'Um jogo de palavras que afetam o oponente.',
                'spark': 'Reflete tanto que o oponente é atingido pelo pensamento.',
                'splash': 'Um ataque de tirar uma fração da vida do oponente.',
            },
            'Química': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Para para pensar e pausa para refletir, recuperando vida.',
                'burn': 'Substâncias em volta causam reações químicas que encostam no oponente.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Recupera seu estado normal, nem muito elétrico e nem pouco, recuperando vida.',
                'ice': 'Afirma que sabe de nada, mas sabe que não sabe ao oponente deixando o oponente confuso e atingido pelo raciocíinio.',
                'scratch': 'Um jogo de palavras que afetam o oponente.',
                'spark': 'Um dos irritados salta para fora e volta para sua órbita, causando um impulso elétrico no oponente.',
                'splash': 'Um ataque de tirar uma fração da vida do oponente.',
            },
            'Geografia': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Para para pensar e pausa para refletir, recuperando vida.',
                'burn': 'Substâncias em volta causam reações químicas que encostam no oponente.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Se localiza e se acha, recuperando vida.',
                'ice': 'Afirma que sabe de nada, mas sabe que não sabe ao oponente deixando o oponente confuso e atingido pelo raciocíinio.',
                'scratch': 'Uma rajada de vento do norte que atinge o oponente.',
                'spark': 'Folhas voam de oeste ao leste e atacam o oponente.',
                'splash': 'Um ataque de tirar uma fração da vida do oponente.',
            },
            'Artes': {
                'annihilate': 'Explosão colossal que causa dano devastador.',
                'battlecry': 'Reestocar tintas, para pintor ou desenhista, é acalma-o, enchendo seu coração(no caso aqui, recupera vida).',
                'burn': 'Substâncias em volta causam reações químicas que encostam no oponente.',
                'explosion': 'Uma explosão intensa de dano alto.',
                'fire': 'Um ataque com a força de vários do mesmo ataque, como se estivesse em vários.',
                'heal': 'Se localiza e se acha, recuperando vida.',
                'ice': 'Afirma que sabe de nada, mas sabe que não sabe ao oponente deixando o oponente confuso e atingido pelo raciocíinio.',
                'scratch': '"Numa folha qualquer, consigo fazer o sol amarelo" encantar o oponete, e o afetar.',
                'spark': 'Folhas voam de oeste ao leste e atacam o oponente.',
                'splash': 'Um ataque de tirar uma fração da vida do oponente.',
            },
        }
        monster = self.current_monster.monster if self.current_monster else None
        category = ATTACK_NAME_CATEGORIES.get(monster.name) if monster else None
        descriptions = {
            **default_descriptions,
            **element_descriptions.get(category, {}),
        }
        return descriptions.get(ability, '')

    def draw_switch(self):
        """Exibe o menu de troca com vida e energia dos monstros disponíveis."""
        # Dimensões e posição do painel de troca.
        width, height = 300, 320
        visible_monsters = 4
        item_height = height / visible_monsters
        v_offset = 0 if self.indexes['switch'] < visible_monsters else -(self.indexes['switch'] - visible_monsters + 1) * item_height
        anim_offset = vector(0, self.menu_open_offset())
        bg_rect = pygame.FRect((0,0), (width, height)).move_to(midleft = self.current_monster.rect.midright + vector(20,0) + anim_offset)
        self.draw_panel(bg_rect, COLORS['blue'])
        pulse_on = sin(pygame.time.get_ticks() / 160) > 0
        highlight_color = COLORS['gold'] if pulse_on else COLORS['dark white']

        # Lista somente os monstros vivos que não estão ativos em campo.
        active_monsters = [(monster_sprite.index, monster_sprite.monster) for monster_sprite in self.player_sprites]
        self.available_monsters = {index: monster for index, monster in self.monster_data['player'].items() if (index, monster) not in active_monsters and monster.health > 0}

        for index, monster in enumerate(self.available_monsters.values()):
            selected = index == self.indexes['switch']
            item_bg_rect = pygame.FRect((0,0), (width, item_height)).move_to(midleft = (bg_rect.left, bg_rect.top + item_height / 2 + index * item_height + v_offset))

            icon_surf = self.monster_frames['icons'][monster.name]
            icon_rect = get_surface_rect(icon_surf, midleft = bg_rect.topleft + vector(10,item_height / 2 + index * item_height + v_offset))
            text_surf = self.fonts['regular'].render(f'{monster.name} ({monster.level})', False, COLORS['red'] if selected else COLORS['black'])
            text_rect = get_surface_rect(text_surf, topleft = (bg_rect.left + 90, icon_rect.top))

            # Destaca a opção atualmente marcada para troca.
            if selected:
                if item_bg_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(self.display_surface, highlight_color, item_bg_rect, 0, 0, 5, 5)
                elif item_bg_rect.collidepoint(bg_rect.midbottom + vector(0,-1)):
                    pygame.draw.rect(self.display_surface, highlight_color, item_bg_rect, 0, 0, 0, 0, 5, 5)
                else:
                    pygame.draw.rect(self.display_surface, highlight_color, item_bg_rect)

            if bg_rect.collidepoint(item_bg_rect.center):
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect)):
                    self.display_surface.blit(surf, rect)
                health_rect = pygame.FRect((text_rect.bottomleft + vector(0,4)), (100,4))
                energy_rect = pygame.FRect((health_rect.bottomleft + vector(0,2)), (80,4))
                draw_bar(self.display_surface, health_rect, monster.health, monster.get_stat('max_health'), COLORS['red'], COLORS['black'])
                draw_bar(self.display_surface, energy_rect, monster.energy, monster.get_stat('max_energy'), COLORS['blue'], COLORS['black'])

    # tela de vitoria / derrota
    def start_result_screen(self, result):
        """Congela as escolhas e inicializa a apresentação de vitória ou derrota."""
        self.result = result
        self.result_start_time = pygame.time.get_ticks()
        self.result_particles = self.create_result_particles(result)
        self.selection_mode = None
        self.current_monster = None
        self.update_all_monsters('pause')

    def create_result_particles(self, result):
        """Gera partículas com cores adequadas ao resultado da batalha."""
        palette = (COLORS['gold'], COLORS['pure white'], COLORS['blue']) if result == 'victory' else (COLORS['red'], COLORS['gray'], COLORS['light-gray'])
        particles = []
        for _ in range(36):
            particles.append({
                'pos': vector(uniform(0, WINDOW_WIDTH), uniform(-WINDOW_HEIGHT, 0)),
                'vel': vector(uniform(-25, 25), uniform(140, 260)),
                'radius': randint(2, 5) if result == 'victory' else randint(1, 3),
                'color': choice(palette),
            })
        return particles

    def update_result_screen(self, dt):
        """Anima partículas; o resultado permanece até o jogador continuar."""
        for particle in self.result_particles:
            particle['pos'] += particle['vel'] * dt
            if particle['pos'].y > WINDOW_HEIGHT + 20:
                particle['pos'].y = -20
                particle['pos'].x = uniform(0, WINDOW_WIDTH)

    def finish_battle(self):
        """Notifica o jogo e a tela de resultado de que a batalha foi concluída."""
        result = self.result
        self.result = None
        self.end_battle(self.character)
        if self.on_battle_finished:
            self.on_battle_finished(result)

    def draw_result_screen(self):
        """Desenha a tela final, suas partículas e a instrução para continuar."""
        elapsed = pygame.time.get_ticks() - self.result_start_time

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(195, int(elapsed / 3))))
        self.display_surface.blit(overlay, (0, 0))

        for particle in self.result_particles:
            pygame.draw.circle(self.display_surface, particle['color'], (int(particle['pos'].x), int(particle['pos'].y)), particle['radius'])

        is_victory = self.result == 'victory'
        title = 'VITORIA!' if is_victory else 'GAME OVER'
        title_color = COLORS['gold'] if is_victory else COLORS['red']
        subtitle = 'Voce venceu a batalha!' if is_victory else 'Seus monstros foram derrotados...'

        scale = 2.2 + 0.15 * sin(elapsed / 180)
        base_surf = self.fonts['bold'].render(title, True, title_color).convert_alpha()
        size = (max(1, int(base_surf.get_width() * scale)), max(1, int(base_surf.get_height() * scale)))
        big_surf = pygame.transform.smoothscale(base_surf, size)
        shadow_base = self.fonts['bold'].render(title, True, COLORS['black']).convert_alpha()
        shadow_surf = pygame.transform.smoothscale(shadow_base, size)

        rect = big_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 30))
        shadow_rect = rect.move(5, 5)
        self.display_surface.blit(shadow_surf, shadow_rect)
        self.display_surface.blit(big_surf, rect)

        sub_surf = self.fonts['regular'].render(subtitle, False, COLORS['white'])
        sub_rect = sub_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 55))
        self.display_surface.blit(sub_surf, sub_rect)

        if elapsed >= self.result_min_display and int(elapsed / 400) % 2 == 0:
            pygame.draw.rect(
                self.display_surface,
                COLORS['gold'],
                self.result_continue_rect,
                border_radius=12,
            )
            pygame.draw.rect(
                self.display_surface,
                COLORS['dark'],
                self.result_continue_rect,
                width=3,
                border_radius=12,
            )
            prompt_surf = self.fonts['small'].render('CLIQUE PARA CONTINUAR', False, COLORS['dark'])
            prompt_rect = prompt_surf.get_rect(center=self.result_continue_rect.center)
            self.display_surface.blit(prompt_surf, prompt_rect)

    def draw_return_button(self):
        """Desenha discretamente o botão de saída entre as barras de vida."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.return_button_rect.collidepoint(mouse_pos)
        fill_color = COLORS['light'] if hovered else COLORS['dark white']
        pygame.draw.rect(self.display_surface, fill_color, self.return_button_rect, border_radius=8)
        pygame.draw.rect(
            self.display_surface,
            COLORS['light-gray'],
            self.return_button_rect,
            width=1,
            border_radius=8,
        )
        label_surf = self.fonts['small'].render('SAIR', False, COLORS['gray'])
        self.display_surface.blit(
            label_surf,
            label_surf.get_rect(center=self.return_button_rect.center),
        )

    def draw_battle_intro(self):
        """Exibe por instantes o aviso de início da batalha."""
        elapsed = pygame.time.get_ticks() - self.battle_transition_start
        if elapsed >= self.BATTLE_INTRO_DURATION:
            return

        progress = elapsed / self.BATTLE_INTRO_DURATION
        opacity = min(1, progress * 5, (1 - progress) * 5)
        self.battle_intro_overlay.fill((0, 0, 0, int(105 * opacity)))
        self.display_surface.blit(self.battle_intro_overlay, (0, 0))

        banner_rect = pygame.Rect(0, 0, 660, 112)
        banner_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(
            self.display_surface,
            COLORS['dark'],
            banner_rect,
            border_radius=18,
        )
        pygame.draw.rect(
            self.display_surface,
            COLORS['gold'],
            banner_rect,
            width=4,
            border_radius=18,
        )
        title = self.fonts['bold'].render('A BATALHA COMEÇOU!', True, COLORS['gold'])
        title.set_alpha(int(255 * opacity))
        self.display_surface.blit(title, title.get_rect(center=banner_rect.center))

    def update(self, dt):
        """Executa um ciclo: atualiza regras e sprites, depois desenha a batalha."""
        self.check_end_battle()

        if self.result:
            # mantem as animacoes (idle) rodando por baixo da tela de resultado
            self.battle_sprites.update(dt)
            self.update_result_screen(dt)
            self.handle_mouse()
        else:
            # updates (ordem original do jogo: input -> timers -> sprites -> checagem de turno)
            self.input()
            self.handle_mouse()
            self.update_timers()
            if self.awaiting_player_switch:
                self.update_all_monsters('pause')
            self.battle_sprites.update(dt)
            self.update_player_return_animation()
            self.update_quiz_feedback()
            self.check_active()

        # drawing
        self.display_surface.blit(self.bg_surf, (0,0))
        self.battle_sprites.draw(self.current_monster, self.selection_side, self.selection_mode, self.indexes['target'], self.player_sprites, self.opponent_sprites)
        self.draw_player_return_animation()
        self.draw_monster_hud()
        if not self.result and not self.awaiting_player_switch:
            self.draw_team_panel('player')
            self.draw_team_panel('opponent')
        self.draw_ui()

        if self.result:
            self.draw_result_screen()
        self.draw_battle_intro()
        self.draw_return_button()