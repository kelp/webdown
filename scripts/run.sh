#!/bin/bash
# Script to find and execute commands in the right environment
# Usage: scripts/run.sh <command> [arguments]

# Find the project root (where this script is located)
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Check for virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    # Use in-project virtualenv
    VENV_PATH="$PROJECT_ROOT/.venv"
else
    # Try to get Poetry virtualenv path
    VENV_PATH=$(cd "$PROJECT_ROOT" && poetry env info -p 2>/dev/null)
fi

if [ -n "$VENV_PATH" ]; then
    # Activate the virtualenv in the current shell
    export PATH="$VENV_PATH/bin:$PATH"
    export VIRTUAL_ENV="$VENV_PATH"
else
    echo "No virtualenv found. Installing dependencies..."
    (cd "$PROJECT_ROOT" && poetry install)

    # Try again to find the virtualenv
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        VENV_PATH="$PROJECT_ROOT/.venv"
    else
        VENV_PATH=$(cd "$PROJECT_ROOT" && poetry env info -p 2>/dev/null)
    fi

    if [ -n "$VENV_PATH" ]; then
        export PATH="$VENV_PATH/bin:$PATH"
        export VIRTUAL_ENV="$VENV_PATH"
    else
        echo "Failed to set up virtualenv. Please check your Poetry installation."
        exit 1
    fi
fi

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

# Run the command
"$@"
