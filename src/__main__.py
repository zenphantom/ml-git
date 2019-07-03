"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python

import click
from operations.init import handle_init_operation


@click.group()
def cli():
    pass


@cli.command(help='Initialize a ML repository')
@click.argument('dataset_source', required=False)
def init(dataset_source):
    handle_init_operation(dataset_source)


@cli.command(help='Add a file to be tracked')
@click.argument('file')
def add(file):
    click.echo(f'Add {file}')


@cli.command(help='Add a file to be tracked')
@click.argument('file', required=False)
def status(file):
    click.echo(f'Status {file}')


@cli.command(help='Upload the data set files and push the file to the remote repository')
def push():
    click.echo('Push')


@cli.command(help='Checkout to a specific tag or data set version')
@click.argument('tag', required=False)
@click.option('--category', help='fully qualified tag name', required=False)
@click.option('--name', help='fully qualified tag name', required=False)
@click.option('--version', help='fully qualified tag name', required=False)
def checkout(tag, category, name, version):
    click.secho(f'Checkout tag: {tag} category: {category} name: {name} version: {version}', fg='red', bold=True)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        click.echo(e, color='red')

