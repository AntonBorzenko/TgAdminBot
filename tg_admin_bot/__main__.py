import asyncio
import sys
import logging

import click

from .main import AdminBot


def update_logger():
    log = logging.getLogger('tg_admin_bot')
    log.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    log.addHandler(stdout_handler)


@click.command()
@click.option('-t', '--token', type=str, envvar='TOKEN', required=True)
def start_bot(token):
    update_logger()
    bot = AdminBot(token)
    asyncio.run(bot.run_updater())


if __name__ == '__main__':
    start_bot()
