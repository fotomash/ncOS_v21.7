#!/bin/bash
echo "🚀 Starting NCOS Voice Journal System..."
python api/main.py &
sleep 2
streamlit run dashboard/zbar_journal_dashboard.py &
python core/ncos_voice_unified.py
