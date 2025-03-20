import time
import threading
import traceback

from typing import Callable
from inspect import isgenerator
from urllib.parse import urlparse
from requests import Response as Res

from cobweb import setting
from cobweb.constant import DealModel, LogTemplate
from cobweb.utils import LoghubDot, check_pause
from cobweb.base import Seed, Queue, BaseItem, Request, Response, logger


class Distributor(threading.Thread):

    def __init__(
            self,
            task: str,
            project: str,
            new: Queue,
            todo: Queue,
            done: Queue,
            upload: Queue,
            register: Callable,
            stop: threading.Event,
            pause: threading.Event,
            SpiderCrawler
    ):
        super().__init__()
        self.task = task
        self.project = project
        self.stop = stop
        self.pause = pause

        self.new = new
        self.todo = todo
        self.done = done
        self.upload = upload
        self.register = register

        self.time_sleep = setting.SPIDER_TIME_SLEEP
        self.thread_num = setting.SPIDER_THREAD_NUM
        self.max_retries = setting.SPIDER_MAX_RETRIES
        self.record_failed = setting.RECORD_FAILED_SPIDER
        self.loghub_dot = LoghubDot()  # todo: 解偶

        self.Crawler = SpiderCrawler

        logger.debug(f"Distribute instance attrs: {self.__dict__}")

    def distribute(self, item, seed, _id: int):
        if isinstance(item, Request):
            seed.params.start_time = time.time()
            self.process(item=item, seed=seed, callback=self.Crawler.download, _id=1)
        elif isinstance(item, Response):
            if _id == 2:
                raise TypeError("parse function can't yield a Response instance")
            dot = isinstance(item.response, Res)
            self.spider_logging(seed, item, dot=dot)
            self.process(item=item, seed=seed, callback=self.Crawler.parse, _id=2)
        elif isinstance(item, BaseItem):
            self.upload.push(item)
        elif isinstance(item, Seed):
            self.new.push((seed, item), direct_insertion=True)
        elif isinstance(item, str) and item == DealModel.poll:
            self.todo.push(seed)
        elif isinstance(item, str) and item == DealModel.done:
            self.done.push(seed)
        elif isinstance(item, str) and item == DealModel.fail:
            seed.params.retry += 1
            if seed.params.retry < self.max_retries:
                self.todo.push(seed)
            else:
                if record_failed := self.record_failed:
                    try:
                        response = Response(seed, "failed", max_retries=True)
                        self.process(response, seed, self.Crawler.parse, _id=2)
                    except:
                        record_failed = False
                if not record_failed:
                    self.done.push(seed)
        else:
            raise TypeError("yield value type error!")

    def process(self, item, seed, callback, _id: int):
        result_iterators = callback(item)
        if not isgenerator(result_iterators):
            raise TypeError(f"{callback.__name__} function isn't a generator!")
        for result_item in result_iterators:
            self.distribute(result_item, seed, _id)

    @check_pause
    def spider(self):
        if seed := self.todo.pop():
            try:
                self.process(item=seed, seed=seed, callback=self.Crawler.request, _id=0)
            except Exception as e:
                url, status = seed.url, e.__class__.__name__
                msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                if getattr(e, "response", None) and isinstance(e.response, Res):
                    url = e.response.request.url
                    status = e.response.status_code
                self.spider_logging(seed, None, error=True, url=url, status=status, msg=msg)
                self.distribute(DealModel.fail, seed, _id=-1)

    def spider_logging(
            self, seed,
            item: Response = None,
            error: bool = False,
            dot: bool = True,
            **kwargs
    ):
        detail_log_info = LogTemplate.log_info(seed.to_dict)
        if error:
            url = kwargs.get("url")
            msg = kwargs.get("msg")
            status = kwargs.get("status")
            if dot:
                self.loghub_dot.build(
                    topic=urlparse(url).netloc,
                    data_size=-1, cost_time=-1,
                    status=status, url=url,
                    seed=seed.to_string,
                    proxy_type=seed.params.proxy_type,
                    proxy=seed.params.proxy,
                    project=self.project,
                    task=self.task, msg=msg,
                )
            logger.info(LogTemplate.download_exception.format(
                detail=detail_log_info,
                retry=seed.params.retry,
                priority=seed.params.priority,
                seed_version=seed.params.seed_version,
                identifier=seed.identifier or "",
                exception=msg
            ))
        else:
            logger.info(LogTemplate.download_info.format(
                detail=detail_log_info,
                retry=seed.params.retry,
                priority=seed.params.priority,
                seed_version=seed.params.seed_version,
                identifier=seed.identifier or "",
                status=item.response,
                response=LogTemplate.log_info(item.to_dict)
            ))
            if dot:
                end_time = time.time()
                stime = seed.params.start_time
                cost_time = end_time - stime if stime else -1
                topic = urlparse(item.response.request.url).netloc
                data_size = int(item.response.headers.get("content-length", 0))
                self.loghub_dot.build(
                    topic=topic, data_size=data_size, cost_time=cost_time,
                    status=200, seed=seed.to_string, url=item.response.url,
                    proxy=seed.params.proxy, proxy_type=seed.params.proxy_type,
                    project=self.project, task=self.task,
                )

    def run(self):
        self.register(self.loghub_dot.build_run, tag="LoghubDot")
        for _ in range(self.thread_num):
            self.register(self.spider, tag="Distributor")
