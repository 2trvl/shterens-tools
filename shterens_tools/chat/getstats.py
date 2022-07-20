import typing
import asyncio
from ..common import *

class GetStats(StatesGroup):
    waiting_for_channel_link = State()
    checking_channel_permission = State()
    waiting_for_stats_messages_range = State()
    waiting_for_tags_preferences = State()
    processing_stats = State()


@dispatcher.message_handler(commands="getstats")
async def getstats(message: types.Message):
    '''
    Entry point in /getstats
    Get statistics for the channel
    
    '''
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text=await locale_string_by_id("getstats-steps-button", message.from_user.id), 
            callback_data="getstats-start"
        )
    )

    await message.answer(
        await locale_string_by_id("getstats-steps", message.from_user.id),
        reply_markup=keyboard
    )


@dispatcher.callback_query_handler(text="getstats-start", state="*")
async def getstats_start(call: types.CallbackQuery, state: FSMContext):
    '''
    /getstats

    '''
    if "substate" not in await state.get_data():
        await call.message.answer(
            await locale_string_by_id("getstats-link", call.from_user.id)
        )
        await GetStats.waiting_for_channel_link.set()


@dispatcher.message_handler(commands="cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    if await state.get_state() is None:
        return
    await state.finish()
    await message.answer(
        await locale_string_by_id("cancel", message.from_user.id), 
        reply_markup=types.ReplyKeyboardRemove()
    )


@dispatcher.message_handler(state=GetStats.waiting_for_channel_link)
async def getstats_link(message: types.Message, state: FSMContext):
    '''
    /getstats : Waiting for channel link

    '''
    username = None

    if is_link(message.text):
        username = link_to_username(message.text)

    elif is_username(message.text):
        username = message.text

    elif is_invite(message.text):
        await state.update_data(substate="request-permission")
        await GetStats.checking_channel_permission.set()
        await getstats_permission(message, state)
        return

    else:
        await message.answer(
            await locale_string_by_id("getstats-link-error", message.from_user.id)
        )
        return
    
    try:
        chatInfo = await app.get_chat(username)
    except MTProtoAPIBadRequest:
        await message.answer(
            await locale_string_by_id("getstats-link-error", message.from_user.id)
        )
        return

    if chatInfo.type == ChatType.CHANNEL:
        await state.update_data(
            substate="range-start", 
            username=username, 
            id=chatInfo.id, 
            name=chatInfo.title
        )
        await GetStats.waiting_for_stats_messages_range.set()
        await getstats_message_range(message, state)
    else:
        await message.answer(
            await locale_string_by_id("getstats-link-error", message.from_user.id)
        )


@dispatcher.message_handler(
    MediaGroupFilter(is_media_group=False), 
    state=GetStats.checking_channel_permission, 
    content_types=["any"])
@dispatcher.callback_query_handler(
    text="getstats-bot-added", 
    state=GetStats.checking_channel_permission)
async def getstats_permission(object: types.Message | types.CallbackQuery, state: FSMContext):
    '''
    /getstats : Checking channel permission

    '''
    getstatsData = await state.get_data()
    
    if getstatsData["substate"] == "request-permission" and isinstance(object, types.Message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=await locale_string_by_id("getstats-permission-button", object.from_user.id),
                callback_data="getstats-bot-added"
            )
        )
        await object.answer(
            await locale_string_by_id("getstats-permission", object.from_user.id), 
            reply_markup=keyboard
        )
        await state.update_data(substate="bot-added")
    
    elif getstatsData["substate"] == "bot-added" and isinstance(object, types.CallbackQuery):
        await object.message.answer(
            await locale_string_by_id("getstats-permission-forward", object.from_user.id)
        )
        await state.update_data(substate="forward-message")

    elif getstatsData["substate"] == "forward-message" and isinstance(object, types.Message):    
        
        if object.is_forward():
            try:
                await app.get_messages(
                    chat_id=object.forward_from_chat.id, 
                    message_ids=object.forward_from_message_id
                )
                await state.update_data(
                    substate="range-start",
                    id=object.forward_from_chat.id,
                    name=object.forward_from_chat.title
                )
                await GetStats.next()
                await getstats_message_range(object, state)
            except (NotAcceptable, AttributeError):
                await object.answer(
                    await locale_string_by_id("getstats-permission-error", object.from_user.id)
                )
        
        elif object.text or object.caption:
            isPost, accessType = is_post_link(object.html_text)
            if isPost:
                try:
                    chatId, messageId = parse_post_link(
                        object.html_text, 
                        accessType
                    )
                    post = await app.get_messages(
                        chat_id=chatId, 
                        message_ids=messageId
                    )
                    await state.update_data(
                        substate="range-start", 
                        id=post.chat.id, 
                        name=post.chat.title
                    )
                    await GetStats.next()
                    await getstats_message_range(object, state)
                except (NotAcceptable, UsernameNotOccupied):
                    await object.answer(
                        await locale_string_by_id("getstats-permission-error", object.from_user.id)
                    )


