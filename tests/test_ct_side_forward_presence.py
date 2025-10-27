from src.cs2_analyzer.application.metrics import calculate_ct_side_forward_presence_count, euclidean_distance
import polars as pl
from dataclasses import dataclass

@dataclass
class MockDemo:
    ticks: pl.DataFrame
    rounds: pl.DataFrame
    tickrate: int
    t_spawn: dict
    ct_spawn: dict

def test_calculate_ct_side_forward_presence_count_no_data():
    assert calculate_ct_side_forward_presence_count(None) == 0.0

def test_calculate_ct_side_forward_presence_count():
    # Mock data
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1],
        "tick": [100, 100, 120],
        "side": ["ct", "ct", "t"],
        "X": [600, 400, 800],
        "Y": [1000, 1000, 1000],
        "Z": [50, 50, 50]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    demo = MockDemo(
        ticks=ticks,
        rounds=rounds,
        tickrate=64,
        t_spawn={"x": 1000, "y": 1000, "z": 50},
        ct_spawn={"x": 0, "y": 1000, "z": 50}
    )

    # Expected result
    # At tick 100, we have two CTs.
    # CT1 at x=600. Dist to CT spawn = 600. Dist to T spawn = 400. Forward.
    # CT2 at x=400. Dist to CT spawn = 400. Dist to T spawn = 600. Not forward.
    # Forward count for round 1 is 1.
    # Average forward count is 1.0
    expected = 1.0

    assert calculate_ct_side_forward_presence_count(demo) == expected