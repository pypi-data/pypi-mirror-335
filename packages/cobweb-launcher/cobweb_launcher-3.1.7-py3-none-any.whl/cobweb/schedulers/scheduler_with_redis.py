import os
import time
import threading
from typing import Callable
from cobweb.db import RedisDB, ApiDB
from cobweb.utils import check_pause
from cobweb.base import Queue, Seed, logger
from cobweb.constant import LogTemplate
from .scheduler import Scheduler
use_api = bool(int(os.getenv("REDIS_API_HOST", 0)))


class RedisScheduler(Scheduler):

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
        super().__init__(task, project, stop, pause, new, todo, done, upload, register)
        self.todo_key = "{%s:%s}:todo" % (project, task)
        self.done_key = "{%s:%s}:done" % (project, task)
        self.fail_key = "{%s:%s}:fail" % (project, task)
        self.heartbeat_key = "heartbeat:%s_%s" % (project, task)
        self.speed_control_key = "speed_control:%s_%s" % (project, task)
        self.reset_lock_key = "lock:reset:%s_%s" % (project, task)
        self.redis_queue_empty_event = threading.Event()
        self.db = ApiDB() if use_api else RedisDB()

    @check_pause
    def reset(self):
        """
        检查过期种子，重新添加到redis缓存中
        """
        reset_wait_seconds = 30
        if self.db.lock(self.reset_lock_key, t=60):

            _min = -int(time.time()) + self.seed_reset_seconds
            self.db.members(self.todo_key, 0, _min=_min, _max="(0")
            self.db.delete(self.reset_lock_key)

        time.sleep(reset_wait_seconds)

    @check_pause
    def schedule(self):
        """
        调度任务，获取redis队列种子，同时添加到doing字典中
        """
        if not self.db.zcount(self.todo_key, 0, "(1000"):
            time.sleep(self.scheduler_wait_seconds)
        elif self.todo.length >= self.todo_queue_size:
            time.sleep(self.todo_queue_full_wait_seconds)
        else:
            members = self.db.members(
                self.todo_key, int(time.time()),
                count=self.todo_queue_size,
                _min=0, _max="(1000"
            )
            for member, priority in members:
                seed = Seed(member, priority=priority)
                self.working_seeds[seed.to_string] = seed.params.priority
                self.todo.push(seed)

    @check_pause
    def insert(self):
        """
        添加新种子到redis队列中
        """
        new_seeds = {}
        del_seeds = set()
        status = self.new.length < self.new_queue_max_size
        for _ in range(self.new_queue_max_size):
            seed_tuple = self.new.pop()
            if not seed_tuple:
                break
            seed, new_seed = seed_tuple
            new_seeds[new_seed.to_string] = new_seed.params.priority
            del_seeds.add(seed)
        if new_seeds:
            self.db.zadd(self.todo_key, new_seeds, nx=True)
        if del_seeds:
            self.done.push(list(del_seeds))
        if status:
            time.sleep(self.new_queue_wait_seconds)

    @check_pause
    def refresh(self):
        """
        刷新doing种子过期时间，防止reset重新消费
        """
        if self.working_seeds:
            refresh_time = int(time.time())
            seeds = {k:-refresh_time - v / 1000 for k, v in self.working_seeds.items()}
            self.db.zadd(self.todo_key, item=seeds, xx=True)
        time.sleep(3)

    @check_pause
    def delete(self):
        """
        删除队列种子，根据状态添加至成功或失败队列，移除doing字典种子索引
        """
        seed_list = []
        status = self.done.length < self.done_queue_max_size

        for _ in range(self.done_queue_max_size):
            seed = self.done.pop()
            if not seed:
                break
            seed_list.append(seed.to_string)

        if seed_list:

            self.db.zrem(self.todo_key, *seed_list)
            self.remove_working_seeds(seed_list)

        if status:
            time.sleep(self.done_queue_wait_seconds)

    def run(self):
        start_time = int(time.time())

        self.register(self.reset, tag="scheduler")
        self.register(self.insert, tag="scheduler")
        self.register(self.delete, tag="scheduler")
        self.register(self.refresh, tag="scheduler")
        self.register(self.schedule, tag="scheduler")

        while not self.stop.is_set():
            working_count = len(self.working_seeds.keys())
            memory_count = self.db.zcount(self.todo_key, "-inf", "(0")
            todo_count = self.db.zcount(self.todo_key, 0, "(1000")
            all_count = self.db.zcard(self.todo_key)
            
            if self.is_empty():
                if self.pause.is_set():
                    execute_time = int(time.time()) - start_time
                    if not self.task_model and execute_time > self.before_scheduler_wait_seconds:
                        logger.info("Done! ready to close thread...")
                        self.stop.set()
                    elif todo_count:
                        logger.info(f"Recovery {self.task} task run！todo seeds count: {todo_count}, queue length: {all_count}")
                        self.pause.clear()
                        # self.execute()
                    else:
                        logger.info("pause! waiting for resume...")
                else:
                    if all_count:
                        logger.info(f"todo seeds count: {todo_count}, queue length: {all_count}")
                        self.pause.clear()
                    else:
                        logger.info("Done! pause set...")
                        self.pause.set()
            else:
                if self.pause.is_set():
                    self.pause.clear()
                logger.info(LogTemplate.launcher_pro_polling.format(
                    task=self.task,
                    doing_len=working_count,
                    todo_len=self.todo.length,
                    done_len=self.done.length,
                    redis_seed_count=all_count,
                    redis_todo_len=todo_count,
                    redis_doing_len=memory_count,
                    upload_len=self.upload.length,
                ))

            time.sleep(30)

        logger.info("Done! Ready to close thread...")

