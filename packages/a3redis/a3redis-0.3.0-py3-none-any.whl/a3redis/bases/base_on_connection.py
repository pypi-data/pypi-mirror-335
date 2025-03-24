# -*- coding: utf-8 -*-
from abc import ABC
import redis

from .redis_client_factory import RedisClientFactory


class BaseOnConnection(ABC):
    rdb: redis.Redis | redis.RedisCluster
    rdb_conf_name: str | None = None

    def __init__(self, rdb: redis.Redis | redis.RedisCluster | None = None):
        class_rdb = getattr(self.__class__, "class_rdb", None)
        self.rdb = rdb or class_rdb or RedisClientFactory.get_rdb(name=self.rdb_conf_name)
