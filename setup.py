import sys
from cx_Freeze import setup, Executable

# Definisci le cartelle delle risorse che vuoi includere.
# Ogni tupla è (percorso_sorgente, percorso_destinazione_nella_build)
# I percorsi sorgente sono relativi al setup.py
# I percorsi destinazione sono relativi alla root della cartella di output (es. build/exe.win-amd64-3.x/)
includefiles = [
    ("image", "image"),  # Copia la cartella 'image' nella sottocartella 'image' della build
    ("sound", "sound"),   # Copia la cartella 'sound' nella sottocartella 'sound' della build
    ("highscores2.json", "highscores2.json") # Includi il file highscores se esiste, altrimenti verrà creato
]

# Imposta la base per l'eseguibile:
# "Win32GUI" è per applicazioni con GUI (non mostra la console).
# Lascia 'None' per applicazioni a riga di comando (mostra la console).
base = None
if sys.platform == "win32":
    base = "Win32GUI" # Per un gioco Pygame, vogliamo nascondere la console

# Opzioni per la build di cx_Freeze
options = {
    'build_exe': {
        'include_files': includefiles,
        # 'packages': ['pygame'], # Aggiungi qui pacchetti che cx_Freeze potrebbe non rilevare automaticamente. Pygame di solito va bene.
        'excludes': ['tkinter', 'unittest', 'pydoc', 'asyncio', 'email', 'html', 'http', 'xml', 'socket', 'test'], # Escludi moduli non necessari per ridurre le dimensioni
        'include_msvcr': True, # Fondamentale su Windows: include le DLL di runtime di Visual C++
    }
}

# Definizione dell'eseguibile
executables = [
    Executable(
        "tetrisgame4.py",       # Il tuo script Python principale
        base=base,              # Il tipo di base (GUI o console)
        target_name="tetrisgame.exe" # Il nome che avrà il tuo file .exe
        , icon="tetris_15552.ico"        # OPZIONALE: Percorso di un file .ico per l'icona dell'eseguibile
                                # Assicurati che 'icona.ico' esista nella stessa directory di setup.py
    )
]

# Configurazione finale del setup
setup(
    name = "TetrisGame",
    version = "4.0",
    description = "Il mio gioco Tetris in Python",
    options = options,
    executables = executables
)