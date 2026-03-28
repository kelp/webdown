#!/bin/bash
# Script to execute commands in the right environment using uv
# Usage: scripts/run.sh <command> [arguments]

# Find the project root (where this script is located)
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Execute whatever command was passed
if [ $# -eq 0 ]; then
    echo "No command specified."
    echo "Usage: $0 <command> [arguments]"
    echo "Examples:"
    echo "  $0 pytest                  # Run tests"
    echo "  $0 pre-commit run          # Run pre-commit manually"
    echo "  $0 python -m webdown.cli   # Run the CLI"
    exit 1
fi

# Run the command via uv
cd "$PROJECT_ROOT" && exec uv run "$@"
