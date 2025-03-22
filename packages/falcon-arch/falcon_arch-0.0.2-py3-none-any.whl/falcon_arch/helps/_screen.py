import os

def clear():
    """Limpa a tela do terminal dependendo do sistema operacional."""
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)
