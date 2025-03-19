import asyncio, websockets, json, sys
from loguru import logger

logger.remove()
logger.add(sys.stdout, format=(
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>  -  <level>{message}</level>"
), level="DEBUG")

class Client():
    def __init__(self, chat_id='default'):
        self.chat_id = chat_id
        self.websocket = None
        self.events = {}

    def event(self, func):
        self.events[func.__name__] = func
        return func
    
    async def connect(self):
        async with websockets.connect(f'wss://api.skigmanetwork.de/ws?bot=TRUE&?code={self.chat_id}') as ws:
            self.websocket = ws
            logger.debug(f'Bot is running on Chat ID {self.chat_id}!')
            await self.listen()
    
    async def send_message(self, content, hidden=False):
        if self.websocket:
            await self.websocket.send(json.dumps({ 'content': content }) if not hidden else content)
        else:
            logger.error('Cannot send a message before websocket is connected!')
    
    async def join_chatroom(self, chat_id):
        self.chat_id = chat_id
        await self.websocket.close()
        async with websockets.connect(f'wss://api.skigmanetwork.de/ws?bot=TRUE&?code={chat_id}') as ws:
            self.websocket = ws
            logger.debug(f'Bot is running on Chat ID {self.chat_id}!')
            await self.listen()

    async def listen(self):
        is_first_message = True
        async for message in self.websocket:
            data = json.loads(message)
            if is_first_message:
                if 'on_ready' in self.events:
                    await self.events['on_ready'](self, data)
                is_first_message = False
            
            event_type = None
            if 'from' in data:
                event_type = 'hidden_message_create'
            elif 'type' in data and data['type'] == 'status':
                event_type = 'online_users_update'
            elif 'type' in data and data['type'] == 'message':
                event_type = 'message_create'
            elif not 'type' in data and 'content' in data:
                event_type = 'system_message_create'
            else:
                event_type = 'unknown'

            if event_type and event_type in self.events:
                await self.events[event_type](self, data)

    def login(self):
        asyncio.run(self.connect())


## probably how it works idk
## fuck python
# client = skigmachat.Client()
# @client.event
# async def on_message(data):
#   print(data)
#
# client.login()