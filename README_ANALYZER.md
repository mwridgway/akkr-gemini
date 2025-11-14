# CS2 Demo Analyzer - Complete Guide

**One-command tactical analysis for Counter-Strike 2 demo files**

## 🎯 What This Does

Transforms CS2 demo files (.dem) into professional tactical analysis reports in 30-60 seconds.

**Input**: `match.dem` (10-50 MB)
**Output**: Comprehensive markdown report with strategic insights, player stats, and coaching recommendations

## 🚀 Quick Start

### For End Users (Non-Technical)

**Step 1: One-Time Setup** (~5 minutes)
```bash
# Install dependencies
poetry install

# Create directories
mkdir data/raw data/compact data/digest reports
```
See `docs/setup.md` for detailed setup instructions.

**Step 2: Add Your Demo**
```bash
# Put your .dem file in data/raw/
cp ~/Downloads/your-match.dem data/raw/
```

**Step 3: Analyze**
```bash
# Single command - does everything
poetry run python generate_tactical_report.py "data/raw/your-match.dem"
```

**Step 4: Read Report**
```
Open: reports/game_analysis_[map]_[timestamp].md
```

### For Claude Desktop Users

After one-time setup, you can analyze demos through conversation:

1. **Drag and drop** a .dem file into Claude Desktop
2. Say: **"Analyze this demo using cs2-analyzer"**
3. Claude will:
   - Run the analysis pipeline
   - Read the digest and full report
   - Give you a concise summary with key insights
   - Provide the full report file path

**Alternative**: Say "Analyze data/raw/my-game.dem" and Claude will handle it.

## 📊 What You Get

### Executive Summary
- Final score (T vs CT)
- Top 3-5 strategic insights
- MVP player with stats
- Most critical recommendation

### Team Performance Analysis
- **T-Side**: Pacing, aggression, execute effectiveness
- **CT-Side**: Setup quality, retake success, rotations

### Critical Rounds Breakdown
- 5 most tactically important rounds
- Timeline of key events (with timestamps)
- Tactical implications

### Player Highlights
- Top 3 performers with detailed stats
- Bottom 3 with improvement areas
- K/D ratios, entry kills, survival rates

### Tactical Recommendations
- Specific T-side adjustments
- Specific CT-side adjustments
- Individual coaching points

### Metrics Appendix
- Time to First Kill (TTFK)
- Bomb Plant Timing
- Entry Success Rate
- Post-Plant Win Rate
- Round Duration
- Deaths Per Round
- Full player statistics table

## 🏗️ Architecture

The analyzer uses a **three-tier approach**:

```
.dem file (10-50 MB)
    ↓
    ↓ [Step 1: Parse with awpy]
    ↓
Demo Object (in memory)
    ↓
    ├─→ Tier 1: Compact State (.compact.txt, ~400KB, 100K tokens)
    │   Purpose: Efficient storage format
    │   Use: Archival, future re-analysis
    │
    ├─→ Tier 2: Digest (.digest.txt, <50KB, <15K tokens)
    │   Purpose: Claude-readable summary
    │   Use: Quick insights, strategic review
    │
    └─→ Tier 3: Full Report (.md, ~10KB)
        Purpose: Comprehensive tactical analysis
        Use: Final deliverable for coaches/players
```

### Why Three Tiers?

1. **Compact State** - Too large for Claude to read directly, but efficient for storage
2. **Digest** - Optimized for Claude to read and analyze (future feature - needs debugging)
3. **Full Report** - Human-readable, shareable, printable

## 🛠️ Tools & Commands

### Primary Command (Recommended)
```bash
# Does everything: compact + digest + report
poetry run python generate_tactical_report.py "demo.dem"
```

### Individual Tools
```bash
# Generate only compact state
poetry run python generate_compact.py "demo.dem"

# Generate only digest (requires demo file)
poetry run python generate_digest.py "demo.dem"

# Analyze existing compact file
poetry run python analyze_compact_demo.py "data/compact/demo.compact.txt"
```

### From Claude Code
```bash
# Use the slash command
/analyze-game data/raw/your-demo.dem
```

## 📁 File Structure

