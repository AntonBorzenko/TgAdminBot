from tg_admin_bot.core import Bot
from .features import BlockingBotsFeature


class AdminBot(Bot):
    def __init__(self, token: str):
        super().__init__(token)
        self.add_feature(BlockingBotsFeature())
