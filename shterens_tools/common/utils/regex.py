import re
import typing
import random
from uuid import UUID
from ..apis.mtprotoapi import pyrogram
from string import ascii_lowercase

usernamePattern = re.compile("^@[a-zA-Z][a-zA-Z0-9_]{4,}$")
linkPattern = re.compile("^http[s]?:\/\/t.me\/[a-zA-Z][a-zA-Z0-9_]{4,}$")

invitePattern = re.compile("^http[s]?:\/\/t.me\/\+[a-zA-Z0-9_]{16}$")
hashtagPattern = re.compile("(\s#+|\s|^)(#[^\s#:;,?.*$%\"@!+^()=№<>`~[\]{\}\-\\\/']+)")

publicMessagePattern = re.compile("^http[s]?:\/\/t.me\/[a-zA-Z][a-zA-Z0-9_]{4,}\/[1-9][0-9]*$")
privateMessagePattern = re.compile("^http[s]?:\/\/t.me\/c\/[1-9][0-9]{9}\/[1-9][0-9]*$")


def is_link(text: str) -> bool:
    return re.match(linkPattern, text)


def is_username(text: str) -> bool:
    return re.match(usernamePattern, text)


def is_invite(text: str) -> bool:
    return re.match(invitePattern, text)


def link_to_username(link: str) -> str:
    return re.sub("http[s]?:\/\/t.me\/", "@", link, 1)


def link_to_https(link: str) -> str:
    return re.sub("http[s]?", "https", link, 1)


def uuid_to_varname(uuid: UUID) -> str:
    return re.sub("[0-9]", random.choice(ascii_lowercase), uuid.hex, 1)


def oneliner_to_multiliner(oneliner: str) -> str:
    return "\n".join(re.split(";[ ]*", oneliner))


def hashtags_in_text(message: pyrogram.types.Message) -> list:
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption
    else:
        text = ""

    hashtags = []

    for item in re.findall(hashtagPattern, text):
        hashtags.append(item[1][1:])
    
    return list(set(hashtags))


def remove_parameter_from_post_link(link: str) -> str:
    '''
    Removes parameters like:
    https://t.me/channel/2180?single

    '''
    return re.sub("\?[a-z]*", "", link, 1)


def is_post_link(text: str) -> typing.Tuple[bool, str]:
    '''
    Returns isPost flag and accessType for parse_post_link

    '''
    text = remove_parameter_from_post_link(text)

    if re.match(publicMessagePattern, text):
        return True, "public"
    elif re.match(privateMessagePattern, text):
        return True, "private"
    else:
        return False, "none"


def parse_post_link(link: str, accessType: str) -> typing.Tuple[str | int, int]:
    '''
    Returns channel username/id and message id
    
    '''
    link = remove_parameter_from_post_link(link)
    parts = link.rsplit("/", 2)
    
    if accessType == "public":
        return parts[1], int(parts[2])
    elif accessType == "private":
        return normalize_channel_id(int(parts[1])), int(parts[2])


def get_post_link(channel: str | int, messageId: int) -> str:
    if type(channel) is str:
        return f"https://t.me/{channel[1:]}/{messageId}"
    else:
        return f"https://t.me/c/{normalize_channel_id(channel)}/{messageId}"


def normalize_channel_id(channel: int) -> int:
    '''
    Currenly Telegram channel id is a 32-bit number 
    Maximum value is 2,147,483,647, that is 10 digits, preceded by a prefix -100
    Example: -1001597581417

    So, this function adds/removes -100 prefix from the channel id in post links
    1168424223 => -1001168424223
    -1001168424223 => 1168424223

    '''
    return -channel-10**12
