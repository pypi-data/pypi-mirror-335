import time
import threading
from typing import Callable
from cobweb import setting
from cobweb.base import Queue, logger
from cobweb.utils import check_pause


class Uploader(threading.Thread):

    def __init__(
            self,
            stop: threading.Event,
            pause: threading.Event,
            upload: Queue, done: Queue,
            register: Callable,
            SpiderPipeline
    ):
        super().__init__()
        self.stop = stop
        self.pause = pause

        self.done = done
        self.upload = upload
        self.register = register

        self.upload_size = setting.UPLOAD_QUEUE_MAX_SIZE
        self.wait_seconds = setting.UPLOAD_QUEUE_WAIT_SECONDS

        self.pipeline = SpiderPipeline()

        logger.debug(f"Uploader instance attrs: {self.__dict__}")

    @check_pause
    def upload_data(self):
        if not self.upload.length:
            time.sleep(self.wait_seconds)
            return
        if self.upload.length < self.upload_size:
            time.sleep(self.wait_seconds)
        data_info, seeds = {}, []
        try:
            for _ in range(self.upload_size):
                item = self.upload.pop()
                if not item:
                    break
                seeds.append(item.seed)
                data = self.pipeline.build(item)
                data_info.setdefault(item.table, []).append(data)
            for table, datas in data_info.items():
                try:
                    self.pipeline.upload(table, datas)
                except Exception as e:
                    logger.info(e)
        except Exception as e:
            logger.info(e)
        if seeds:
            self.done.push(seeds)

        logger.info("upload pipeline close!")

    def run(self):
        self.register(self.upload_data, tag="Uploader")


