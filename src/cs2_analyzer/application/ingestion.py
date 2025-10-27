from typing import Protocol, Any
from pathlib import Path
from awpy.demo import Demo


class DemoParser(Protocol):
    """Protocol for demo file parsers."""

    def parse(self, file_path: str) -> Any:
        """
        Parse a demo file and return a demo object.

        Args:
            file_path: Path to the demo file

        Returns:
            Parsed demo object with game data
        """
        ...


class AwpyDemoParser:
    """Demo parser implementation using the awpy library."""

    def parse(self, file_path: str) -> Demo:
        """
        Parse a CS2 demo file using awpy.

        Args:
            file_path: Path to the .dem file

        Returns:
            awpy Demo object with parsed game data including:
                - ticks: DataFrame with tick-level player positions
                - events: Dict of event DataFrames (bomb_planted, player_death, etc.)
                - rounds: DataFrame with round metadata
                - header: Dict with map name and other metadata
                - tickrate: Server tickrate
                - t_players, ct_players: Player lists
                - bombsite_locations: Dict with site coordinates
        """
        demo = Demo(Path(file_path))
        demo.parse()
        return demo
