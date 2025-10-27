import argparse
from .application.services import GameService
from .interface_adapters.parquet_repository import ParquetGameRepository

from .application.metrics import calculate_t_side_avg_dist_to_bombsite

def main():
    parser = argparse.ArgumentParser(description="Analyze CS2 demo files.")
    parser.add_argument("file_path", type=str, help="Path to the demo file.")
    args = parser.parse_args()

    game_repository = ParquetGameRepository()
    game_service = GameService(game_repository)

    demo = game_service.process_game(args.file_path)
    avg_dist = calculate_t_side_avg_dist_to_bombsite(demo)
    print(f"T-Side Average Distance to Bombsite: {avg_dist}")

if __name__ == "__main__":
    main()
