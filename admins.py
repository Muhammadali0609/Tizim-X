from telegram import ChatMemberAdministrator, ChatMemberOwner


async def is_admin(chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)

    return isinstance(
        member,
        (
            ChatMemberAdministrator,
            ChatMemberOwner
        )
    )
