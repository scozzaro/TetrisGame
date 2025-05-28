# TetrisGame
Gioco del Tetris

#per creare l'eseguibile
python setup.py build


La Logica di Gioco - Il Cuore Pulsante del Tetris
La "parte vera" del gioco di Tetris è gestita principalmente da un insieme di funzioni interconnesse che lavorano insieme all'interno del ciclo principale del gioco (run()). Queste funzioni sono responsabili di tutto ciò che rende Tetris riconoscibile: la caduta dei blocchi, la loro manipolazione, la scomparsa delle linee e la gestione della fine del gioco.


1. Generazione e Inizializzazione dei Pezzi
  La nascita di ogni nuovo pezzo è un processo cruciale.
  
  generate_next_piece()
  Questa funzione è semplice ma fondamentale:
  
  Sceglie in modo casuale l'indice del prossimo pezzo (self.next_piece_index) tra le forme (SHAPES) disponibili.
  Crea una copia ([row[:] for row in SHAPES[...]]) della forma del pezzo scelto e la memorizza in self.next_piece. Questo è importante per evitare che le rotazioni del pezzo attuale influenzino la forma di quello successivo.
  Associa il colore corrispondente (self.next_color) dalla lista COLORS.
  new_piece()
  Questa è la funzione che "fa nascere" il pezzo che il giocatore controllerà:
  
  Il pezzo che prima era self.next_piece (quello nell'anteprima) diventa il pezzo corrente (self.piece), con la sua forma e colore.
  Viene posizionato al centro orizzontale della griglia, nella parte superiore (self.piece_y = 0).
  Cruciale: Chiama immediatamente self.generate_next_piece() per preparare il prossimo pezzo che il giocatore vedrà nell'anteprima.
  Esegue un controllo di collisione iniziale. Se il nuovo pezzo collide subito appena generato (significa che la griglia è piena fino in cima), imposta self.game_over = True, terminando la partita.

  
2. Movimento e Rotazione dei Pezzi
  Il giocatore interagisce con i pezzi attraverso queste azioni.
  
  check_collision(piece, offset_x, offset_y)
  Questa è una delle funzioni più importanti del gioco, in quanto determina se un'azione (movimento o rotazione) è valida.
  
  Prende in input una piece (che potrebbe essere il pezzo corrente o una sua versione ruotata/spostata) e le coordinate offset_x, offset_y dove si vorrebbe posizionare il suo "angolo" superiore sinistro.
  Itera su ogni singola "cella" che compone la piece.
  Per ogni cella piena del pezzo, calcola le sue coordinate assolute (px, py) sulla griglia di gioco.
  Esegue i seguenti controlli:
  Collisione con bordi orizzontali: px < 0 (fuori a sinistra) o px >= GRID_WIDTH (fuori a destra).
  Collisione con bordo inferiore: py >= GRID_HEIGHT (fuori dal basso).
  Collisione con blocchi esistenti: Se la cella della griglia alla posizione (py, px) è già occupata da un altro blocco (valore diverso da 0).
  Se anche solo una di queste condizioni è vera per una qualsiasi cella del pezzo, la funzione restituisce True (collisione). Altrimenti, se tutte le celle del pezzo possono essere posizionate senza problemi, restituisce False.
  rotate_piece()
  Permette al giocatore di cambiare l'orientamento del pezzo:
  
  Crea una versione rotated del pezzo corrente. La logica [list(row) for row in zip(*self.piece[::-1])] è un modo Pythonico per ruotare una matrice di 90 gradi in senso orario.
  Prima di applicare la rotazione, verifica una collisione usando self.check_collision() con il pezzo ruotato alle coordinate attuali. Questo impedisce al pezzo di ruotare in posizioni non valide (es. attraverso altri blocchi o fuori dai bordi).
  Se la rotazione è valida, self.piece viene aggiornato con la forma ruotata.
  move_piece(dx, dy)
  Gestisce lo spostamento del pezzo da parte del giocatore:
  
  Prende dx (spostamento orizzontale) e dy (spostamento verticale).
  Anche qui, prima di spostare il pezzo, esegue un controllo di collisione con le nuove coordinate desiderate (self.piece_x + dx, self.piece_y + dy).
  Solo se non c'è collisione, il pezzo viene effettivamente spostato aggiornando self.piece_x e self.piece_y.
  drop_piece()
  Esegue la "caduta istantanea" (Hard Drop):
  
  Utilizza un ciclo while per spostare il pezzo verso il basso (self.piece_y += 1) finché non collide con qualcosa (un altro blocco o il fondo della griglia).
  Una volta che il pezzo si è fermato, chiama self.merge_piece(), self.clear_lines(), e self.new_piece() per bloccare il pezzo, eliminare le linee e generare il successivo.

  
3. Integrazione nella Griglia
  Una volta che un pezzo si è fermato, diventa parte della griglia di gioco.
  
  merge_piece()
  Questo è il passaggio in cui il pezzo "atterra" e diventa parte della griglia:
  
  Itera su tutte le celle del self.piece corrente.
  Per ogni cella piena del pezzo, la sua posizione assoluta sulla griglia (self.piece_y + y, self.piece_x + x) viene aggiornata per contenere il self.color del pezzo. Questo "disegna" il pezzo permanentemente sulla griglia di gioco.
  clear_lines()
  La logica per eliminare le linee complete e aggiornare il punteggio:
  
  Crea una new_grid vuota per costruire la griglia aggiornata.
  Conta lines_cleared.
  Scansiona ogni riga della self.grid esistente:
  Se una riga non contiene 0 (ovvero, è completamente piena di blocchi colorati), significa che è una linea completa. lines_cleared viene incrementato, e questa riga non viene aggiunta a new_grid.
  Se una riga contiene 0 (non è completa), viene aggiunta a new_grid.
  Dopo aver processato tutte le righe, lines_cleared nuove righe vuote ([0] * GRID_WIDTH) vengono inserite all'inizio di new_grid. Questo fa sì che i blocchi al di sopra delle linee eliminate scendano.
  Se lines_cleared > 0, riproduce un suono (self.line_sound.play()) e aggiorna il self.score (con un bonus per più linee eliminate contemporaneamente: lines_cleared ** 2).
  Infine, self.grid viene sostituita con la new_grid pulita.
  
  
4. Gestione del Punteggio e dei Record
  Il sistema di punteggio e il salvataggio dei record sono parte integrante dell'esperienza di gioco.
  
  save_score(name, score)
  Gestisce il salvataggio dei punteggi alti:
  
  Tenta di caricare i punteggi esistenti dal file highscores2.json. Se il file non esiste o è corrotto, parte con una lista vuota.
  Aggiunge il nuovo punteggio (come un dizionario {"name": name, "score": score}) alla lista.
  Ordina la lista dei punteggi in ordine decrescente (reverse=True) e la tronca ai MAX_SCORES (10) record più alti.
  Salva la lista aggiornata nel file JSON.
  load_highscores()
  Questa funzione è l'opposto di save_score:
  
  Tenta di aprire e leggere il file highscores2.json.
  Se il file è trovato e il JSON è valido, restituisce la lista dei record.
  Se il file non esiste, è corrotto o il formato non è corretto, restituisce una lista vuota e stampa un messaggio di errore.
  get_highest_score()
  Utilizzata all'avvio del gioco per determinare la difficoltà iniziale:
  
  Carica tutti i punteggi alti.
  Estrae solo i valori numerici dei punteggi.
  Restituisce il punteggio più alto trovato o 0 se non ci sono record.
  
  
5. Inizializzazione della Difficoltà
  Il gioco si adatta ai progressi del giocatore.
  
  riempi_blocchi_difficolta()
  Questa funzione aggiunge blocchi casuali alla griglia all'inizio di una nuova partita, rendendola più difficile in base al punteggio più alto raggiunto:
  
  Calcola il numero di blocchi da aggiungere in base a self.difficolta (derivata dal punteggio più alto). Più alto è il punteggio, più blocchi vengono aggiunti.
  Aggiunge questi blocchi in posizioni casuali nella parte inferiore della griglia (dalla metà in giù) con colori casuali. Questo riduce lo spazio disponibile e aumenta la sfida.





**Scopo della Funzione check_collision**

La funzione check_collision(self, piece, offset_x, offset_y) ha un ruolo cruciale nel gioco Tetris: determina se un determinato pezzo, posizionato in una specifica coordinata (offset_x, offset_y), si sovrappone a blocchi già presenti nella griglia o supera i bordi della griglia stessa.

Viene chiamata in diverse situazioni:

Quando un pezzo cade: per verificare se il pezzo è arrivato in fondo o ha toccato un altro blocco.
Quando un pezzo si muove lateralmente: per assicurarsi che non esca dai bordi o non si sovrapponga ad altri blocchi.
Quando un pezzo ruota: per vedere se la rotazione è valida, cioè se il pezzo ruotato non finisce fuori dai bordi o dentro altri blocchi.
Quando un nuovo pezzo appare: per controllare subito se il gioco è finito (se il nuovo pezzo collide all'istante).
Come Funziona Passo Dopo Passo
Analizziamo il codice riga per riga:

Python

def check_collision(self, piece, offset_x, offset_y):
    # Itera attraverso le righe e le colonne del pezzo che stai esaminando
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            # Controlla solo i "blocchi attivi" del pezzo (dove cell è 1)
            if cell:
                # Calcola la posizione effettiva (assoluta) del blocco sulla griglia principale
                px = offset_x + x
                py = offset_y + y
                
                # --- Controllo Collisione con i Bordi ---
                # Se il blocco esce dai lati (sinistro o destro) o dal fondo della griglia
                if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT:
                    return True # C'è una collisione
                
                # --- Controllo Collisione con altri Blocchi già presenti ---
                # Importante: py >= 0 serve a ignorare le celle che sono sopra la griglia (y negativa),
                # perché il pezzo inizia a cadere da lì e non deve generare collisioni iniziali.
                # Se la cella della griglia in quella posizione non è vuota (self.grid[py][px] è diverso da 0)
                if py >= 0 and self.grid[py][px]:
                    return True # C'è una collisione
    
    # Se il loop finisce senza trovare collisioni
    return False # Non c'è collisione
Spiegazione Dettagliata:

for y, row in enumerate(piece): e for x, cell in enumerate(row):: Questi due cicli nidificati scorrono attraverso ogni cella del pezzo (piece). piece è una lista di liste che rappresenta la forma del pezzo attuale (es. [[0, 1, 0], [1, 1, 1]] per il pezzo T). y e x sono le coordinate relative all'interno della matrice piece. cell è il valore della cella (1 se c'è un blocco, 0 se è vuota).

if cell:: Questa condizione assicura che il codice all'interno venga eseguito solo se la cella del pezzo che stiamo esaminando contiene effettivamente un blocco (valore 1), ignorando gli spazi vuoti nella forma del pezzo.

px = offset_x + x e py = offset_y + y: Qui avviene la magia. offset_x e offset_y sono le coordinate della posizione in alto a sinistra del pezzo sulla griglia principale. Per ogni singolo blocco (cell) all'interno del pezzo, calcoliamo le sue coordinate (px, py) sulla griglia globale aggiungendo gli offset alle sue coordinate (x, y) relative.

if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT:: Questo è il controllo della collisione con i bordi.

px < 0: Il blocco è uscito dal bordo sinistro.
px >= GRID_WIDTH: Il blocco è uscito dal bordo destro.
py >= GRID_HEIGHT: Il blocco è andato sotto il fondo della griglia. Se una di queste condizioni è vera, significa che il pezzo nella sua posizione proposta si scontra con un bordo, quindi la funzione ritorna immediatamente True.
if py >= 0 and self.grid[py][px]:: Questo è il controllo della collisione con blocchi già presenti.

py >= 0: Questa condizione è fondamentale. I pezzi iniziano la loro caduta con piece_y che può essere 0 o anche negativa (se il pezzo è più alto di 1 blocco e la sua parte superiore è fuori dallo schermo). Non vogliamo che il gioco termini immediatamente se la parte superiore di un pezzo è ancora "nel cielo" ma collide con un blocco in quella posizione fittizia. Quindi, controlliamo solo se py è all'interno della griglia visibile o sotto di essa.
self.grid[py][px]: Se la cella corrispondente nella griglia principale (self.grid) in quella posizione (py, px) contiene già un blocco (cioè il suo valore non è 0), allora c'è una collisione con un blocco esistente. In questo caso, la funzione ritorna True.
return False: Se tutti i blocchi del pezzo sono stati controllati e nessuna delle condizioni di collisione (px < 0, px >= GRID_WIDTH, py >= GRID_HEIGHT, self.grid[py][px]) è stata soddisfatta, significa che il pezzo può essere posizionato in quelle coordinate senza problemi. La funzione ritorna False, indicando "nessuna collisione".

Esempio e Disegno
Immaginiamo una griglia di Tetris semplificata e un pezzo che sta cadendo.

Scenario:

Griglia (self.grid): Supponiamo una piccola porzione di griglia. I numeri rappresentano i colori dei blocchi, 0 indica una cella vuota.

(0,0) (1,0) (2,0) ...
[0, 0, 0, ...]  (Riga 0)
[0, 0, 0, ...]  (Riga 1)
[0, 5, 0, ...]  (Riga 2)  <- C'è un blocco qui
[0, 5, 5, ...]  (Riga 3)
[0, 0, 0, ...]  (Riga 4)
Pezzo (piece): Il pezzo 'I' (linea orizzontale) ruotato di 90 gradi.

[0, 1, 0]
[0, 1, 0]
[0, 1, 0]
[0, 1, 0]
Tentativo di Spostamento:

offset_x = 1 (Posizione iniziale del pezzo a 1 colonna da sinistra)
offset_y = 1 (Posizione iniziale del pezzo a 1 riga dall'alto)
Disegno (Immaginario):

Griglia:
(0,0)   (1,0)   (2,0)   (3,0)
[     ][     ][     ][     ] R0
[     ][     ][ Blocco ][     ] R1  <-- self.grid[1][2] = Colore (un blocco esiste qui)
[     ][     ][     ][     ] R2
[     ][     ][     ][     ] R3


Pezzo (forma I verticale):
  [ ]
  [X]
  [X]
  [X]
  [ ]

Ora, applichiamo la funzione check_collision con piece (la 'I' verticale), offset_x = 1, offset_y = 0.

Processo check_collision:

Il pezzo I ha i blocchi a (1,0), (1,1), (1,2), (1,3) rispetto alla sua propria origine (0,0).

Iterazione 1: Cella del pezzo (0, 1) - Blocco 'X' in alto

x = 1, y = 0, cell = 1
px = offset_x + x = 1 + 1 = 2
py = offset_y + y = 0 + 0 = 0
Controlli:
Bordi: px=2 non è <0 o >=GRID_WIDTH. py=0 non è >=GRID_HEIGHT. OK.
Griglia: py=0 è >=0. self.grid[0][2] è 0 (vuoto). OK.
Iterazione 2: Cella del pezzo (1, 1) - Blocco 'X' successivo

x = 1, y = 1, cell = 1
px = offset_x + x = 1 + 1 = 2
py = offset_y + y = 0 + 1 = 1
Controlli:
Bordi: OK.
Griglia: py=1 è >=0. self.grid[1][2] NON è 0 (contiene un blocco!).
RISULTATO: return True (Collisione rilevata!)
La funzione si fermerebbe qui e tornerebbe True, indicando che il pezzo non può essere posizionato in (1,0) perché collide con il blocco esistente in (2,1) della griglia.

Questo meccanismo permette al gioco di sapere se un'azione (movimento, rotazione o caduta) è valida prima di eseguirla, garantendo che i pezzi non si sovrappongano o escano dai limiti del campo di gioco.
