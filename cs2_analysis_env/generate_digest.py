#!/usr/bin/env python3
"""
Generate a Claude-digestible summary (<50KB) from awpy Demo object.
This format is optimized for direct Claude reading and strategic analysis.
"""
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def generate_digest_from_demo(demo, output_path: str) -> str:
    """
    Generate a compact digest optimized for Claude Code analysis.
    Target: <50KB, human-readable, strategically relevant.
    """
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("CS2 GAME DIGEST - Claude-Optimized Strategic Summary")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Map: {demo.header.get('map_name', 'unknown')}")
    lines.append(f"Tickrate: {demo.tickrate}")
    lines.append(f"Total Rounds: {len(demo.rounds)}")
    lines.append("")

    # Player Roster
    lines.append("PLAYER ROSTER")
    lines.append("-" * 80)

    # Determine teams
    t_players = demo.t_players if hasattr(demo, 't_players') else []
    ct_players = demo.ct_players if hasattr(demo, 'ct_players') else []

    if t_players:
        lines.append(f"T-Side ({len(t_players)}): {', '.join(t_players)}")
    if ct_players:
        lines.append(f"CT-Side ({len(ct_players)}): {', '.join(ct_players)}")
    lines.append("")

    # Calculate player stats
    player_stats = defaultdict(lambda: {'kills': 0, 'deaths': 0, 'assists': 0, 'first_kills': 0})

    # Process each round
    rounds_data = []

    for idx, round_row in enumerate(demo.rounds.iter_rows(named=True), start=1):
        round_info = {
            'number': idx,
            'winner': round_row.get('winner_side', 'unknown'),
            'reason': round_row.get('end_reason', 'unknown'),
            'tick_start': round_row.get('start_tick', 0),
            'tick_end': round_row.get('end_tick', 0),
            'freeze_end': round_row.get('freeze_time_end_tick', 0),
            'events': []
        }

        # Calculate duration
        duration_ticks = round_info['tick_end'] - round_info['tick_start']
        duration_s = duration_ticks / demo.tickrate if demo.tickrate else 0
        round_info['duration'] = duration_s

        # Extract events for this round
        round_start = round_info['tick_start']
        round_end = round_info['tick_end']

        # Deaths
        if 'player_death' in demo.events:
            deaths_df = demo.events['player_death']
            round_deaths = deaths_df.filter(
                (deaths_df['tick'] >= round_start) &
                (deaths_df['tick'] <= round_end)
            )

            first_kill = None
            for death_row in round_deaths.iter_rows(named=True):
                tick = death_row.get('tick', 0)
                attacker = death_row.get('attacker_name', 'unknown')
                victim = death_row.get('user_name', 'unknown')
                weapon = death_row.get('weapon', 'unknown')

                # Track stats
                if attacker != victim:  # Not suicide
                    player_stats[attacker]['kills'] += 1
                player_stats[victim]['deaths'] += 1

                # First kill
                if first_kill is None:
                    first_kill = {
                        'tick': tick,
                        'time': (tick - round_info['freeze_end']) / demo.tickrate,
                        'killer': attacker,
                        'victim': victim,
                        'weapon': weapon
                    }
                    player_stats[attacker]['first_kills'] += 1

                # Add to events
                time_in_round = (tick - round_info['freeze_end']) / demo.tickrate
                round_info['events'].append({
                    'type': 'kill',
                    'time': time_in_round,
                    'attacker': attacker,
                    'victim': victim,
                    'weapon': weapon
                })

            round_info['first_kill'] = first_kill
            round_info['total_deaths'] = len(round_deaths)

        # Bomb plants
        if 'bomb_planted' in demo.events:
            plants_df = demo.events['bomb_planted']
            round_plants = plants_df.filter(
                (plants_df['tick'] >= round_start) &
                (plants_df['tick'] <= round_end)
            )

            for plant_row in round_plants.iter_rows(named=True):
                tick = plant_row.get('tick', 0)
                site = plant_row.get('site', 'unknown')
                planter = plant_row.get('user_name', 'unknown')
                time_in_round = (tick - round_info['freeze_end']) / demo.tickrate

                round_info['bomb_plant'] = {
                    'tick': tick,
                    'time': time_in_round,
                    'site': site,
                    'planter': planter
                }

                round_info['events'].append({
                    'type': 'plant',
                    'time': time_in_round,
                    'site': site,
                    'planter': planter
                })

        # Bomb defuses
        if 'bomb_defused' in demo.events:
            defuses_df = demo.events['bomb_defused']
            round_defuses = defuses_df.filter(
                (defuses_df['tick'] >= round_start) &
                (defuses_df['tick'] <= round_end)
            )

            for defuse_row in round_defuses.iter_rows(named=True):
                tick = defuse_row.get('tick', 0)
                defuser = defuse_row.get('user_name', 'unknown')
                time_in_round = (tick - round_info['freeze_end']) / demo.tickrate

                round_info['bomb_defuse'] = {
                    'tick': tick,
                    'time': time_in_round,
                    'defuser': defuser
                }

                round_info['events'].append({
                    'type': 'defuse',
                    'time': time_in_round,
                    'defuser': defuser
                })

        rounds_data.append(round_info)

    # Game Summary Statistics
    lines.append("GAME SUMMARY")
    lines.append("-" * 80)

    t_wins = sum(1 for r in rounds_data if r['winner'] == 't')
    ct_wins = sum(1 for r in rounds_data if r['winner'] == 'ct')

    lines.append(f"Final Score: T {t_wins} - {ct_wins} CT")

    avg_round_duration = sum(r['duration'] for r in rounds_data) / len(rounds_data) if rounds_data else 0
    lines.append(f"Average Round Duration: {avg_round_duration:.1f}s")

    # TTFK
    first_kills = [r['first_kill'] for r in rounds_data if r.get('first_kill')]
    if first_kills:
        avg_ttfk = sum(fk['time'] for fk in first_kills) / len(first_kills)
        lines.append(f"Average Time to First Kill: {avg_ttfk:.1f}s")

    # Bomb plants
    plants = [r for r in rounds_data if r.get('bomb_plant')]
    if plants:
        avg_plant_time = sum(r['bomb_plant']['time'] for r in plants) / len(plants)
        lines.append(f"Average Bomb Plant Time: {avg_plant_time:.1f}s")

        post_plant_wins = sum(1 for r in plants if r['winner'] == 't')
        lines.append(f"Post-Plant Win Rate: {post_plant_wins}/{len(plants)} ({post_plant_wins/len(plants)*100:.0f}%)")

        # Site preference
        site_counts = defaultdict(int)
        for r in plants:
            site_counts[r['bomb_plant']['site']] += 1
        lines.append(f"Site Preference: {dict(site_counts)}")

    lines.append("")

    # Player Statistics
    lines.append("PLAYER STATISTICS")
    lines.append("-" * 80)
    lines.append(f"{'Player':<20} {'K':<5} {'D':<5} {'K/D':<6} {'FK':<5}")
    lines.append("-" * 80)

    sorted_players = sorted(
        player_stats.items(),
        key=lambda x: x[1]['kills'] / max(x[1]['deaths'], 1),
        reverse=True
    )

    for player, stats in sorted_players:
        kd = stats['kills'] / max(stats['deaths'], 1)
        lines.append(
            f"{player:<20} {stats['kills']:<5} {stats['deaths']:<5} "
            f"{kd:<6.2f} {stats['first_kills']:<5}"
        )

    lines.append("")

    # Round-by-Round Summary
    lines.append("ROUND-BY-ROUND SUMMARY")
    lines.append("-" * 80)

    for r in rounds_data:
        header = f"Round {r['number']}: {r['winner'].upper()} win ({r['duration']:.1f}s)"
        lines.append(header)

        # First kill
        if r.get('first_kill'):
            fk = r['first_kill']
            lines.append(f"  First Kill: {fk['time']:>5.1f}s - {fk['killer']} > {fk['victim']} ({fk['weapon']})")

        # Bomb plant
        if r.get('bomb_plant'):
            bp = r['bomb_plant']
            lines.append(f"  Bomb Plant: {bp['time']:>5.1f}s - Site {bp['site']} by {bp['planter']}")

        # Bomb defuse
        if r.get('bomb_defuse'):
            bd = r['bomb_defuse']
            lines.append(f"  Defuse:     {bd['time']:>5.1f}s - {bd['defuser']}")

        # Total kills
        total_kills = r.get('total_deaths', 0)
        lines.append(f"  Total Kills: {total_kills}")

        # End reason
        if r.get('reason'):
            lines.append(f"  End Reason: {r['reason']}")

        lines.append("")

    # Key Insights Section
    lines.append("STRATEGIC INSIGHTS")
    lines.append("-" * 80)

    # Identify critical rounds
    lines.append("Critical Rounds:")

    # Heavy casualty rounds
    high_kill_rounds = [r for r in rounds_data if r.get('total_deaths', 0) >= 8]
    if high_kill_rounds:
        lines.append(f"  High Casualty Rounds (8+ kills): {[r['number'] for r in high_kill_rounds[:5]]}")

    # Quick rounds
    quick_rounds = [r for r in rounds_data if r.get('total_deaths', 0) <= 3]
    if quick_rounds:
        lines.append(f"  Quick Rounds (≤3 kills): {[r['number'] for r in quick_rounds[:5]]}")

    # Successful retakes
    retakes = [r for r in rounds_data if r.get('bomb_plant') and r['winner'] == 'ct']
    if retakes:
        lines.append(f"  Successful CT Retakes: {[r['number'] for r in retakes[:5]]}")

    lines.append("")

    # Entry success analysis
    if first_kills:
        # Determine which players are T vs CT (simplified)
        t_entry_wins = 0
        ct_entry_wins = 0

        for fk in first_kills:
            killer = fk['killer']
            # Simplified: assume first half is one team's perspective
            # In reality, would need to track which side each player was on per round
            round_num = next(r['number'] for r in rounds_data if r.get('first_kill') == fk)
            round_data = rounds_data[round_num - 1]

            if round_data['winner'] == 't':
                t_entry_wins += 1
            else:
                ct_entry_wins += 1

        lines.append(f"Entry Frag Analysis:")
        lines.append(f"  Rounds where first kill team won: {(t_entry_wins + ct_entry_wins) / len(first_kills) * 100:.0f}%")

    lines.append("")
    lines.append("=" * 80)
    lines.append(f"End of Digest | Total Size: {len('\\n'.join(lines))} characters")
    lines.append("=" * 80)

    # Write to file
    digest_content = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(digest_content)

    size_kb = len(digest_content) / 1024
    print(f"Digest generated: {output_path} ({size_kb:.1f} KB)")

    return output_path


def main():
    """Generate digest from awpy demo file."""
    if len(sys.argv) < 2:
        print("Usage: python generate_digest.py <demo.dem>")
        sys.exit(1)

    demo_path = sys.argv[1]

    # Parse demo
    print(f"Parsing demo: {demo_path}")
    from awpy.parser import DemoParser

    parser = DemoParser(
        demofile=demo_path,
        parse_rate=128,  # Parse every 128 ticks for efficiency
        parse_frames=True,
        parse_kill_frames=False
    )

    demo = parser.parse()

    # Generate digest
    demo_stem = Path(demo_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/digest/{demo_stem}_{timestamp}.digest.txt"

    Path("data/digest").mkdir(exist_ok=True)

    generate_digest_from_demo(demo, output_path)

    print(f"\nSuccess! Digest ready for Claude analysis:")
    print(f"  {output_path}")


if __name__ == '__main__':
    main()