```
akkr-gemini/
├── data/
│   ├── raw/                    ← PUT .DEM FILES HERE
│   ├── compact/                ← Auto-generated storage format
│   ├── digest/                 ← Auto-generated Claude summaries
│   └── processed/              ← Legacy (optional)
│
├── reports/                    ← ANALYSIS REPORTS APPEAR HERE
│   └── game_analysis_*.md
│
├── .claude/
│   ├── commands/
│   │   └── analyze-game.md     ← Slash command for Claude Code
│   └── skills/
│       └── cs2-analyzer/       ← Skill for Claude Desktop
│
├── docs/
│   ├── setup.md                ← One-time setup guide
│   └── analysis_tools.md       ← Technical documentation
│
├── src/cs2_analyzer/           ← Core analysis library
│
└── Scripts:
    ├── generate_compact.py         ← Tier 1 generator
    ├── generate_digest.py          ← Tier 2 generator
    ├── analyze_compact_demo.py     ← Metrics calculator
    └── generate_tactical_report.py ← Main pipeline (ALL IN ONE)
```

## 📈 Performance

- **15-round match**: ~30 seconds
- **30-round match**: ~45 seconds
- **50-round match**: ~60-90 seconds

**Output sizes**:
- Compact: ~400-900 KB (depends on rounds)
- Digest: ~3-10 KB
- Report: ~5-15 KB

## 🎓 Example Workflow

### Scenario: Analyzing Team Performance

1. **Coach gets demo file** from FACEIT after scrim
   ```bash
   cp ~/Downloads/scrim-vs-teamX.dem data/raw/
   ```

2. **Run analysis**
   ```bash
   poetry run python generate_tactical_report.py "data/raw/scrim-vs-teamX.dem"
   ```

3. **Review report** (opens in 30 seconds)
   ```
   reports/game_analysis_de_mirage_20251114_143022.md
   ```

4. **Key findings** (from report):
   - T-side struggling: 35% round win rate
   - Post-plant disasters: Only 45% win rate (should be 70%+)
   - Entry fragging weak: 38% success
   - Player X: 0.6 K/D, needs positioning work

5. **Coach uses insights** for:
   - VOD review focus areas
   - Practice drills (post-plant setups)
   - Individual coaching (Player X positioning)
   - Next scrim strategy adjustments

## 🔧 For Developers

### Adding New Metrics

Edit `analyze_compact_demo.py`:
```python
def calculate_new_metric(metadata, rounds):
    """Calculate your metric."""
    # Your logic here
    return metric_value
```

Then add to report in `generate_tactical_report.py`.

### Modifying Report Format

Edit `generate_tactical_report.py` in the `generate_markdown_report()` function.

### Testing

```bash
# Run all tests
poetry run pytest

# Test specific metric
poetry run pytest tests/test_metrics.py::test_calculate_ttfk
```

## ❓ Troubleshooting

### "Demo file not found"
- Check file path is correct
- Ensure file is in `data/raw/` directory
- Use absolute path if needed

### "awpy parsing failed"
- Demo file might be corrupted
- Ensure it's a CS2 demo (not CS:GO)
- Try re-downloading the demo

### "Module not found"
- Run `poetry install`
- Activate environment: `poetry shell`

### Analysis is slow
- Expected for long matches (50+ rounds)
- Check available RAM (needs ~2GB)
- Use SSD instead of HDD if possible

### Empty digest generated
- Known issue - digest data extraction needs debugging
- Full report still works perfectly
- Track progress: Issue #TBD

## 🚀 Future Enhancements

**Short-term**:
- [x] Three-tier architecture
- [x] Single-command analysis
- [x] Comprehensive reports
- [ ] Debug digest data extraction
- [ ] CLI wrapper script

**Medium-term**:
- [ ] Multi-demo comparison
- [ ] Positional heatmaps
- [ ] Utility usage analysis
- [ ] Economic analysis

**Long-term**:
- [ ] Interactive query mode
- [ ] Real-time streaming analysis
- [ ] ML-based pattern recognition
- [ ] Team performance dashboards

## 📝 Credits

Built with:
- **awpy** - CS2 demo parser
- **Polars** - High-performance dataframes
- **Pandas** - Data manipulation
- **Claude Code** - AI-assisted development

## 📄 License

[Your license here]

## 🤝 Contributing

Contributions welcome! Please read docs/contributing.md first.

---

**Questions?** Check `docs/setup.md` or `docs/analysis_tools.md` for more details.
