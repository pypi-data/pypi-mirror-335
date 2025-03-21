import os
import tempfile


class Config:
    _temp_dir = None

    @classmethod
    def get_temp_dir(cls):
        if cls._temp_dir is None:
            cls._temp_dir = os.path.join(tempfile.gettempdir(), 'docsplit')
            os.makedirs(cls._temp_dir, exist_ok=True)
        return cls._temp_dir

    @classmethod
    def set_temp_dir(cls, path):
        cls._temp_dir = path
        os.makedirs(path, exist_ok=True)