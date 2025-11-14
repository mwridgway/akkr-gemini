#!/bin/bash

# Check if a demo file path is provided
if [ -z "$1" ]; then
  echo "Error: No demo file path provided."
  echo "Usage: ./scripts/analyze_game.sh <path_to_demo_file>"
  exit 1
fi

DEMO_FILE_PATH="$1"

# Run the analysis pipeline
echo "Running analysis on: $DEMO_FILE_PATH"
poetry run python generate_tactical_report.py "$DEMO_FILE_PATH"

# Check if the command was successful
if [ $? -ne 0 ]; then
  echo "Error: Analysis pipeline failed."
  exit 1
fi

# Find the latest report file in the reports directory
# The report file name is based on the demo file name, so we can use that to find it.
# We'll get the base name of the demo file, without the extension.
DEMO_FILE_BASENAME=$(basename "$DEMO_FILE_PATH" .dem)
LATEST_REPORT=$(ls -t reports/game_analysis_${DEMO_FILE_BASENAME}_*.md | head -n 1)


if [ -z "$LATEST_REPORT" ]; then
  echo "Error: Could not find the generated report."
  exit 1
fi

echo "Analysis complete."
echo "Generated report: $LATEST_REPORT"
