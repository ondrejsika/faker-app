#!/usr/bin/env python

import asyncio
import websockets
import argparse
import logging
import json

root_parser = argparse.ArgumentParser()
root_parser.add_argument(
    '-c', '--client', action='append', type=str, required=True)
root_parser.add_argument("--debug", action="store_true")
root_parser.add_argument("--debug-ws", action="store_true")

args = root_parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG if args.debug_ws else logging.INFO)


async def hello(client):
    while True:
        try:
            async with websockets.connect(client) as websocket:
                logging.info("CONNECTED:%s:%d" % (
                    websocket.remote_address[0], websocket.remote_address[1]))
                try:
                    while True:
                        payload_str = await websocket.recv()
                        payload = json.loads(payload_str)
                        logging.debug(payload_str)
                        if payload["counter"] % 1000 == 0:
                            logging.info(payload_str)

                except websockets.exceptions.ConnectionClosedError as e:
                    pass
        except OSError as e:
            pass
        await asyncio.sleep(1)


loop = asyncio.get_event_loop()
for client in args.client:
    loop.create_task(hello(client))
loop.run_forever()
