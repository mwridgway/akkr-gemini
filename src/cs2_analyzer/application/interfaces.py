from typing import Protocol
from ..domain.entities import Game

class GameRepository(Protocol):
    def save(self, game: Game) -> None:
        ...

    def get(self, game_id: str) -> Game:
        ...
