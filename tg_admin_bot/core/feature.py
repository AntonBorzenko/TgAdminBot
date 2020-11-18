from aiogram import Dispatcher, Bot

from abc import ABC, abstractmethod


class Feature(ABC):
    bot: Bot = None
    dispatcher = None
    _applied = False

    def apply_to(self, bot: Bot, dispatcher: Dispatcher):
        if self._applied:
            raise ValueError('Feature should be applied only once')

        self.bot = bot
        self.dispatcher = dispatcher

        self._on_apply_feature()
        self._applied = True

    @abstractmethod
    def _on_apply_feature(self):
        pass
