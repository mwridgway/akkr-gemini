import tempfile
import shutil
from pathlib import Path
from src.cs2_analyzer.interface_adapters.parquet_repository import ParquetGameRepository
from src.cs2_analyzer.domain.entities import Game, Team, Player, Round


def test_save_and_load_game_roundtrip():
    """Test that a game can be saved and loaded correctly."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()

    try:
        repo = ParquetGameRepository(base_path=temp_dir)

        # Create test game
        players_t = [
            Player(steam_id=12345, name='PlayerT1', team='T'),
            Player(steam_id=12346, name='PlayerT2', team='T')
        ]
        players_ct = [
            Player(steam_id=67890, name='PlayerCT1', team='CT'),
            Player(steam_id=67891, name='PlayerCT2', team='CT')
        ]

        teams = [
            Team(name='Terrorist', players=players_t),
            Team(name='Counter-Terrorist', players=players_ct)
        ]

        rounds = [
            Round(
                round_number=1,
                winner='t',
                events=[
                    {'tick': 100, 'event_type': 'player_death', 'user_steamid': 67890}
                ],
                positions=[
                    {'tick': 100, 'player_steamid': 12345, 'side': 't', 'X': 100, 'Y': 200, 'Z': 50, 'yaw': 45, 'pitch': 0}
                ]
            ),
            Round(
                round_number=2,
                winner='ct',
                events=[],
                positions=[]
            )
        ]

        game = Game(map_name='de_dust2', teams=teams, rounds=rounds)

        # Save game
        repo.save(game)

        # Check that parquet files were created
        assert (Path(temp_dir) / 'games.parquet').exists()
        assert (Path(temp_dir) / 'teams.parquet').exists()
        assert (Path(temp_dir) / 'players.parquet').exists()
        assert (Path(temp_dir) / 'rounds.parquet').exists()
        assert (Path(temp_dir) / 'events.parquet').exists()
        assert (Path(temp_dir) / 'positions.parquet').exists()

        # Load all games to get the game_id
        import pandas as pd
        games_df = pd.read_parquet(Path(temp_dir) / 'games.parquet')
        assert len(games_df) == 1
        game_id = games_df.iloc[0]['game_id']

        # Load the game back
        loaded_game = repo.get(game_id)

        # Verify game data
        assert loaded_game.map_name == 'de_dust2'
        assert len(loaded_game.teams) == 2
        assert len(loaded_game.rounds) == 2

        # Verify teams
        assert loaded_game.teams[0].name == 'Terrorist'
        assert len(loaded_game.teams[0].players) == 2
        assert loaded_game.teams[0].players[0].steam_id == 12345
        assert loaded_game.teams[0].players[0].name == 'PlayerT1'

        # Verify rounds
        assert loaded_game.rounds[0].round_number == 1
        assert loaded_game.rounds[0].winner == 't'
        assert len(loaded_game.rounds[0].events) == 1
        assert len(loaded_game.rounds[0].positions) == 1

        # Verify events
        event = loaded_game.rounds[0].events[0]
        assert event['event_type'] == 'player_death'
        assert event['tick'] == 100

        # Verify positions
        position = loaded_game.rounds[0].positions[0]
        assert position['player_steamid'] == 12345
        assert position['X'] == 100

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_save_game_with_no_teams():
    """Test that games with no teams are saved correctly."""
    temp_dir = tempfile.mkdtemp()

    try:
        repo = ParquetGameRepository(base_path=temp_dir)
        game = Game(map_name='de_inferno', teams=[], rounds=[])

        repo.save(game)

        # Verify games table exists
        assert (Path(temp_dir) / 'games.parquet').exists()

        # Teams file should not exist (no data to save)
        # Actually, with current implementation, empty files are not created
        # So we just verify the game was saved
        import pandas as pd
        games_df = pd.read_parquet(Path(temp_dir) / 'games.parquet')
        assert len(games_df) == 1
        assert games_df.iloc[0]['num_teams'] == 0

    finally:
        shutil.rmtree(temp_dir)


def test_save_multiple_games():
    """Test that multiple games can be saved to the same tables."""
    temp_dir = tempfile.mkdtemp()

    try:
        repo = ParquetGameRepository(base_path=temp_dir)

        # Save first game
        game1 = Game(
            map_name='de_dust2',
            teams=[Team(name='T1', players=[Player(steam_id=1, name='P1', team='T')])],
            rounds=[Round(round_number=1, winner='t', events=[], positions=[])]
        )
        repo.save(game1)

        # Save second game
        game2 = Game(
            map_name='de_inferno',
            teams=[Team(name='T2', players=[Player(steam_id=2, name='P2', team='T')])],
            rounds=[Round(round_number=1, winner='ct', events=[], positions=[])]
        )
        repo.save(game2)

        # Verify both games are in the table
        import pandas as pd
        games_df = pd.read_parquet(Path(temp_dir) / 'games.parquet')
        assert len(games_df) == 2
        assert set(games_df['map_name']) == {'de_dust2', 'de_inferno'}

    finally:
        shutil.rmtree(temp_dir)


def test_load_nonexistent_game():
    """Test that loading a nonexistent game raises an error."""
    temp_dir = tempfile.mkdtemp()

    try:
        repo = ParquetGameRepository(base_path=temp_dir)

        # Try to load a game that doesn't exist
        try:
            repo.get('nonexistent-game-id')
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

    finally:
        shutil.rmtree(temp_dir)


def test_save_game_with_complex_events():
    """Test that complex event data is handled correctly."""
    temp_dir = tempfile.mkdtemp()

    try:
        repo = ParquetGameRepository(base_path=temp_dir)

        rounds = [
            Round(
                round_number=1,
                winner='t',
                events=[
                    {
                        'tick': 100,
                        'event_type': 'bomb_planted',
                        'user_steamid': 12345,
                        'site': 'A',
                        'X': 100.5,
                        'Y': 200.5,
                        'Z': 50.0
                    }
                ],
                positions=[]
            )
        ]

        game = Game(map_name='de_mirage', teams=[], rounds=rounds)
        repo.save(game)

        # Load and verify event data
        import pandas as pd
        games_df = pd.read_parquet(Path(temp_dir) / 'games.parquet')
        game_id = games_df.iloc[0]['game_id']

        loaded_game = repo.get(game_id)
        event = loaded_game.rounds[0].events[0]

        assert event['event_type'] == 'bomb_planted'
        assert event['user_steamid'] == 12345
        assert event['site'] == 'A'
        assert event['X'] == 100.5

    finally:
        shutil.rmtree(temp_dir)
