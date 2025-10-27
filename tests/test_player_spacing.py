from src.cs2_analyzer.application.metrics import calculate_player_spacing
import polars as pl
from dataclasses import dataclass

@dataclass
class MockDemo:
    ticks: pl.DataFrame
    rounds: pl.DataFrame
    tickrate: int

def test_calculate_player_spacing_no_data():
    assert calculate_player_spacing(None, 't') == 0.0
    assert calculate_player_spacing(None, 'ct') == 0.0

def test_calculate_player_spacing():
    # Mock data
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1],
        "tick": [100, 100, 100],
        "side": ["t", "t", "t"],
        "X": [0, 3, 6],
        "Y": [0, 0, 0],
        "Z": [0, 0, 0]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    demo = MockDemo(
        ticks=ticks,
        rounds=rounds,
        tickrate=64
    )

    # Expected result
    # At tick 100, we have three T-side players.
    # P1 at (0,0,0), P2 at (3,0,0), P3 at (6,0,0)
    # Dist P1-P2 = 3
    # Dist P1-P3 = 6
    # Dist P2-P3 = 3
    # Average distance = (3 + 6 + 3) / 3 = 4.0
    expected = 4.0

    assert calculate_player_spacing(demo, 't') == expected