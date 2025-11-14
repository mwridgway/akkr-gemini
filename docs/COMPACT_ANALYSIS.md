# Compact Game State Analysis

## Overview

This feature provides an **ultra-compact text representation** of CS2 game state optimized for AI-driven analysis with Claude Code. Instead of pre-calculating metrics, it creates a human-readable but maximally compressed format that fits in Claude's context window, allowing for flexible, natural language analysis.

## Key Features

- **10-30x compression** vs standard Parquet storage
- **Human-readable** text format with legend/index system
- **Delta encoding** for positions (only store changes)
- **Player indexing** (P0-P9 instead of 64-bit steamids)
- **Event abbreviations** (D=death, BP=plant, etc.)
- **Token-optimized** (~50K-150K tokens for full game)

## Quick Start

### 1. Generate Compact Game State

```bash
# Basic usage
poetry run python generate_compact.py path/to/demo.dem

# Custom sample interval (higher = more compression, less detail)
poetry run python generate_compact.py path/to/demo.dem --interval 64

# Custom output directory
poetry run python generate_compact.py path/to/demo.dem --output analysis/compact
```

### 2. Analyze with Claude Code

Use the `/analyze-game` slash command:

```
/analyze-game data/raw/falcons-vs-vitality-m1-inferno.dem
```

This will:
1. Generate the compact game state
2. Guide Claude to analyze it
3. Produce a markdown report in `reports/`

## Format Specification

### Header Section

```
# MAP: de_ancient | ROUNDS: 15 | TICK: 64
# PLAYERS: P0:s1mple(T) P1:electroNic(T) ... P9:ZywOo(CT)
# SITES: A(123,456,10) B(789,234,10)
# FORMAT LEGEND:
#   Positions: tick:X,Y,Z,yaw,pitch (initial) then tick:+dX,+dY,+dZ,+dy,+dp (deltas)
#   Events: tick:CODE,params | D=death H=hurt BP=plant BD=defuse
#   Players: P0-P9 indexed above
```

### Round Section

```
## ROUND 0 (t win) | t1000-t7500
### Positions
P0 1000:100,200,50,90,0 1032:+2,+3,0,+1,0 1064:-1,+5,0,0,0
P1 1000:150,200,50,85,5 1032:+1,+2,0,0,0
...
### Events
1234:D,P3>P8,AK,HS | 1235:H,P8>P3,25 | 5234:BP,P2,A
```

### Position Format

- **Initial**: `tick:X,Y,Z,yaw,pitch` (absolute coordinates)
- **Delta**: `tick:+dX,+dY,+dZ,+dyaw,+dpitch` (changes from last position)
- Only includes movement above threshold (stationary players omitted)

### Event Codes

| Code | Meaning | Format |
|------|---------|--------|
| `D` | Death | `tick:D,P{attacker}>P{victim},{weapon},HS?` |
| `BP` | Bomb Plant | `tick:BP,P{planter},{site}` |
| `BD` | Bomb Defuse | `tick:BD,P{defuser}` |
| `H` | Player Hurt | `tick:H,P{attacker}>P{victim},{damage}` |
| `F` | Weapon Fire | `tick:F,P{shooter},{weapon}` |
| `G` | Grenade | `tick:G,P{thrower},{type}` |
| `SM` | Smoke Started | `tick:SM,{X},{Y},{Z}` |
| `IN` | Inferno Started | `tick:IN,{X},{Y},{Z}` |

### Weapon Codes

`AK`=AK47, `AWP`=AWP, `M4`=M4A1, `DE`=Deagle, `GL`=Glock, `USP`=USP

## Compression Characteristics

### Typical Game (15 rounds, 64 tick)

| Component | Raw Data | Parquet | Compact | Ratio |
|-----------|----------|---------|---------|-------|
| Positions | ~22,000 records | 2-3 MB | 50-100 KB | 20-60x |
| Events | ~3,000 records | 200-400 KB | 50-80 KB | 4-8x |
| Metadata | Minimal | 5 KB | 2 KB | 2x |
| **Total** | **~650 KB** | **2-5 MB** | **100-200 KB** | **10-30x** |

### Token Estimates

- **Full game** (all rounds, 32-tick sampling): 50K-150K tokens
- **Single round**: 3K-10K tokens
- **Critical events only**: 10K-30K tokens

