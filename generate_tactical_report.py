#!/usr/bin/env python3
"""
Generate a comprehensive tactical report from compact game state analysis.
"""
import sys
from datetime import datetime
from analyze_compact_demo import parse_compact_file, calculate_ttfk, calculate_bomb_plant_timing
from analyze_compact_demo import calculate_round_duration, calculate_deaths_per_round
from analyze_compact_demo import calculate_entry_success_rate, calculate_post_plant_win_rate
from analyze_compact_demo import calculate_team_win_rates, analyze_player_performance
from analyze_compact_demo import extract_critical_rounds
import re


def analyze_round_details(rounds):
    """Extract detailed round-by-round information."""
    detailed_rounds = []

    for round_info in rounds:
        death_events = [e for e in round_info.events if ':D,' in e]
        plant_events = [e for e in round_info.events if ':BP,' in e]

        # Extract kill sequence
        kills = []
        for event in death_events:
            tick_match = re.search(r'^(\d+):D,P(\d+)>P(\d+)', event)
            if tick_match:
                tick = int(tick_match.group(1))
                killer = int(tick_match.group(2))
                victim = int(tick_match.group(3))
                kills.append((tick, killer, victim))

        # Extract plant info
        plant_tick = None
        plant_site = None
        if plant_events:
            plant_match = re.search(r'^(\d+):BP,P(\d+),([AB])', plant_events[0])
            if plant_match:
                plant_tick = int(plant_match.group(1))
                plant_site = plant_match.group(3)

        detailed_rounds.append({
            'round_num': round_info.round_number,
            'winner': round_info.winner,
            'tick_start': round_info.tick_start,
            'tick_end': round_info.tick_end,
            'kills': kills,
            'plant_tick': plant_tick,
            'plant_site': plant_site,
            'total_deaths': len(death_events)
        })

    return detailed_rounds


