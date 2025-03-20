import sys
import os
from contextlib import contextmanager
import io
@contextmanager
def temporary_sys_path(new_path):
    original_sys_path = sys.path.copy()
    sys.path.insert(0, new_path)
    try:
        yield
    finally:
        sys.path = original_sys_path

so_path = os.path.join(os.path.dirname(__file__), "isobiscuit_engine")

try:
    with temporary_sys_path(so_path):
        import engine
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