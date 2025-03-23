
import io

try:
    from . import engine
except ImportError as e:
    print("⚠️ Warning: The engine does not work on your machine. You are using the deprecated fallback engine, which may be slower and lack some features. ⚠️")
    from . import _engine_py as engine

class Engine:
    def __init__(self, data_sector, code_sector, mem_sector, zip: io.BytesIO, debug=False, ):
        self.__engine = engine.Engine(data_sector, code_sector, mem_sector, zip, debug)
    def kill(self):
        self.__engine.kill()
    """Run"""
    def run(self):
        return self.__engine.run()