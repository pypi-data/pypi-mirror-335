# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
Utilities
'''

import zoneinfo

import click


@click.command('list-timezones', options_metavar='[options]')
@click.option('-s', '--search',
              default=None, metavar='<query>', type=str,
              help='Search time zone')
@click.pass_obj
def list_timezones(context, search):
    '''
    List available time zones

    This command display the available time zones in python's zoneinfo module.
    Use the -s/--search option to search for a specific time zone.
    '''
    timezones = zoneinfo.available_timezones()

    if search:
        result = []
        for tz in timezones:
            if search.lower() in tz.lower():
                result.append(tz)
        if not result:
            result.append(f'No time zone "{search}" found.')
    else:
        result = list(timezones)

    result.sort()

    for tz in result:
        click.echo(tz)
