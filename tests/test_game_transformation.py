import polars as pl
from dataclasses import dataclass
from unittest.mock import Mock
from src.cs2_analyzer.application.services import GameService
from src.cs2_analyzer.domain.entities import Team, Player, Round


@dataclass
class MockDemo:
    """Mock demo object for testing."""
    header: dict
    t_players: list
    ct_players: list
    rounds: pl.DataFrame
    events: dict
    ticks: pl.DataFrame


def test_build_teams_with_players():
    """Test that teams and players are correctly extracted from demo."""
    # Create mock repository and parser
    mock_repo = Mock()
    mock_parser = Mock()

    service = GameService(mock_repo, mock_parser)

    # Create mock demo with players
    demo = MockDemo(
        header={'map_name': 'de_dust2'},
        t_players=[
            {'steamid': 12345, 'name': 'PlayerT1'},
            {'steamid': 12346, 'name': 'PlayerT2'}
        ],
        ct_players=[
            {'steamid': 67890, 'name': 'PlayerCT1'},
            {'steamid': 67891, 'name': 'PlayerCT2'}
        ],
        rounds=pl.DataFrame(),
        events={},
        ticks=pl.DataFrame()
    )

    teams = service._build_teams(demo)

    assert len(teams) == 2

    # Check T-side team
    t_team = teams[0]
    assert t_team.name == 'Terrorist'
    assert len(t_team.players) == 2
    assert t_team.players[0].steam_id == 12345
    assert t_team.players[0].name == 'PlayerT1'
    assert t_team.players[0].team == 'T'

    # Check CT-side team
    ct_team = teams[1]
    assert ct_team.name == 'Counter-Terrorist'
    assert len(ct_team.players) == 2
    assert ct_team.players[0].steam_id == 67890
    assert ct_team.players[0].name == 'PlayerCT1'
    assert ct_team.players[0].team == 'CT'


def test_build_teams_empty():
    """Test that empty teams are handled correctly."""
    mock_repo = Mock()
    mock_parser = Mock()
    service = GameService(mock_repo, mock_parser)

    demo = MockDemo(
        header={'map_name': 'de_dust2'},
        t_players=[],
        ct_players=[],
        rounds=pl.DataFrame(),
        events={},
        ticks=pl.DataFrame()
    )

    teams = service._build_teams(demo)
    assert len(teams) == 0


def test_build_rounds_with_events():
    """Test that rounds are correctly extracted with events."""
    mock_repo = Mock()
    mock_parser = Mock()
    service = GameService(mock_repo, mock_parser)

    # Create mock demo with rounds
    demo = MockDemo(
        header={'map_name': 'de_dust2'},
        t_players=[],
        ct_players=[],
        rounds=pl.DataFrame({
            'round_num': [1, 2],
            'winner_side': ['t', 'ct']
        }),
        events={
            'player_death': pl.DataFrame({
                'round_num': [1, 1, 2],
                'tick': [100, 200, 150],
                'user_steamid': [12345, 67890, 12345]
            })
        },
        ticks=pl.DataFrame({
            'round_num': [1],
            'tick': [100],
            'player_steamid': [12345],
            'side': ['t'],
            'X': [0],
            'Y': [0],
            'Z': [0],
            'yaw': [0],
            'pitch': [0]
        })
    )

    rounds = service._build_rounds(demo)

    assert len(rounds) == 2

    # Check round 1
    round1 = rounds[0]
    assert round1.round_number == 1
    assert round1.winner == 't'
    assert len(round1.events) == 2
    assert round1.events[0]['event_type'] == 'player_death'
    assert round1.events[0]['tick'] == 100

    # Check round 2
    round2 = rounds[1]
    assert round2.round_number == 2
    assert round2.winner == 'ct'
    assert len(round2.events) == 1


def test_extract_round_positions_sampling():
    """Test that positions are sampled correctly."""
    mock_repo = Mock()
    mock_parser = Mock()
    service = GameService(mock_repo, mock_parser)

    # Create many ticks to test sampling
    ticks_data = []
    for tick_num in range(0, 320, 4):  # 80 ticks
        ticks_data.append({
            'round_num': 1,
            'tick': tick_num,
            'player_steamid': 12345,
            'side': 't',
            'X': tick_num,
            'Y': 0,
            'Z': 0,
            'yaw': 0,
            'pitch': 0
        })

    demo = MockDemo(
        header={'map_name': 'de_dust2'},
        t_players=[],
        ct_players=[],
        rounds=pl.DataFrame(),
        events={},
        ticks=pl.DataFrame(ticks_data)
    )

    positions = service._extract_round_positions(demo, 1)

    # With sample_interval=16, we should get ~1/4 of the ticks
    # 80 unique ticks / 16 = 5 sampled ticks
    assert len(positions) == 5
    assert positions[0]['tick'] == 0
    assert positions[0]['X'] == 0


def test_parse_demo_full_integration():
    """Test full demo parsing integration."""
    mock_repo = Mock()
    mock_parser = Mock()

    # Create complete mock demo with properly structured ticks DataFrame
    mock_parser.parse.return_value = MockDemo(
        header={'map_name': 'de_inferno'},
        t_players=[{'steamid': 111, 'name': 'T1'}],
        ct_players=[{'steamid': 222, 'name': 'CT1'}],
        rounds=pl.DataFrame({
            'round_num': [1],
            'winner_side': ['t']
        }),
        events={},
        ticks=pl.DataFrame({
            'round_num': pl.Series([], dtype=pl.Int64),
            'tick': pl.Series([], dtype=pl.Int64),
            'player_steamid': pl.Series([], dtype=pl.Int64),
            'side': pl.Series([], dtype=pl.Utf8),
            'X': pl.Series([], dtype=pl.Float64),
            'Y': pl.Series([], dtype=pl.Float64),
            'Z': pl.Series([], dtype=pl.Float64),
            'yaw': pl.Series([], dtype=pl.Float64),
            'pitch': pl.Series([], dtype=pl.Float64)
        })
    )

    service = GameService(mock_repo, mock_parser)
    game, demo = service._parse_demo('test.dem')

    assert game.map_name == 'de_inferno'
    assert len(game.teams) == 2
    assert len(game.rounds) == 1
    assert game.rounds[0].round_number == 1
    assert game.rounds[0].winner == 't'
