import os
from dotenv import load_dotenv, set_key, dotenv_values

class EnvManager:
    def __init__(self, env_path='.env'):
        self.env_path = env_path
        load_dotenv(self.env_path)

    def get(self, key, default=None):
        return os.getenv(key, default)

    def set(self, key, value):
        set_key(self.env_path, key, value)

    def all(self):
        return dotenv_values(self.env_path) 