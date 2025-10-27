from pathlib import Path
from typing import List
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import uuid
from datetime import datetime

from ..application.interfaces import GameRepository
from ..domain.entities import Game, Team, Player, Round


class ParquetGameRepository(GameRepository):
    """
    Repository implementation using Apache Parquet for storage.
    Implements a normalized schema with 6 tables for OLAP optimization.
    """

    def __init__(self, base_path: str = "data/processed"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, game: Game) -> None:
        """
        Save a Game entity to normalized Parquet tables.

        Tables created:
        - games.parquet: Game metadata
        - teams.parquet: Team information
        - players.parquet: Player information
        - rounds.parquet: Round metadata
        - events.parquet: All game events
        - positions.parquet: Player position data
        """
        # Generate unique game_id
        game_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # 1. Save game metadata
        self._save_game_metadata(game_id, game, timestamp)

        # 2. Save teams
        self._save_teams(game_id, game.teams)

        # 3. Save players
        self._save_players(game_id, game.teams)

        # 4. Save rounds
        self._save_rounds(game_id, game.rounds)

        # 5. Save events
        self._save_events(game_id, game.rounds)

        # 6. Save positions
        self._save_positions(game_id, game.rounds)

        print(f"Saved game {game_id} ({game.map_name}) to Parquet storage")

    def get(self, game_id: str) -> Game:
        """
        Load a Game entity from Parquet tables by game_id.

        Reconstructs the full Game entity from normalized tables.
        """
        # 1. Load game metadata
        games_df = self._load_table('games')
        if games_df.empty or game_id not in games_df['game_id'].values:
            raise ValueError(f"Game {game_id} not found")

        game_row = games_df[games_df['game_id'] == game_id].iloc[0]
        map_name = game_row['map_name']

        # 2. Load teams
        teams = self._load_teams(game_id)

        # 3. Load rounds
        rounds = self._load_rounds(game_id)

        return Game(map_name=map_name, teams=teams, rounds=rounds)

    def _save_game_metadata(self, game_id: str, game: Game, timestamp: str) -> None:
        """Save game metadata to games.parquet."""
        game_data = {
            'game_id': [game_id],
            'map_name': [game.map_name],
            'timestamp': [timestamp],
            'num_teams': [len(game.teams)],
            'num_rounds': [len(game.rounds)]
        }

        df = pd.DataFrame(game_data)
        self._append_to_table('games', df)

    def _save_teams(self, game_id: str, teams: List[Team]) -> None:
        """Save teams to teams.parquet."""
        if not teams:
            return

        team_data = []
        for idx, team in enumerate(teams):
            team_data.append({
                'team_id': f"{game_id}_team_{idx}",
                'game_id': game_id,
                'name': team.name,
                'num_players': len(team.players)
            })

        df = pd.DataFrame(team_data)
        self._append_to_table('teams', df)

    def _save_players(self, game_id: str, teams: List[Team]) -> None:
        """Save players to players.parquet."""
        if not teams:
            return

        player_data = []
        for team_idx, team in enumerate(teams):
            team_id = f"{game_id}_team_{team_idx}"
            for player in team.players:
                player_data.append({
                    'player_id': f"{team_id}_player_{player.steam_id}",
                    'team_id': team_id,
                    'game_id': game_id,
                    'steam_id': player.steam_id,
                    'name': player.name,
                    'team': player.team
                })

        df = pd.DataFrame(player_data)
        self._append_to_table('players', df)

    def _save_rounds(self, game_id: str, rounds: List[Round]) -> None:
        """Save rounds to rounds.parquet."""
        if not rounds:
            return

        round_data = []
        for round_obj in rounds:
            round_data.append({
                'round_id': f"{game_id}_round_{round_obj.round_number}",
                'game_id': game_id,
                'round_number': round_obj.round_number,
                'winner': round_obj.winner,
                'num_events': len(round_obj.events) if round_obj.events else 0,
                'num_positions': len(round_obj.positions) if round_obj.positions else 0
            })

        df = pd.DataFrame(round_data)
        self._append_to_table('rounds', df)

    def _save_events(self, game_id: str, rounds: List[Round]) -> None:
        """Save all events to events.parquet."""
        if not rounds:
            return

        event_data = []
        for round_obj in rounds:
            round_id = f"{game_id}_round_{round_obj.round_number}"
            if not round_obj.events:
                continue

            for event_idx, event in enumerate(round_obj.events):
                event_entry = {
                    'event_id': f"{round_id}_event_{event_idx}",
                    'round_id': round_id,
                    'game_id': game_id,
                    'tick': event.get('tick'),
                    'event_type': event.get('event_type'),
                }
                # Store additional event data as JSON-serializable fields
                for key, value in event.items():
                    if key not in ['tick', 'event_type']:
                        # Convert to string if not a primitive type
                        if isinstance(value, (int, float, str, bool, type(None))):
                            event_entry[key] = value
                        else:
                            event_entry[key] = str(value)

                event_data.append(event_entry)

        if event_data:
            df = pd.DataFrame(event_data)
            self._append_to_table('events', df)

    def _save_positions(self, game_id: str, rounds: List[Round]) -> None:
        """Save position data to positions.parquet."""
        if not rounds:
            return

        position_data = []
        for round_obj in rounds:
            round_id = f"{game_id}_round_{round_obj.round_number}"
            if not round_obj.positions:
                continue

            for pos_idx, position in enumerate(round_obj.positions):
                position_data.append({
                    'position_id': f"{round_id}_pos_{pos_idx}",
                    'round_id': round_id,
                    'game_id': game_id,
                    'tick': position.get('tick'),
                    'player_steamid': position.get('player_steamid'),
                    'side': position.get('side'),
                    'X': position.get('X'),
                    'Y': position.get('Y'),
                    'Z': position.get('Z'),
                    'yaw': position.get('yaw'),
                    'pitch': position.get('pitch')
                })

        if position_data:
            df = pd.DataFrame(position_data)
            self._append_to_table('positions', df)

    def _append_to_table(self, table_name: str, df: pd.DataFrame) -> None:
        """Append DataFrame to a Parquet table file."""
        table_path = self.base_path / f"{table_name}.parquet"

        if table_path.exists():
            # Read existing table and append
            existing_df = pd.read_parquet(table_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_parquet(table_path, engine='pyarrow', index=False)
        else:
            # Create new table
            df.to_parquet(table_path, engine='pyarrow', index=False)

    def _load_table(self, table_name: str) -> pd.DataFrame:
        """Load a Parquet table."""
        table_path = self.base_path / f"{table_name}.parquet"

        if not table_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(table_path)

    def _load_teams(self, game_id: str) -> List[Team]:
        """Load teams for a game."""
        teams_df = self._load_table('teams')
        players_df = self._load_table('players')

        if teams_df.empty:
            return []

        game_teams_df = teams_df[teams_df['game_id'] == game_id]
        teams = []

        for _, team_row in game_teams_df.iterrows():
            team_id = team_row['team_id']

            # Load players for this team
            team_players_df = players_df[players_df['team_id'] == team_id]
            players = []

            for _, player_row in team_players_df.iterrows():
                player = Player(
                    steam_id=int(player_row['steam_id']),
                    name=player_row['name'],
                    team=player_row['team']
                )
                players.append(player)

            team = Team(name=team_row['name'], players=players)
            teams.append(team)

        return teams

    def _load_rounds(self, game_id: str) -> List[Round]:
        """Load rounds for a game."""
        rounds_df = self._load_table('rounds')
        events_df = self._load_table('events')
        positions_df = self._load_table('positions')

        if rounds_df.empty:
            return []

        game_rounds_df = rounds_df[rounds_df['game_id'] == game_id]
        rounds = []

        for _, round_row in game_rounds_df.iterrows():
            round_id = round_row['round_id']

            # Load events for this round
            round_events_df = events_df[events_df['round_id'] == round_id] if not events_df.empty else pd.DataFrame()
            events = round_events_df.to_dict('records') if not round_events_df.empty else []

            # Load positions for this round
            round_positions_df = positions_df[positions_df['round_id'] == round_id] if not positions_df.empty else pd.DataFrame()
            positions = round_positions_df.to_dict('records') if not round_positions_df.empty else []

            round_obj = Round(
                round_number=int(round_row['round_number']),
                winner=round_row['winner'],
                events=events,
                positions=positions
            )
            rounds.append(round_obj)

        return rounds
