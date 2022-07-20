from ..resources.config import config
from aiogram.dispatcher import FSMContext
from aiogram_media_group import media_group_handler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher.filters import Text, MediaGroupFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, RetryAfter, BadRequest as BotAPIBadRequest

botToken = config.get("BotAPI", "botToken")

bot = Bot(token=botToken, parse_mode=types.ParseMode.HTML)
dispatcher = Dispatcher(bot, storage=MongoStorage())


class BotAPIChatMemberStatus(types.ChatMemberStatus):
    '''
    Modified aiogram.types.ChatMemberStatus with is_kicked() method
    See BotAPIChatMemberUpdated and BotAPIChatMember
    '''
    @classmethod
    def is_kicked(cls, role: str) -> bool:
        return role == cls.KICKED


class BotAPIChatMember(types.ChatMember):
    '''
    Modified aiogram.types.ChatMember class with is_kicked() method, 
    which returns whether the status change is due to a chat kick
    '''
    def __init__(self, chatMember: types.ChatMember):
        self.status = chatMember.status
        self.user = chatMember.user

    def is_kicked(self) -> bool:
        return BotAPIChatMemberStatus.is_kicked(self.status)


class BotAPIChatMemberUpdated(types.ChatMemberUpdated):
    '''
    Modified aiogram.types.ChatMember Updated with useful method
    to_message() to convert the chat member's status into a message,
    also information about the status of the chat participant is presented
    BotAPIChatMember class with is_kicked() method
    '''
    def __init__(self, memberInfo: types.ChatMemberUpdated):
        self.chat = memberInfo.chat
        self.from_user = memberInfo.from_user
        self.date = memberInfo.date.timestamp()
        self.old_chat_member = BotAPIChatMember(memberInfo.old_chat_member)
        self.new_chat_member = BotAPIChatMember(memberInfo.new_chat_member)
        self.invite_link = memberInfo.invite_link

    def to_message(self):
        return BotAPIMessage(
            message_id=1,
            date=self.date.timestamp(),
            from_user=self.from_user,
            chat=BotAPIChat(
                id=self.from_user.id,
                type="private"
            )
        )


class BotAPIMessage(types.Message):
    '''
    Simple wrapper over the class aiogram.types.Message needed
    to easily create an object of similar structure
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BotAPIChat(types.Chat):
    '''
    Simple wrapper over the class aiogram.types.Chat needed
    to easily create an object of similar structure
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def state_by_id(id: int) -> FSMContext:
    return dispatcher.current_state(user=id)
