from src.cs2_analyzer.application.metrics import calculate_rotation_timing, calculate_rotation_success_rate, calculate_engagement_success_on_rotation
import polars as pl
from dataclasses import dataclass

@dataclass
class MockDemo:
    ticks: pl.DataFrame
    rounds: pl.DataFrame
    tickrate: int
    bombsite_locations: dict
    events: dict

def test_calculate_rotation_timing_no_data():
    assert calculate_rotation_timing(None) == 0.0

def test_calculate_rotation_timing():
    # Mock data
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1, 1, 1],
        "tick": [100, 110, 120, 130, 140],
        "side": ["ct", "ct", "ct", "ct", "ct"],
        "X": [0, 50, 100, 50, 0],
        "Y": [0, 0, 0, 0, 0],
        "Z": [0, 0, 0, 0, 0],
        "player_steamid": [1, 1, 1, 1, 1]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    bombsite_locations = {
        "A": {"x": 0, "y": 0, "z": 0, "radius": 10},
        "B": {"x": 100, "y": 0, "z": 0, "radius": 10}
    }

    demo = MockDemo(
        ticks=ticks,
        rounds=rounds,
        tickrate=10, # 1 tick per second for simplicity
        bombsite_locations=bombsite_locations,
        events = {}
    )

    # Expected result
    # Player starts at A (tick 100), leaves at tick 110.
    # Enters B at tick 120. Rotation time A->B = 10 ticks = 1 second.
    # Leaves B at tick 130.
    # Enters A at tick 140. Rotation time B->A = 10 ticks = 1 second.
    # Average rotation time = (1 + 1) / 2 = 1.0 seconds.
    expected = 1.0

    assert calculate_rotation_timing(demo) == expected

def test_calculate_rotation_success_rate_no_data():
    assert calculate_rotation_success_rate(None) == 0.0

def test_calculate_rotation_success_rate():
    # Mock data
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1, 1, 1, 1, 1],
        "tick": [100, 110, 120, 130, 140, 150, 160],
        "side": ["ct", "ct", "ct", "ct", "ct", "ct", "ct"],
        "X": [0, 50, 100, 50, 0, 100, 50],
        "Y": [0, 0, 0, 0, 0, 0, 0],
        "Z": [0, 0, 0, 0, 0, 0, 0],
        "player_steamid": [1, 1, 1, 1, 1, 2, 2]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    bombsite_locations = {
        "A": {"x": 0, "y": 0, "z": 0, "radius": 10},
        "B": {"x": 100, "y": 0, "z": 0, "radius": 10}
    }
    
    player_death_events = pl.DataFrame({
        "event_name": ["player_death"],
        "user_steamid": [2],
        "tick": [155] 
    })

    demo = MockDemo(
        ticks=ticks,
        rounds=rounds,
        tickrate=10, # 1 tick per second for simplicity
        bombsite_locations=bombsite_locations,
        events={"player_death": player_death_events}
    )

    # Expected result
    # Player 1: Rotates A -> B (completes at tick 120), and B -> A (completes at tick 140).
    # Player 1 survives for more than 3 seconds after each rotation. Both successful.
    # Player 2: Starts moving from B at tick 150, but dies at tick 155.
    # Player 2 does not complete a rotation.
    # Total rotations = 2, successful rotations = 2.
    # Success rate = 2 / 2 = 1.0
    expected = 1.0

    assert calculate_rotation_success_rate(demo) == expected

def test_calculate_engagement_success_on_rotation_no_data():
    assert calculate_engagement_success_on_rotation(None) == 0.0

def test_calculate_engagement_success_on_rotation():
    # Mock data
    ticks = pl.DataFrame({
        "round_num": [1, 1, 1, 1, 1],
        "tick": [100, 110, 120, 130, 140],
        "side": ["ct", "ct", "ct", "ct", "ct"],
        "X": [0, 50, 100, 50, 0],
        "Y": [0, 0, 0, 0, 0],
        "Z": [0, 0, 0, 0, 0],
        "player_steamid": [1, 1, 1, 1, 1]
    })

    rounds = pl.DataFrame({
        "round_num": [1],
        "freeze_end": [90]
    })

    bombsite_locations = {
        "A": {"x": 0, "y": 0, "z": 0, "radius": 10},
        "B": {"x": 100, "y": 0, "z": 0, "radius": 10}
    }
    
    player_death_events = pl.DataFrame({
        "event_name": ["player_death", "player_death"],
        "user_steamid": [2, 1],
        "attacker_steamid": [1, 3],
        "tick": [115, 135] 
    })

    demo = MockDemo(
        ticks=ticks,
        rounds=rounds,
        tickrate=10,
        bombsite_locations=bombsite_locations,
        events={"player_death": player_death_events}
    )

    # Expected result
    # Player 1: Rotates A -> B (110 -> 120) and B -> A (130 -> 140).
    # During A -> B rotation, at tick 115, player 1 kills player 2. Engagement success.
    # During B -> A rotation, at tick 135, player 1 is killed by player 3. Engagement fail.
    # Total engagements on rotation = 2. Successful engagements = 1.
    # Success rate = 1 / 2 = 0.5
    expected = 0.5

    assert calculate_engagement_success_on_rotation(demo) == expected