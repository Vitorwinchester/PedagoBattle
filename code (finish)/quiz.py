# -*- coding: utf-8 -*-
"""
Banco de perguntas do quiz de batalha.

Cada pergunta é um dicionário com:
    'category' : 'humanas' ou 'exatas'
    'question' : texto da pergunta
    'options'  : lista com 4 alternativas
    'correct'  : índice (0-3) da alternativa correta

Os bancos gerais preservam as perguntas existentes, enquanto QUIZ_POR_MATERIA
separa as perguntas dos monstros pedagógicos por disciplina. As novas perguntas
foram elaboradas para o 5º e o 6º ano. Durante uma batalha, as perguntas são
sorteadas sem repetição até que o banco da matéria seja percorrido.
"""


QUIZ_EXATAS = [
	# --- EXATAS: conteúdos de matemática e ciências do 5º ao 7º ano ---
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma escola comprou 9 caixas com 24 cadernos cada e distribuiu 37. Quantos sobraram?',
	 'options': ['169', '179', '189', '206'], 'correct': 1},
	{'category': 'exatas', 'question': 'Uma conta de 160 reais recebeu desconto de 15%. Qual foi o valor pago?',
	 'options': ['24 reais', '126 reais', '136 reais', '145 reais'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Um terreno retangular mede 12 m por 7 m. Qual é a diferença entre sua área e seu perímetro?',
	 'options': ['38', '42', '46', '84'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Qual fração é equivalente a 0,375?',
	 'options': ['3/8', '3/5', '5/8', '7/8'], 'correct': 0},
	{'category': 'exatas', 'question': 'Resolva: 5x - 7 = 38.',
	 'options': ['7', '8', '9', '10'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma receita usa 0,75 kg de farinha por bolo. Quantos gramas são necessários para 4 bolos?',
	 'options': ['750 g', '1.500 g', '3.000 g', '4.750 g'], 'correct': 2},
	{'category': 'exatas', 'question': 'Os ângulos de um triângulo medem x, 2x e 3x. Quanto mede o maior ângulo?',
	 'options': ['30 graus', '60 graus', '90 graus', '120 graus'], 'correct': 2},
	{'category': 'exatas', 'question': 'Um triângulo tem base de 14 cm e altura de 9 cm. Qual é sua área?',
	 'options': ['46 cm²', '63 cm²', '126 cm²', '252 cm²'], 'correct': 1},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'O gelo seco passa diretamente do estado sólido para o gasoso. Como se chama essa mudança?',
	 'options': ['Condensação', 'Sublimação', 'Solidificação', 'Fusão'], 'correct': 1},
	{'category': 'exatas', 'question': 'Na fotossíntese, além de água e luz, qual gás é usado para produzir glicose?',
	 'options': ['Oxigênio', 'Nitrogênio', 'Gás carbônico', 'Hidrogênio'], 'correct': 2},
	{'category': 'exatas', 'question': 'Em uma cadeia alimentar, fungos e muitas bactérias atuam principalmente como:',
	 'options': ['Produtores', 'Decompositores', 'Herbívoros', 'Predadores'], 'correct': 1},
	{'category': 'exatas', 'question': 'A Terra gira em torno do próprio eixo. Qual fenômeno esse movimento causa principalmente?',
	 'options': ['As estações do ano', 'As fases da Lua', 'A alternância entre dia e noite', 'O ano bissexto'], 'correct': 2},
	
	# --- EXATAS (matemática, física, química, biologia) ---
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma caixa tem 18 fileiras com 7 livros em cada. Quantos livros há?',
	 'options': ['116', '126', '136', '146'], 'correct': 1},
	{'category': 'exatas', 'question': 'Qual é a raiz quadrada de 144?',
	 'options': ['10', '11', '12', '14'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é (36 dividido por 6) + (3 x 4)?',
	 'options': ['14', '16', '18', '20'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma garrafa tem 2,5 litros. Quantos mililitros isso representa?',
	 'options': ['250 ml', '2.050 ml', '2.500 ml', '25.000 ml'], 'correct': 2},
	{'category': 'exatas', 'question': 'Se 3x + 5 = 26, quanto vale x?',
	 'options': ['6', '7', '8', '9'], 'correct': 1},
	{'category': 'exatas', 'question': 'Qual é a soma dos ângulos internos de um hexágono?',
	 'options': ['360 graus', '540 graus', '720 graus', '900 graus'], 'correct': 2},
	{'category': 'exatas', 'question': 'Um ciclista percorre 45 km em 3 horas. Qual é sua velocidade média?',
	 'options': ['12 km/h', '15 km/h', '18 km/h', '135 km/h'], 'correct': 1},
	{'category': 'exatas', 'question': 'Um produto de 80 reais teve desconto de 25%. Qual é o preço final?',
	 'options': ['20 reais', '55 reais', '60 reais', '65 reais'], 'correct': 2},
	{'category': 'exatas', 'question': 'A Terra leva aproximadamente quanto tempo para dar uma volta ao redor do Sol?',
	 'options': ['24 horas', '30 dias', '365 dias', '12 horas'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 48 dividido pelo resultado de 2 x 3?',
	 'options': ['8', '16', '24', '72'], 'correct': 0},
	{'category': 'exatas', 'question': 'Uma mistura tem 1 parte de sal para 4 partes de água. Em 20 copos, quantos são de sal?',
	 'options': ['4', '5', '16', '19'], 'correct': 1},
	{'category': 'exatas', 'question': 'Qual componente do sangue ajuda principalmente na defesa contra microrganismos?',
	 'options': ['Hemácia', 'Leucócito', 'Plaqueta', 'Plasma'], 'correct': 1},
	]
QUIZ_HUMANAS = [
	# --- HUMANAS (história, geografia, português, filosofia) ---
	{'category': 'humanas', 'question': 'Quantos anos se passaram entre a chegada portuguesa em 1500 e a Independência em 1822?',
	 'options': ['302 anos', '312 anos', '322 anos', '332 anos'], 'correct': 2},
	{'category': 'humanas', 'question': 'Em qual continente fica a França metropolitana?',
	 'options': ['Ásia', 'Europa', 'África', 'América'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual acontecimento ocorreu primeiro?',
	 'options': ['Independência do Brasil', 'Proclamação da República', 'Abolição da escravidão', 'Chegada da família real'], 'correct': 3},
	{'category': 'humanas', 'question': 'Qual continente possui a maior área territorial?',
	 'options': ['África', 'América do Sul', 'Ásia', 'Europa'], 'correct': 2},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'A Segunda Guerra Mundial terminou em 1945. Em que ano começou?',
	 'options': ['1914', '1929', '1939', '1942'], 'correct': 2},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Aristóteles foi professor de qual importante personagem da Antiguidade?',
	 'options': ['Júlio César', 'Alexandre, o Grande', 'Cleópatra', 'Homero'], 'correct': 1},
	{'category': 'humanas', 'question': 'Um navio sai do litoral brasileiro rumo a leste. Qual oceano atravessa primeiro?',
	 'options': ['Pacífico', 'Índico', 'Atlântico', 'Ártico'], 'correct': 2},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Na frase "Marina visitou Recife", quais palavras são substantivos próprios?',
	 'options': ['visitou e Marina', 'Marina e Recife', 'a e Recife', 'visitou e Recife'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Em "O vento sussurrava entre as árvores", qual recurso de linguagem foi usado?',
	 'options': ['Comparação', 'Personificação', 'Ironia', 'Enumeração'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'A capital do Brasil foi transferida do Rio de Janeiro para Brasília em que ano?',
	 'options': ['1945', '1950', '1960', '1964'], 'correct': 2},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual era um dos principais objetivos do Tratado de Tordesilhas?',
	 'options': ['Dividir terras entre Portugal e Espanha', 'Acabar com a escravidão', 'Criar as capitanias', 'Independizar o Brasil'], 'correct': 0},
	{'category': 'humanas', 'question': 'O Cubismo, associado a Picasso, caracteriza-se por representar figuras usando:',
	 'options': ['Formas geométricas e vários pontos de vista', 'Somente paisagens reais', 'Cenas mitológicas em mosaico', 'Cores sem formas'], 'correct': 0},

	
	# --- HUMANAS: conteúdos de língua portuguesa, história e geografia ---
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Na frase "Os pesquisadores analisaram as amostras", qual é o sujeito?',
	 'options': ['As amostras', 'Analisaram', 'Os pesquisadores', 'Pesquisadores analisaram'], 'correct': 2},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Em "As atletas permaneceram confiantes", a palavra "confiantes" é:',
	 'options': ['Um advérbio', 'Um adjetivo', 'Um verbo', 'Um pronome'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Em "Embora estivesse chovendo, o jogo continuou", a palavra "embora" indica:',
	 'options': ['Uma causa', 'Uma conclusão', 'Uma oposição/concessão', 'Uma explicação'], 'correct': 2},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Na frase "Quando chegamos, a aula já havia começado", qual ação aconteceu primeiro?',
	 'options': ['Chegamos', 'A aula começou', 'As duas ao mesmo tempo', 'Nenhuma aconteceu'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual pontuação separa corretamente os itens de uma enumeração?',
	 'options': ['Ponto de interrogação', 'Vírgula', 'Travessão sempre', 'Reticências'], 'correct': 1},
	{'category': 'humanas', 'question': 'Qual região brasileira possui o maior número de estados?',
	 'options': ['Norte', 'Nordeste', 'Centro-Oeste', 'Sul'], 'correct': 1},
	{'category': 'humanas', 'question': 'Uma cidade está ao sul da Linha do Equador e a oeste do Meridiano de Greenwich. Em quais hemisférios está?',
	 'options': ['Norte e oriental', 'Sul e ocidental', 'Sul e oriental', 'Norte e ocidental'], 'correct': 1},
	{'category': 'humanas', 'question': 'Num mapa de escala 1:200.000, 1 cm representa 2 km. Quantos km representam 4,5 cm?',
	 'options': ['4,5 km', '6,5 km', '9 km', '90 km'], 'correct': 2},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Por que muitos povos indígenas viviam em diferentes regiões do território antes de 1500?',
	 'options': ['Formavam uma única sociedade com os mesmos costumes', 'Eram diversos povos com línguas e modos de vida próprios', 'Tinham chegado todos da Europa', 'Viviam somente no litoral'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual evento ocorreu primeiro na história do Brasil?',
	 'options': ['Proclamação da República', 'Lei Áurea', 'Independência', 'Chegada da família real portuguesa'], 'correct': 3},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'A Lei Áurea foi assinada em 1888 e a República foi proclamada em 1889. Qual ocorreu primeiro?',
	 'options': ['A Proclamação da República', 'A assinatura da Lei Áurea', 'Ocorreram no mesmo ano', 'A Independência'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'O Tratado de Tordesilhas estabeleceu uma divisão de territórios entre quais reinos europeus?',
	 'options': ['Portugal e Espanha', 'França e Inglaterra', 'Espanha e Holanda', 'Portugal e Itália'], 'correct': 0},
	]

QUIZ_NOVAS_LINGUAGEM = [
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual é o plural da palavra "animal"?',
	 'options': ['Animales', 'Animais', 'Animalis', 'Animalzes'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual palavra é sinônimo de "alegre"?',
	 'options': ['Feliz', 'Cansado', 'Bravo', 'Quieto'], 'correct': 0},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Quantas sílabas tem a palavra "boneca"?',
	 'options': ['Duas', 'Três', 'Quatro', 'Cinco'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual frase está pontuada corretamente como uma pergunta?',
	 'options': ['Onde fica a biblioteca.', 'Onde fica a biblioteca!', 'Onde fica a biblioteca?', 'Onde, fica a biblioteca'], 'correct': 2},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Na frase "Os alunos chegaram cedo", qual é o verbo?',
	 'options': ['Os', 'Alunos', 'Chegaram', 'Cedo'], 'correct': 2},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Na expressão "flor perfumada", qual palavra é um adjetivo?',
	 'options': ['Flor', 'Perfumada', 'A', 'Na'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual é o infinitivo do verbo "brincaram"?',
	 'options': ['Brincar', 'Brincando', 'Brinquei', 'Brincadeira'], 'correct': 0},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual palavra está escrita corretamente?',
	 'options': ['Canpo', 'Campo', 'Cãpo', 'Camppo'], 'correct': 1},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual pronome pode substituir "Marina e eu" na frase "Marina e eu estudamos"?',
	 'options': ['Nós', 'Eles', 'Ela', 'Vocês'], 'correct': 0},
	{'category': 'humanas', 'subject': 'portugues', 'question': 'Qual é o antônimo de "claro"?',
	 'options': ['Brilhante', 'Escuro', 'Luminoso', 'Branco'], 'correct': 1},
]

