from src.cs2_analyzer.application.metrics import calculate_t_side_avg_dist_to_bombsite
import polars as pl
from dataclasses import dataclass

@dataclass
class MockDemo:
    events: dict
    ticks: pl.DataFrame
    rounds: pl.DataFrame
    tickrate: int

def test_calculate_t_side_avg_dist_to_bombsite_no_data():
    assert calculate_t_side_avg_dist_to_bombsite(None) == 0.0

def test_calculate_t_side_avg_dist_to_bombsite():
    # Mock data
    bomb_planted_events = pl.DataFrame({
        "site": [394, 486],
        "user_X": [100, 200],
        "user_Y": [1000, 1000],
        "user_Z": [50, 50]
    })

    ticks = pl.DataFrame({
        "round_num": [1, 1, 1],
        "tick": [100, 110, 120],
        "side": ["t", "t", "ct"],
        "X": [150, 160, 300],
        "Y": [1000, 1000, 1000],
        "Z": [50, 50, 50]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    demo = MockDemo(
        events={'bomb_planted': bomb_planted_events},
        ticks=ticks,
        rounds=rounds,
        tickrate=64
    )

    # Expected result
    # Player positions at ticks 100, 110 (t-side)
    # Pos1: (150, 1000, 50)
    # Pos2: (160, 1000, 50)
    # Bombsite A: (100, 1000, 50)
    # Bombsite B: (200, 1000, 50)
    # Dist1A = 50, Dist1B = 50. Min = 50
    # Dist2A = 60, Dist2B = 40. Min = 40
    # Average = (50 + 40) / 2 = 45.0
    expected = 45.0

    assert calculate_t_side_avg_dist_to_bombsite(demo) == expected