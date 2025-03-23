# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import caldav
import click
from caldav.lib import error

from caldavctl import dav


# CALENDARS

@click.command('list', options_metavar='[options]')
@click.pass_obj
def list_calendars(context):
    '''
    List the available calendars present on the server or servers
    '''
    for name, server in context['config'].servers():
        with caldav.DAVClient(**server) as client:
            for calendar in client.principal().calendars():
                click.echo(f'Server {name}:')
                click.echo(f'    CALENDAR = {calendar.name}')
                click.echo(f'    ID = {calendar.id}')
                click.echo(f'    COMPONENTS = {', '.join(calendar.get_supported_components())}')
                click.echo(f'    URL = {calendar.url}')
                click.echo()


@click.command('create', options_metavar='[options]')
@click.argument('name', metavar='<calendar>')
@click.option('--cal-id', help='Calendar UID to use in the new calendar', metavar='<uid>')
@click.pass_obj
def create_calendar(context, name, cal_id=None):
    '''
    Create a calendar on the default server or optionally in another server

    <calendar> - calendar name
    '''
    _, server = context['config'].get_server()

    with caldav.DAVClient(**server) as client:
        principal = client.principal()
        try:
            new_calendar = principal.make_calendar(name=name, cal_id=cal_id)
        except error.AuthorizationError as msg:
            raise click.UsageError(f'Error creating the calendar (maybe duplicate UID?) with: {msg}')

        print(f'Calendar "{name}" created.')
    return new_calendar


@click.command('delete', options_metavar='[options]')
@click.argument('calendar-id', metavar='<uid>')
@click.pass_obj
def delete_calendar(context, calendar_id):
    '''
    Delete a calendar from the default server or optionally from another
    server. It's possible to have calendars with the same name, so we use the
    id to identify the calendar to delete.
    '''
    _, server = context['config'].get_server()

    with dav.caldav_calendar(server, calendar_id) as calendar:
        name = calendar.name
        calendar.delete()
        print(f'Calendar "{name}" deleted.')
