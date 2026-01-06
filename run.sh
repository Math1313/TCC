#!/bin/bash

echo "🚀 Trello Card Copier"
echo ""

if [ ! -d ".venv" ]; then
    echo "📦 Création environnement virtuel..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
python main.py
