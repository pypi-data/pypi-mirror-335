import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from caldavctl.object_parser import ObjectParser, ParserError
from caldavctl.event_builder import parse_event, check_if_naive, EVENT_LEXICON


sample_event_data_i = """
        SUMMARY: This is a description
        LOCATION: [[Timbuktu]] # With a comment
        CATEGORIES: Birthday, Shopping, Training
        TIMEZONE: Europe/Lisbon
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45
        DESCRIPTION: [[
        Once upon a time,
        There was a little lamb
        ]]
        """

sample_event_data_ii = '''# Mandatory
SUMMARY: Example summary
DTSTART: 2024-12-30 09:00
DTEND: 2024-12-30 09:45

# Optional
LOCATION:
CATEGORIES:
TIMEZONE: Europe/Lisbon
DESCRIPTION: [[ ]]

# NOTES:
#
#   * Date and time:
#       * The dates must be in iso format, for instance: 2024-12-29 13:45;
#       * The timezone used if the one defined by default or the one defined in
#         "TIMEZONE";
#   * Categories: the categories are a comma separeted list;
#   * Description: The description can be multi line, just make sure it's
#     delimited by [[ ]].'''


@pytest.fixture
def default_timezone():
    return ZoneInfo('UTC')


def test_tokenize():
    parser = ObjectParser(sample_event_data_i, EVENT_LEXICON)
    tokens = parser.tokenize()
    expected_tokens = [
        ['summary', 'This is a description'],
        ['location', 'Timbuktu'],
        ['categories', 'Birthday, Shopping, Training'],
        ['timezone', "Europe/Lisbon"],
        ['dtstart', '2024-01-20 09:00'],
        ['dtend', '2024-01-20 09:45'],
        ['description', 'Once upon a time,\n        There was a little lamb']
    ]

    assert tokens == expected_tokens


def test_parse_i():
    parser = ObjectParser(sample_event_data_i, EVENT_LEXICON)
    tokens = parser.tokenize()
    result = parser.parse(tokens)

    expected_result = {
        'summary': 'This is a description',
        'location': 'Timbuktu',
        'categories': ['Birthday', 'Shopping', 'Training'],
        'timezone': ZoneInfo('Europe/Lisbon'),
        'dtstart': datetime(2024, 1, 20, 9, 0),
        'dtend': datetime(2024, 1, 20, 9, 45),
        'description': 'Once upon a time,\n        There was a little lamb'
    }

    assert result['summary'] == expected_result['summary']
    assert result['location'] == expected_result['location']
    assert result['categories'] == expected_result['categories']
    assert result['description'] == expected_result['description']
    assert result['dtstart'] == expected_result['dtstart']
    assert result['dtend'] == expected_result['dtend']
    assert result['timezone'] == expected_result['timezone']


def test_parse_ii():
    parser = ObjectParser(sample_event_data_ii, EVENT_LEXICON)
    tokens = parser.tokenize()
    result = parser.parse(tokens)

    expected_result = {
        'summary': 'Example summary',
        'location': '',
        'categories': [],
        'timezone': ZoneInfo('Europe/Lisbon'),
        'dtstart': datetime(2024, 12, 30, 9, 0),
        'dtend': datetime(2024, 12, 30, 9, 45),
        'description': ''
    }

    assert result['summary'] == expected_result['summary']
    assert 'location' not in result
    assert 'categories' not in result
    assert 'description' not in result
    assert result['dtstart'] == expected_result['dtstart']
    assert result['dtend'] == expected_result['dtend']
    assert result['timezone'] == expected_result['timezone']


def test_check_if_naive():
    naive_date = datetime(2024, 1, 20, 9, 0)
    tz = ZoneInfo('Europe/Lisbon')
    localized_date = check_if_naive(naive_date, tz)

    assert f'{localized_date.tzinfo}' == 'Europe/Lisbon'
    assert localized_date.utcoffset() == tz.utcoffset(naive_date)


def test_parse_event_with_naive_dates(default_timezone):
    event_with_naive_dates = (
        """
        SUMMARY: Test Event
        LOCATION: Timbuktu
        TIMEZONE: Europe/Lisbon
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45Z  # UTC date
        """
    )

    result = parse_event(event_with_naive_dates, default_timezone)
    tz = ZoneInfo('Europe/Lisbon')

    assert result['dtstart'].tzinfo == tz
    assert result['dtend'].tzinfo == timezone.utc


def test_unknown_key():
    event_with_unknown_key = (
        """
        SUMMARY: Test Event
        UNKNOWN_KEY: This should fail
        """
    )
    parser = ObjectParser(event_with_unknown_key, EVENT_LEXICON)

    with pytest.raises(ParserError, match='Unknown key:'):
        parser.run()


def test_invalid_date():
    event_with_invalid_date = (
        """
        SUMMARY: Test Event
        DTSTART: invalid-date
        """
    )

    parser = ObjectParser(event_with_invalid_date, EVENT_LEXICON)

    with pytest.raises(ParserError, match='Invalid date format'):
        parser.run()


def test_event_no_timezone():
    sample_event_no_timezone = '''# Mandatory
    SUMMARY: Example summary
    DTSTART: 2024-12-30 09:00
    DTEND: 2024-12-30 09:45

    # Optional
    LOCATION:
    CATEGORIES:
    DESCRIPTION: [[ ]]'''

    result = parse_event(sample_event_no_timezone, ZoneInfo('Europe/Lisbon'))

    assert f'{result['dtstart'].tzinfo}' == 'Europe/Lisbon'
    assert f'{result['dtend'].tzinfo}' == 'Europe/Lisbon'
