# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
caldavctl uses a simple format to create new objects. this format is parsed and
converted into iCalendar objects.
'''

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from datetime import datetime
from abc import ABC, abstractmethod


STRING = 0
LIST = 1
DATE = 2
INTEGER = 3
TZ = 4

# States:
KEY = 0
VALUE = 1
COMMENT = 2


class ValueParser(ABC):
    def __init__(self, value):
        self.value = value
        self.tokens = ()

    @abstractmethod
    def tokenize(self):
        ...

    @abstractmethod
    def validate(self):
        ...

    def parse(self):
        self.tokenize()
        self.validate()
        return self.tokens


class ParserError(Exception):
    pass


class ObjectParser:
    def __init__(self, object, lexicon):
        self.object = object
        self.lexicon = lexicon

    def tokenize(self):
        data = self.object
        tokens = []
        pos = 0
        lenght = len(data)
        state = KEY
        while pos < lenght:
            if data[pos] in ' \t':  # Ignore spaces
                pos += 1
                continue
            if data[pos] == '#':  # Ignore comments
                pos = data.find('\n', pos) + 1
                if pos == 0:  # End of file
                    pos = lenght
                continue

            if state == KEY:  # Find the key
                if data[pos] == '\n':
                    pos += 1
                    continue
                end = data.find(':', pos)
                if end == -1:
                    raise ParserError('Could not find key/value pair.')
                key = data[pos:end].strip().lower()
                pos = end + 1
                state = VALUE
                continue

            if state == VALUE:  # Find the value
                if pos == lenght or data[pos] == '\n':  # End of file or empty value
                    pos += 1
                    state = KEY
                    continue
                if data[pos:pos + 2] == '[[':  # Multi line string
                    end = data.find(']]', pos)
                    value = data[pos + 2:end].strip()
                    tokens.append([key, value])
                    pos = end + 2
                    state = KEY
                    continue
                else:
                    # Single line string
                    end = data.find('\n', pos)
                    if end == -1:  # End of file
                        end = lenght
                    comment = data.find('#', pos)
                    if comment < end and comment != -1:
                        value = data[pos:comment].strip()
                    else:
                        value = data[pos:end].strip()
                    tokens.append([key, value])
                    pos = end + 1
                    state = KEY
                    continue
            pos += 1
        return tokens

    def parse(self, tokens):
        result = {}
        for key, value in tokens:
            if key not in self.lexicon:
                raise ParserError(f'Unknown key: "{key}".')

            optional = self.lexicon[key][1]
            value_type = self.lexicon[key][0]

            if not value and not optional:
                raise ParserError(f'Key "{key}" is not optional')
            elif not value and optional:
                continue

            if value_type == STRING:
                result[key] = value
            elif value_type == LIST:
                result[key] = [v.strip() for v in value.split(',')]
            elif value_type == DATE:
                try:
                    result[key] = datetime.fromisoformat(value)
                except ValueError:
                    raise ParserError(f'Invalid date format for: "{value}"')
            elif value_type == INTEGER:
                try:
                    result[key] = int(value)
                except ValueError:
                    raise ParserError(f'Invalid integer: "{value}"')
            elif value_type == TZ:
                try:
                    result[key] = ZoneInfo(value)
                except ZoneInfoNotFoundError:
                    raise ParserError(f'Invalid timezone: "{value}"')
            elif issubclass(value_type, ValueParser):
                if key not in result:
                    result[key] = []
                result[key].append(value_type(value).parse())

        return result

    def run(self):
        tokens = self.tokenize()
        result = self.parse(tokens)
        return result
