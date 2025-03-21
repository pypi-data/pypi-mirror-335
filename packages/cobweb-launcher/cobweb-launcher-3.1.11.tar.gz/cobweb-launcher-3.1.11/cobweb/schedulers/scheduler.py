import threading

from cobweb import setting
from typing import Callable
from cobweb.base import Queue
from abc import ABC, abstractmethod


class Scheduler(ABC, threading.Thread):

    __LAUNCHER_FUNC__ = ["_reset", "_scheduler", "_insert", "_refresh", "_delete"]

    def __init__(
            self,
            task,
            project,
            stop: threading.Event,
            pause: threading.Event,
            new: Queue,
            todo: Queue,
            done: Queue,
            upload: Queue,
            register: Callable
    ):
        super().__init__()
        self.task = task
        self.project = project

        self.task_model = setting.TASK_MODEL
        self.seed_reset_seconds = setting.SEED_RESET_SECONDS
        self.scheduler_wait_seconds = setting.SCHEDULER_WAIT_SECONDS
        self.new_queue_wait_seconds = setting.NEW_QUEUE_WAIT_SECONDS
        self.done_queue_wait_seconds = setting.DONE_QUEUE_WAIT_SECONDS
        self.todo_queue_full_wait_seconds = setting.TODO_QUEUE_FULL_WAIT_SECONDS
        self.before_scheduler_wait_seconds = setting.BEFORE_SCHEDULER_WAIT_SECONDS

        self.todo_queue_size = setting.TODO_QUEUE_SIZE
        self.new_queue_max_size = setting.NEW_QUEUE_MAX_SIZE
        self.done_queue_max_size = setting.DONE_QUEUE_MAX_SIZE
        self.upload_queue_max_size = setting.UPLOAD_QUEUE_MAX_SIZE

        self.stop = stop
        self.pause = pause

        self.new = new
        self.todo = todo
        self.done = done
        self.upload = upload

        self.register = register

        self.working_seeds = dict()

    def is_empty(self):
        if self.new.length == 0 and self.todo.length == 0 and self.done.length == 0 and self.upload.length == 0:
            return True
        else:
            return False

    def remove_working_seeds(self, seeds: list = None):
        for seed in seeds:
            if seed in self.working_seeds:
                self.working_seeds.pop(seed)

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def schedule(self):
        ...

    @abstractmethod
    def insert(self):
        ...

    @abstractmethod
    def refresh(self):
        ...

    @abstractmethod
    def delete(self):
        ...


