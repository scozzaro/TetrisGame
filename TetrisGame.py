import pygame          # Libreria per creare videogiochi 2D in Python
import random          # Per generare numeri casuali (usato per i pezzi e blocchi casuali)
import sys             # Per uscire dal programma in modo sicuro
import json            # Per gestire salvataggi e letture di file JSON (classifica)
import os              # Per operazioni sul file system (es. verifica esistenza file)
import math            # Per eventuali calcoli matematici (non ancora usato direttamente)

# --- Costanti ---
GRID_WIDTH = 10        # Numero di colonne nella griglia (standard Tetris)
GRID_HEIGHT = 20       # Numero di righe nella griglia
CELL_SIZE = 30         # Dimensione di ogni cella in pixel

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE   # Larghezza della finestra di gioco in pixel
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE # Altezza della finestra di gioco in pixel


HIGHSCORE_FILE = "highscores.json"  # Nome del file per salvare i punteggi
MAX_SCORES = 10                     # Numero massimo di record salvati


SHAPES = [
    [[1, 1, 1, 1]],                  # Pezzo I
    [[1, 1], [1, 1]],                # Pezzo O
    [[0, 1, 0], [1, 1, 1]],          # Pezzo T
    [[1, 1, 0], [0, 1, 1]],          # Pezzo S
    [[0, 1, 1], [1, 1, 0]],          # Pezzo Z
    [[1, 0, 0], [1, 1, 1]],          # Pezzo L
    [[0, 0, 1], [1, 1, 1]]           # Pezzo J
]


COLORS = [
    (0, 255, 255),    # I - azzurro
    (255, 255, 0),    # O - giallo
    (128, 0, 128),    # T - viola
    (0, 255, 0),      # S - verde
    (255, 0, 0),      # Z - rosso
    (255, 165, 0),    # L - arancione
    (0, 0, 255)       # J - blu
]


