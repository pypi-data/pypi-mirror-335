# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import calendar
import os
import re
import subprocess
import tempfile
from datetime import datetime, timedelta

import click


def calmonth(year, month, number, firstweekday=0):
    date = datetime(year, month, 15)
    today = datetime.now()
    months = []
    for _ in range(number):
        mst = calendar.TextCalendar(firstweekday=firstweekday
                                    ).formatmonth(date.year, date.month).split("\n")
        # Format month
        max_len = max([len(ln) for ln in mst])
        mst = [ln.ljust(max_len).center(max_len + 2) for ln in mst]
        # Highlight current day
        if today.year == date.year and today.month == date.month:
            for i, ln in enumerate(mst):
                mst[i] = ln.replace(f" {today.day:2} ", f">{today.day:2}<")

        months.append(mst)
        date.replace(day=15)
        date += timedelta(days=30)

    max_ln = max([len(m) for m in months])
    merged = [""] * max_ln
    space = ""
    for m in months:
        for i, ln in enumerate(m):
            merged[i] += ln + space

    return [ln for ln in merged if ln.strip()]


def edit_text_with_editor(initial_text: str, suffix: str = '.tmp') -> str:
    # Determine the editor from $EDITOR or $VISUAL, defaulting to 'vi'
    editor = os.environ.get('VISUAL') or os.environ.get('EDITOR') or 'vi'

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w+') as temp_file:
        temp_filename = temp_file.name
        temp_file.write(initial_text)
        temp_file.flush()  # Ensure content is written to disk

    try:
        # Open the editor with the temporary file
        subprocess.run([editor, temp_filename])

        # Read the modified content back
        with open(temp_filename, 'r') as temp_file:
            modified_text = temp_file.read()
    finally:
        # Clean up the temporary file
        os.unlink(temp_filename)

    return modified_text


def deep_merge_dict(source, destination):
    """
    Merge two dictionaries, if key exists on both dictionaries then the source will prevail

    Based on:
    From: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            if isinstance(node, dict):
                # see test_deep_merge_dict_conflicting_types
                deep_merge_dict(value, node)
            else:
                destination[key] = value
        else:
            destination[key] = value
    return destination


def check_if_naive(date, tz):
    '''
    Check if a date is naïve and if it is localize it with the timezone defined
    in tz.
    '''
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date = date.replace(tzinfo=tz)
    return date


def to_datetime(dt_str, tz):
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        raise click.UsageError(f'Invalid date "{dt_str}", use iso format.')
    return dt


def duration_validation(duration):
    '''
    Validates a duration difined according to RFC 2445 iCalendar specification:

    dur-value  = (["+"] / "-") "P" (dur-date / dur-time / dur-week)
    dur-date   = dur-day [dur-time]
    dur-time   = "T" (dur-hour / dur-minute / dur-second)
    dur-week   = 1*DIGIT "W"
    dur-hour   = 1*DIGIT "H" [dur-minute]
    dur-minute = 1*DIGIT "M" [dur-second]
    dur-second = 1*DIGIT "S"
    dur-day    = 1*DIGIT "D"
    '''

    h = r'\d+H'
    m = r'\d+M'
    s = r'\d+S'
    dur_time = rf'T(?:{h}{m}{s}|{h}{m}|{h}{s}|{m}{s}|{h}|{m}|{s})'

    duration_re = (
        r'^[+-]?P'
        r'(?:'
        r'\d+W|'
        rf'\d+D(?:{dur_time})?|'
        rf'{dur_time}'
        r')$'
    )

    duration = duration.upper().strip()
    return bool(re.match(duration_re, duration))


def duration_to_timedelta(duration):
    '''
    Converts durations used in iCalendar files to python's timedelta

    No attempt is made to validade the "duration" format. If the "duration" is
    malformed the result is undefined.
    '''
    translate = {
        'W': 'weeks',
        'D': 'days',
        'H': 'hours',
        'M': 'minutes',
        'S': 'seconds'
    }

    duration = duration.upper().strip()
    signal = 1
    tmp_int = ''
    duration_dict = {}
    for i, ch in enumerate(duration):
        if i == 0 and ch == '-':
            signal = -1
        elif ch.isdigit():
            tmp_int += ch
        elif ch in ('P', 'T'):
            pass
        else:
            duration_dict[translate[ch]] = int(tmp_int)
            tmp_int = ''

    return signal * timedelta(**duration_dict)
