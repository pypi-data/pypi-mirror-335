import json
import time
import hashlib


class SeedParams:

    def __init__(self, retry, priority, seed_version, seed_status=None, proxy_type=None, proxy=None):
        self.retry = retry or 0
        self.priority = priority or 300
        self.seed_version = seed_version or int(time.time())
        self.seed_status = seed_status
        self.proxy_type = proxy_type
        self.proxy = proxy


class Seed:

    __SEED_PARAMS__ = [
        "retry",
        "priority",
        "seed_version",
        "seed_status",
        "proxy_type",
        "proxy"
    ]

    def __init__(
            self,
            seed,
            sid=None,
            retry=None,
            priority=None,
            seed_version=None,
            seed_status=None,
            proxy_type=None,
            proxy=None,
            **kwargs
    ):
        if any(isinstance(seed, t) for t in (str, bytes)):
            try:
                item = json.loads(seed)
                self._init_seed(item)
            except json.JSONDecodeError:
                self.__setattr__("url", seed)
        elif isinstance(seed, dict):
            self._init_seed(seed)
        else:
            raise TypeError(Exception(
                f"seed type error, "
                f"must be str or dict! "
                f"seed: {seed}"
            ))

        seed_params = {
            "retry": retry,
            "priority": priority,
            "seed_version": seed_version,
            "seed_status": seed_status,
            "proxy_type": proxy_type,
            "proxy": proxy
        }

        if kwargs:
            self._init_seed(kwargs)
            seed_params.update({
                k:v for k, v in kwargs.items()
                if k in self.__SEED_PARAMS__
            })
        if sid or not getattr(self, "sid", None):
            self._init_id(sid)
        self.params = SeedParams(**seed_params)

    def __getattr__(self, name):
        return None

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def __repr__(self):
        chars = [f"{k}={v}" for k, v in self.__dict__.items()]
        return f'{self.__class__.__name__}({", ".join(chars)})'

    def _init_seed(self, seed_info:dict):
        for k, v in seed_info.items():
            if k not in self.__SEED_PARAMS__:
                self.__setattr__(k, v)

    def _init_id(self, sid):
        if not sid:
            sid = hashlib.md5(self.to_string.encode()).hexdigest()
        self.__setattr__("sid", sid)

    @property
    def to_dict(self) -> dict:
        seed = self.__dict__.copy()
        if seed.get("params"):
            del seed["params"]
        return seed

    @property
    def to_string(self) -> str:
        return json.dumps(
            self.to_dict,
            ensure_ascii=False,
            separators=(",", ":")
        )

    @property
    def get_all(self):
        return json.dumps(
            self.__dict__,
            ensure_ascii=False,
            separators=(",", ":")
        )

