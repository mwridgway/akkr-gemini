#!/usr/bin/env python3
"""Investigate awpy demo structure."""

import sys
from src.cs2_analyzer.application.ingestion import AwpyDemoParser

def main():
    demo_path = "data/raw/falcons-vs-vitality-m1-inferno.dem"

    print(f"Parsing demo: {demo_path}\n")
    parser = AwpyDemoParser()
    demo = parser.parse(demo_path)

    print("=" * 60)
    print("DEMO OBJECT STRUCTURE")
    print("=" * 60)

    # Check attributes
    print(f"\nAttributes: {dir(demo)}")

    # Header
    if hasattr(demo, 'header'):
        print(f"\nHeader: {demo.header}")

    # Players
    print(f"\nT Players type: {type(demo.t_players) if hasattr(demo, 't_players') else 'N/A'}")
    if hasattr(demo, 't_players') and demo.t_players:
        print(f"T Players ({len(demo.t_players)}): {demo.t_players[:3]}")

    print(f"\nCT Players type: {type(demo.ct_players) if hasattr(demo, 'ct_players') else 'N/A'}")
    if hasattr(demo, 'ct_players') and demo.ct_players:
        print(f"CT Players ({len(demo.ct_players)}): {demo.ct_players[:3]}")

    # Ticks
    if hasattr(demo, 'ticks') and demo.ticks is not None:
        print(f"\nTicks DataFrame:")
        print(f"  Shape: {demo.ticks.shape}")
        print(f"  Columns: {demo.ticks.columns}")

        # Get unique players
        unique_players = demo.ticks.select(['steamid', 'name', 'side']).unique()
        print(f"\n  Unique players ({len(unique_players)}):")
        for row in unique_players.iter_rows(named=True):
            print(f"    {row['steamid']}: {row['name']} ({row['side']})")
    else:
        print(f"\nTicks: None or missing")

    # Rounds
    if hasattr(demo, 'rounds') and demo.rounds is not None:
        print(f"\nRounds DataFrame:")
        print(f"  Shape: {demo.rounds.shape}")
        print(f"  Columns: {demo.rounds.columns}")

    # Events
    if hasattr(demo, 'events') and demo.events:
        print(f"\nEvents available: {list(demo.events.keys())}")
        if 'player_death' in demo.events:
            deaths = demo.events['player_death']
            print(f"\nPlayer Deaths DataFrame:")
            print(f"  Shape: {deaths.shape}")
            print(f"  Columns: {deaths.columns}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total ticks: {demo.ticks.shape[0]:,}")
    print(f"Total rounds: {demo.rounds.shape[0] if demo.rounds is not None else 0}")
    print(f"Total deaths: {demo.events['player_death'].shape[0] if 'player_death' in demo.events else 0}")
    print(f"Tickrate: {demo.tickrate}")

if __name__ == '__main__':
    main()
