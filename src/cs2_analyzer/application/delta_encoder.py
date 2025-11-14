"""
Delta-based game state encoder for ultra-compact representation.

Optimized for Claude Code context window - creates human-readable but
maximally compressed text format with legend/index system.
"""

from typing import Dict, List, Tuple
import polars as pl
from dataclasses import dataclass


@dataclass
class CompactGameState:
    """Compressed game state representation."""
    header: str
    rounds: List[str]

    def to_text(self) -> str:
        """Convert to complete text representation."""
        return f"{self.header}\n\n" + "\n\n".join(self.rounds)

    def token_estimate(self) -> int:
        """Rough token count estimate (1 token ≈ 4 chars)."""
        return len(self.to_text()) // 4


class DeltaEncoder:
    """
    Encodes CS2 demo data into ultra-compact text format.

    Format Design:
    - Human-readable abbreviations
    - Player indexing (P0-P9)
    - Delta encoding for positions
    - Event abbreviations
    - Tick-relative timestamps
    """

    # Event type abbreviations
    EVENT_CODES = {
        'player_death': 'D',
        'bomb_planted': 'BP',
        'bomb_defused': 'BD',
        'player_hurt': 'H',
        'weapon_fire': 'F',
        'grenade_thrown': 'G',
        'smoke_started': 'SM',
        'inferno_started': 'IN',
    }

    # Weapon abbreviations
    WEAPON_CODES = {
        'ak47': 'AK',
        'awp': 'AWP',
        'm4a1': 'M4',
        'deagle': 'DE',
        'glock': 'GL',
        'usp': 'USP',
    }

    def __init__(self, demo):
        """Initialize with awpy demo object."""
        self.demo = demo
        self.player_index = {}  # steamid -> index mapping
        self._build_player_index()

    def _build_player_index(self):
        """Create player index from demo."""
        if self.demo.ticks is None or len(self.demo.ticks) == 0:
            return

        # Extract unique players from ticks DataFrame
        # Each player appears with steamid and name
        unique_players = self.demo.ticks.select(['steamid', 'name']).unique()

        # Create index (assign indices 0-9 for the 10 unique players)
        all_players = []
        for row in unique_players.iter_rows(named=True):
            steamid = row['steamid']
            name = row['name']

            # Don't add duplicates
            if not any(p[0] == steamid for p in all_players):
                all_players.append((steamid, name))

        # Sort by steamid for consistency
        all_players.sort(key=lambda x: x[0])

        # Create index mapping
        for idx, (steamid, name) in enumerate(all_players):
            self.player_index[steamid] = {
                'idx': idx,
                'name': name,
                'team': None  # Team changes by round (CT/T switch)
            }

    def encode(self, sample_interval: int = 32) -> CompactGameState:
        """
        Encode demo into compact format.

        Args:
            sample_interval: Sample positions every N ticks (32 = ~0.5s @ 64 tick)

        Returns:
            CompactGameState object
        """
        header = self._encode_header()
        rounds = self._encode_rounds(sample_interval)

        return CompactGameState(header=header, rounds=rounds)

    def _encode_header(self) -> str:
        """
        Encode game metadata and legend.

        Format:
        # MAP: de_ancient | ROUNDS: 15 | TICK: 64
        # PLAYERS: P0:s1mple(T) P1:electroNic(T) ...
        # SITES: A(x,y,z) B(x,y,z)
        # FORMAT: Positions = tick:X,Y,Z,yaw,pitch (then +dX,+dY,+dZ,+dyaw,+dpitch)
        # FORMAT: Events = tick:CODE,details (D=death,BP=plant,H=hurt,etc)
        """
        lines = []

        # Map info
        map_name = self.demo.header.get('map_name', 'unknown') if hasattr(self.demo, 'header') else 'unknown'
        num_rounds = len(self.demo.rounds) if self.demo.rounds is not None else 0
        tickrate = self.demo.tickrate if hasattr(self.demo, 'tickrate') else 64

        lines.append(f"# MAP: {map_name} | ROUNDS: {num_rounds} | TICK: {tickrate}")

        # Player index
        players_sorted = sorted(self.player_index.items(),
                               key=lambda x: x[1]['idx'])
        player_strs = [f"P{info['idx']}:{info['name']}"
                      for steamid, info in players_sorted]
        lines.append(f"# PLAYERS: {' '.join(player_strs)}")

        # Bombsites
        if hasattr(self.demo, 'bombsite_locations') and self.demo.bombsite_locations:
            sites = []
            for site, loc in self.demo.bombsite_locations.items():
                x, y, z = int(loc['x']), int(loc['y']), int(loc['z'])
                sites.append(f"{site}({x},{y},{z})")
            lines.append(f"# SITES: {' '.join(sites)}")

        # Format legend
        lines.append("# ")
        lines.append("# FORMAT LEGEND:")
        lines.append("#   Positions: tick:X,Y,Z (initial) then tick:+dX,+dY,+dZ (deltas)")
        lines.append("#   Events: tick:CODE,params | D=death H=hurt BP=plant BD=defuse F=fire G=nade SM=smoke IN=fire")
        lines.append("#   Players: P0-P9 indexed above | Weapons: AK=AK47 AWP=AWP M4=M4A1 etc")

        return '\n'.join(lines)

    def _encode_rounds(self, sample_interval: int) -> List[str]:
        """Encode all rounds."""
        rounds = []

        if self.demo.rounds is None or len(self.demo.rounds) == 0:
            return rounds

        for round_data in self.demo.rounds.iter_rows(named=True):
            round_num = round_data.get('round_num', 0)
            round_str = self._encode_round(round_num, round_data, sample_interval)
            rounds.append(round_str)

        return rounds

    def _encode_round(self, round_num: int, round_data: dict, sample_interval: int) -> str:
        """Encode a single round."""
        lines = []

        # Round header
        winner = round_data.get('winner', 'unknown')  # Changed from 'winner_side' to 'winner'
        start_tick = round_data.get('freeze_end', 0)
        end_tick = round_data.get('end', start_tick + 10000)  # Changed from 'end_tick' to 'end'

        lines.append(f"## ROUND {round_num} ({winner} win) | t{start_tick}-t{end_tick}")

        # Encode positions
        positions = self._encode_positions(round_num, start_tick, end_tick, sample_interval)
        if positions:
            lines.append("### Positions")
            lines.extend(positions)

        # Encode events
        events = self._encode_events(round_num, start_tick, end_tick)
        if events:
            lines.append("### Events")
            lines.append(' | '.join(events))

        return '\n'.join(lines)

    def _encode_positions(self, round_num: int, start_tick: int,
                         end_tick: int, sample_interval: int) -> List[str]:
        """
        Encode positions with delta compression.

        Format per player: P0 1000:100,200,50,90,0 1032:+2,+3,0,+1,0 1064:-1,+5,0,0,0
        """
        if self.demo.ticks is None or len(self.demo.ticks) == 0:
            return []

        # Filter to this round
        round_ticks = self.demo.ticks.filter(
            (pl.col('round_num') == round_num) &
            (pl.col('tick') >= start_tick) &
            (pl.col('tick') <= end_tick)
        )

        if len(round_ticks) == 0:
            return []

        # Sample every N ticks
        sampled = round_ticks.filter(
            (pl.col('tick') - start_tick) % sample_interval == 0
        ).sort(['steamid', 'tick'])

        # Group by player
        player_lines = []
        last_state = {}  # steamid -> last position

        for steamid in sampled['steamid'].unique():
            player_data = sampled.filter(pl.col('steamid') == steamid)

            if steamid not in self.player_index:
                continue

            player_idx = self.player_index[steamid]['idx']
            positions = []

            for row in player_data.iter_rows(named=True):
                tick = row['tick']
                x, y, z = int(row['X']), int(row['Y']), int(row['Z'])

                if steamid not in last_state:
                    # First position - absolute (no yaw/pitch in CS2 awpy data)
                    positions.append(f"{tick}:{x},{y},{z}")
                    last_state[steamid] = (x, y, z)
                else:
                    # Delta encoding
                    last_x, last_y, last_z = last_state[steamid]
                    dx = x - last_x
                    dy = y - last_y
                    dz = z - last_z

                    # Only include if there's movement
                    if dx != 0 or dy != 0 or dz != 0:
                        positions.append(f"{tick}:{dx:+d},{dy:+d},{dz:+d}")
                        last_state[steamid] = (x, y, z)

            if positions:
                player_lines.append(f"P{player_idx} {' '.join(positions)}")

        return player_lines

    def _encode_events(self, round_num: int, start_tick: int, end_tick: int) -> List[str]:
        """
        Encode events in compact format.

        Format: tick:CODE,params
        Examples:
          1234:D,P3>P8,AK,HS  (death: P3 killed P8 with AK, headshot)
          5234:BP,P2,A        (bomb plant: P2 planted at A)
          2100:H,P5>P7,25     (hurt: P5 damaged P7 for 25hp)
        """
        if not hasattr(self.demo, 'events') or not self.demo.events:
            return []

        events = []

        # Process death events
        if 'player_death' in self.demo.events:
            deaths = self.demo.events['player_death']
            round_deaths = deaths.filter(
                (pl.col('tick') >= start_tick) &
                (pl.col('tick') <= end_tick)
            ).sort('tick')

            for row in round_deaths.iter_rows(named=True):
                tick = row['tick']
                attacker = row.get('attacker_steamid')
                victim = row.get('user_steamid')
                weapon = row.get('weapon', '')
                is_hs = row.get('is_headshot', False)

                # Get player indices
                att_idx = self.player_index.get(attacker, {}).get('idx', '?')
                vic_idx = self.player_index.get(victim, {}).get('idx', '?')

                # Abbreviate weapon
                weapon_code = self._abbrev_weapon(weapon)
                hs_flag = ',HS' if is_hs else ''

                events.append(f"{tick}:D,P{att_idx}>P{vic_idx},{weapon_code}{hs_flag}")

        # Process bomb events
        if 'bomb_planted' in self.demo.events:
            plants = self.demo.events['bomb_planted']
            round_plants = plants.filter(
                (pl.col('tick') >= start_tick) &
                (pl.col('tick') <= end_tick)
            )

            for row in round_plants.iter_rows(named=True):
                tick = row['tick']
                planter = row.get('user_steamid')
                site = row.get('site', 0)
                site_char = 'A' if site == 394 else 'B'

                plant_idx = self.player_index.get(planter, {}).get('idx', '?')
                events.append(f"{tick}:BP,P{plant_idx},{site_char}")

        # Add more event types as needed...

        return events

    def _abbrev_weapon(self, weapon: str) -> str:
        """Abbreviate weapon name."""
        if not weapon:
            return 'UNK'

        weapon_lower = weapon.lower()
        for full, abbrev in self.WEAPON_CODES.items():
            if full in weapon_lower:
                return abbrev

        # Return first 3 chars if not found
        return weapon[:3].upper()


def encode_demo_compact(demo, sample_interval: int = 32) -> str:
    """
    Convenience function to encode demo as compact text.

    Args:
        demo: awpy Demo object
        sample_interval: Sample positions every N ticks

    Returns:
        Compact text representation
    """
    encoder = DeltaEncoder(demo)
    compact = encoder.encode(sample_interval)
    return compact.to_text()
