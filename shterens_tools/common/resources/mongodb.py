import typing
import asyncio
from .logs import *
from ..apis.botapi import *
from motor import motor_asyncio
from pymongo.errors import OperationFailure

mongoClient = None
shterensToolsDB = None
usersCollection = None


async def init_db(
) -> typing.Tuple[motor_asyncio.AsyncIOMotorClient,
                  motor_asyncio.AsyncIOMotorDatabase,
                  motor_asyncio.AsyncIOMotorCollection]:
    '''
    Gets shterens_tools database, in which creates users collection

    '''
    mongoClient: motor_asyncio.AsyncIOMotorClient = motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    #  Patch get_io_loop to avoid conflicts with multiple event loops
    mongoClient.get_io_loop = asyncio.get_running_loop
    
    if "shterens_tools" not in await mongoClient.list_database_names():
        mongoClient.get_database("shterens_tools")

    shterensToolsDB: motor_asyncio.AsyncIOMotorDatabase = mongoClient.shterens_tools
    
    try:
        if "users" not in await shterensToolsDB.list_collection_names():
            await shterensToolsDB.create_collection("users")
    except OperationFailure:
        pass

    usersCollection: motor_asyncio.AsyncIOMotorCollection = shterensToolsDB.users

    return mongoClient, shterensToolsDB, usersCollection


async def add_user(id: types.base.Integer):
    logger.info(f"/start : New user with id {id} added")
    await usersCollection.insert_one({ "_id": id, "language": "en", "channels": [] })


async def user_by_id(id: types.base.Integer) -> dict:
    return await usersCollection.find_one({ "_id": id })


async def lang_by_id(id: types.base.Integer) -> str:
    return (await user_by_id(id))["language"]


async def set_lang(id: types.base.Integer, lang: str):
    await usersCollection.update_one({ "_id": id }, { "$set": { "language": lang }})


#  This event loop is for mongodb init only, so it can be safely closed
loop = asyncio.new_event_loop()
mongoClient, shterensToolsDB, usersCollection = loop.run_until_complete(init_db())
loop.close()
