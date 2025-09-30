import argparse
from .application.services import GameService
from .interface_adapters.parquet_repository import ParquetGameRepository

from .application.metrics import calculate_t_side_avg_dist_to_bombsite

def main():
    file_path = "C:\\dev\\akkr-gemini\\data\\raw\\falcons-vs-vitality-m1-inferno.dem"

    game_repository = ParquetGameRepository()
    game_service = GameService(game_repository)

    demo = game_service.process_game(file_path)
    avg_dist = calculate_t_side_avg_dist_to_bombsite(demo)
    print(f"T-Side Average Distance to Bombsite: {avg_dist}")

if __name__ == "__main__":
    main()
