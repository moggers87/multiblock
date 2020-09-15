##
#
# Copyright (C) 2020 Matt Molyneaux
#
# This file is part of Multiblock.
#
# Multiblock is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Multiblock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Multiblock.  If not, see <https://www.gnu.org/licenses/>.
#
##

"""
Documentation for this module can be found in :doc:`commandline`
"""

import logging

import click

from . import __version__
from .config import DEFAULT_PATH, Config

logger = logging.getLogger("multiblock")


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", count=True,
              help="Verbose output, can be used multiple times to increase logging level")
def multiblock(verbose):
    """
    Sync block and mute lists over multiple Mastodon accounts
    """
    logger.addHandler(logging.StreamHandler())
    if verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARN)


@multiblock.group(short_help="Manage Mastodon accounts")
def accounts():
    pass


@accounts.command("add", short_help="Add a new account")
@click.option("-r", "--refresh", is_flag=True, short_help="Refresh access token")
@click.argument("user", nargs=1, required=True)
def account_add(refresh, user):
    with Config(DEFAULT_PATH) as cfg:
        if user in cfg.accounts.keys() and not refresh:
            raise click.ClickException("{} already exists")
        if refresh:
            cfg.clear_token(user)
        url = cfg.get_auth_url(user)
        click.echo("Open the following URL and enter the code: %s" % url)
        secret = cfg.log_in(user, code=click.prompt("Secret"))
        cfg.add_account(user, secret)
    click.echo("%s added" % user)


@accounts.command("remove", short_help="remove an existing account")
@click.argument("user", nargs=1, required=True)
def account_remove(user):
    with Config(DEFAULT_PATH) as cfg:
        cfg.remove_address(user)


@accounts.command("list", short_help="List accounts")
def account_list():
    with Config(DEFAULT_PATH) as cfg:
        accounts = list(cfg.accounts().keys())
        accounts.sort()

    click.echo("\n".join(accounts))


@multiblock.command(short_help="Sync accounts")
@click.option("--blocks/--no-blocks", default=True, help="Sync block lists between accounts")
@click.option("--mutes/--no-mutes", default=True, help="Sync mute lists between accounts")
@click.option("--domains/--no-domains", default=True, help="Sync hidden domain lists between accounts")
def sync(blocks, mutes, domains):
    pass
