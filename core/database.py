import os
from falkordb import FalkorDB
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    _instance = None

    @classmethod
    def get_client(cls) -> FalkorDB:
        if cls._instance is None:
            host = os.getenv("FALKORDB_HOST", "localhost")
            port = int(os.getenv("FALKORDB_PORT", 6379))
            cls._instance = FalkorDB(host=host, port=port)
        return cls._instance