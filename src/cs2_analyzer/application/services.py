from typing import Tuple, Dict, List
from .interfaces import GameRepository
from .ingestion import DemoParser, AwpyDemoParser
from ..domain.entities import Game, Team, Player, Round


class GameService:
    def __init__(self, game_repository: GameRepository, demo_parser: DemoParser = None):
        self.game_repository = game_repository
        self.demo_parser = demo_parser or AwpyDemoParser()

    def process_game(self, file_path: str) -> object:
        """Processes a demo file and saves the game data."""
        game, demo = self._parse_demo(file_path)
        self.game_repository.save(game)
        return demo

    def _parse_demo(self, file_path: str) -> Tuple[Game, object]:
        """Parses a demo file and creates a comprehensive Game entity."""
        demo = self.demo_parser.parse(file_path)

        # Extract map name
        map_name = demo.header.get('map_name', 'unknown')

        # Build teams and players
        teams = self._build_teams(demo)

        # Build rounds with events and positions
        rounds = self._build_rounds(demo)

        game = Game(map_name=map_name, teams=teams, rounds=rounds)
        return game, demo

    def _build_teams(self, demo) -> List[Team]:
        """Build Team and Player entities from demo data."""
        teams = []

        # T-side team
        t_players = []
        if hasattr(demo, 't_players') and demo.t_players:
            for player_data in demo.t_players:
                player = Player(
                    steam_id=player_data.get('steamid', 0),
                    name=player_data.get('name', 'Unknown'),
                    team='T'
                )
                t_players.append(player)

        if t_players:
            teams.append(Team(name='Terrorist', players=t_players))

        # CT-side team
        ct_players = []
        if hasattr(demo, 'ct_players') and demo.ct_players:
            for player_data in demo.ct_players:
                player = Player(
                    steam_id=player_data.get('steamid', 0),
                    name=player_data.get('name', 'Unknown'),
                    team='CT'
                )
                ct_players.append(player)

        if ct_players:
            teams.append(Team(name='Counter-Terrorist', players=ct_players))

        return teams

    def _build_rounds(self, demo) -> List[Round]:
        """Build Round entities with comprehensive event and position data."""
        rounds = []

        if not hasattr(demo, 'rounds') or demo.rounds is None:
            return rounds

        # Iterate through rounds DataFrame
        for round_row in demo.rounds.iter_rows(named=True):
            round_num = round_row.get('round_num', 0)
            winner = round_row.get('winner_side', 'unknown')

            # Extract events for this round
            events = self._extract_round_events(demo, round_num)

            # Extract position data for this round
            positions = self._extract_round_positions(demo, round_num)

            round_entity = Round(
                round_number=round_num,
                winner=winner,
                events=events,
                positions=positions
            )
            rounds.append(round_entity)

        return rounds

    def _extract_round_events(self, demo, round_num: int) -> List[Dict]:
        """Extract all events for a specific round."""
        events = []

        if not hasattr(demo, 'events') or not demo.events:
            return events

        # Collect events from all event types
        for event_type, event_df in demo.events.items():
            if event_df is None or event_df.is_empty():
                continue

            # Filter events for this round
            round_events = event_df.filter(event_df['round_num'] == round_num)

            # Convert to dictionaries
            for event_row in round_events.iter_rows(named=True):
                event_dict = dict(event_row)
                event_dict['event_type'] = event_type
                events.append(event_dict)

        # Sort events by tick
        events.sort(key=lambda e: e.get('tick', 0))

        return events

    def _extract_round_positions(self, demo, round_num: int) -> List[Dict]:
        """Extract position data for a specific round (sampled for efficiency)."""
        positions = []

        if not hasattr(demo, 'ticks') or demo.ticks is None:
            return positions

        # Filter ticks for this round
        round_ticks = demo.ticks.filter(demo.ticks['round_num'] == round_num)

        if round_ticks.is_empty():
            return positions

        # Sample positions every N ticks to reduce data volume (every 16 ticks = ~0.25s at 64 tick)
        sample_interval = 16
        unique_ticks = sorted(round_ticks.select('tick').unique().to_series())
        sampled_ticks = unique_ticks[::sample_interval]

        for tick in sampled_ticks:
            tick_data = round_ticks.filter(round_ticks['tick'] == tick)

            for pos_row in tick_data.iter_rows(named=True):
                position_dict = {
                    'tick': pos_row.get('tick'),
                    'player_steamid': pos_row.get('player_steamid'),
                    'side': pos_row.get('side'),
                    'X': pos_row.get('X'),
                    'Y': pos_row.get('Y'),
                    'Z': pos_row.get('Z'),
                    'yaw': pos_row.get('yaw'),
                    'pitch': pos_row.get('pitch')
                }
                positions.append(position_dict)

        return positions
