# -*- coding: utf-8 -*-
from typing import Dict, Union, Optional
from dataclasses import dataclass, field
from redis import Redis, ConnectionPool, Sentinel, RedisCluster, RedisError


DEFAULT_NAME = "default"


class RedisMode:
    Standalone = "standalone"
    Sentinel = "sentinel"
    Cluster = "cluster"


@dataclass
class Conf:
    mode: str
    init: Optional[dict] = field(default_factory=lambda: dict())
    runtime: Optional[dict] = field(default_factory=lambda: dict())


class RedisClientFactory(object):
    _name2conf: Dict[str, Conf] = dict()

    _name2redis: Dict[str, Redis] = dict()
    _name2sentinel: Dict[str, Sentinel] = dict()
    _name2master_redis: Dict[str, Redis] = dict()
    _name2slave_redis: Dict[str, Redis] = dict()
    _name2cluster: Dict[str, RedisCluster] = dict()

    @classmethod
    def is_valid_rdb(cls, rdb: Redis) -> bool:
        try:
            rdb.ping()
            return True
        except RedisError:
            return False

    # 初始化1：多server配置
    @classmethod
    def init_redis_clients(cls, conf: dict):
        for name, info in conf.items():
            _conf = Conf(**info)
            cls._name2conf[name] = _conf
            cls.init_one_redis_client(name=name, conf=_conf)

    # 初始化2：单个server配置
    @classmethod
    def init_one_redis_client(cls, name: str, conf: Conf):
        cls._name2conf[name] = conf
        assert conf.init is not None
        if conf.mode == RedisMode.Standalone:
            connection_pool = ConnectionPool(**conf.init)
            redis = Redis(connection_pool=connection_pool)
            cls._name2redis[name] = redis
        elif conf.mode == RedisMode.Sentinel:
            assert conf.runtime is not None
            sentinel = Sentinel(**conf.init)
            cls._name2sentinel[name] = sentinel
            cls._name2master_redis[name] = sentinel.master_for(**conf.runtime)
            cls._name2slave_redis[name] = sentinel.slave_for(**conf.runtime)
        elif conf.mode == RedisMode.Cluster:
            assert "connection_pool" not in conf.init
            cluster = RedisCluster(**conf.init)
            cls._name2cluster[name] = cluster
        else:
            raise AssertionError(f"Invalid redis server mode [{conf.mode}]")

    # 初始化3：没有指定任何参数，就使用默认配置redis://127.0.0.1:6379/0
    @classmethod
    def _init_default_rdb(cls):
        cls.init_one_redis_client(DEFAULT_NAME, Conf(mode=RedisMode.Standalone, init={"decode_responses": True}))

    @classmethod
    def get_rdb(cls, name: str | None = None, readonly: bool = False) -> Union[Redis, RedisCluster]:
        if name is None:
            name = DEFAULT_NAME

        conf = cls._name2conf.get(name)
        if conf is None:
            if name == DEFAULT_NAME:
                cls._init_default_rdb()
                return cls._name2redis[DEFAULT_NAME]
            else:
                raise AssertionError(f"Invalid redis client [{name}]")

        assert conf.mode in [RedisMode.Standalone, RedisMode.Sentinel, RedisMode.Cluster]
        if conf.mode == RedisMode.Standalone:
            return cls._name2redis[name]
        elif conf.mode == RedisMode.Sentinel:
            # find cache
            if readonly:
                cache_redis = cls._name2slave_redis.get(name)
            else:
                cache_redis = cls._name2master_redis.get(name)
            # check
            if cache_redis is not None and cls.is_valid_rdb(cache_redis):
                return cache_redis

            # new
            sentinel: Sentinel = cls._name2sentinel[name]
            assert conf.runtime is not None

            if readonly:
                slave_redis = sentinel.slave_for(**conf.runtime)
                cls._name2slave_redis[name] = slave_redis
                return slave_redis
            else:
                master_redis = sentinel.master_for(**conf.runtime)
                cls._name2master_redis[name] = master_redis
                return master_redis
        else:
            return cls._name2cluster[name]
