import json
from typing import Union
from cobweb.base import (
    Seed,
    BaseItem,
    Request,
    Response,
    ConsoleItem,
)


class Crawler:

    @staticmethod
    def request(seed: Seed) -> Union[Request, BaseItem]:
        yield Request(seed.url, seed, timeout=5)

    @staticmethod
    def download(item: Request) -> Union[Seed, BaseItem, Response, str]:
        response = item.download()
        yield Response(item.seed, response, **item.to_dict)

    @staticmethod
    def parse(item: Response) -> BaseItem:
        upload_item = item.to_dict
        upload_item["text"] = item.response.text
        yield ConsoleItem(item.seed, data=json.dumps(upload_item, ensure_ascii=False))

