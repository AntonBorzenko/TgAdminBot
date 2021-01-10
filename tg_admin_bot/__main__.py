import asyncio

import click

from .main import AdminBot
from . import update_logger


@click.command()
@click.option('-t', '--token', type=str, envvar='TG_TOKEN', required=True)
def start_bot(token):
    update_logger()

    bot = AdminBot(token)
    asyncio.run(bot.run_updater())


if __name__ == '__main__':
    start_bot()
