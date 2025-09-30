from ..application.interfaces import GameRepository
from ..domain.entities import Game

class ParquetGameRepository(GameRepository):
    def save(self, game: Game) -> None:
        # TODO: Implement Parquet saving logic
        print(f"Saving game {game.map_name} to Parquet")

    def get(self, game_id: str) -> Game:
        # TODO: Implement Parquet loading logic
        print(f"Loading game {game_id} from Parquet")
        return Game(map_name="de_dust2", teams=[], rounds=[])
