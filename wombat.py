#! /usr/bin/env python

import os
import click
import yaml
import subprocess

from jinja2 import Template

# Default settings for mail accounts and folder
mail_account_defaults = {'configuration': 'offlineimap.yaml',
                         'path': os.environ['HOME'] + '/cloud/wombat/mail',
                         'template': 'offlineimaprc.template',
                         'rc': os.environ['HOME'] + '/.offlineimaprc'}


@click.group()
def wombat():
    """
    Manage the expenditure of time and money.
    """
    pass


@wombat.command()
def get():
    """
    Get data from remote sources or syncrhonise.
    """
    oimap_data = {}
    oimap_data.update(mail_account_defaults)
    oimap = oimap_data['configuration']
    with open(oimap, 'r') as yfile:
        oimap_data.update(yaml.safe_load(yfile))
    oimap_data.update(os.environ)

    with open(oimap_data['template'], 'r') as rcfile:
        oimaprc = Template(rcfile.read())

    with open(oimap_data['rc'], 'w') as ofile:
        ofile.write(oimaprc.render(oimap_data))

    for acct in oimap_data['accounts']:
        folder = oimap_data['path'] + "/" + acct['name']
        os.makedirs(folder, exist_ok=True)

    click.echo("Synchronising with offlineimap")
    for acct in oimap_data['accounts']:
        oimap_result = subprocess.run(['offlineimap',
                                       '-o',
                                       '-a',
                                       acct['name']])
        oimap_result.check_returncode()

    click.echo("Indexing with notmuch")
    notmuch_result = subprocess.run(['notmuch', 'new'])
    notmuch_result.check_returncode()

    click.echo("All done")
    return


@wombat.command()
def index():
    """
    Create or update indices needed for efficient search.
    """
    click.echo("index() is not yet implemented")


if __name__ == '__main__':
    wombat()
