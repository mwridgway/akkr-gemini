# GEMINI.md

This file provides guidance to the Gemini CLI when working with code in this repository.

## Project Overview

This is a **CS2 Demo Analyzer** - a Python application for parsing Counter-Strike 2 demo files and calculating strategic gameplay metrics. The project follows **Clean Architecture** principles with a modular, layered design optimized for analytical workloads.

## Gemini's Workflow for CS2 Demo Analysis

My primary goal is to provide a "one-shot" tactical analysis of a CS2 demo file. I will use the scripts and tools available in this repository to achieve this.

### Step 1: Execute the "One-Shot" Analysis Script

I will start by executing the main analysis script, which generates all the necessary analysis artifacts (compact representation, digest, and a preliminary report).

```bash
poetry run python generate_tactical_report.py "{{demo_file_path}}"
```

This command will:
- Parse the demo file.
- Create a compact representation in `data/compact/`.
- Create a digest summary in `data/digest/`.
- Generate a preliminary markdown report in `reports/`.

### Step 2: Perform In-Depth Analysis on the Compact Representation

After the main script has run, I will perform a more detailed analysis by using the `analyze_compact_demo.py` script on the generated compact file. This allows me to extract detailed metrics and insights from the structured data.

```bash
poetry run python analyze_compact_demo.py "data/compact/{{demo_filename}}.compact.txt"
```

### Step 3: Synthesize and Summarize the Findings

I will then process the output from the analysis script to identify the most important tactical insights. I will summarize these findings for you, including:

- The final match score.
- Key team performance metrics (e.g., win rates, round durations).
- Top-performing players and their key stats (K/D, entry kills).
- Critical rounds that turned the tide of the game.
- Actionable recommendations based on the analysis.

### Step 4: Present the Report

I will present the summarized findings to you in a clear and concise format. I can also provide the full analysis report upon request.

This workflow allows me to leverage the full power of the analysis tools you have built, providing a comprehensive and detailed tactical breakdown of any CS2 demo.