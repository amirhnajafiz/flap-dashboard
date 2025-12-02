from abc import ABC, classmethod


class Parser(ABC):
    def __init__(self, dir_path: str, mono: float, wall: float):
        self.dir_path = dir_path
        self.mono = mono
        self.wall = wall
    
    @classmethod
    def parse(self) -> bool:
        pass
