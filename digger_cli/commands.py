#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import os

from functools import update_wrapper
from click_repl import repl as crepl
from discogs import Artist, List, Release, Search

def requires_env(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = os.environ.get(name)
            if not token:
                raise click.UsageError('Unable to read environment variable {0}. Try exporting the variable first.'.format(name))
            func(token, *args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


@click.group()
def cli():
    pass

@cli.command()
def repl():
    click.secho('     _ _                                      _ _ ')
    click.secho('    | (_)                                    | (_)')
    click.secho('  __| |_  __ _  __ _  ___ _ __ ___ ______ ___| |_ ')
    click.secho(' / _` | |/ _` |/ _` |/ _ \ \'__/ __|______/ __| | |')
    click.secho('| (_| | | (_| | (_| |  __/ |  \__ \     | (__| | |')
    click.secho(' \__,_|_|\__, |\__, |\___|_|  |___/      \___|_|_|')
    click.secho('          __/ | __/ |                             ')
    click.secho('         |___/ |___/                              ')

    prompt_kwargs = {
        'message': u'discogs> '
    }
    crepl(click.get_current_context(), prompt_kwargs=prompt_kwargs)

@cli.command('artist')
@click.argument('id')
def artist(id):
    """Retrieve artist information and their associated releases."""
    artist = Artist(id)
    artist.show()

@cli.command('list')
@click.argument('id')
@click.option('--comments', is_flag=True, help='Display comments')
@click.option('--release', type=int)
@click.option('--export', is_flag=True, help='Exports the list as JSON')
@requires_env('TOKEN')
def list(token, id, comments, release, export):
    """Retrieve user list information and their associated releases."""
    userlist = List(id, user_token=token)
    if export:
        userlist.export(comments)
    elif release:
        userlist.showSingle(comments, release)
    else:
        userlist.show(comments)

@cli.command('release')
@click.argument('id')
def release(id):
    """Retrieve a single release from the discogs database."""
    r = Release(id)

    # try:
    r.show()
    # except Exception as e:
    #     click.secho('Unable to fetch release id: {id} ({e})'.format(id=id, e=e), fg='red')

@cli.command('search')
@click.argument('query')
@click.option('--lookup', default='release')
@requires_env('TOKEN')
def search(token, query, lookup):
    """Search for Discogs artist, release, label information."""
    s = Search(query, type=lookup, user_token=token)

    try:
        s.show()
    except IOError as e:
        pass
    except Exception as e:
        click.secho('Unable to perform a {t} search for {q} ({e})'.format(
             t=lookup, q=query, e=e), fg='red')

if __name__ == '__main__':
    cli()
