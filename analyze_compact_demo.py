#!/usr/bin/env python3
"""
Analyze a compact CS2 game state file and extract strategic metrics.
"""
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class PlayerInfo:
    index: str
    name: str


@dataclass
class GameMetadata:
    map_name: str
    rounds: int
    tickrate: int
    players: Dict[str, str]  # P0 -> name


@dataclass
class RoundInfo:
    round_number: int
    winner: str
    tick_start: int
    tick_end: int
    events: List[str]  # Raw event lines


@dataclass
class MetricResult:
    metric_name: str
    value: float
    description: str


def parse_compact_file(filepath: str) -> Tuple[GameMetadata, List[RoundInfo]]:
    """Parse the compact game state file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    map_match = re.search(r'# Map: (\S+)', content)
    rounds_match = re.search(r'# Rounds: (\d+)', content)
    tickrate_match = re.search(r'# Tickrate: (\d+)', content)

    map_name = map_match.group(1) if map_match else "unknown"
    num_rounds = int(rounds_match.group(1)) if rounds_match else 0
    tickrate = int(tickrate_match.group(1)) if tickrate_match else 128

    # Extract player mapping
    players = {}
    player_line_match = re.search(r'# PLAYERS: (.+)', content)
    if player_line_match:
        player_str = player_line_match.group(1)
        # Parse P0:name P1:name format
        for match in re.finditer(r'(P\d+):(\S+)', player_str):
            players[match.group(1)] = match.group(2)

    metadata = GameMetadata(map_name, num_rounds, tickrate, players)

    # Extract rounds
    rounds = []
    round_pattern = r'## ROUND (\d+) \((\w+) win\) \| t(\d+)-t(\d+)\n### Positions\n.*?\n### Events\n(.*?)(?=\n## ROUND|\Z)'

    for match in re.finditer(round_pattern, content, re.DOTALL):
        round_num = int(match.group(1))
        winner = match.group(2)
        tick_start = int(match.group(3))
        tick_end = int(match.group(4))
        events_str = match.group(5).strip()

        # Parse events
        events = []
        if events_str:
            events = events_str.split(' | ')

        rounds.append(RoundInfo(round_num, winner, tick_start, tick_end, events))

    return metadata, rounds


def calculate_ttfk(metadata: GameMetadata, rounds: List[RoundInfo]) -> float:
    """Calculate average time to first kill (seconds after round start)."""
    times = []
    for round_info in rounds:
        death_events = [e for e in round_info.events if ':D,' in e]
        if death_events:
            # Extract tick from first death event
            first_death = death_events[0]
            tick_match = re.search(r'^(\d+):', first_death)
            if tick_match:
                death_tick = int(tick_match.group(1))
                time_to_kill = (death_tick - round_info.tick_start) / metadata.tickrate
                times.append(time_to_kill)

    return sum(times) / len(times) if times else 0.0


def calculate_bomb_plant_timing(metadata: GameMetadata, rounds: List[RoundInfo]) -> float:
    """Calculate average bomb plant time (seconds after round start)."""
    times = []
    for round_info in rounds:
        plant_events = [e for e in round_info.events if ':BP,' in e]
        if plant_events:
            plant_event = plant_events[0]
            tick_match = re.search(r'^(\d+):', plant_event)
            if tick_match:
                plant_tick = int(tick_match.group(1))
                time_to_plant = (plant_tick - round_info.tick_start) / metadata.tickrate
                times.append(time_to_plant)

    return sum(times) / len(times) if times else 0.0


def calculate_round_duration(metadata: GameMetadata, rounds: List[RoundInfo]) -> float:
    """Calculate average round duration in seconds."""
    durations = [(r.tick_end - r.tick_start) / metadata.tickrate for r in rounds]
    return sum(durations) / len(durations) if durations else 0.0


def calculate_entry_success_rate(rounds: List[RoundInfo]) -> float:
    """Calculate T-side entry success rate (first kill wins)."""
    first_kills = []
    for round_info in rounds:
        death_events = [e for e in round_info.events if ':D,' in e]
        if death_events:
            first_death = death_events[0]
            # Extract killer player index
            killer_match = re.search(r',P(\d+)>', first_death)
            if killer_match:
                killer_idx = int(killer_match.group(1))
                # P0-P4 are typically one team, P5-P9 another
                # Determine if killer's team won
                if round_info.winner == 't':
                    # Assume P0-P4 are Vitality (CT), P5-P9 are Falcons (T)
                    first_kills.append(killer_idx >= 5)

    return sum(first_kills) / len(first_kills) if first_kills else 0.0


def calculate_deaths_per_round(rounds: List[RoundInfo]) -> float:
    """Calculate average deaths per round."""
    death_counts = []
    for round_info in rounds:
        death_events = [e for e in round_info.events if ':D,' in e]
        death_counts.append(len(death_events))

    return sum(death_counts) / len(death_counts) if death_counts else 0.0


def calculate_post_plant_win_rate(rounds: List[RoundInfo]) -> float:
    """Calculate T-side post-plant win rate."""
    plant_rounds = [r for r in rounds if any(':BP,' in e for e in r.events)]
    t_wins = sum(1 for r in plant_rounds if r.winner == 't')

    return t_wins / len(plant_rounds) if plant_rounds else 0.0


def extract_critical_rounds(rounds: List[RoundInfo]) -> List[Tuple[int, str]]:
    """Extract rounds with interesting tactical features."""
    critical = []

    for round_info in rounds:
        death_count = len([e for e in round_info.events if ':D,' in e])
        plant_count = len([e for e in round_info.events if ':BP,' in e])

        # Identify interesting rounds
        if death_count <= 3:
            critical.append((round_info.round_number, f"Quick round ({death_count} deaths)"))
        elif death_count >= 8:
            critical.append((round_info.round_number, f"Heavy casualties ({death_count} deaths)"))

        if plant_count > 0 and round_info.winner == 'ct':
            critical.append((round_info.round_number, "Successful CT retake"))

    return critical[:5]  # Top 5 critical rounds


def calculate_team_win_rates(rounds: List[RoundInfo]) -> Dict[str, float]:
    """Calculate win rates for each side."""
    t_wins = sum(1 for r in rounds if r.winner == 't')
    ct_wins = sum(1 for r in rounds if r.winner == 'ct')
    total = len(rounds)

    return {
        't_win_rate': t_wins / total if total > 0 else 0.0,
        'ct_win_rate': ct_wins / total if total > 0 else 0.0,
        't_rounds': t_wins,
        'ct_rounds': ct_wins
    }


def analyze_player_performance(metadata: GameMetadata, rounds: List[RoundInfo]) -> Dict[str, Dict]:
    """Analyze individual player performance."""
    player_stats = {idx: {'kills': 0, 'deaths': 0, 'first_kills': 0}
                    for idx in metadata.players.keys()}

    for round_info in rounds:
        death_events = [e for e in round_info.events if ':D,' in e]

        for i, event in enumerate(death_events):
            # Parse killer and victim
            match = re.search(r'P(\d+)>P(\d+)', event)
            if match:
                killer_idx = f"P{match.group(1)}"
                victim_idx = f"P{match.group(2)}"

                if killer_idx in player_stats:
                    player_stats[killer_idx]['kills'] += 1
                    if i == 0:  # First kill of round
                        player_stats[killer_idx]['first_kills'] += 1

                if victim_idx in player_stats:
                    player_stats[victim_idx]['deaths'] += 1

    # Convert to named stats
    named_stats = {}
    for idx, stats in player_stats.items():
        name = metadata.players.get(idx, idx)
        kd_ratio = stats['kills'] / stats['deaths'] if stats['deaths'] > 0 else stats['kills']
        named_stats[name] = {
            'kills': stats['kills'],
            'deaths': stats['deaths'],
            'first_kills': stats['first_kills'],
            'kd_ratio': round(kd_ratio, 2)
        }

    return named_stats


def generate_analysis_report(filepath: str):
    """Generate a comprehensive analysis report."""
    metadata, rounds = parse_compact_file(filepath)

    print(f"=== CS2 Tactical Analysis ===")
    print(f"Map: {metadata.map_name}")
    print(f"Rounds: {metadata.rounds}")
    print(f"Tickrate: {metadata.tickrate}")
    print()

    print("=== Team Performance ===")
    win_rates = calculate_team_win_rates(rounds)
    print(f"T-Side Rounds Won: {win_rates['t_rounds']}/{len(rounds)} ({win_rates['t_win_rate']*100:.1f}%)")
    print(f"CT-Side Rounds Won: {win_rates['ct_rounds']}/{len(rounds)} ({win_rates['ct_win_rate']*100:.1f}%)")
    print()

    print("=== Strategic Metrics ===")
    ttfk = calculate_ttfk(metadata, rounds)
    print(f"Time to First Kill: {ttfk:.1f}s")

    plant_time = calculate_bomb_plant_timing(metadata, rounds)
    print(f"Average Bomb Plant Time: {plant_time:.1f}s")

    round_duration = calculate_round_duration(metadata, rounds)
    print(f"Average Round Duration: {round_duration:.1f}s")

    deaths_per_round = calculate_deaths_per_round(rounds)
    print(f"Average Deaths Per Round: {deaths_per_round:.1f}")

    entry_success = calculate_entry_success_rate(rounds)
    print(f"Entry Success Rate: {entry_success*100:.1f}%")

    post_plant_win = calculate_post_plant_win_rate(rounds)
    print(f"Post-Plant Win Rate: {post_plant_win*100:.1f}%")
    print()

    print("=== Player Performance ===")
    player_stats = analyze_player_performance(metadata, rounds)

    # Sort by K/D ratio
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1]['kd_ratio'], reverse=True)

    print(f"{'Player':<12} {'Kills':<6} {'Deaths':<7} {'K/D':<6} {'Entry Kills'}")
    print("-" * 55)
    for name, stats in sorted_players:
        print(f"{name:<12} {stats['kills']:<6} {stats['deaths']:<7} {stats['kd_ratio']:<6} {stats['first_kills']}")
    print()

    print("=== Critical Rounds ===")
    critical_rounds = extract_critical_rounds(rounds)
    for round_num, description in critical_rounds:
        print(f"Round {round_num}: {description}")
    print()

    return metadata, rounds, {
        'ttfk': ttfk,
        'plant_time': plant_time,
        'round_duration': round_duration,
        'deaths_per_round': deaths_per_round,
        'entry_success': entry_success,
        'post_plant_win': post_plant_win,
        'win_rates': win_rates,
        'player_stats': player_stats,
        'critical_rounds': critical_rounds
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_compact_demo.py <compact_file>")
        sys.exit(1)

    compact_file = sys.argv[1]
    generate_analysis_report(compact_file)
