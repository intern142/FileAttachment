#!/usr/bin/env python3
"""
Auto-update PROGRESS.md with task completion status.
Usage: python update_progress.py "Task description" [--status done|pending|in_progress]
"""
import argparse
import re
from datetime import datetime
from pathlib import Path


PROGRESS_FILE = Path("PROGRESS.md")


def update_progress(task: str, status: str = "done"):
    if not PROGRESS_FILE.exists():
        print("PROGRESS.md not found")
        return
    
    content = PROGRESS_FILE.read_text(encoding='utf-8')
    now = datetime.now().strftime("%H:%M")
    
    # Update last updated timestamp
    content = re.sub(
        r'\*\*Last Updated:\*\* .*',
        f'**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M IST")}',
        content
    )
    
    # Find and update task in table
    status_icons = {"done": "✅", "in_progress": "🔄", "pending": "⏳"}
    icon = status_icons.get(status, "✅")
    
    # Pattern to match task row in completed tasks table
    pattern = rf'(\| \d{{2}}:\d{{2}} \| {re.escape(task)} \| )(.*?)(\|)'
    
    def replace_status(match):
        return f'{match.group(1)}{icon} {status.title()}{match.group(3)}'
    
    new_content = re.sub(pattern, replace_status, content)
    
    if new_content == content:
        # Task not found in completed, add to completed table
        task_row = f"| {now} | {task} | {icon} {status.title()} | - |\n"
        # Insert before "## 📁 Current File Structure"
        new_content = content.replace(
            "## 📁 Current File Structure",
            f"{task_row}## 📁 Current File Structure"
        )
    
    PROGRESS_FILE.write_text(new_content, encoding='utf-8')
    print(f"Updated: {task} -> {status}")


def add_next_step(step: str):
    if not PROGRESS_FILE.exists():
        return
    
    content = PROGRESS_FILE.read_text(encoding='utf-8')
    step_item = f"- [ ] {step}\n"
    
    # Add to immediate next steps
    if "### Immediate (Next 30 min)" in content:
        content = content.replace(
            "### Immediate (Next 30 min)\n",
            f"### Immediate (Next 30 min)\n{step_item}"
        )
    
    PROGRESS_FILE.write_text(content, encoding='utf-8')
    print(f"Added next step: {step}")


def complete_next_step(step_text: str):
    if not PROGRESS_FILE.exists():
        return
    
    content = PROGRESS_FILE.read_text(encoding='utf-8')
    # Find and check the box
    pattern = rf'- \[ \] {re.escape(step_text)}'
    replacement = f'- [x] {step_text}'
    new_content = re.sub(pattern, replacement, content)
    
    PROGRESS_FILE.write_text(new_content, encoding='utf-8')
    print(f"Completed: {step_text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update PROGRESS.md")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--status", choices=["done", "in_progress", "pending"], default="done")
    parser.add_argument("--add-step", help="Add a next step")
    parser.add_argument("--complete-step", help="Mark next step as done")
    
    args = parser.parse_args()
    
    if args.add_step:
        add_next_step(args.add_step)
    elif args.complete_step:
        complete_next_step(args.complete_step)
    elif args.task:
        update_progress(args.task, args.status)
    else:
        parser.print_help()