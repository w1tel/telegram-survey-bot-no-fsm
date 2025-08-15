from telebot.types import Message
from typing import Tuple


def get_key(msg_or_call) -> Tuple[int, int]:
    if isinstance(msg_or_call, Message):
        return (msg_or_call.chat.id, msg_or_call.from_user.id)
    else:
        return (msg_or_call.message.chat.id, msg_or_call.from_user.id)
