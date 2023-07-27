

# main.py  
import sys  
import os  
import traceback  
from datetime import datetime  
from http import HTTPStatus  
  
from aiohttp import web  
from aiohttp.web import Request, Response, json_response  
from botbuilder.core import (  
    BotFrameworkAdapterSettings,  
    TurnContext,  
    BotFrameworkAdapter,  
    MemoryStorage,  
    ConversationState  
)  
from botbuilder.core.integration import aiohttp_error_middleware  
from botbuilder.schema import Activity, ActivityTypes  
  
from bot import MyBot  
from config import DefaultConfig  
  
CONFIG = DefaultConfig()  
  
# Create adapter.  
# See https://aka.ms/about-bot-adapter to learn more about how bots work.  
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)  
ADAPTER = BotFrameworkAdapter(SETTINGS)  
  
# ...  
  
memory_storage = MemoryStorage()  
conversation_state = ConversationState(memory_storage)  
BOT = MyBot(conversation_state) 


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
