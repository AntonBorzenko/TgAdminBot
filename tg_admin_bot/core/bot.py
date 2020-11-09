import logging

from aiogram import Bot as AioBot, Dispatcher

from .feature import Feature


log = logging.getLogger(__name__)


class Bot:
    def __init__(self, token: str, dispatcher: Dispatcher = None):
        self.aiobot = AioBot(token)
        self.dispatcher = dispatcher or Dispatcher(bot=self.aiobot)
        self.features = []

    def add_feature(self, feature: Feature):
        try:
            feature.apply_to(self.aiobot, self.dispatcher)
            self.features.append(feature)
        except Exception as e:
            log.error(f"Cannot be applied {feature.__class__} to dispatcher", exc_info=True)
            raise

    async def run_updater(self):
        try:
            log.info('Starting bot updater...')
            await self.dispatcher.start_polling()
        except Exception as e:
            log.error(e)
        finally:
            await self.aiobot.close()
