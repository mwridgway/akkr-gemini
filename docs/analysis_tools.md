# CS2 Demo Analysis Tools

## Overview

This directory contains Python scripts for analyzing CS2 demo files and generating tactical reports. The workflow uses an ultra-compact game state representation for efficient processing.

## Quick Start

**Generate a tactical report from a demo file:**

```bash
poetry run python generate_tactical_report.py "data/raw/your-demo.dem"
```

This single command will:
1. Generate the compact game state representation (if needed)
2. Calculate all strategic metrics
3. Create a comprehensive markdown report in `reports/`

## Available Scripts

### 1. `generate_compact.py`
Converts a CS2 `.dem` file into an ultra-compact text representation.

**Usage:**
```bash
poetry run python generate_compact.py "data/raw/demo.dem"
```

**Output:**
- Compact file saved to: `data/compact/demo_YYYYMMDD_HHMMSS.compact.txt`
- File size: ~400KB (vs several MB for raw demo)
- Format: Delta-encoded positions + event sequences

**Options:**
- Sample interval: 32 ticks (configurable in script)
- Caching: Automatically reuses existing compact files if sample interval matches

### 2. `analyze_compact_demo.py`
Parses compact game state and calculates strategic metrics.

**Usage:**
```bash
poetry run python analyze_compact_demo.py "data/compact/demo.compact.txt"
```

**Output:** Console summary with:
- Team performance (T/CT win rates)
- Strategic metrics (TTFK, bomb plant timing, entry success, etc.)
- Player statistics (K/D, entry kills)
- Critical round identification

**Metrics Calculated:**
- Time To First Kill (TTFK)
- Bomb Plant Timing
- Round Duration
- Deaths Per Round
- Entry Success Rate
- Post-Plant Win Rate
- Player K/D ratios

### 3. `generate_tactical_report.py` ⭐
**Primary tool** - Generates comprehensive markdown tactical analysis.

**Usage:**
```bash
# From demo file (auto-generates compact state)
poetry run python generate_tactical_report.py "data/raw/demo.dem"

# From existing compact file
poetry run python generate_tactical_report.py "data/compact/demo.compact.txt"
```

**Output:**
- Markdown report: `reports/game_analysis_[map]_[timestamp].md`
- Includes: Executive summary, team analysis, critical rounds, player highlights, recommendations

## Analysis Workflow for Claude

**When using the `/analyze-game` slash command:**

1. **DO NOT** try to read the compact file directly (it's 100K+ tokens)
2. **DO** run `generate_tactical_report.py` which handles everything
3. **DO** read the generated markdown report from `reports/`
4. **DO** summarize key findings for the user

### Typical Claude Workflow:

```bash
# Step 1: Generate report (single command)
poetry run python generate_tactical_report.py "path/to/demo.dem"

# Step 2: Read the generated report
# (File will be in reports/ directory)

# Step 3: Summarize findings
# - Final score
# - Top 3 insights
# - MVP player
# - Key recommendations
```

## Compact Format Reference

The compact game state uses:

- **Player indices**: P0-P9 (mapped in header)
- **Positions**: `tick:X,Y,Z,yaw,pitch` then delta encoding `tick:+dX,+dY,+dZ,+dyaw,+dpitch`
- **Events**: `tick:CODE,params`
  - `D` = death
  - `BP` = bomb plant
  - `BD` = bomb defuse
  - `H` = hurt
  - `F` = fire
  - `G` = grenade throw
  - `SM` = smoke
  - `IN` = incendiary/molly
- **Ticks**: Absolute game ticks (divide by tickrate for seconds)

## Report Structure

Generated reports include:

### 1. Executive Summary
- 3-5 key strategic insights
- Match result
- Top performer
- Critical metrics

### 2. Team Performance
- **T-Side Analysis**: Pacing, aggression, executes, entry success
- **CT-Side Analysis**: Setup, retakes, rotational efficiency

### 3. Critical Rounds
- 5 most tactically interesting rounds
- Timeline of key events with timestamps
- Tactical implications

### 4. Player Highlights
- Top 3 performers with stats
- Bottom 3 with improvement areas
- K/D ratios, entry kills, survival rates

### 5. Strategic Recommendations
- T-side tactical adjustments
- CT-side tactical adjustments
- Individual coaching points

### 6. Appendix
- Full metrics table
- Complete player statistics

## File Sizes

- **Raw .dem file**: 10-50 MB
- **Compact .txt file**: ~400 KB (100K tokens)
- **Generated report**: 5-15 KB

## Performance

- Compact generation: ~10-30 seconds
- Analysis + report: ~2-5 seconds
- Total end-to-end: ~15-35 seconds

## Troubleshooting

**Issue**: "No compact file found"
- **Solution**: The script will auto-generate it if you provide a .dem file

**Issue**: "File too large to read"
- **Solution**: Don't read compact files directly - use the Python scripts

**Issue**: "awpy parsing error"
- **Solution**: Check demo file integrity, ensure it's a valid CS2 demo

## Future Improvements

Potential enhancements:
- [ ] Claude-digestible summary format (<50KB)
- [ ] Positional heatmap analysis
- [ ] Utility usage patterns
- [ ] Economic analysis (force buys, eco rounds)
- [ ] Clutch situation identification
- [ ] Trading effectiveness by player pair
