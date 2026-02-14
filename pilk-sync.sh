#!/bin/bash
# Pilk Git Sync - Pull all active projects
set -e

ACTIVE_PROJECTS=(
    "Pilk-Option-Chain"
    "pilk-scanner"
    "pilk-efa"
    "Pilk-Dashboard"
    "pilk-tasks"
    "Pilk-Automate"
)

echo "🔄 Pilk Git Sync - $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

for project in "${ACTIVE_PROJECTS[@]}"; do
    PROJECT_PATH="$HOME/Projects/$project"
    
    if [ -d "$PROJECT_PATH" ]; then
        echo "📦 Syncing: $project"
        cd "$PROJECT_PATH"
        
        # Check if we have uncommitted changes
        if [ -n "$(git status --porcelain)" ]; then
            echo "  ⚠️  Uncommitted changes detected - skipping pull"
        else
            git pull --rebase origin "$(git branch --show-current)"
            echo "  ✅ Synced"
        fi
    else
        echo "  ❌ Not found: $PROJECT_PATH"
    fi
    
    echo ""
done

echo "✨ Sync complete"
