#!/usr/bin/env python3
"""
Pilk-Tasks Natural Language Parser

Satsuki uses this to convert JSON task output into natural language summaries.
"""

import json
import sys
from datetime import datetime
from collections import Counter


def format_date(due_date: str) -> str:
    """Format due date for natural language."""
    if not due_date:
        return "no due date"
    
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d")
        today = datetime.now()
        delta = (due.date() - today.date()).days
        
        if delta < 0:
            return f"overdue by {-delta} day(s)"
        elif delta == 0:
            return "due today"
        elif delta == 1:
            return "due tomorrow"
        elif delta <= 7:
            return f"due in {delta} days"
        else:
            return f"due {due.strftime('%B %d')}"
    except:
        return "due soon"


def generate_summary(tasks_json: str) -> str:
    """Generate natural language summary from tasks JSON."""
    
    try:
        tasks = json.loads(tasks_json)
    except json.JSONDecodeError:
        return "Error: Could not parse task data."
    
    if not tasks:
        return "No tasks found."
    
    completed = [t for t in tasks if t.get('status') == 'completed']
    todo = [t for t in tasks if t.get('status') == 'todo']
    in_progress = [t for t in tasks if t.get('status') == 'in-progress']
    
    total = len(tasks)
    completed_count = len(completed)
    todo_count = len(todo) + len(in_progress)
    
    # Group by priority
    high_priority = [t for t in todo if t.get('priority') == 'high']
    medium_priority = [t for t in todo if t.get('priority') == 'medium']
    low_priority = [t for t in todo if t.get('priority') == 'low']
    
    # Group by category
    work_tasks = [t for t in tasks if t.get('category') == 'work']
    personal_tasks = [t for t in tasks if t.get('category') == 'personal']
    urgent_tasks = [t for t in tasks if t.get('category') == 'urgent']
    
    # Extract all tags
    all_tags = []
    for t in tasks:
        tags = t.get('tags', [])
        if tags:
            all_tags.extend(tags)
    tag_counter = Counter(all_tags)
    top_tags = [tag for tag, count in tag_counter.most_common(5)]
    
    # Build summary
    summary = []
    summary.append(f"You have {total} task(s) — {completed_count} completed, {todo_count} to do.\n")
    
    if completed:
        summary.append("\n✅ Completed:\n")
        for task in completed:
            title = task.get('title', 'Unknown')
            category = task.get('category', '')
            tags = task.get('tags', [])
            tag_str = ', '.join(tags) if tags else 'none'
            summary.append(f"  • {title} ({category}) — tags: {tag_str}\n")
    
    if todo:
        summary.append("\n⬜ To Do:\n")
        
        if high_priority:
            summary.append("  🔴 High Priority:\n")
            for task in high_priority:
                title = task.get('title', 'Unknown')
                due = format_date(task.get('due_date'))
                summary.append(f"    • {title} — {due}\n")
        
        if medium_priority:
            summary.append("  🟡 Medium Priority:\n")
            for task in medium_priority:
                title = task.get('title', 'Unknown')
                due = format_date(task.get('due_date'))
                summary.append(f"    • {title} — {due}\n")
        
        if low_priority:
            summary.append("  🟢 Low Priority:\n")
            for task in low_priority:
                title = task.get('title', 'Unknown')
                due = format_date(task.get('due_date'))
                summary.append(f"    • {title} — {due}\n")
    
    # Tag insights
    if top_tags:
        summary.append("\n🏷️ Most Used Tags:\n")
        for i, (tag, count) in enumerate(top_tags, 1):
            summary.append(f"  {i}. {tag} ({count})\n")
    
    # Suggestions
    if todo:
        # Check due soon
        today = datetime.now().strftime('%Y-%m-%d')
        due_soon = [t for t in todo if t.get('due_date') and t.get('due_date') <= today]
        
        if due_soon:
            summary.append("\n⚠️ Due Today/Overdue:\n")
            for task in due_soon:
                title = task.get('title', 'Unknown')
                summary.append(f"  • {title}\n")
        
        if high_priority:
            summary.append("\n💡 Suggestion: Focus on high priority tasks first!\n")
    
    return ''.join(summary)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Read from file or stdin
        input_file = sys.argv[1]
        
        if input_file == '-':
            # Read from stdin
            tasks_json = sys.stdin.read()
        else:
            # Read from file
            with open(input_file, 'r') as f:
                tasks_json = f.read()
    else:
        return "Usage: python3 pilk_tasks_parser.py <tasks.json>"
    
    summary = generate_summary(tasks_json)
    print(summary)


if __name__ == '__main__':
    main()
