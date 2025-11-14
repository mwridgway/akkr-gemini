import argparse
from .application.services import GameService
from .application.ingestion import AwpyDemoParser
from .interface_adapters.parquet_repository import ParquetGameRepository

from .application.metrics import calculate_t_side_avg_dist_to_bombsite


def main():
    parser = argparse.ArgumentParser(description="Analyze CS2 demo files.")
    parser.add_argument("file_path", type=str, help="Path to the demo file.")
    args = parser.parse_args()

    print(f"\n=== CS2 Demo Analyzer ===")
    print(f"Processing: {args.file_path}\n")

    # Initialize components
    demo_parser = AwpyDemoParser()
    game_repository = ParquetGameRepository()
    game_service = GameService(game_repository, demo_parser)

    # Process the demo file (parses, transforms to Game entity, saves to Parquet)
    print("Parsing demo file...")
    demo = game_service.process_game(args.file_path)
    print("[OK] Demo parsed and saved to Parquet storage\n")

    # Calculate and display metrics
    print("=== Metrics ===")
    avg_dist = calculate_t_side_avg_dist_to_bombsite(demo)
    print(f"T-Side Average Distance to Bombsite: {avg_dist:.2f}")

    print("\n[OK] Analysis complete!")


if __name__ == "__main__":
    main()