def generate_markdown_report(compact_filepath: str, output_dir: str = "reports"):
    """Generate comprehensive markdown tactical report."""
    from pathlib import Path

    # Parse data
    metadata, rounds = parse_compact_file(compact_filepath)

    # Calculate metrics
    ttfk = calculate_ttfk(metadata, rounds)
    plant_time = calculate_bomb_plant_timing(metadata, rounds)
    round_duration = calculate_round_duration(metadata, rounds)
    deaths_per_round = calculate_deaths_per_round(rounds)
    entry_success = calculate_entry_success_rate(rounds)
    post_plant_win = calculate_post_plant_win_rate(rounds)
    win_rates = calculate_team_win_rates(rounds)
    player_stats = analyze_player_performance(metadata, rounds)
    critical_rounds = extract_critical_rounds(rounds)
    detailed_rounds = analyze_round_details(rounds)

    # Determine teams (assuming P0-P4 are one team, P5-P9 another)
    team_ct = [metadata.players[f"P{i}"] for i in range(5) if f"P{i}" in metadata.players]
    team_t = [metadata.players[f"P{i}"] for i in range(5, 10) if f"P{i}" in metadata.players]

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"game_analysis_{metadata.map_name}_{timestamp}.md"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# CS2 Tactical Analysis: {metadata.map_name.replace('de_', '').title()}\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Demo**: {Path(compact_filepath).name}\n")
        f.write(f"**Map**: {metadata.map_name}\n")
        f.write(f"**Final Score**: T {win_rates['t_rounds']} - {win_rates['ct_rounds']} CT\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **T-side dominated** with {win_rates['t_win_rate']*100:.0f}% round wins ({win_rates['t_rounds']}/{len(rounds)} rounds)\n")
        f.write(f"- **Post-plant excellence**: {post_plant_win*100:.0f}% win rate after bomb plant indicates strong site execution and crossfire setups\n")
        f.write(f"- **Aggressive pacing**: Average TTFK of {ttfk:.1f}s shows early engagements and map control fights\n")

        # Identify top performers
        sorted_players = sorted(player_stats.items(), key=lambda x: x[1]['kd_ratio'], reverse=True)
        top_player = sorted_players[0]
        f.write(f"- **{top_player[0]} dominates** with {top_player[1]['kd_ratio']} K/D ratio and {top_player[1]['kills']} kills\n")

        # Entry success insights
        if entry_success < 0.4:
            f.write(f"- **Entry fragging struggles**: {entry_success*100:.0f}% success rate indicates difficult opening duels\n")
        elif entry_success > 0.6:
            f.write(f"- **Strong entries**: {entry_success*100:.0f}% success rate shows effective initial contact wins\n")
        else:
            f.write(f"- **Balanced opening duels**: {entry_success*100:.0f}% entry success rate\n")

        f.write("\n")

        # Team Performance
        f.write("## Team Performance\n\n")

        f.write("### T-Side Analysis\n")
        f.write(f"**Rounds Won**: {win_rates['t_rounds']}/{len(rounds)} ({win_rates['t_win_rate']*100:.1f}%)\n\n")
        f.write(f"- **Pacing**: TTFK of {ttfk:.1f}s indicates {'aggressive' if ttfk < 20 else 'methodical' if ttfk < 30 else 'slow'} tempo\n")
        f.write(f"- **Bomb Plant Timing**: Average plant at {plant_time:.1f}s ({'early' if plant_time < 35 else 'mid' if plant_time < 50 else 'late'} round timing)\n")
        f.write(f"- **Executes**: {post_plant_win*100:.0f}% post-plant win rate demonstrates {'excellent' if post_plant_win > 0.7 else 'solid' if post_plant_win > 0.5 else 'weak'} site takes and trades\n")
        f.write(f"- **Entry Success**: {entry_success*100:.0f}% first kill win rate\n\n")

        f.write("### CT-Side Analysis\n")
        f.write(f"**Rounds Won**: {win_rates['ct_rounds']}/{len(rounds)} ({win_rates['ct_win_rate']*100:.1f}%)\n\n")

        retake_rounds = len([r for r in detailed_rounds if r['plant_tick'] and r['winner'] == 'ct'])
        f.write(f"- **Retake Success**: {retake_rounds} successful retakes out of {len([r for r in detailed_rounds if r['plant_tick']])} plants\n")
        f.write(f"- **Defensive Pressure**: {'High' if ttfk < 20 else 'Moderate' if ttfk < 30 else 'Conservative'} - CTs engaging early\n")

        ct_win_pct = win_rates['ct_win_rate']
        if ct_win_pct < 0.4:
            f.write(f"- **Struggles**: Only {win_rates['ct_rounds']} rounds won suggests weak site holds or poor rotations\n")
        f.write("\n")

        # Critical Rounds
        f.write("## Critical Rounds\n\n")
        for round_num, description in critical_rounds[:5]:
            round_data = next(r for r in detailed_rounds if r['round_num'] == round_num)
            f.write(f"### Round {round_num}: {description}\n")
            f.write(f"- **Winner**: {round_data['winner'].upper()}\n")
            f.write(f"- **Duration**: {(round_data['tick_end'] - round_data['tick_start']) / metadata.tickrate:.1f}s\n")

            if round_data['plant_tick']:
                plant_time_s = (round_data['plant_tick'] - round_data['tick_start']) / metadata.tickrate
                f.write(f"- **Bomb Plant**: Site {round_data['plant_site']} at {plant_time_s:.1f}s\n")

            if round_data['kills']:
                f.write(f"- **Key Events**:\n")
                for i, (tick, killer, victim) in enumerate(round_data['kills'][:3]):  # First 3 kills
                    time_s = (tick - round_data['tick_start']) / metadata.tickrate
                    killer_name = metadata.players.get(f"P{killer}", f"P{killer}")
                    victim_name = metadata.players.get(f"P{victim}", f"P{victim}")
                    f.write(f"  - {time_s:.1f}s: {killer_name} eliminates {victim_name}\n")

            # Tactical notes
            if round_data['total_deaths'] <= 3:
                f.write(f"- **Tactical Note**: Quick decisive round - possibly eco or stack situation\n")
            elif round_data['total_deaths'] >= 8:
                f.write(f"- **Tactical Note**: Extended engagement with multiple trades\n")

            if round_data['plant_tick'] and round_data['winner'] == 'ct':
                f.write(f"- **Tactical Note**: CT retake successful - good rotation or T overextension\n")

            f.write("\n")

        # Player Highlights
        f.write("## Player Highlights\n\n")

        f.write("### Top Performers\n\n")
        for name, stats in sorted_players[:3]:
            f.write(f"**{name}**: {stats['kills']} kills, {stats['deaths']} deaths, {stats['kd_ratio']} K/D\n")
            if stats['first_kills'] >= 3:
                f.write(f"- Strong entry fragger with {stats['first_kills']} opening kills\n")
            if stats['kd_ratio'] >= 2.0:
                f.write(f"- Dominant performance with exceptional fragging\n")
            if stats['deaths'] <= len(rounds) * 0.4:
                f.write(f"- Excellent survival rate and positioning\n")
            f.write("\n")

        f.write("### Areas for Improvement\n\n")
        for name, stats in sorted_players[-3:]:
            f.write(f"**{name}**: {stats['kills']} kills, {stats['deaths']} deaths, {stats['kd_ratio']} K/D\n")
            if stats['kd_ratio'] < 0.5:
                f.write(f"- Struggled significantly - review positioning and crosshair placement\n")
            if stats['deaths'] >= len(rounds) * 0.8:
                f.write(f"- High death count suggests aggressive positioning without impact\n")
            if stats['first_kills'] == 0 and stats['kills'] > 5:
                f.write(f"- No opening kills - consider more aggressive initial positioning\n")
            f.write("\n")

        # Strategic Recommendations
        f.write("## Strategic Recommendations\n\n")

        f.write("### For T-Side\n")
        if post_plant_win > 0.8:
            f.write(f"1. **Maintain post-plant discipline** - Current {post_plant_win*100:.0f}% win rate is excellent\n")
        else:
            f.write(f"1. **Improve post-plant positions** - Only {post_plant_win*100:.0f}% win rate after plant\n")

        if entry_success < 0.4:
            f.write(f"2. **Entry fragging setup** - {entry_success*100:.0f}% success rate needs utility support and refragging\n")

        if plant_time > 50:
            f.write(f"3. **Faster executes** - {plant_time:.0f}s average plant time leaves little bomb timer\n")

        if ttfk > 30:
            f.write(f"4. **Increase tempo** - {ttfk:.1f}s TTFK allows CT heavy rotations\n")

        f.write("\n### For CT-Side\n")
        if win_rates['ct_win_rate'] < 0.4:
            f.write(f"1. **Strengthen site holds** - {win_rates['ct_win_rate']*100:.0f}% win rate needs improvement\n")
            f.write(f"2. **Earlier rotations** - Review demo for late rotation patterns\n")

        retake_success = retake_rounds / len([r for r in detailed_rounds if r['plant_tick']]) if detailed_rounds else 0
        if retake_success < 0.3:
            f.write(f"3. **Retake coordination** - Practice post-plant retake protocols\n")

        f.write(f"4. **Utility usage** - Save grenades for retakes and delaying T executes\n")

        f.write("\n### Individual Coaching Points\n")
        # Bottom 2 performers
        for name, stats in sorted_players[-2:]:
            f.write(f"- **{name}**: Focus on survival and trade opportunities ({stats['kd_ratio']} K/D needs improvement)\n")

        f.write("\n")

        # Metrics Summary
        f.write("## Appendix: Metrics Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Time to First Kill | {ttfk:.1f}s |\n")
        f.write(f"| Bomb Plant Timing | {plant_time:.1f}s |\n")
        f.write(f"| Round Duration | {round_duration:.1f}s |\n")
        f.write(f"| Deaths Per Round | {deaths_per_round:.1f} |\n")
        f.write(f"| Entry Success Rate | {entry_success*100:.1f}% |\n")
        f.write(f"| Post-Plant Win Rate | {post_plant_win*100:.1f}% |\n")
        f.write(f"| T-Side Win Rate | {win_rates['t_win_rate']*100:.1f}% |\n")
        f.write(f"| CT-Side Win Rate | {win_rates['ct_win_rate']*100:.1f}% |\n")
        f.write("\n")

        # Player stats table
        f.write("### Player Statistics\n\n")
        f.write("| Player | Kills | Deaths | K/D | Entry Kills |\n")
        f.write("|--------|-------|--------|-----|-------------|\n")
        for name, stats in sorted_players:
            f.write(f"| {name} | {stats['kills']} | {stats['deaths']} | {stats['kd_ratio']} | {stats['first_kills']} |\n")

    print(f"Report generated: {output_path}")
    return output_path


