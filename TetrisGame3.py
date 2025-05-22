import pygame
import random
import sys
import json
import os
import math

# --- Funzione per trovare le risorse ---
# Questa funzione è essenziale per far funzionare il gioco dopo che è stato impacchettato.
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for frozen app.
    cx_Freeze puts resources in the same directory as the executable.
    """
    if getattr(sys, "frozen", False):
        # The application is frozen (running as an executable)
        base_path = os.path.dirname(sys.executable)
    else:
        # The application is not frozen (running as a script)
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Costanti ---
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

HIGHSCORE_FILE = "highscores2.json" # Il file JSON verrà creato nella stessa directory dell'eseguibile
MAX_SCORES = 10

SHAPES = [
    [[1, 1, 1, 1]],        # Pezzo I
    [[1, 1], [1, 1]],      # Pezzo O
    [[0, 1, 0], [1, 1, 1]], # Pezzo T
    [[1, 1, 0], [0, 1, 1]], # Pezzo S
    [[0, 1, 1], [1, 1, 0]], # Pezzo Z
    [[1, 0, 0], [1, 1, 1]], # Pezzo L
    [[0, 0, 1], [1, 1, 1]]  # Pezzo J
]

COLORS = [
    (0, 255, 255),  # I - azzurro
    (255, 255, 0),  # O - giallo
    (128, 0, 128),  # T - viola
    (0, 255, 0),    # S - verde
    (255, 0, 0),    # Z - rosso
    (255, 165, 0),  # L - arancione
    (0, 0, 255)     # J - blu
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # --- Carica immagini e suoni usando la funzione resource_path ---
        self.background_image = pygame.image.load(resource_path(os.path.join("image", "sfondo1.jpg"))).convert()
        # Lo sfondo dovrebbe riempire l'intero schermo
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.mixer.init()
        self.line_sound = pygame.mixer.Sound(resource_path(os.path.join("sound", "vie.ogg")))

        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.score_saved = False

        # --- NUOVO: Crea una superficie separata per la griglia di gioco ---
        # Questa superficie conterrà solo la griglia di Tetris stessa
        self.game_surface_width = GRID_WIDTH * CELL_SIZE
        self.game_surface_height = GRID_HEIGHT * CELL_SIZE
        self.game_surface = pygame.Surface((self.game_surface_width, self.game_surface_height), pygame.SRCALPHA) # Usa SRCALPHA per la trasparenza
        # --- FINE NUOVO ---

        highest_score = self.get_highest_score()
        print(f"Punteggio più alto caricato: {highest_score}")
        self.difficolta = min(highest_score // 100, 10)
        print(f"Difficoltà impostata: {self.difficolta}")

        self.riempi_blocchi_difficolta()

        self.next_piece_index = None
        self.next_piece = None
        self.next_color = None
        self.generate_next_piece()
        self.new_piece()
        self.fall_time = 0

        self.fall_speed = max(150, 500 - self.difficolta * 35)
        print(f"Velocità di caduta: {self.fall_speed} ms")

        # --- NUOVA VARIABILE PER LA VISIBILITÀ DELL'ANTEPRIMA ---
        self.show_next_piece_preview = False

    def ask_player_name(self):
        name = ""
        input_active = True
        font = pygame.font.SysFont("Arial", 28)

        while input_active:
            self.screen.fill((0, 0, 0))

            # Prima riga del messaggio
            prompt_line1 = font.render("Game Over!", True, (255, 255, 255))
            # Seconda riga del messaggio
            prompt_line2 = font.render("Inserisci il tuo nome:", True, (255, 255, 255))

            name_text = font.render(name + "|", True, (255, 255, 0))

            # Calcola le posizioni per centrare le righe del prompt
            # Sposta la prima riga un po' più in alto
            self.screen.blit(prompt_line1, (SCREEN_WIDTH // 2 - prompt_line1.get_width() // 2, SCREEN_HEIGHT // 2 - 60)) # Spostato più in alto
            # Sposta la seconda riga in modo che sia sotto la prima
            self.screen.blit(prompt_line2, (SCREEN_WIDTH // 2 - prompt_line2.get_width() // 2, SCREEN_HEIGHT // 2 - 20)) # Sotto la prima riga

            # La riga del nome del giocatore rimane invariata o leggermente più in basso
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20)) # Spostato leggermente più in basso

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode
        return name.strip()

    def get_highest_score(self):
        # Carica i punteggi, che ora sono una lista di dizionari
        scores_data = self.load_highscores()
        print("Scores caricati per highest_score:", scores_data)
        if scores_data:
            # Estrae solo i valori numerici dei punteggi
            numerical_scores = [s['score'] for s in scores_data if isinstance(s, dict) and 'score' in s]
            return max(numerical_scores) if numerical_scores else 0
        return 0

    def load_highscores(self):
        try:
            # CORREZIONE QUI: Rimosso os.path.join("image", ...)
            highscore_file_path = resource_path(HIGHSCORE_FILE)
            print(highscore_file_path)
            with open(highscore_file_path, "r") as f:
                scores = json.load(f)
            # Modifica la verifica per accettare liste di dizionari con chiavi 'name' e 'score'
            if isinstance(scores, list) and all(isinstance(s, dict) and 'name' in s and 'score' in s for s in scores):
                return scores
            else:
                print(f"File highscores2.json contiene dati non validi: {scores}. Verrà resettato.")
                return [] # Restituisci lista vuota se il formato non è corretto
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Errore caricamento highscores: {e}. Il file potrebbe non esistere o essere corrotto.")
            return []

    def riempi_blocchi_difficolta(self):
        if self.difficolta <= 0:
            return

        numero_blocchi = int((GRID_WIDTH * GRID_HEIGHT) * (self.difficolta / 80))

        for _ in range(numero_blocchi):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(GRID_HEIGHT // 2, GRID_HEIGHT - 1)
            if self.grid[y][x] == 0:
                colore_random = random.choice(COLORS)
                self.grid[y][x] = colore_random

    def show_about(self):
        self.screen.fill((0, 0, 0)) # Sfondo nero
        clock = pygame.time.Clock()

        lines = [
            "TETRIS PYTHON",
            "",
            "Autore: ",
            "Vincenzo Scozzaro",
            "Versione: 1.0",
            "",
            "Licenza: GPL",
            "Contatti: ",
            "info@example.com",
            "",
            "", # Aggiungi spazi extra per un effetto migliore
            "",
            "Un'avventura classica",
            "nel mondo dei ",
            "blocchi cadenti!",
            "",
            "",
            "Premi ESC o INVIO",
            "per tornare al menu"
        ]

        # Parametri per l'effetto di scorrimento e prospettiva
        start_y = SCREEN_HEIGHT + 50 # Inizia leggermente sotto lo schermo per un ingresso più morbido
        scroll_speed = 0.5 # Velocità di scorrimento (regola per rallentare o accelerare)
        base_font_size = 40 # Dimensione iniziale del font
        max_font_size = 80 # Dimensione massima che il font può raggiungere
        perspective_factor = 0.005 # Controlla quanto velocemente il testo si "allontana"
        center_x = SCREEN_WIDTH // 2 # Centro orizzontale dello schermo

        font_name = pygame.font.get_default_font() # Usa il font di default di Pygame

        running = True
        current_y_offset = 0 # Offset verticale complessivo dello scorrimento

        while running:
            self.screen.fill((0, 0, 0)) # Pulisci lo schermo ad ogni frame

            # Calcola la posizione iniziale per disegnare il testo
            display_y = start_y + current_y_offset

            for i, line in enumerate(lines):
                # Calcola la posizione y del testo sulla base dell'offset attuale e dello spazio tra le righe
                line_y = display_y + i * 50 # Aumenta lo spazio tra le righe per chiarezza

                # Calcola la distanza dal centro verticale (per la prospettiva)
                # Più una riga è vicina al centro alto dello schermo, più deve essere "piccola" e "lontana"
                distance_from_center_y = (SCREEN_HEIGHT / 2 - line_y)

                # Applica la prospettiva: il testo si rimpicciolisce
                # Per la dimensione del font: più la riga è "lontana" (più alta sullo schermo), più è piccola
                # Limita la dimensione minima del font per non farlo scomparire
                font_size = max(base_font_size - int(abs(distance_from_center_y) * perspective_factor * 2), 16)
                # Aumenta la dimensione massima quando è più vicino alla base
                font_size = min(font_size, max_font_size)

                current_font = pygame.font.SysFont(font_name, int(font_size))

                # Renderizza il testo
                text_surface = current_font.render(line, True, (255, 255, 0)) # Testo giallo per Star Wars

                # Calcola la posizione orizzontale: centrato, senza inclinazione
                text_x = center_x - text_surface.get_width() // 2

                # Disegna il testo sullo schermo
                # Assicurati che il testo sia visibile solo quando è all'interno della finestra
                if -text_surface.get_height() < line_y < SCREEN_HEIGHT:
                    self.screen.blit(text_surface, (int(text_x), int(line_y)))

            pygame.display.flip() # Aggiorna lo schermo
            clock.tick(60) # Limita i frame a 60 FPS

            # Aggiorna l'offset verticale per lo scorrimento
            current_y_offset -= scroll_speed

            # Gestione degli eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                        running = False # Esci dalla schermata About

            # Se tutto il testo è uscito dallo schermo, lo riavvolgi
            total_text_height = len(lines) * 50 # Approssimazione basata su spacing
            if display_y + total_text_height < 0:
                current_y_offset = 0


    def show_menu(self):
        menu_font = pygame.font.SysFont("Arial", 36)
        selected = 0
        options = ["Gioca", "Record", "About"]

        while True:
            self.screen.blit(self.background_image, (0, 0))

            for i, option in enumerate(options):
                color = (255, 0, 0) if i == selected else (255, 255, 255)
                text = menu_font.render(option, True, color)
                text_border = menu_font.render(option, True, (0, 0, 0))

                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                y = SCREEN_HEIGHT // 2 + i * 50

                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(text_border, (x + dx, y + dy))

                self.screen.blit(text, (x, y))

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            return
                        elif selected == 1:
                            self.show_record()
                        elif selected == 2:
                            self.show_about()

    def show_record(self):
        self.screen.fill((0, 0, 0))
        highscores = self.load_highscores() # Carica i punteggi come lista di dizionari

        title = self.font.render("Top 10 Record", True, (255, 255, 0))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Mostra i punteggi estratti dai dizionari
        for i, entry in enumerate(highscores):
            # Assicurati che 'entry' sia un dizionario e contenga 'name' e 'score'
            if isinstance(entry, dict) and 'name' in entry and 'score' in entry:
                text = self.font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, (255, 255, 255))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100 + i * 30))
            else:
                # Gestisci il caso di un record malformato nel file (anche se load_highscores dovrebbe prevenire)
                text = self.font.render(f"{i+1}. Record malformato", True, (255, 100, 100))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100 + i * 30))


        reset_text = self.font.render("D per Resettare i record", True, (200, 0, 0))
        self.screen.blit(reset_text, (SCREEN_WIDTH // 2 - reset_text.get_width() // 2, SCREEN_HEIGHT - 50))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        waiting = False
                    elif event.key == pygame.K_d:
                        pygame.draw.rect(self.screen, (0, 0, 0), (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))
                        confirm_font = pygame.font.Font(None, 36)
                        confirm_text = confirm_font.render("Sei sicuro? S o ESC", True, (255, 0, 0))
                        self.screen.blit(confirm_text, (SCREEN_WIDTH // 2 - confirm_text.get_width() // 2, SCREEN_HEIGHT - 50))
                        pygame.display.flip()

                        confirming = True
                        while confirming:
                            for confirm_event in pygame.event.get():
                                if confirm_event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif confirm_event.type == pygame.KEYDOWN:
                                    if confirm_event.key == pygame.K_s:
                                        # CORREZIONE QUI: Rimosso os.path.join("image", ...)
                                        highscore_file_path = resource_path(HIGHSCORE_FILE)
                                        print(highscore_file_path)
                                        if os.path.exists(highscore_file_path):
                                            os.remove(highscore_file_path)
                                            print("File dei record eliminato.")
                                        else:
                                            print("Il file dei record non esiste.")
                                        confirming = False
                                        waiting = False # esci dalla schermata dei record
                                    elif confirm_event.key == pygame.K_ESCAPE:
                                        confirming = False # annulla l'operazione

    def generate_next_piece(self):
        # Scegli un indice casuale per il prossimo pezzo
        self.next_piece_index = random.randint(0, len(SHAPES) - 1)
        self.next_piece = [row[:] for row in SHAPES[self.next_piece_index]]
        self.next_color = COLORS[self.next_piece_index]

    def new_piece(self):
        # Il pezzo attuale diventa quello che prima era il "prossimo pezzo"
        self.piece_index = self.next_piece_index
        self.piece = [row[:] for row in self.next_piece]
        self.color = self.next_color

        self.piece_x = GRID_WIDTH // 2 - len(self.piece[0]) // 2
        self.piece_y = 0

        # Genera subito il prossimo pezzo per l'anteprima
        self.generate_next_piece()

        if self.check_collision(self.piece, self.piece_x, self.piece_y):
            self.game_over = True

    def check_collision(self, piece, offset_x, offset_y):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    px = offset_x + x
                    py = offset_y + y
                    if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT:
                        return True
                    if py >= 0 and self.grid[py][px]:
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.piece_y + y][self.piece_x + x] = self.color

    def clear_lines(self):
        new_grid = []
        lines_cleared = 0
        for row in self.grid:
            if 0 not in row:
                lines_cleared += 1
            else:
                new_grid.append(row)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0] * GRID_WIDTH)
        if lines_cleared > 0:
            self.line_sound.play()
        self.grid = new_grid
        self.score += lines_cleared ** 2

    def rotate_piece(self):
        rotated = [list(row) for row in zip(*self.piece[::-1])]
        if not self.check_collision(rotated, self.piece_x, self.piece_y):
            self.piece = rotated

    def move_piece(self, dx, dy):
        if not self.check_collision(self.piece, self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy

    def drop_piece(self):
        while not self.check_collision(self.piece, self.piece_x, self.piece_y + 1):
            self.piece_y += 1
        self.merge_piece()
        self.clear_lines()
        self.new_piece()

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell != 0:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, cell, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_piece(self):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((self.piece_x + x) * CELL_SIZE, (self.piece_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.color, rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw_game_over(self):
        game_over_text = "GAME OVER"
        press_r_text = "Press R"

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    border1 = self.font.render(game_over_text, True, (0, 0, 0))
                    border2 = self.font.render(press_r_text, True, (0, 0, 0))
                    self.screen.blit(border1, (SCREEN_WIDTH // 2 - border1.get_width() // 2 + dx,
                                                SCREEN_HEIGHT // 2 - 30 + dy))
                    self.screen.blit(border2, (SCREEN_WIDTH // 2 - border2.get_width() // 2 + dx,
                                                SCREEN_HEIGHT // 2 + 10 + dy))

        text1 = self.font.render(game_over_text, True, (255, 255, 0))
        text2 = self.font.render(press_r_text, True, (0, 255, 0))
        self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    def draw_score(self):
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def draw_next_piece(self):
        PREVIEW_CELL_SIZE = CELL_SIZE // 2

        preview_x_offset = int(SCREEN_WIDTH * 0.78)

        preview_y_offset = 10

        box_width = 4 * PREVIEW_CELL_SIZE
        box_height = 4 * PREVIEW_CELL_SIZE

        pygame.draw.rect(self.screen, (50, 50, 50), (preview_x_offset - 5, preview_y_offset - 5, box_width + 10, box_height + 10), 0)
        pygame.draw.rect(self.screen, (200, 200, 200), (preview_x_offset - 5, preview_y_offset - 5, box_width + 10, box_height + 10), 2)

        next_text = self.font.render("NEXT", True, (255, 255, 255))
        self.screen.blit(next_text, (preview_x_offset + box_width // 2 - next_text.get_width() // 2, preview_y_offset + box_height + 10))

        if self.next_piece:
            piece_w = len(self.next_piece[0])
            piece_h = len(self.next_piece)

            center_x_in_box = (box_width - piece_w * PREVIEW_CELL_SIZE) // 2
            center_y_in_box = (box_height - piece_h * PREVIEW_CELL_SIZE) // 2

            for y, row in enumerate(self.next_piece):
                for x, cell in enumerate(row):
                    if cell:
                        rect_x = preview_x_offset + center_x_in_box + x * PREVIEW_CELL_SIZE
                        rect_y = preview_y_offset + center_y_in_box + y * PREVIEW_CELL_SIZE
                        rect = pygame.Rect(rect_x, rect_y, PREVIEW_CELL_SIZE, PREVIEW_CELL_SIZE)
                        pygame.draw.rect(self.screen, self.next_color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def save_score(self, name, score):
        try:
            # CORREZIONE QUI: Rimosso os.path.join("image", ...)
            highscore_file_path = resource_path(HIGHSCORE_FILE)
            print(highscore_file_path)
            if os.path.exists(highscore_file_path):
                with open(highscore_file_path, "r") as file:
                    highscores = json.load(file)
            else:
                highscores = []
        except (FileNotFoundError, json.JSONDecodeError): # Specificare le eccezioni
            highscores = []

        highscores.append({"name": name, "score": score})
        highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:MAX_SCORES]

        with open(highscore_file_path, "w") as file:
            json.dump(highscores, file, indent=4)

    def run(self):
        self.show_menu()

        while True:
            self.screen.blit(self.background_image, (0, 0))
            self.draw_grid()
            self.draw_piece()
            self.draw_score()

            # --- CONDIZIONE PER DISEGNARE L'ANTEPRIMA ---
            if self.show_next_piece_preview:
                self.draw_next_piece()

            if self.game_over:
                # Chiedi il nome e salva il punteggio una sola volta
                if not self.score_saved:
                    name = self.ask_player_name()
                    self.save_score(name, self.score)
                    self.score_saved = True # Segna che il punteggio è stato salvato

                self.draw_game_over()
                pygame.display.flip() # Aggiorna lo schermo per mostrare il testo di game over

                # Gestione dell'input per riavviare il gioco solo dopo aver mostrato game over
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.__init__() # Reinizializza il gioco
                            self.run() # Riavvia il ciclo principale del gioco
                            return # Esce dalla funzione run corrente per evitare cicli sovrapposti
                self.clock.tick(60) # Continua a tickare anche in game over per gestire input
                continue # Continua il ciclo while True per mostrare Game Over finché non si preme 'R'


            # Logica di gioco normale (solo se game_over è False)
            self.fall_time += self.clock.get_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if not self.game_over: # Assicurati che i controlli funzionino solo in gioco
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.drop_piece()
                        # --- GESTIONE DEL TASTO 'H' ---
                        elif event.key == pygame.K_h:
                            self.show_next_piece_preview = not self.show_next_piece_preview # Inverte lo stato

            if not self.game_over and self.fall_time > self.fall_speed:
                if not self.check_collision(self.piece, self.piece_x, self.piece_y + 1):
                    self.piece_y += 1
                else:
                    self.merge_piece()
                    self.clear_lines()
                    self.new_piece()
                self.fall_time = 0

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    Tetris().run()
