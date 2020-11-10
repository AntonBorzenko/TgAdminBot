import typing
import logging

from aiogram import types, exceptions

from tg_admin_bot.core import Feature


log = logging.getLogger(__name__)


class UserBlocker:
    class User:
        def __init__(self, user_id: int):
            self.id = user_id
            self.messages_ids = []

        def add_message_id(self, message_id):
            self.messages_ids.append(message_id)

    def __init__(self, min_user_queue: int = 3, timer: int = 30):
        self._min_user_queue = min_user_queue
        self._timer = timer
        self._observed_users: typing.Dict[int, UserBlocker.User] = {}
        self._last_reg_time: typing.Optional[int] = None
        self._on_block_users = []
        self._queue_len: int = 0

    def __len__(self):
        return self._queue_len

    async def add_user(self, user_id: int, reg_time: int):
        if self._last_reg_time is None or reg_time - self._last_reg_time > self._timer:
            self._observed_users = {user_id: UserBlocker.User(user_id)}
            self._queue_len = 1
        else:
            if self._observed_users.get(user_id) is None:
                self._observed_users[user_id] = UserBlocker.User(user_id)
            self._queue_len += 1
        self._last_reg_time = reg_time

        if self._queue_len >= self._min_user_queue:
            await self._block_users()

    async def add_user_message(self, user_id: int, user_message_id: int, current_time: int = None):
        if current_time is not None \
                and self._last_reg_time is not None \
                and current_time - self._last_reg_time > self._timer:
            self._observed_users = {}
            self._queue_len = 0
            return

        if user_id in self._observed_users:
            self._observed_users[user_id].add_message_id(user_message_id)

    def on_block_user(self, on_block: typing.Callable[[int, typing.List[int]], typing.Coroutine]):
        self._on_block_users.append(on_block)

    async def _block_users(self):
        for user in self._observed_users.values():
            for on_block in self._on_block_users:
                await on_block(user.id, user.messages_ids)
        self._observed_users = {}


class BlockingBotsFeature(Feature):
    def __init__(self, min_user_queue: int = 3, timer: int = 30):
        self._min_user_queue = min_user_queue
        self._timer = timer

        self._user_blockers: typing.Dict[int, UserBlocker] = {}

    def _on_apply_feature(self):
        self.dispatcher.register_message_handler(self._on_new_chat_members,
                                                 content_types=types.ContentType.NEW_CHAT_MEMBERS)
        self.dispatcher.register_message_handler(self._on_new_message,
                                                 content_types=types.ContentType.ANY)

    def _create_user_blocker(self, chat_id):
        if chat_id not in self._user_blockers:
            user_blocker = UserBlocker(self._min_user_queue, self._timer)
            user_blocker.on_block_user(self._get_block_user_func(chat_id))
            self._user_blockers[chat_id] = user_blocker

    async def _on_new_message(self, event: types.Message):
        chat_id = event.chat.id

        if chat_id > 0:
            return

        self._create_user_blocker(chat_id)
        await self._user_blockers[chat_id].add_user_message(
            event.from_user.id, event.message_id, int(event.date.timestamp())
        )

    async def _on_new_chat_members(self, event: types.Message):
        await self._on_new_message(event)

        chat_id = event.chat.id
        if chat_id > 0:
            return

        self._create_user_blocker(chat_id)
        for chat_member in event.new_chat_members:
            if chat_member.id == event.from_user.id:
                log.info(f'User#{chat_member.id} is joined to chat#{chat_id}')
                await self._user_blockers[chat_id].add_user(chat_member.id, int(event.date.timestamp()))

    def _get_block_user_func(self, chat_id: int):
        async def block_user(user_id: int, messages_ids: typing.List[int]):
            log.info(f'Blocking user#{user_id} and deleting messages {messages_ids}')
            try:
                for message_id in messages_ids:
                    await self.bot.delete_message(chat_id, message_id)
            except exceptions.TelegramAPIError:
                log.error(f'Cannot delete messages {messages_ids} from user#{user_id} in chat#{chat_id}')
                await self.bot.send_message(chat_id, 'I don\'t have permissions to delete messages, please fix it')

            try:
                await self.bot.kick_chat_member(chat_id, user_id)
            except exceptions.TelegramAPIError:
                log.error(f'Cannot kick user#{user_id} from chat#{chat_id}')
                await self.bot.send_message(chat_id, 'I don\'t have permissions to kick spam bots, please fix it')
        return block_user
