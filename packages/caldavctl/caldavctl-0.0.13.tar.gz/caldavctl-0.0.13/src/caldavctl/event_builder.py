# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from datetime import datetime

from icalendar import Alarm, Calendar, Event

from caldavctl import get_name, get_version
from caldavctl.object_parser import (
    DATE,
    INTEGER,
    LIST,
    STRING,
    TZ,
    ObjectParser,
    ParserError,
    ValueParser,
)
from caldavctl.utils import check_if_naive, duration_validation, duration_to_timedelta


class AlarmParser(ValueParser):
    def tokenize(self):
        self.tokens = self.value.split(maxsplit=1)

    def validate(self):
        duration = self.tokens[0].upper().strip()
        if not duration_validation(duration):
            raise ParserError(f'Invalid duration "{self.tokens[0]}" for alarm trigger.')
        self.tokens[0] = duration_to_timedelta(duration)


EVENT_LEXICON = {
    # token: (type, optional?)
    'summary': (STRING, True),
    'location': (STRING, True),
    'categories': (LIST, True),
    'dtstart': (DATE, False),
    'dtend': (DATE, False),
    'description': (STRING, True),
    'percentage': (INTEGER, True),
    'timezone': (TZ, True),
    'priority': (INTEGER, True),
    'alarm': (AlarmParser, True)
}


def parse_event(event_icalendar, timezone):
    result = ObjectParser(event_icalendar, EVENT_LEXICON).run()

    # Check if the start and/or end dates are naïve
    tz = timezone if 'timezone' not in result else result['timezone']
    result['dtstart'] = check_if_naive(result['dtstart'], tz)
    result['dtend'] = check_if_naive(result['dtend'], tz)

    return result


event_optional_keys = (
    'summary',
    'location',
    'priority',
    'description',
    'categories',
    'alarm',
)


def event_builder(event_data, tz):
    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('prodid', f'-//NA//{get_name()} V{get_version()}//EN')

    event = Event()
    # Mandatory keys in a VEVENT object
    event.add('uid', str(uuid.uuid4()))
    event.add('dtstamp', datetime.now(tz))
    event.add('dtstart', event_data.get('dtstart'))
    event.add('dtend', event_data.get('dtend'))
    # Optional keys:
    for key in event_optional_keys:
        if key in event_data:
            if key == 'categories':
                for category in event_data.get('categories'):
                    event.add('categories', category)
            if key == 'alarm':
                data = event_data.get(key)
                for alarm_data in data:
                    alarm = Alarm()
                    alarm.add('trigger', alarm_data[0])
                    if len(alarm_data) == 2:
                        alarm.add('description', alarm_data[1])
                    else:
                        alarm.add('description', 'Default caldavctl description')
                    alarm.add('action', 'display')
                    event.add_component(alarm)
            else:
                event.add(key, event_data.get(key))

    calendar.add_component(event)

    return calendar.to_ical().decode('utf-8')
