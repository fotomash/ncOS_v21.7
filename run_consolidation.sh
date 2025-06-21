#!/bin/bash
# Quick consolidation runner for ncOS

echo "🚀 Starting ncOS Consolidation and Remapping"
echo "============================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Run the consolidation
python3 consolidate_and_remap.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Consolidation completed successfully!"
    echo ""
    echo "📁 New project structure created in: ncOS_consolidated/"
    echo "📄 Check consolidation_report.json for details"
    echo "📋 Read CONSOLIDATION_SUMMARY.md for next steps"
else
    echo ""
    echo "❌ Consolidation failed. Check the logs for details."
    exit 1
fi
