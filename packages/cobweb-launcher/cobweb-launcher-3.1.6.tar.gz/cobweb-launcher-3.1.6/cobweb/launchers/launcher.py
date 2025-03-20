import time
import uuid
import inspect
import threading
import importlib

from cobweb import setting
from cobweb.base import Seed, Queue, logger
from cobweb.utils.tools import dynamic_load_class
from cobweb.launchers.distributor import Distributor
from cobweb.launchers.uploader import Uploader


class Launcher:

    _NEW_QUEUE_ = Queue()
    _TODO_QUEUE_ = Queue()
    _DONE_QUEUE_ = Queue()
    _UPLOAD_QUEUE_ = Queue()

    __WORKER_THREAD__ = dict()
    __REGISTER_FUNC__ = dict()

    def __init__(self, task, project, custom_setting=None, **kwargs):
        super().__init__()

        self.task = task
        self.project = project

        self._app_time = int(time.time())
        self._stop = threading.Event()  # 结束事件
        self._pause = threading.Event()  # 暂停事件

        _setting = dict()

        if custom_setting:
            if isinstance(custom_setting, dict):
                _setting = custom_setting
            else:
                if isinstance(custom_setting, str):
                    custom_setting = importlib.import_module(custom_setting)
                if not inspect.ismodule(custom_setting):
                    raise Exception
                for k, v in custom_setting.__dict__.items():
                    if not k.startswith("__") and not inspect.ismodule(v):
                        _setting[k] = v

        _setting.update(**kwargs)

        for k, v in _setting.items():
            setattr(setting, k.upper(), v)

        self._done_model = setting.DONE_MODEL
        self._task_model = setting.TASK_MODEL

        self.Scheduler = dynamic_load_class(setting.SCHEDULER)
        self.SpiderCrawler = dynamic_load_class(setting.CRAWLER)
        self.SpiderPipeline = dynamic_load_class(setting.PIPELINE)

    @property
    def request(self):
        """
        自定义request函数
        use case:
            from cobweb.base import Request, BaseItem
            @launcher.request
            def request(seed: Seed) -> Union[Request, BaseItem]:
                ...
                yield Request(seed.url, seed)
        """
        def decorator(func):
            self.SpiderCrawler.request = func
        return decorator

    @property
    def download(self):
        """
        自定义download函数
        use case:
            from cobweb.base import Request, Response, Seed, BaseItem
            @launcher.download
            def download(item: Request) -> Union[Seed, BaseItem, Response, str]:
                ...
                yield Response(item.seed, response)
        """
        def decorator(func):
            self.SpiderCrawler.download = func
        return decorator

    @property
    def parse(self):
        """
        自定义parse函数, xxxItem为自定义的存储数据类型
        use case:
            from cobweb.base import Request, Response
            @launcher.parse
            def parse(item: Response) -> BaseItem:
               ...
               yield xxxItem(seed, **kwargs)
        """
        def decorator(func):
            self.SpiderCrawler.parse = func
        return decorator

    def start_seeds(self, seeds: list):
        seed_list = [Seed(seed) for seed in seeds]
        self._TODO_QUEUE_.push(seed_list)
        return seed_list

    def _register(self, func, tag: str = "launcher"):
        name = tag + ":" + func.__name__ + "_" + str(uuid.uuid4())
        self.__REGISTER_FUNC__[name] = func
        if not self.__WORKER_THREAD__.get(name):
            worker_thread = threading.Thread(name=name, target=func)
            self.__WORKER_THREAD__[name] = worker_thread
            worker_thread.start()

    def _monitor(self):
        while not self._stop.is_set():
            if self._pause.is_set():
                time.sleep(15)
                continue
            for name, worker_thread in self.__WORKER_THREAD__.items():
                if not worker_thread.is_alive():
                    logger.info(f"{name} thread is dead. Restarting...")
                    func = self.__REGISTER_FUNC__[name]
                    worker_thread = threading.Thread(name=name, target=func)
                    self.__WORKER_THREAD__[name] = worker_thread
                    worker_thread.start()
                time.sleep(3)

    def start(self):
        self._pause.is_set()

        self.Scheduler(
            task=self.task,
            project=self.project,
            stop=self._stop,
            pause=self._pause,
            new=self._NEW_QUEUE_,
            todo=self._TODO_QUEUE_,
            done=self._DONE_QUEUE_,
            upload=self._UPLOAD_QUEUE_,
            register=self._register
        ).start()

        Distributor(
            task=self.task,
            project=self.project,
            new=self._NEW_QUEUE_,
            todo=self._TODO_QUEUE_,
            done=self._DONE_QUEUE_,
            upload=self._UPLOAD_QUEUE_,
            register=self._register,
            stop=self._stop, pause=self._pause,
            SpiderCrawler=self.SpiderCrawler
        ).start()

        Uploader(
            stop=self._stop, pause=self._pause,
            done=self._DONE_QUEUE_,
            upload=self._UPLOAD_QUEUE_,
            register=self._register,
            SpiderPipeline=self.SpiderPipeline
        ).start()

        self._monitor()