QUIZ_NOVAS_MATEMATICA = [
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 348 + 276?',
	 'options': ['514', '614', '624', '634'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 72 dividido por 8?',
	 'options': ['8', '9', '10', '11'], 'correct': 1},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma caixa tem 6 fileiras com 5 lápis em cada. Quantos lápis há?',
	 'options': ['11', '25', '30', '35'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 3/4 de 20?',
	 'options': ['5', '10', '15', '16'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Um retângulo mede 8 cm de comprimento e 5 cm de largura. Qual é seu perímetro?',
	 'options': ['13 cm', '26 cm', '40 cm', '80 cm'], 'correct': 1},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quantos centímetros há em 2,5 metros?',
	 'options': ['25 cm', '205 cm', '250 cm', '2.500 cm'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Uma aula começa às 13h30 e dura 1 hora e 15 minutos. A que horas termina?',
	 'options': ['14h15', '14h30', '14h45', '15h15'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 3,6 + 1,25?',
	 'options': ['4,21', '4,75', '4,85', '5,85'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Quanto é 144 dividido por 12?',
	 'options': ['10', '11', '12', '14'], 'correct': 2},
	{'category': 'exatas', 'subject': 'matematica', 'question': 'Qual número completa a sequência: 4, 8, 12, __?',
	 'options': ['14', '15', '16', '18'], 'correct': 2},
]

QUIZ_NOVAS_HISTORIA_FILOSOFIA = [
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Em que ano o Brasil declarou sua Independência de Portugal?',
	 'options': ['1500', '1822', '1888', '1889'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual documento acabou oficialmente com a escravidão no Brasil em 1888?',
	 'options': ['Constituição de 1824', 'Lei Áurea', 'Tratado de Tordesilhas', 'Carta de Pero Vaz'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual cidade se tornou a capital do Brasil em 1960?',
	 'options': ['Salvador', 'Rio de Janeiro', 'Brasília', 'São Paulo'], 'correct': 2},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual destes objetos pode ajudar um historiador a conhecer o passado?',
	 'options': ['Uma ferramenta antiga', 'Uma nuvem de chuva', 'Uma planta que ainda cresce', 'Uma pedra sem marcas'], 'correct': 0},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Antes da chegada dos portugueses, quem já vivia no território que hoje é o Brasil?',
	 'options': ['Diversos povos indígenas', 'Somente portugueses', 'Somente espanhóis', 'Povos vindos da Antártida'], 'correct': 0},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Qual atividade foi muito importante para a economia colonial no Nordeste do Brasil?',
	 'options': ['Produção de açúcar', 'Fabricação de automóveis', 'Extração de petróleo', 'Construção de aviões'], 'correct': 0},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Na Filosofia, fazer perguntas e buscar razões ajuda principalmente a:',
	 'options': ['Pensar sobre ideias e compreender o mundo', 'Decorar sem entender', 'Impedir conversas', 'Evitar aprender coisas novas'], 'correct': 0},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Em uma conversa filosófica, o que é importante fazer ao ouvir uma opinião diferente?',
	 'options': ['Escutar e pensar nos motivos apresentados', 'Interromper sempre', 'Ignorar a pessoa', 'Mudar de assunto imediatamente'], 'correct': 0},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Uma regra justa para a turma deve:',
	 'options': ['Valer apenas para alguns', 'Ajudar todos a conviver com respeito', 'Impedir que alguém participe', 'Mudar sem explicação'], 'correct': 1},
	{'category': 'humanas', 'subject': 'historia_filosofia', 'question': 'Quando comparamos diferentes explicações para um fato, estamos praticando:',
	 'options': ['Reflexão e pensamento crítico', 'Uma conta de multiplicação', 'Uma brincadeira de adivinhação', 'Uma medição de temperatura'], 'correct': 0},
]

