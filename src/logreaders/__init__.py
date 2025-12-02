from abc import ABC


class Reader(ABC):
    def __init__(self, dir_path: str, mono: float, wall: float):
        self.dir_path = dir_path
        self.mono = mono
        self.wall = wall
    
    @classmethod
    def start(self) -> bool:
        pass