## Use Cases

### 1. AI-Driven Analysis

Let Claude analyze the compact state and produce:
- Strategic patterns
- Tactical recommendations
- Player performance insights
- Round-by-round breakdowns

### 2. Rapid Prototyping

Test new analysis ideas without implementing metric calculations:
- Ask Claude to calculate custom metrics
- Explore data interactively
- Validate hypotheses quickly

### 3. Context-Aware Reports

Generate reports that reference specific moments:
- "At tick 5234, P2 planted at A"
- "P3 got the entry at tick 1234"
- Natural language with precise references

### 4. Streaming/Live Analysis

Potential future use:
- Stream compact deltas during live match
- Real-time AI commentary
- Coach dashboards

## API Usage

### Python API

```python
from src.cs2_analyzer.compact_analysis import (
    generate_compact_state,
    save_compact_state,
    create_analysis_template
)

# Generate compact representation
compact_text, metadata = generate_compact_state(
    demo_path="path/to/demo.dem",
    sample_interval=32
)

print(f"Token estimate: {len(compact_text) // 4:,}")

# Save to file
output_path = save_compact_state(
    demo_path="path/to/demo.dem",
    output_dir="data/compact",
    sample_interval=32
)

# Create analysis template
template = create_analysis_template(
    demo_path="path/to/demo.dem",
    compact_state_path=output_path
)
```

### Delta Encoder API

```python
from src.cs2_analyzer.application.delta_encoder import (
    DeltaEncoder,
    encode_demo_compact
)
from src.cs2_analyzer.application.ingestion import AwpyDemoParser

# Parse demo
parser = AwpyDemoParser()
demo = parser.parse("path/to/demo.dem")

# Quick encoding
compact_text = encode_demo_compact(demo, sample_interval=32)

# Advanced usage
encoder = DeltaEncoder(demo)
compact = encoder.encode(sample_interval=32)

print(f"Header:\n{compact.header}\n")
print(f"Round 0:\n{compact.rounds[0]}\n")
print(f"Estimated tokens: {compact.token_estimate():,}")
```

## Configuration

### Sample Interval Tuning

The `sample_interval` parameter controls compression vs detail tradeoff:

| Interval | Samples/sec (64 tick) | Detail Level | Use Case |
|----------|-----------------------|--------------|----------|
| 16 | 4/sec | High | Detailed movement analysis |
| 32 | 2/sec | Medium (default) | General analysis |
| 64 | 1/sec | Low | High-level overview |
| 128 | 0.5/sec | Minimal | Executive summary |

### Position Threshold

Positions are only recorded if:
- X/Y/Z changes OR
- Yaw changes > 5° OR
- Pitch changes > 5°

Stationary players are omitted to save space.

## Troubleshooting

### "Column not found" error

Ensure awpy version compatibility:
```bash
poetry show awpy
# Should be 2.0.2 or later
```

### Large token counts

Reduce sample interval:
```bash
poetry run python generate_compact.py demo.dem --interval 64
```

### Missing events

Check if event type is implemented in `delta_encoder.py`:
- Currently: death, bomb plant, bomb defuse
- Add more in `_encode_events()` method

## Future Enhancements

- [ ] Binary format option (MessagePack/Protobuf)
- [ ] Incremental/streaming encoding
- [ ] Keyframe + delta hybrid (periodic full state)
- [ ] Additional event types (grenades, smokes, mollies)
- [ ] Inventory tracking (weapon pickups/drops)
- [ ] Player stats deltas (health, armor, money)
- [ ] Map heatmap integration
- [ ] Web viewer for compact format

## Performance

Parsing a 460MB demo file:
- **Parsing time**: ~30-60 seconds (awpy overhead)
- **Encoding time**: ~5-10 seconds
- **Total**: ~40-70 seconds
- **Output size**: ~100-200 KB (1/2000th of input)

## Related Files

- `src/cs2_analyzer/application/delta_encoder.py` - Core encoding logic
- `src/cs2_analyzer/compact_analysis.py` - High-level API
- `generate_compact.py` - CLI tool
- `.claude/commands/analyze-game.md` - Slash command for analysis
- `reports/` - Generated analysis reports
- `data/compact/` - Compact state files
