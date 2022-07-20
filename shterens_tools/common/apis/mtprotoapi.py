import typing
import pyrogram
from pyrogram.enums import ChatType
from ..resources.config import config
from pyrogram.errors import (
    FloodWait,
    NotAcceptable,
    UsernameNotOccupied,
    BadRequest as MTProtoAPIBadRequest
)

apiId = config.getint("MTProtoAPI", "apiId")
apiHash = config.get("MTProtoAPI", "apiHash")
botToken = config.get("BotAPI", "botToken")

app = pyrogram.Client(
    "shterens_tools",
    api_id=apiId,
    api_hash=apiHash,
    bot_token=botToken,
    in_memory=True
)

class MTProtoMessage(pyrogram.types.Message):
    '''
    Modified class pyrogram.types.Message with method is_service_message(),
    which returns whether the message is a service message
    
    these are notifications about:
    * avatar changes
    * messages pins
    * voice chat starting and so on ...
    '''
    def __init__(self, message: pyrogram.types.Message):
        for key, value in message.__dict__.items():
            setattr(self, key, value)
    
    def is_service_message(self):
        return self.service


async def get_post_messages(chatId: int, messageId: int) -> typing.List[pyrogram.types.Message]:
    '''
    Returns a message from a chat or the message group it belongs to

    :param chatId: Id of the chat in which the message was sent
    :param messageId: Message id
    '''
    try:
        post = await app.get_media_group(
            chat_id=chatId, 
            message_id=messageId
        )
    except ValueError:
        post = await app.get_messages(
            chat_id=chatId, 
            message_ids=[messageId]
        )
    return post
