# CS2 Demo Analyzer - Setup Guide

This guide helps you set up the CS2 Demo Analyzer for the first time. After setup, you can analyze demos with simple commands from Claude Desktop.

## Prerequisites

You need these installed on your computer:

### 1. Python 3.11 or Higher

**Check if you have Python**:
```bash
python --version
```

**If you need to install**:
- Windows: Download from [python.org](https://www.python.org/downloads/)
- Mac: `brew install python@3.11`
- Linux: `sudo apt install python3.11`

### 2. Poetry (Python Package Manager)

**Check if you have Poetry**:
```bash
poetry --version
```

**If you need to install**:
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Mac/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

## Installation Steps

### Step 1: Clone or Download This Project

```bash
# If using git
git clone <repository-url>
cd akkr-gemini

# Or download and extract the ZIP file, then navigate to the folder
```

### Step 2: Install Dependencies

```bash
# Install all required Python packages
poetry install
```

This will install:
- awpy (CS2 demo parser)
- pandas (data analysis)
- polars (high-performance dataframes)
- pytest (testing)

**Expected output**: "Installing dependencies from lock file" and a list of installed packages.

### Step 3: Create Required Directories

```bash
# Windows
mkdir data\raw data\compact data\digest reports

# Mac/Linux
mkdir -p data/raw data/compact data/digest reports
```

This creates:
- `data/raw/` - Put your .dem files here
- `data/compact/` - Auto-generated compact state files
- `data/digest/` - Auto-generated digest summaries
- `reports/` - Auto-generated tactical reports

### Step 4: Add Demo Files

Copy your CS2 demo files (.dem) into `data/raw/`:

```bash
# Example
cp ~/Downloads/match.dem data/raw/
```

**Where to get demo files**:
- FACEIT: Download from match room after game ends
- HLTV: Professional match demos from hltv.org
- CS2 Game: Your own matchmaking replays

### Step 5: Test the Installation

```bash
# Activate the poetry environment
poetry shell

# Run a test analysis (if you have a demo file)
python generate_tactical_report.py "data/raw/your-demo.dem"
```

**If successful**, you should see:
```
[OK] Compact state saved: data/compact/your-demo_20251114_120000.compact.txt
Digest generated: data/digest/your-demo_20251114_120000.digest.txt
Report generated: reports/game_analysis_de_mapname_20251114_120000.md
```

## Using from Claude Desktop

Once setup is complete, you can use the skill from Claude Desktop:

### Method 1: Drag and Drop

1. Open Claude Desktop
2. Drag a .dem file into the chat
3. Type: "analyze this demo"

### Method 2: File Path

1. Open Claude Desktop
2. Type: "Analyze data/raw/my-game.dem using cs2-analyzer skill"

### Method 3: Auto-Select

1. Open Claude Desktop
2. Type: "Analyze the latest demo with cs2-analyzer"
3. Claude will list available demos for you to choose

## Troubleshooting

### Error: "python not found"

**Solution**: Install Python 3.11+ (see Prerequisites above)

### Error: "poetry not found"

**Solution**: Install Poetry (see Prerequisites above)

### Error: "Module 'awpy' not found"

**Solution**: Run `poetry install` from the project directory

### Error: "Demo file not found"

**Solution**: Check the file path. Make sure the .dem file is in `data/raw/` directory.

### Error: "awpy parsing failed"

**Possible causes**:
- Demo file is corrupted
- Demo file is from unsupported CS version (need CS2 demos)
- Demo file is incomplete (match didn't finish)

**Solution**: Try a different demo file or re-download the demo.

### Error: "Permission denied"

**Solution**:
- Windows: Run PowerShell/Command Prompt as Administrator
- Mac/Linux: Check file permissions with `chmod +x generate_tactical_report.py`

### Analysis is very slow

**Expected performance**:
- 15-round match: ~30 seconds
- 30-round match: ~45 seconds
- 50+ round match: ~60-90 seconds

If slower, check:
- SSD vs HDD (SSDs are much faster)
- Available RAM (analysis needs ~2GB)
- CPU usage (close other applications)

## Directory Structure

After setup, your project should look like this:

```
akkr-gemini/
├── .claude/
│   ├── commands/
│   │   └── analyze-game.md
│   └── skills/
│       └── cs2-analyzer/
│           ├── skill.md
│           └── prompt.md
├── data/
│   ├── raw/              ← Put .dem files here
│   ├── compact/          ← Auto-generated
│   ├── digest/           ← Auto-generated
│   └── processed/        ← Legacy (optional)
├── reports/              ← Analysis reports appear here
├── src/
│   └── cs2_analyzer/     ← Core analysis code
├── docs/
│   ├── setup.md          ← This file
│   └── analysis_tools.md
├── generate_compact.py
├── generate_digest.py
├── analyze_compact_demo.py
├── generate_tactical_report.py
└── pyproject.toml
```

## Updating

To update dependencies:

```bash
poetry update
```

To update the analysis scripts, pull latest changes:

```bash
git pull origin main
poetry install  # Re-install if dependencies changed
```

## Getting Help

If you encounter issues:

1. **Check the error message** - It usually tells you what's wrong
2. **Verify all prerequisites** are installed (Python, Poetry)
3. **Try a different demo file** - The current one might be corrupted
4. **Check docs/analysis_tools.md** - More detailed technical info
5. **Ask Claude** - Describe the error you're seeing

## Next Steps

Once setup is complete:

1. ✅ Add demo files to `data/raw/`
2. ✅ Use the cs2-analyzer skill from Claude Desktop
3. ✅ Get tactical reports in seconds
4. ✅ Share reports with your team/coach
5. ✅ Track improvement over multiple matches

Happy analyzing! 🎮
