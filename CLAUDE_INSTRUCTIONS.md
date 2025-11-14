# Instructions for Claude Desktop

When analyzing CS2 demo files in this project, follow these steps:

## Quick Analysis

When user says "analyze [demo file]" or drags a .dem file:

1. **Run the analysis pipeline**:
   ```bash
   poetry run python generate_tactical_report.py "DEMO_FILE_PATH"
   ```

2. **Read the digest** (if available):
   - File location: `data/digest/[demo_name]_[timestamp].digest.txt`
   - Contains: Round-by-round summary, player stats, key events

3. **Read the full report**:
   - File location: `reports/game_analysis_[map]_[timestamp].md`
   - Contains: Complete tactical analysis

4. **Summarize for user**:
   ```
   ✅ Analysis Complete: [Map Name]

   📊 Match Overview:
   - Final Score: T X - Y CT
   - Rounds: Z

   🎯 Top 3 Strategic Insights:
   1. [Insight 1]
   2. [Insight 2]
   3. [Insight 3]

   ⭐ MVP: [Player Name]
   - [K/D ratio]
   - [Key stats]

   💡 Critical Recommendation:
   [Most important tactical adjustment needed]

   📄 Full Report: [file path]
   ```

## Available Commands

- `poetry run python generate_tactical_report.py "path/to/demo.dem"` - Full analysis (recommended)
- `poetry run python generate_compact.py "path/to/demo.dem"` - Generate compact state only
- `poetry run python analyze_compact_demo.py "path/to/compact.txt"` - Analyze existing compact file

## File Locations

- **Input demos**: `data/raw/` (user puts .dem files here)
- **Compact states**: `data/compact/` (auto-generated)
- **Digests**: `data/digest/` (auto-generated, <50KB summaries)
- **Reports**: `reports/` (auto-generated, final markdown reports)

## Error Handling

If analysis fails:
- Check if demo file exists
- Verify poetry environment is active
- Ensure dependencies are installed (poetry install)
- Try a different demo file (might be corrupted)

## Example Usage

**User**: "Analyze the Dust2 demo"

**You**:
1. List .dem files in data/raw/
2. Ask which one if multiple Dust2 demos
3. Run analysis command
4. Read outputs
5. Provide summary
