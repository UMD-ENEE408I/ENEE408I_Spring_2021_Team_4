#!/usr/bin/env python3

import asyncio
import json
import websockets
import threading
import time
import queue

# A simple object for communicating with a websocket server
class RobotChatClient(object):
    def __init__(self, uri, callback):
        self.uri = uri
        self.callback = callback

        self.send_message_dict_queue = asyncio.Queue()
        self.event_loop = asyncio.new_event_loop()
        self.websocket = None

        self.thread = threading.Thread(target=self.send_receive_thread,
                                       args=[self.event_loop,])
        self.thread.start()

        # Hack to wait for the websocket to be created
        while self.websocket is None:
            time.sleep(0.001)

    # This cannot be the best way to handle asynchronous routines like this
    # but it works and it is one of the simpler ways
    def send_receive_thread(self, event_loop):
        # Set the event loop for this thread to be the same as the other thread
        asyncio.set_event_loop(event_loop)

        # Make the websocket in this thread since it's not clear
        # if event loops can be shared between threads
        # This is not good because there is not a super easy way
        # to close the socket on exit
        self.websocket = asyncio.get_event_loop().run_until_complete(websockets.connect(self.uri))

        # For every message that is received, decode the message into
        # a dictionary and pass it to the callback
        async def _receive_coroutine():
            async for message in self.websocket:
                message_dict = json.loads(message)
                asyncio.get_event_loop().call_soon_threadsafe(
                    self.callback, message_dict)

        # Run the receive routine continuously on this thread
        asyncio.get_event_loop().run_until_complete(_receive_coroutine())

    async def _send_coroutine(self, message_dict):
        message_json_string = json.dumps(message_dict)
        await self.websocket.send(message_json_string)

    # Encode a python dictionary into a string and send it with a websocket
    def send(self, message_dict):
        asyncio.run_coroutine_threadsafe(self._send_coroutine(message_dict), self.event_loop)
