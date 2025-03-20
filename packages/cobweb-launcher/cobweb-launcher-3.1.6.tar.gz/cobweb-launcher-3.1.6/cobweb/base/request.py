import random
import requests


class Request:

    __REQUEST_ATTRS__ = {
        "params",
        "headers",
        "cookies",
        "data",
        "json",
        "files",
        "auth",
        "timeout",
        "proxies",
        "hooks",
        "stream",
        "verify",
        "cert",
        "allow_redirects",
    }

    def __init__(
            self,
            url,
            seed,
            random_ua=True,
            check_status_code=True,
            **kwargs
    ):
        self.url = url
        self.seed = seed
        self.check_status_code = check_status_code
        self.request_setting = {}

        for k, v in kwargs.items():
            if k in self.__class__.__REQUEST_ATTRS__:
                self.request_setting[k] = v
                continue
            self.__setattr__(k, v)

        if not getattr(self, "method", None):
            self.method = "POST" if self.request_setting.get("data") or self.request_setting.get("json") else "GET"

        if random_ua:
            self._build_header()

    @property
    def _random_ua(self) -> str:
        v1 = random.randint(4, 15)
        v2 = random.randint(3, 11)
        v3 = random.randint(1, 16)
        v4 = random.randint(533, 605)
        v5 = random.randint(1000, 6000)
        v6 = random.randint(10, 80)
        user_agent = (f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{v1}_{v2}) AppleWebKit/{v4}.{v3} "
                      f"(KHTML, like Gecko) Chrome/105.0.0.0 Safari/{v4}.{v3} Edg/105.0.{v5}.{v6}")
        return user_agent

    def _build_header(self) -> dict:
        if not self.request_setting.get("headers"):
            self.request_setting["headers"] = {"accept": "*/*", "user-agent": self._random_ua}
        elif "user-agent" not in [key.lower() for key in self.request_setting["headers"].keys()]:
            self.request_setting["headers"]["user-agent"] = self._random_ua

    def download(self) -> requests.Response:
        response = requests.request(self.method, self.url, **self.request_setting)
        if self.check_status_code:
            response.raise_for_status()
        return response

    @property
    def to_dict(self):
        _dict = self.__dict__.copy()
        _dict.pop('url')
        _dict.pop('seed')
        _dict.pop('check_status_code')
        _dict.pop('request_setting')
        return _dict