QUIZ_NOVAS_QUIMICA = [
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Qual estado da matéria tem forma e volume próprios?',
	 'options': ['Sólido', 'Líquido', 'Gasoso', 'Vapor'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'A água líquida colocada em um copo muda de forma para acompanhar o recipiente. Qual característica isso mostra?',
	 'options': ['Líquidos têm forma variável', 'Líquidos não têm volume', 'Líquidos são sempre sólidos', 'Líquidos não ocupam espaço'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'O que acontece com a água quando ela congela e vira gelo?',
	 'options': ['Passa do líquido para o sólido', 'Passa do sólido para o líquido', 'Passa do gás para o líquido', 'Passa do líquido para o gás'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Como se chama a passagem da água líquida para o vapor?',
	 'options': ['Fusão', 'Evaporação', 'Solidificação', 'Condensação'], 'correct': 1},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Quando o vapor de água esfria e forma gotinhas, ocorre:',
	 'options': ['Condensação', 'Fusão', 'Combustão', 'Solidificação'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Qual método pode separar pedras maiores misturadas à areia usando uma peneira?',
	 'options': ['Peneiração', 'Evaporação', 'Congelamento', 'Imantação'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Água e óleo formam uma mistura em que é possível ver duas partes. Essa mistura é:',
	 'options': ['Heterogênea', 'Homogênea', 'Um único elemento', 'Um gás puro'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Qual destes materiais costuma se dissolver na água?',
	 'options': ['Açúcar', 'Areia', 'Pedra', 'Óleo'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Quando um cubo de gelo derrete, ele passa do estado:',
	 'options': ['Sólido para o líquido', 'Líquido para o gasoso', 'Gasoso para o sólido', 'Líquido para o sólido'], 'correct': 0},
	{'category': 'exatas', 'subject': 'quimica', 'question': 'Qual exemplo mostra uma mistura homogênea?',
	 'options': ['Água com sal bem dissolvido', 'Água com areia', 'Água e óleo', 'Pedras com folhas'], 'correct': 0},
]

QUIZ_NOVAS_GEOGRAFIA = [
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Em qual continente fica o Brasil?',
	 'options': ['América do Sul', 'Europa', 'Ásia', 'África'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual é o nome da capital do Brasil?',
	 'options': ['Brasília', 'Rio de Janeiro', 'Salvador', 'São Paulo'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual oceano banha a maior parte do litoral do Brasil?',
	 'options': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Em um mapa, para que serve a legenda?',
	 'options': ['Explicar o significado dos símbolos', 'Mostrar a previsão do tempo', 'Medir a temperatura', 'Indicar a hora'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual ponto cardeal fica na direção em que o Sol nasce?',
	 'options': ['Leste', 'Oeste', 'Norte', 'Sul'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual é a maior região do Brasil em tamanho?',
	 'options': ['Norte', 'Sul', 'Sudeste', 'Centro-Oeste'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Como chamamos uma área de terra cercada de água por todos os lados?',
	 'options': ['Ilha', 'Península', 'Vale', 'Planície'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual destas opções é um rio brasileiro muito extenso?',
	 'options': ['Rio Amazonas', 'Rio Tâmisa', 'Rio Sena', 'Rio Nilo'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'O que mostra um mapa físico?',
	 'options': ['Elementos naturais, como rios e montanhas', 'Somente as ruas de uma cidade', 'A lista de moradores', 'Os horários das escolas'], 'correct': 0},
	{'category': 'humanas', 'subject': 'geografia', 'difficulty': 'easy',
	 'question': 'Qual região brasileira fica mais ao sul do país?',
	 'options': ['Sul', 'Norte', 'Nordeste', 'Centro-Oeste'], 'correct': 0},
]

QUIZ_NOVAS_ARTES = [
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'O que é uma colagem?',
	 'options': ['Uma imagem feita juntando materiais, como papéis e tecidos', 'Uma escultura feita apenas de pedra', 'Uma música tocada sem instrumentos', 'Uma dança feita em roda'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'Quais são as três cores primárias usadas na pintura?',
	 'options': ['Vermelho, amarelo e azul', 'Verde, laranja e roxo', 'Preto, branco e cinza', 'Rosa, marrom e verde'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'Qual material é muito usado para desenhar no papel?',
	 'options': ['Lápis de cor', 'Colher de cozinha', 'Chave de metal', 'Copo de vidro'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'O que um ator ou uma atriz faz no teatro?',
	 'options': ['Representa uma personagem', 'Pinta uma parede da escola', 'Constrói um instrumento musical', 'Desenha um mapa'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'Na dança, o corpo é usado principalmente para:',
	 'options': ['Criar movimentos e expressar ideias', 'Medir o tamanho de uma tela', 'Misturar tintas', 'Escrever uma partitura'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'O que é ritmo na música?',
	 'options': ['A organização dos sons e das batidas no tempo', 'A mistura de cores em um desenho', 'O formato de uma escultura', 'A fala de uma personagem'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'Qual destas obras de arte tem forma e volume e pode ser vista de vários lados?',
	 'options': ['Uma escultura', 'Uma canção', 'Um poema falado', 'Uma coreografia'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'Em uma pintura, quais cores costumam ser chamadas de quentes?',
	 'options': ['Vermelho, laranja e amarelo', 'Azul, verde e violeta', 'Preto, branco e cinza', 'Azul, branco e preto'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'O que é um retrato?',
	 'options': ['Uma imagem que representa uma pessoa', 'Uma dança em grupo', 'Um instrumento de sopro', 'Uma peça de teatro sem atores'], 'correct': 0},
	{'category': 'humanas', 'subject': 'artes', 'difficulty': 'easy',
	 'question': 'O que é uma apresentação musical?',
	 'options': ['Uma apresentação em que músicos cantam ou tocam', 'Uma exposição de mapas', 'Uma aula de pintura de esculturas', 'Uma competição de corrida'], 'correct': 0},
]

QUIZ_NOVAS_FILOSOFIA = [
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'O que a Filosofia nos incentiva a fazer?',
	 'options': ['Fazer perguntas e pensar sobre as ideias', 'Aceitar tudo sem pensar', 'Decorar palavras sem entender', 'Parar de conversar'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Quando alguém apresenta uma opinião diferente, o que é respeitoso fazer?',
	 'options': ['Ouvir e pensar no que a pessoa explicou', 'Interromper e gritar', 'Rir da pessoa', 'Ignorar sempre'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Qual atitude ajuda a resolver um desentendimento entre colegas?',
	 'options': ['Conversar e tentar entender os dois lados', 'Espalhar o problema para todos', 'Culpar alguém sem escutar', 'Deixar de falar para sempre'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Uma regra justa para a turma deve:',
	 'options': ['Ajudar todos a conviver com respeito', 'Valer somente para os amigos', 'Impedir algumas pessoas de participar', 'Mudar sem ninguém saber'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'O que significa dar uma razão para a sua opinião?',
	 'options': ['Explicar por que você pensa assim', 'Repetir a opinião mais alta', 'Mudar de assunto', 'Escolher uma resposta ao acaso'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Se encontramos uma informação nova, qual atitude ajuda a pensar melhor?',
	 'options': ['Verificar e comparar as informações', 'Acreditar sem perguntar', 'Esquecer tudo o que sabemos', 'Escolher a resposta mais engraçada'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Por que é importante cumprir uma promessa?',
	 'options': ['Porque ajuda a construir confiança', 'Porque impede qualquer conversa', 'Porque todos devem pensar igual', 'Porque nunca podemos mudar de ideia'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'O que é uma escolha responsável?',
	 'options': ['Pensar nas consequências antes de agir', 'Fazer qualquer coisa sem pensar', 'Deixar sempre outra pessoa escolher', 'Escolher o que prejudica os outros'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Como podemos mostrar respeito por pessoas com costumes diferentes?',
	 'options': ['Escutando e tratando cada pessoa com consideração', 'Fazendo piada dos costumes', 'Dizendo que só um jeito é correto', 'Evitando conhecer outras pessoas'], 'correct': 0},
	{'category': 'humanas', 'subject': 'filosofia', 'difficulty': 'easy',
	 'question': 'Qual pergunta ajuda a refletir sobre a amizade?',
	 'options': ['Como posso ser um bom amigo?', 'Quantas janelas há na escola?', 'Qual é a cor mais rápida?', 'Onde fica o maior planeta?'], 'correct': 0},
]

QUIZ_POR_MATERIA = {
	'Jabu': [
		question for question in QUIZ_HUMANAS
		if question.get('subject') == 'portugues'
	] + QUIZ_NOVAS_LINGUAGEM,
	'Rosial': QUIZ_NOVAS_GEOGRAFIA,
	'Palhetin': QUIZ_NOVAS_ARTES,
	'Equonci': [
		question for question in QUIZ_EXATAS
		if question.get('subject') == 'matematica'
	] + QUIZ_NOVAS_MATEMATICA,
	'Prezen': QUIZ_NOVAS_FILOSOFIA,
	'Triátomo': [
		question for question in QUIZ_EXATAS
		if question.get('subject') == 'quimica'
	] + QUIZ_NOVAS_QUIMICA,
}

QUIZ_QUESTIONS = QUIZ_EXATAS + QUIZ_HUMANAS
# Mantém a divisão de dificuldade já usada pelo quiz e identifica questões
# introdutórias para que crianças também encontrem perguntas fáceis.
for question in QUIZ_EXATAS[:12] + QUIZ_HUMANAS[:12]:
	question['difficulty'] = 'hard'
for question in QUIZ_EXATAS[12:] + QUIZ_HUMANAS[12:]:
	question['difficulty'] = 'medium'
for question in (
	[QUIZ_EXATAS[index] for index in (12, 15, 20, 21, 23)]
	+ [QUIZ_HUMANAS[index] for index in (1, 3, 6, 7, 12, 16, 17)]
):
	question['difficulty'] = 'easy'
