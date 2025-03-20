import sys
import os
from contextlib import contextmanager

# Kontextmanager, um sys.path temporär zu ändern
@contextmanager
def temporary_sys_path(new_path):
    original_sys_path = sys.path.copy()
    sys.path.insert(0, new_path)  # Füge den neuen Pfad am Anfang hinzu
    try:
        yield  # Der Code innerhalb dieses Blocks wird ausgeführt
    finally:
        sys.path = original_sys_path  # Stelle sys.path wieder her

# Der Pfad zu deiner .so-Datei
so_path = os.path.join(os.path.dirname(__file__), "isobiscuit_engine")

# Temporär sys.path ändern
try:
    with temporary_sys_path(so_path):
        import engine  # Importiere das Cython-Modul (die .so-Datei wird hier geladen)
        print("✅ Engine loaded successfully!")
except ImportError as e:
    from . import _engine_py as engine

class Engine:
    def __init__(self, data_sector, code_sector, mem_sector, zip: io.BytesIO, debug=False, ):
        self.__engine = engine.Engine(data_sector, code_sector, mem_sector, zip, debug)
    def kill(self):
        self.__engine.kill()
    """Run"""
    def run(self):
        return self.__engine.run()