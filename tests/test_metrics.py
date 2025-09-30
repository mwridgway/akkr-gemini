from src.cs2_analyzer.application.metrics import calculate_ttfk, calculate_time_to_bomb_plant, calculate_average_death_timestamp

def test_calculate_ttfk():
    events = [
        {"event_name": "round_start"},
        {"event_name": "player_death", "timestamp": 10.5},
        {"event_name": "player_death", "timestamp": 15.2},
    ]
    assert calculate_ttfk(events) == 10.5

def test_calculate_time_to_bomb_plant():
    events = [
        {"event_name": "round_start"},
        {"event_name": "bomb_planted", "timestamp": 30.2},
    ]
    assert calculate_time_to_bomb_plant(events) == 30.2

def test_calculate_average_death_timestamp():
    events = [
        {"event_name": "round_start"},
        {"event_name": "player_death", "timestamp": 10.5},
        {"event_name": "player_death", "timestamp": 15.2},
        {"event_name": "player_death", "timestamp": 20.0},
    ]
    assert calculate_average_death_timestamp(events) == (10.5 + 15.2 + 20.0) / 3
