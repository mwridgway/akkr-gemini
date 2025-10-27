from pathlib import Path
from typing import Tuple
from .interfaces import GameRepository
from ..domain.entities import Game
from awpy.demo import Demo

class GameService:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    def process_game(self, file_path: str) -> object:
        """Processes a demo file and saves the game data."""
        game, demo = self._parse_demo(file_path)
        self.game_repository.save(game)
        return demo

    def _parse_demo(self, file_path: str) -> Tuple[Game, object]:
        """Parses a demo file and creates a Game entity."""
        demo = Demo(Path(file_path))
        demo.parse()
        # TODO: Transform the parsed data into a Game entity
        game = Game(map_name=demo.header['map_name'], teams=[], rounds=[])
        return game, demo
