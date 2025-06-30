#!/bin/bash
# Run all tests and save an HTML report with timestamp

set -e

# Ensure the tests directory exists
mkdir -p tests

# Generate timestamp for unique filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="tests/reports/report_${TIMESTAMP}.html"

# Run pytest and generate the HTML report
pytest --html="$REPORT_FILE" --self-contained-html

echo "Test report saved to $REPORT_FILE"