class Tetris:
    def __init__(self):
        pygame.init()  # Inizializza pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Crea la finestra di gioco
        pygame.display.set_caption("Tetris")  # Titolo della finestra
        self.clock = pygame.time.Clock()  # Oggetto per regolare il frame rate
        self.font = pygame.font.SysFont("Arial", 24)  # Font di base per i testi

         # Caricamento sfondo
        self.background_image = pygame.image.load("image/sfondo1.jpg").convert()  # Carica immagine di sfondo
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scala lo sfondo alla finestra



        pygame.mixer.init()  # Inizializza il sistema audio
        self.line_sound = pygame.mixer.Sound("sound/boss_cry.ogg")  # Carica un suono per la rimozione delle righe


        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]  # Griglia di gioco inizialmente vuota (0 = cella vuota)
        self.score = 0               # Punteggio iniziale
        self.game_over = False      # Flag di fine gioco


        # Imposta difficoltà in base al punteggio massimo
        highest_score = self.get_highest_score()  # Recupera il punteggio più alto
        print(highest_score)
        self.difficolta = min(highest_score // 100, 10)  # Calcola la difficoltà: massimo 10
        print("difficoltà")
        print(self.difficolta) 

        
        self.riempi_blocchi_difficolta()  # Riempie la griglia con blocchi casuali in base alla difficoltà



        self.new_piece()           # Genera il primo pezzo
        self.fall_time = 0        # Tempo accumulato per far cadere il pezzo

        #self.fall_speed = 500  # millisecondi
        # Più alta è la difficoltà, più veloce è la caduta (minore il tempo tra un passo e l'altro)
        # Difficoltà 0 => 500ms, difficoltà 10 => 150ms (più difficile)

        self.fall_speed = max(150, 500 - self.difficolta * 35)  # Velocità di caduta: più alta la difficoltà, più veloce
        print(f"Velocità di caduta: {self.fall_speed} ms")




    def get_highest_score(self):
        try:
            with open(HIGHSCORE_FILE, "r") as file:  # Apre il file dei punteggi
                highscores = json.load(file)         # Carica i dati JSON
            return max(highscores) if highscores else 0  # Ritorna il punteggio massimo, o 0 se vuoto
        except (FileNotFoundError, json.JSONDecodeError):
            return 0  # Se il file non esiste o è danneggiato, ritorna 0



    def riempi_blocchi_difficolta(self):
        if self.difficolta <= 0:
            return  # Se difficoltà zero, non fa nulla

        numero_blocchi = int((GRID_WIDTH * GRID_HEIGHT) * (self.difficolta / 80))  # Calcola quanti blocchi casuali inserire


        for _ in range(numero_blocchi):
            x = random.randint(0, GRID_WIDTH - 1)  # Posizione x casuale
            y = random.randint(GRID_HEIGHT // 2, GRID_HEIGHT - 1)  # y solo nella metà bassa della griglia
            if self.grid[y][x] == 0:  # Se cella vuota
                colore_random = random.choice(COLORS)  # Colore casuale
                self.grid[y][x] = colore_random  # Inserisce blocco colorato nella griglia


    def show_about(self):
        self.screen.fill((0, 0, 0))  # Sfondo nero
        clock = pygame.time.Clock()

        lines = [
            "TETRIS PYTHON",
            "Autore: Vincenzo Scozzaro",
            "Versione: 1.0",
            "Licenza: GPL",
            "Contatti: info@example.com",
            "",
            "Premi ESC o Invio per tornare"
        ]

        # Impostazioni per animazione
        start_y = SCREEN_HEIGHT
        spacing = 40
        speed = 1.2  # Velocità di scorrimento
        base_font_size = 36
        min_font_size = 16

        # Carica font generico
        font_name = pygame.font.get_default_font()

        running = True
        while running:
            self.screen.fill((0, 0, 0))
            y = start_y
            for i, line in enumerate(lines):
                # Diminuisce la dimensione del font man mano che sale (simula prospettiva)
                scale = max(min_font_size, base_font_size - int((SCREEN_HEIGHT - y) * 0.03))
                font = pygame.font.SysFont(font_name, scale)
                text = font.render(line, True, (255, 255, 0))
                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                self.screen.blit(text, (x, int(y)))
                y += spacing

            pygame.display.flip()
            clock.tick(60)
            start_y -= speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                        running = False

            # Quando tutte le righe sono uscite dallo schermo, riavvolgi
            if y < 0:
                start_y = SCREEN_HEIGHT


    def show_about_old(self):
        self.screen.fill((0, 0, 0))

        lines = [
            "TETRIS PYTHON",
            "Autore: Vincenzo Scozzaro",
            "Versione: 1.0",
            "Licenza: GPL",
            "Contatti: info@example.com",  # opzionale
            "",
            "Premi ESC o Invio per tornare"
        ]

        for i, line in enumerate(lines):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (
                SCREEN_WIDTH // 2 - text.get_width() // 2,
                80 + i * 30
            ))

        pygame.display.flip()

        # Attende pressione di un tasto per uscire
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                        waiting = False
                    

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

                # BORDO spesso (8 direzioni)
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(text_border, (x + dx, y + dy))

                # Testo principale
                self.screen.blit(text, (x, y))

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() 
                elif event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE or  event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit() 
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:  # Gioca
                            return  # esce dal menu per iniziare il gioco
                        elif selected == 1:  # Record
                            self.show_record()
                        elif selected == 2:  # About
                            self.show_about()


    def show_record(self):
        self.screen.fill((0, 0, 0))
        highscores = self.load_highscores()
        
        title = self.font.render("Top 10 Record", True, (255, 255, 0))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        for i, score in enumerate(highscores):
            text = self.font.render(f"{i+1}. {score}", True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100 + i * 30))

        # Aggiunta della scritta in basso
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
                         # Cancella l'area in basso
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
                                        if os.path.exists(HIGHSCORE_FILE):
                                            os.remove(HIGHSCORE_FILE)
                                            print("File dei record eliminato.")
                                        else:
                                            print("Il file dei record non esiste.")
                                        confirming = False
                                        waiting = False  # esci dalla schermata dei record
                                    elif confirm_event.key == pygame.K_ESCAPE:
                                        confirming = False  # annulla l'operazione




    def new_piece(self):
        self.piece_index = random.randint(0, len(SHAPES) - 1)
        self.piece = [row[:] for row in SHAPES[self.piece_index]]
        self.color = COLORS[self.piece_index]
        self.piece_x = GRID_WIDTH // 2 - len(self.piece[0]) // 2
        self.piece_y = 0

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
                    pygame.draw.rect(self.screen, cell, rect)                 # disegna il blocco
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)         # disegna bordo


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
 
        # Render del bordo (testo nero intorno al testo principale rosso)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    # Bordi neri
                    border1 = self.font.render(game_over_text, True, (0, 0, 0))
                    border2 = self.font.render(press_r_text, True, (0, 0, 0))
                    self.screen.blit(border1, (SCREEN_WIDTH // 2 - border1.get_width() // 2 + dx,
                                            SCREEN_HEIGHT // 2 - 30 + dy))
                    self.screen.blit(border2, (SCREEN_WIDTH // 2 - border2.get_width() // 2 + dx,
                                            SCREEN_HEIGHT // 2 + 10 + dy))

        # Testo principale rosso
        text1 = self.font.render(game_over_text, True, (255, 255, 0))
        text2 = self.font.render(press_r_text, True, (0, 255, 0))
        self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 10))


    def draw_score(self):
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def load_highscores(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_highscore(self):
        highscores = self.load_highscores()
        highscores.append(self.score)
        highscores = sorted(highscores, reverse=True)[:MAX_SCORES]
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(highscores, f)


    def run(self):
        self.show_menu()  # mostra il menu prima di iniziare il gioco

        while True:
            self.screen.blit(self.background_image, (0, 0))
            self.draw_grid()
            self.draw_piece()
            self.draw_score()

            if self.game_over:
                self.draw_game_over()
                if not hasattr(self, 'score_saved'):
                    self.save_highscore()
                    self.score_saved = True
                
                highest_score = self.get_highest_score()
                print(highest_score)
                self.difficolta = min(highest_score // 100, 10)
                print("difficoltà")
                print(self.difficolta) 

            pygame.display.flip()
            self.clock.tick(60)
            self.fall_time += self.clock.get_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.__init__()
                            self.run()
                            return
                    else:
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

            if not self.game_over and self.fall_time > self.fall_speed:
                if not self.check_collision(self.piece, self.piece_x, self.piece_y + 1):
                    self.piece_y += 1
                else:
                    self.merge_piece()
                    self.clear_lines()
                    self.new_piece()
                self.fall_time = 0



if __name__ == "__main__":
    Tetris().run()
