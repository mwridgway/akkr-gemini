---
description: Analyze a CS2 demo file using Claude with ultra-compact game state representation
args: demo_file_path
---

You are a CS2 tactical analyst. Your task is to analyze a CS2 demo file and produce a comprehensive strategic report.

## Architecture Overview

The analysis uses a multi-tier approach:
1. **Compact State** (.compact.txt) - Storage format (~400KB, 100K tokens) - NOT for Claude reading
2. **Digest** (.digest.txt) - Claude-readable summary (<50KB) - Read this for strategic insights
3. **Full Report** (.md) - Comprehensive tactical analysis - Final deliverable

## Demo File Selection

Demo file provided: {{demo_file_path}}

**If no demo file path provided**: List available demos in `data/raw/` and ask user which to analyze.

## Workflow (3 Steps)

### Step 1: Generate All Formats

Run this single command:

```bash
poetry run python generate_tactical_report.py "{{demo_file_path}}"
```

This automatically creates:
- Compact state in `data/compact/`
- **Digest in `data/digest/`** ← Claude reads this
- Full report in `reports/`

### Step 2: Read the Digest for Strategic Analysis

Find and read the digest file from `data/digest/` (will match the demo filename with timestamp).

The digest contains:
- Game metadata and player roster
- Round-by-round summaries
- Player statistics
- Key events timeline
- Strategic insights

Use this to understand game flow and identify patterns directly.

### Step 3: Review and Enhance the Generated Report

Read the full markdown report from `reports/` and:
1. Verify it captures the key insights you identified from the digest
2. Add additional strategic observations based on your digest analysis
3. Enhance tactical recommendations with specific examples
4. Summarize findings for the user

## After Report Generation

1. **Read the generated report** from `reports/` directory
2. **Summarize key findings** for the user with:
   - Match result (final score)
   - Top 3 strategic insights
   - Best performing player
   - Most critical recommendation
3. **Offer to dive deeper** into specific areas if user wants details

The Python script automatically calculates:
- **Pacing patterns**: Time to first kill, bomb plant timing, death clustering
- **Aggression profiles**: T-side push patterns, CT forward holds, player spacing
- **Rotational efficiency**: CT rotation speed and success rates
- **Execute effectiveness**: Entry success, trade efficiency, post-plant win rates
- **Critical rounds**: Eco rounds, force buys, clutch situations
- **Player performance**: Individual impact, positioning, decision-making

## Manual Analysis (If Script Fails)

If the Python script doesn't work, generate compact state and analyze manually:

```bash
poetry run python generate_compact.py "{{demo_file_path}}"
```

**Note**: The compact file will be too large to read directly. Instead, use grep/bash to extract specific sections:
- Metadata and player list (first 20 lines)
- Specific rounds of interest
- Event sequences

Then use the metrics framework to calculate insights and write the report manually.

## Report Quality Guidelines

When reviewing the generated report, ensure it:
- Focuses on **WHY** not just WHAT - explains strategic implications
- Uses **specific examples** with tick timestamps and round numbers
- Stays **concise** - this is for coaches/players, not academics
- Highlights **actionable insights** - what can the team change?
- Considers **context** - eco rounds vs gun rounds, advantages/disadvantages

## Workflow Summary

1. ✅ Run `poetry run python generate_tactical_report.py "{{demo_file_path}}"`
2. ✅ Read the generated markdown report from `reports/`
3. ✅ Summarize key findings for user (final score, top insights, MVP, recommendations)
4. ✅ Offer to dive deeper into specific areas

**Start now with the demo file**: {{demo_file_path}}
