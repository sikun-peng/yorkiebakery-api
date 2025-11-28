#!/bin/bash
# Test runner script for Yorkie Bakery API
# This ensures the correct PYTHONPATH is set

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run pytest with all arguments passed to this script
pytest "$@"
