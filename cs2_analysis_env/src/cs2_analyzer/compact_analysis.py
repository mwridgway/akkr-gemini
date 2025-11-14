"""
Compact game state analysis module.

Provides utilities for generating ultra-compact game representations
and AI-driven analysis using Claude Code.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from .application.ingestion import AwpyDemoParser
from .application.delta_encoder import encode_demo_compact


def generate_compact_state(demo_path: str, sample_interval: int = 32) -> tuple[str, dict, object]:
    """
    Generate compact game state from demo file.

    Args:
        demo_path: Path to .dem file
        sample_interval: Sample positions every N ticks (32 = ~0.5s @ 64 tick)

    Returns:
        Tuple of (compact_text, metadata_dict, demo_object)
    """
    # Parse demo
    parser = AwpyDemoParser()
    demo = parser.parse(demo_path)

    # Generate compact representation
    compact_text = encode_demo_compact(demo, sample_interval)

    # Extract metadata
    metadata = {
        'demo_path': demo_path,
        'map_name': demo.header.get('map_name', 'unknown') if hasattr(demo, 'header') else 'unknown',
        'num_rounds': len(demo.rounds) if demo.rounds is not None else 0,
        'tickrate': demo.tickrate if hasattr(demo, 'tickrate') else 64,
        'generated_at': datetime.now().isoformat(),
    }

    return compact_text, metadata, demo


def save_compact_state(demo_path: str,
                       output_dir: str = 'data/compact',
                       sample_interval: int = 32,
                       force: bool = False,
                       generate_digest: bool = True) -> str:
    """
    Generate and save compact game state to file.
    Also generates a Claude-digestible summary (<50KB) for direct analysis.

    Args:
        demo_path: Path to .dem file
        output_dir: Directory to save compact state
        sample_interval: Sample positions every N ticks
        force: If True, regenerate even if output exists
        generate_digest: If True, also generate Claude-readable digest

    Returns:
        Path to saved file (existing or newly created)
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate expected filename
    demo_name = Path(demo_path).stem

    # Check for existing compact files with this demo name
    existing_files = list(output_path.glob(f"{demo_name}_*.compact.txt"))

    if existing_files and not force:
        # Use most recent existing file
        latest_file = max(existing_files, key=lambda p: p.stat().st_mtime)

        # Read metadata to check sample interval
        with open(latest_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# Sample Interval:'):
                    cached_interval = int(line.split(':')[1].strip().split()[0])
                    if cached_interval == sample_interval:
                        # Perfect match - reuse
                        file_size = latest_file.stat().st_size
                        token_est = file_size // 4

                        print(f"\n[CACHE HIT] Using existing compact state:")
                        print(f"  {latest_file}")
                        print(f"  Size: {file_size:,} bytes (~{token_est:,} tokens)")
                        print(f"  Sample interval: {cached_interval} ticks (matches requested)")
                        print(f"\n  Use --force to regenerate")
                        
                        # --- FIX: Generate digest if missing on cache hit ---
                        if generate_digest:
                            try:
                                from generate_digest import generate_digest_from_demo
                                demo_name = Path(demo_path).stem
                                # Extract timestamp from the cached compact file name
                                timestamp_match = re.search(r'(\d{8}_\d{6})', str(latest_file))
                                if timestamp_match:
                                    timestamp = timestamp_match.group(1)
                                    digest_dir = Path('data/digest')
                                    digest_filepath = digest_dir / f"{demo_name}_{timestamp}.digest.txt"

                                    if not digest_filepath.exists():
                                        print("\n[INFO] Digest file not found for cached state. Generating...")
                                        # This is inefficient as it re-parses the demo, but it's a
                                        # self-contained fix without major refactoring.
                                        _ , _, demo = generate_compact_state(demo_path, sample_interval)
                                        digest_dir.mkdir(parents=True, exist_ok=True)
                                        generate_digest_from_demo(demo, str(digest_filepath))
                            except Exception as e:
                                print(f"\n[Warning] Could not generate digest for cached file: {e}")
                        # --- END FIX ---

                        return str(latest_file)
                    break

        print(f"\n[CACHE MISS] Existing file has different sample interval, regenerating...")

    # Generate compact state
    compact_text, metadata, demo = generate_compact_state(demo_path, sample_interval)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{demo_name}_{timestamp}.compact.txt"
    filepath = output_path / filename

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# METADATA\n")
        f.write(f"# Generated: {metadata['generated_at']}\n")
        f.write(f"# Source: {metadata['demo_path']}\n")
        f.write(f"# Map: {metadata['map_name']}\n")
        f.write(f"# Rounds: {metadata['num_rounds']}\n")
        f.write(f"# Tickrate: {metadata['tickrate']}\n")
        f.write(f"# Sample Interval: {sample_interval} ticks\n")
        f.write(f"#\n")
        f.write(compact_text)

    # Estimate token count
    token_est = len(compact_text) // 4
    print(f"\n[OK] Compact state saved: {filepath}")
    print(f"  Size: {len(compact_text):,} chars (~{token_est:,} tokens)")
    print(f"  Map: {metadata['map_name']}")
    print(f"  Rounds: {metadata['num_rounds']}")

    # Generate Claude-digestible summary if requested
    if generate_digest:
        try:
            from generate_digest import generate_digest_from_demo

            # Create digest directory
            digest_dir = Path('data/digest')
            digest_dir.mkdir(parents=True, exist_ok=True)

            # Generate digest filename (same timestamp as compact file)
            digest_filename = f"{demo_name}_{timestamp}.digest.txt"
            digest_filepath = digest_dir / digest_filename

            # Generate digest
            print(f"\n[Generating digest...]")
            generate_digest_from_demo(demo, str(digest_filepath))

        except Exception as e:
            print(f"\n[Warning] Could not generate digest: {e}")
            # Don't fail the whole operation if digest fails

    return str(filepath)


def create_analysis_template(demo_path: str,
                             compact_state_path: Optional[str] = None) -> str:
    """
    Create markdown template for game analysis.

    Args:
        demo_path: Original demo file path
        compact_state_path: Path to compact state file (optional)

    Returns:
        Markdown template string
    """
    demo_name = Path(demo_path).stem
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    template = f"""# CS2 Tactical Analysis: {demo_name}
**Date**: {timestamp}
**Demo**: {demo_path}
{f'**Compact State**: {compact_state_path}' if compact_state_path else ''}

## Executive Summary
[3-5 bullet points with key insights]

-
-
-

## Team Performance

### T-Side Analysis
- **Pacing**: [TTFK, plant timing, tempo observations]
- **Aggression**: [Push patterns, site preference, fakes]
- **Executes**: [Entry success, trade efficiency, post-plant performance]

### CT-Side Analysis
- **Setup**: [Default positions, rotations, aggression]
- **Retakes**: [Success rate, player coordination]
- **Adaptations**: [Counter-strats observed]

## Critical Rounds

### Round X: [Brief description]
- **Timeline**: [Key events with tick timestamps]
- **Turning Point**: [What decided the round]
- **Tactical Note**: [What this reveals about team strategy]

## Player Highlights

### Top Performers
- **[Player Name]**: [Impact plays, positioning notes]

### Areas for Improvement
- **[Player Name]**: [Issues observed, recommendations]

## Strategic Recommendations

1. **For T-Side**: [Specific tactical adjustments]
2. **For CT-Side**: [Specific tactical adjustments]
3. **Individual**: [Player-specific coaching points]

## Appendix: Metrics Summary
| Metric | Value | Notes |
|--------|-------|-------|
| Avg TTFK | - | - |
| Avg Bomb Plant Time | - | - |
| T Entry Success Rate | - | - |
| Trade Efficiency | - | - |
| Post-Plant Win Rate | - | - |
| CT Rotation Success | - | - |
"""

    return template
