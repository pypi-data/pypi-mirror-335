# -*- coding: utf-8 -*-
import redis

from a3redis.bases.base_on_connection import BaseOnConnection


class BaseStructure(BaseOnConnection):
    main_key: str = ""

    def __init__(self, rdb: redis.Redis | redis.RedisCluster | None = None, main_key: str | None = None, **kwargs):
        super().__init__(rdb=rdb)

        self.main_key = main_key or self.main_key
        assert self.main_key not in (None, ""), "main_key must be set"
        if len(kwargs.keys()) > 0:
            self.main_key = self.main_key.format(**kwargs)

    def delete(self) -> int:
        return self.rdb.delete(self.main_key)

    def exists(self) -> bool:
        return bool(self.rdb.exists(self.main_key))

    def expire(self, seconds: int) -> bool:
        return self.rdb.expire(self.main_key, seconds)
