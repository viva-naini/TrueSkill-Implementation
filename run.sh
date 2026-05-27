#!/bin/bash
# Run script for Ultimate Frisbee Power Rankings

cd "$(dirname "$0")"
if [ -d ".venv" ]; then
	source .venv/bin/activate
elif [ -d "venv" ]; then
	source venv/bin/activate
fi

# Use the activated Python to run Streamlit, and point to the actual App.py entry
python -m streamlit run App.py
