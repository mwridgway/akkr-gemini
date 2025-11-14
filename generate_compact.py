#!/usr/bin/env python3
"""
Generate compact game state representation from CS2 demo file.

Usage:
    python generate_compact.py path/to/demo.dem
    python generate_compact.py path/to/demo.dem --interval 64 --output data/compact
"""

import sys
import argparse
from pathlib import Path

from src.cs2_analyzer.compact_analysis import save_compact_state


def main():
    parser = argparse.ArgumentParser(
        description='Generate ultra-compact game state from CS2 demo file'
    )
    parser.add_argument(
        'demo_path',
        help='Path to CS2 demo file (.dem)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=32,
        help='Position sample interval in ticks (default: 32 = ~0.5s @ 64 tick)'
    )
    parser.add_argument(
        '--output',
        default='data/compact',
        help='Output directory for compact state files (default: data/compact)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration even if output file exists'
    )

    args = parser.parse_args()

    # Validate demo file exists
    demo_file = Path(args.demo_path)
    if not demo_file.exists():
        print(f"Error: Demo file not found: {args.demo_path}", file=sys.stderr)
        return 1

    print(f"\nGenerating compact game state...")
    print(f"   Demo: {args.demo_path}")
    print(f"   Sample interval: {args.interval} ticks")
    print(f"   Output: {args.output}/\n")

    try:
        # Generate and save compact state
        output_path = save_compact_state(
            demo_path=args.demo_path,
            output_dir=args.output,
            sample_interval=args.interval,
            force=args.force
        )

        print(f"\nSuccess! Use this file for Claude Code analysis:")
        print(f"   {output_path}\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error generating compact state: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