if __name__ == '__main__':
    import subprocess
    import glob

    if len(sys.argv) < 2:
        print("Usage: python generate_tactical_report.py <demo_file_or_compact_file>")
        print("  Example: python generate_tactical_report.py data/raw/game.dem")
        print("  Example: python generate_tactical_report.py data/compact/game.compact.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check if input is a .dem file or .compact.txt file
    if input_file.endswith('.dem'):
        print(f"Demo file detected: {input_file}")
        print("Generating compact game state...")

        # Run generate_compact.py
        result = subprocess.run(
            ['python', 'generate_compact.py', input_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error generating compact file: {result.stderr}")
            sys.exit(1)

        print(result.stdout)

        # Find the generated compact file
        # Extract base name from demo file
        from pathlib import Path
        demo_path = Path(input_file)
        base_name = demo_path.stem

        # Find most recent compact file matching this demo
        compact_files = list(Path('data/compact').glob(f'{base_name}_*.compact.txt'))
        if not compact_files:
            print(f"Error: No compact file found for {base_name}")
            sys.exit(1)

        # Use the most recent one
        compact_file = str(sorted(compact_files)[-1])
        print(f"Using compact file: {compact_file}")

    elif input_file.endswith('.compact.txt'):
        compact_file = input_file
        print(f"Compact file detected: {compact_file}")
    else:
        print(f"Error: Input must be a .dem or .compact.txt file")
        sys.exit(1)

    # Generate the report
    print("\nGenerating tactical analysis report...")
    generate_markdown_report(compact_file)
