# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta

import pytest

from caldavctl.utils import deep_merge_dict, duration_to_timedelta, duration_validation


def test_deep_merge_dict_simple():
    source = {'a': 1, 'b': 2}
    destination = {'b': 3, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': 1, 'b': 2, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_nested():
    source = {'a': {'x': 1}, 'b': 2}
    destination = {'a': {'y': 3}, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1, 'y': 3}, 'b': 2, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_overwrite():
    source = {'a': {'x': 5}, 'b': 6}
    destination = {'a': {'x': 1, 'y': 3}, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 5, 'y': 3}, 'b': 6, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_empty_source():
    source = {}
    destination = {'a': 1, 'b': 2}
    result = deep_merge_dict(source, destination)
    expected = {'a': 1, 'b': 2}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_empty_destination():
    source = {'a': {'x': 1}, 'b': 2}
    destination = {}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}, 'b': 2}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_conflicting_types():
    source = {'a': {'x': 1}}
    destination = {'a': 5}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_nested_empty_dict():
    source = {'a': {}}
    destination = {'a': {'x': 1}}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


test_data_duration_validation = (
    ("P1W", True),         # 1 week
    ("P1D", True),         # 1 day
    ("PT1H", True),        # 1 hour
    ("PT1M", True),        # 1 minute
    ("PT1S", True),        # 1 second
    ("P1DT1H", True),      # 1 day, 1 hour
    ("P1DT1M", True),      # 1 day, 1 minute
    ("PT1H1M", True),      # 1 hour, 1 minute
    ("PT1H1S", True),      # 1 hour, 1 second
    ("PT1M1S", True),      # 1 minute, 1 second
    ("P1DT1H1M1S", True),  # 1 day, 1 hour, 1 minute, 1 second
    ("-P1W", True),        # Negative 1 week
    ("+P1W", True),        # Positive 1 week
    ("P", False),          # Empty duration
    ("PT", False),         # Empty time duration
    ("P1H", False),        # Missing T for time
    ("P1S", False),        # Missing T for time
    ("PPT1H", False),      # Double P
    ("P1DT", False),       # Empty time part
    ("P1WT1H", False),     # Weeks cannot be combined with other units
    ("PT1D", False),       # Days must not appear after T
)


@pytest.mark.parametrize('duration, match', test_data_duration_validation)
def test_duration_validation(duration: str, match: bool):
    result = duration_validation(duration)
    print(f"{duration} {'passes' if match == result else 'does not validade'}")
    assert result == match


test_data = (
    # Basic positive durations
    ('P1W', timedelta(weeks=1)),
    ('P1D', timedelta(days=1)),
    ('PT1H', timedelta(hours=1)),
    ('PT1M', timedelta(minutes=1)),
    ('PT1S', timedelta(seconds=1)),

    # Basic negative durations
    ('-P1W', -timedelta(weeks=1)),
    ('-P1D', -timedelta(days=1)),
    ('-PT1H', -timedelta(hours=1)),
    ('-PT1M', -timedelta(minutes=1)),
    ('-PT1S', -timedelta(seconds=1)),

    # Complex positive durations
    ('P1DT2H', timedelta(days=1, hours=2)),
    ('P1DT2H3M', timedelta(days=1, hours=2, minutes=3)),
    ('P1DT2H3M4S', timedelta(days=1, hours=2, minutes=3, seconds=4)),
    ('PT2H3M4S', timedelta(hours=2, minutes=3, seconds=4)),
    ('PT3M4S', timedelta(minutes=3, seconds=4)),

    # Complex negative durations
    ('-P1DT2H', -timedelta(days=1, hours=2)),
    ('-P1DT2H3M', -timedelta(days=1, hours=2, minutes=3)),
    ('-P1DT2H3M4S', -timedelta(days=1, hours=2, minutes=3, seconds=4)),
    ('-PT2H3M4S', -timedelta(hours=2, minutes=3, seconds=4)),
    ('-PT3M4S', -timedelta(minutes=3, seconds=4)),

    # Large numbers
    ('P365D', timedelta(days=365)),
    ('PT24H', timedelta(hours=24)),
    ('PT60M', timedelta(minutes=60)),
    ('PT3600S', timedelta(seconds=3600)),

    # Common real-world cases
    ('PT15M', timedelta(minutes=15)),     # Common meeting reminder
    ('P1DT12H', timedelta(days=1, hours=12)),  # Day and a half
    ('PT30M', timedelta(minutes=30)),     # Half hour
    ('-PT15M', -timedelta(minutes=15)),   # 15 minutes before
    ('P7D', timedelta(weeks=1)),          # One week expressed in days

    # Edge cases
    ('PT0S', timedelta(seconds=0)),       # Zero duration
    ('P0D', timedelta(days=0)),           # Zero days
    ('PT1H0M0S', timedelta(hours=1)),     # Explicit zeros
    ('P1DT0H0M0S', timedelta(days=1)),    # Explicit zeros

    # Mixed cases with weird spacing (if your function handles it)
    ('P1DT23H45M10S', timedelta(days=1, hours=23, minutes=45, seconds=10)),
    ('-P1DT23H45M10S', -timedelta(days=1, hours=23, minutes=45, seconds=10)),
    (' P1DT23H45M10S ', timedelta(days=1, hours=23, minutes=45, seconds=10)),  # Extra spaces

    # Weeks
    ('P2W', timedelta(weeks=2)),
    ('-P2W', -timedelta(weeks=2)),
)


@pytest.mark.parametrize('duration, result', test_data)
def test_duration_to_timedelta(duration, result):
    td = duration_to_timedelta(duration)
    print(f'Testing "{duration}" computed {td} expected result {result} - {"passed" if td == result else "failed"}')
    assert td == result