@dispatcher.message_handler(MediaGroupFilter(is_media_group=True), state="*", content_types=["any"])
@media_group_handler
async def handle_forwarded_media_group(messages: typing.List[types.Message]):
    state = state_by_id(messages[0].from_user.id)
    stateData = await state.get_data()

    if messages[0].is_forward() and await state.get_state():
        
        if "substate" in stateData:
            if stateData["substate"] == "forward-message":
                await getstats_permission(messages[0], state)
            elif stateData["substate"] in ("range-start-handle", "range-end"):
                await getstats_message_range(messages[0], state)


@dispatcher.message_handler(MediaGroupFilter(is_media_group=False), 
                            state=GetStats.waiting_for_stats_messages_range, 
                            content_types=["any"])
async def getstats_message_range(message: types.Message, state: FSMContext):
    '''
    /getstats : Waiting for channel message

    '''
    getstatsData = await state.get_data()

    if getstatsData["substate"] == "range-start":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            await locale_string_by_id("getstats-range-start-default-button", message.from_user.id)
        )
        await message.answer(
            await locale_string_by_id("getstats-message-range-start", message.from_user.id), 
            reply_markup=keyboard
        )
        await state.update_data(substate="range-start-handle", range=[1, 1])

    elif getstatsData["substate"] == "range-start-handle":

        if message.is_forward():

            if message.forward_from_chat:

                if message.forward_from_chat.id == getstatsData["id"]:
                    await message.answer(
                        await locale_string_by_id("getstats-message-range-end", message.from_user.id), 
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    await state.update_data(
                        substate="range-end", 
                        range=[message.forward_from_message_id, 1]
                    )
                else:
                    await message.answer(
                        await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                    )
            else:
                await message.answer(
                    await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                )
        
        elif message.text or message.caption:

            if message.html_text in localesButtonGroup["getstats-range-default"]:
                await message.answer(
                    await locale_string_by_id("getstats-message-range-end", message.from_user.id), 
                    reply_markup=types.ReplyKeyboardRemove()
                )
                await state.update_data(substate="range-end")
            
            else:
                isPost, accessType = is_post_link(message.html_text)
                if isPost:
                    try:
                        chatId, messageId = parse_post_link(message.html_text, accessType)
                        
                        if accessType == "public":
                            if "username" in getstatsData:
                                chatId = (await app.get_chat(getstatsData["username"])).id
                            else:
                                await message.answer(
                                    await locale_string_by_id("getstats-permission-error", message.from_user.id)
                                )
                                return
                        
                        if chatId == getstatsData["id"]:
                            post = await get_post_messages(chatId, messageId)
                            await message.answer(
                                await locale_string_by_id("getstats-message-range-end", message.from_user.id), 
                                reply_markup=types.ReplyKeyboardRemove()
                            )
                            await state.update_data(substate="range-end", range=[post[0].id, 1])
                        else:
                            await message.answer(
                                await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                            )
                    
                    except (NotAcceptable, UsernameNotOccupied):
                        await message.answer(
                            await locale_string_by_id("getstats-permission-error", message.from_user.id)
                        )

    elif getstatsData["substate"] == "range-end":
        
        if message.is_forward():

            if message.forward_from_chat:

                if message.forward_from_chat.id == getstatsData["id"]:

                    if message.forward_from_message_id >= getstatsData["range"][0]:
                        await state.update_data(
                            substate="tags-options", 
                            range=[getstatsData["range"][0], 
                            message.forward_from_message_id]
                        )
                        await GetStats.next()
                        await getstats_tags(message, state)
                    else:
                        await message.answer(
                            await locale_string_by_id("getstats-message-range-end-error", message.from_user.id)
                        )
                else:
                    await message.answer(
                        await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                    )
            else:
                await message.answer(
                    await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                )
        
        elif message.text or message.caption:
            isPost, accessType = is_post_link(message.html_text)
            if isPost:
                try:
                    chatId, messageId = parse_post_link(message.html_text, accessType)
                    
                    if accessType == "public":
                        if "username" in getstatsData:
                            chatId = (await app.get_chat(getstatsData["username"])).id
                        else:
                            await message.answer(
                                await locale_string_by_id("getstats-permission-error", message.from_user.id)
                            )
                            return
                    
                    if chatId == getstatsData["id"]:
                        post = await get_post_messages(chatId, messageId)
                        
                        if post[0].id >= getstatsData["range"][0]:
                            await state.update_data(
                                substate="tags-options", 
                                range=[getstatsData["range"][0], 
                                post[0].id]
                            )
                            await GetStats.next()
                            await getstats_tags(message, state)
                        else:
                            await message.answer(
                                await locale_string_by_id("getstats-message-range-end-error", message.from_user.id)
                            )
                    else:
                        await message.answer(
                            await locale_string_by_id("getstats-message-range-error", message.from_user.id)
                        )
                
                except (NotAcceptable, UsernameNotOccupied):
                    await message.answer(
                        await locale_string_by_id("getstats-permission-error", message.from_user.id)
                    )


@dispatcher.message_handler(state=GetStats.waiting_for_tags_preferences)
async def getstats_tags(message: types.Message, state: FSMContext):
    '''
    /getstats : Waiting for tags preferences

    '''
    getstatsData = await state.get_data()

    if getstatsData["substate"] == "tags-options":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            * await locale_string_by_id("getstats-tags-preferences-buttons", message.from_user.id)
        )
        await message.answer(
            await locale_string_by_id("getstats-tags-preferences", message.from_user.id), 
            reply_markup=keyboard
        )
        await state.update_data(substate="tags-option-chosen")
    
    elif getstatsData["substate"] == "tags-option-chosen":
        if message.text in localesButtonGroup["getstats-tags-skip"]:
            await state.update_data(
                substate="processing", 
                include=[], 
                exclude=[]
            )
            await GetStats.processing_stats.set()
            await getstats_processing(message, state)
        
        elif message.text in localesButtonGroup["getstats-tags-include"]:
            await message.answer(
                await locale_string_by_id("getstats-tags-preferences-include", message.from_user.id), 
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.update_data(substate="include")

        elif message.text in localesButtonGroup["getstats-tags-exclude"]:
            await message.answer(
                await locale_string_by_id("getstats-tags-preferences-exclude", message.from_user.id), 
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.update_data(substate="exclude")
    
    elif getstatsData["substate"] == "include":
        await state.update_data(
            substate="processing", 
            include=message.text.replace("#", "").split(), 
            exclude=[]
        )
        await GetStats.processing_stats.set()
        await getstats_processing(message, state)

    elif getstatsData["substate"] == "exclude":
        await state.update_data(
            substate="processing", 
            include=[], 
            exclude=message.text.replace("#", "").split()
        )
        await GetStats.processing_stats.set()
        await getstats_processing(message, state)


async def getstats_processing(message: types.Message, state: FSMContext, inChannel: bool=False):
    '''
    /getstats : Processing channel's stats

    '''
    getstatsData = await state.get_data()

    #  Pyrogram needs to cache access hash, and then the channel can be accessed by its id
    #  This happens in the case of public channels, in which it is not necessary to add a bot
    if "username" in getstatsData:
        await app.get_chat(getstatsData["username"])
    
    #  That it is currently only possible to edit messages without reply_markup
    progressMessage = await message.answer(
        await locale_string_by_id("getstats-args-saved", message.from_user.id),
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    progressMessage = await message.answer(
        await locale_string_by_id("getstats-preprocessing", message.from_user.id)
    )
    
    stats = {"messages": [], "tags": {}}
    startId = getstatsData["range"][0]
    endId = getstatsData["range"][1]
    
    #  Create progressbar
    progress = ProgressBar(
        tasks=endId-startId+1,
        prefix=await locale_string_by_id("getstats-processing-prefix", message.from_user.id)
    )

    await state.update_data(substate="processing.searching_for_tags")

    try:
        while startId < endId+1:
            for attempt in range(5):
                try:
                    post = await get_post_messages(chatId=getstatsData["id"], messageId=startId)
                    post[0] = MTProtoMessage(post[0])
                    
                    if not post[0].empty and not post[0].is_service_message():
                        stats["messages"].append(post[0].id)
                        tags = hashtags_in_text(post[0])
                        for tag in tags:
                            if tag in stats["tags"]:
                                stats["tags"][tag] += 1
                            else:
                                stats["tags"][tag] = 1
                            await asyncio.sleep(0)
                    
                    if progress.update(len(post)):
                        await progressMessage.edit_text(progress.get())
                    
                    startId = post[-1].id + 1
                    await asyncio.sleep(0)

                    #  Checks if /cancel has been called
                    if await state.get_state() is None:
                        return
                
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                else:
                    break
            else:
                raise FloodWait
        else:
            #  Finish progress bar if it's not
            if progress.isNotFinised:
                await progressMessage.edit_text(progress.get())
            
            await state.update_data(substate="processing.applying_tags_preferences")

            tags = stats["tags"].copy().keys()
            include = getstatsData["include"]
            exclude = getstatsData["exclude"]
            
            if include:
                for tag in tags:
                    if tag not in include:
                        stats["tags"].pop(tag)
                    await asyncio.sleep(0)

            elif exclude:
                for tag in exclude:
                    stats["tags"].pop(tag, None)
                    await asyncio.sleep(0)

            await state.update_data(substate="processing.creating_stats_message")

            if inChannel:
                statsResult = await locale_string_by_id("getstats-processing-result-in-channel", message.from_user.id)
                statsResult = statsResult.format(
                    await create_post_reference(getstatsData, stats["messages"][0]),
                    len(stats["messages"]),
                    await create_tags_list(stats["tags"], message.from_user.id)
                )
                #  Edit in channel action
            else:
                statsResult = await locale_string_by_id("getstats-processing-result", message.from_user.id)
                statsResult = statsResult.format(
                    getstatsData["name"],
                    await create_post_reference(getstatsData, stats["messages"][0]),
                    await create_post_reference(getstatsData, stats["messages"][-1]),
                    len(stats["messages"]),
                    await create_tags_list(stats["tags"], message.from_user.id)
                )
            
            logger.info(f"/getstats : Statistics generated for «{getstatsData['name']}» by user with id {message.from_user.id}")
            await message.answer(
                text=statsResult, 
                disable_web_page_preview=True
            )
    
    except NotAcceptable:
        logger.error(f"/getstats : NotAcceptable : Statistics for «{getstatsData['name']}» by user with id {message.from_user.id}")
        await message.answer(
            await locale_string_by_id("getstats-processing-access-error", message.from_user.id)
        )
    
    except FloodWait:
        logger.error(f"/getstats : FloodWait : Statistics for «{getstatsData['name']}» by user with id {message.from_user.id}")
        await message.answer(
            await locale_string_by_id("getstats-processing-flood-error", message.from_user.id)
        )
    
    await state.finish()


async def create_post_reference(data: dict, messageId: int) -> str:    
    
    if "username" in data:
        channel = data["username"]
    else:
        channel = data["id"]
    
    for attempt in range(5):
        try:
            post = await app.get_messages(
                chat_id=channel, 
                message_ids=messageId
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        else:
            break
    else:
        raise FloodWait
    
    return "<a href=\"{}\">{}</a>".format(
        get_post_link(channel, messageId), 
        post.date.strftime("%d.%m.%Y")
    )


async def create_tags_list(tags: typing.Dict[str, int], userId: int) -> str:
    tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True))
    tagsList = []
    
    for tag, value in tags.items():
        tagsList.append(f"{tag} – {value}")
        await asyncio.sleep(0)
    
    if tagsList:
        return ", ".join(tagsList)
    else:
        return await locale_string_by_id("getstats-processing-result-no-tags", userId)
