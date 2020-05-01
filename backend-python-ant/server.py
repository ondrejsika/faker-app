#!/usr/bin/env python

import asyncio
import json
import websockets
import socket
import time
import logging
import argparse
import random
import collections
import quotes
import prometheus_client


root_parser = argparse.ArgumentParser()
root_parser.add_argument("--host", type=str, default="0.0.0.0")
root_parser.add_argument("--port", type=int, default=80)
root_parser.add_argument("--metrics-port", type=int, default=8080)
root_parser.add_argument("--instance", type=int, default=0)
root_parser.add_argument("--wait", type=int)
root_parser.add_argument("--debug", action="store_true")
root_parser.add_argument("--debug-ws", action="store_true")

args = root_parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG if args.debug_ws else logging.INFO)

HOSTNAME = socket.gethostname()
STARTUP_TIME = int(time.time())
BACKEND_ID = "%s-%d-%d" % (HOSTNAME, args.instance, STARTUP_TIME)

prom_counter = prometheus_client.Counter("message", "Number of send messages")

CLIENTS = set()
COUNTER = collections.Counter()

def random_quote():
    return "%s: %s" % quotes.Quotes().random()


def register(websocket):
    CLIENTS.add(websocket)
    logging.info("CONNECTED:%s:%d" %
                 (websocket.remote_address[0], websocket.remote_address[1]))


def unregister(websocket):
    CLIENTS.remove(websocket)
    logging.info("DISCONNECTED:%s:%d" %
                 (websocket.remote_address[0], websocket.remote_address[1]))


async def hello(websocket, path):
    register(websocket)
    try:
        while True:
            COUNTER[websocket] += 1
            COUNTER["_total"] += 1
            prom_counter.inc()
            payload = json.dumps({
                "backend_impl": "python-ant",
                "backend_id": BACKEND_ID,
                "clients_count": len(CLIENTS),
                "counter": COUNTER[websocket],
                "counter_total": COUNTER["_total"],
                "timestamp": int(time.time()),
                "message": random_quote(),
            })
            await websocket.send(payload)
            logging.debug("%s %s" % (BACKEND_ID, payload))
            wait = (args.wait or random.randint(100, 1000)) / 1000.
            await asyncio.sleep(wait)

    finally:
        unregister(websocket)

logging.info("STARTUP:%s" % BACKEND_ID)
prometheus_client.start_http_server(args.metrics_port)
start_server = websockets.serve(hello, args.host, args.port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
