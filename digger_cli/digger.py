#!/usr/bin/env python

from __future__ import unicode_literals

import click
import subprocess

from prompt_toolkit import prompt

from __init__ import __version__

HELP = 'Syntax: d <command> [options]'
EXIT = ['quit', 'exit', 'logoff', 'sys64738']
TOKEN = 'd '

def execute(cmd):
    try:
        subprocess.call(cmd, shell=True)
    except Exception as e:
        click.secho(e, fg='red')

def cli():
    click.secho('     _ _                                      _ _ ')
    click.secho('    | (_)                                    | (_)')
    click.secho('  __| |_  __ _  __ _  ___ _ __ ___ ______ ___| |_ ')
    click.secho(' / _` | |/ _` |/ _` |/ _ \ \'__/ __|______/ __| | |')
    click.secho('| (_| | | (_| | (_| |  __/ |  \__ \     | (__| | |')
    click.secho(' \__,_|_|\__, |\__, |\___|_|  |___/      \___|_|_|')
    click.secho('          __/ | __/ |                             ')
    click.secho('         |___/ |___/                              ')

    click.echo('Version:' + __version__)

    while True:
        try:
            command = prompt('digger-cli> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if text in EXIT:
            break

        if text.startswith(TOKEN):
            execute(text)
        else:
            click.secho('I didn\'t quite get that. ' + HELP, fg='red')

if __name__ == '__main__':
    cli()
    