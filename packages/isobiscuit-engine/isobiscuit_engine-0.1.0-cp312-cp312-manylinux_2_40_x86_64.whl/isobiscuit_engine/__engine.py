import io
import engine


class Engine:
    def __init__(self, data_sector, code_sector, mem_sector, zip: io.BytesIO, debug=False, ):
        self.__engine = engine.Engine(data_sector, code_sector, mem_sector, zip, debug)
    def kill(self):
        self.__engine.kill()
    """Run"""
    def run(self):
        self.__engine.run()