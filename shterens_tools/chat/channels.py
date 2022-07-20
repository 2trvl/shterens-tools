from ..common import *
from .getstats import GetStats, getstats_message_range

@dispatcher.my_chat_member_handler()
async def channel_added(memberInfo: types.ChatMemberUpdated):
    '''
    state.get_data()["type"] ???

        if memberInfo.new_chat_member.can_edit_messages:
            all good
        else:
            await app.send_message(memberInfo.from_user.id, "I need edit messages right")

    elif memberInfo.new_chat_member.is_kicked():
        print("Remove from list")

    elif stateData["substate"] == "channels-add"...
    
    '''
    memberInfo = BotAPIChatMemberUpdated(memberInfo)
    state = state_by_id(memberInfo.from_user.id)
    stateData = await state.get_data()

    if memberInfo.new_chat_member.is_chat_admin() and await state.get_state():
        
        if "substate" in stateData:
            if stateData["substate"] in ("bot-added", "forward-message"):
                await state.update_data(
                    substate="range-start", 
                    id=memberInfo.chat.id, 
                    name=memberInfo.chat.title
                )
                await GetStats.next()
                await getstats_message_range(memberInfo.to_message(), state)

    elif memberInfo.new_chat_member.is_kicked():
        print("Remove from list")
