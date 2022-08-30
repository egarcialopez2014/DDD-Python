import redis
from domain import events
import config
import logging
import json
from dataclasses import asdict

r =redis.Redis(**config.get_redis_host_and_port())

def publish(channel, event:events.Event):
    logging.debug('publishing: channel = %s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))
