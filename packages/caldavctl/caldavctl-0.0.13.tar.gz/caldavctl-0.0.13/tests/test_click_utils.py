# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from caldavctl.click_utils import OptionsCompatibility


def test_click_utils_compatibility():
    compatibility = OptionsCompatibility(['today', 'week', 'dtstart', 'dtend'])
    compatibility.set_exception(['dtstart', 'dtend'])

    test_compatibility = {
        'today': {
            'week': False,
            'dtstart': False,
            'dtend': False,
        },
        'week': {
            'today': False,
            'dtstart': False,
            'dtend': False,
        },
        'dtstart': {
            'today': False,
            'week': False,
            'dtend': True,
        },
        'dtend': {
            'today': False,
            'week': False,
            'dtstart': True,
        },
    }

    assert test_compatibility == compatibility.compatibility
