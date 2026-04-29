#!/usr/bin/env python3
"""
stats.py - Analyze and display commit statistics from logs.

Provides summary information about the bot's activity, including
streak tracking, total commits, and daily/weekly breakdowns.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

COMMIT_TRACKER = ".commit_tracker.json"
COMMIT_LOG = "commit_log.txt"
DAILY_LOG = "daily_log.txt"


def load_tracker():
    """Load the commit tracker JSON file."""
    if not os.path.exists(COMMIT_TRACKER):
        return {}
    with open(COMMIT_TRACKER, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def count_commits_from_log():
    """Count total commits recorded in commit_log.txt."""
    if not os.path.exists(COMMIT_LOG):
        return 0
    with open(COMMIT_LOG, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return len(lines)


def parse_daily_log():
    """
    Parse daily_log.txt to extract per-day commit counts.

    Returns:
        dict: A mapping of date strings (YYYY-MM-DD) to commit counts.
    """
    daily_counts = defaultdict(int)
    if not os.path.exists(DAILY_LOG):
        return daily_counts

    with open(DAILY_LOG, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expected format: "YYYY-MM-DD: N commits"
            try:
                parts = line.split(":")
                date_str = parts[0].strip()
                count_part = parts[1].strip().split()[0]
                daily_counts[date_str] = int(count_part)
            except (IndexError, ValueError):
                continue

    return daily_counts


def calculate_streak(daily_counts):
    """
    Calculate the current and longest commit streaks.

    Args:
        daily_counts (dict): Date -> commit count mapping.

    Returns:
        tuple: (current_streak, longest_streak) as integers.
    """
    if not daily_counts:
        return 0, 0

    today = datetime.utcnow().date()
    sorted_dates = sorted(daily_counts.keys(), reverse=True)

    # Current streak
    current_streak = 0
    check_date = today
    for _ in range(len(sorted_dates) + 1):
        date_str = check_date.strftime("%Y-%m-%d")
        if daily_counts.get(date_str, 0) > 0:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # Longest streak
    longest_streak = 0
    temp_streak = 0
    prev_date = None
    for date_str in sorted(daily_counts.keys()):
        if daily_counts[date_str] == 0:
            temp_streak = 0
            prev_date = None
            continue
        current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if prev_date and (current_date - prev_date).days == 1:
            temp_streak += 1
        else:
            temp_streak = 1
        longest_streak = max(longest_streak, temp_streak)
        prev_date = current_date

    return current_streak, longest_streak
