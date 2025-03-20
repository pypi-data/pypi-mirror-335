import time

from cobweb.base import logger
from cobweb.constant import LogTemplate
from .launcher import Launcher, check_pause


class LauncherAir(Launcher):

    # def _scheduler(self):
    #     if self.start_seeds:
    #         self.__LAUNCHER_QUEUE__['todo'].push(self.start_seeds)

    @check_pause
    def _insert(self):
        new_seeds = {}
        del_seeds = set()
        status = self.__LAUNCHER_QUEUE__['new'].length < self._new_queue_max_size
        for _ in range(self._new_queue_max_size):
            seed_tuple = self.__LAUNCHER_QUEUE__['new'].pop()
            if not seed_tuple:
                break
            seed, new_seed = seed_tuple
            new_seeds[new_seed.to_string] = new_seed.params.priority
            del_seeds.add(seed.to_string)
        if new_seeds:
            self.__LAUNCHER_QUEUE__['todo'].push(new_seeds)
        if del_seeds:
            self.__LAUNCHER_QUEUE__['done'].push(del_seeds)
        if status:
            time.sleep(self._new_queue_wait_seconds)

    @check_pause
    def _delete(self):
        seeds = []
        status = self.__LAUNCHER_QUEUE__['done'].length < self._done_queue_max_size

        for _ in range(self._done_queue_max_size):
            seed = self.__LAUNCHER_QUEUE__['done'].pop()
            if not seed:
                break
            seeds.append(seed.to_string)

        if seeds:
            self._remove_doing_seeds(seeds)

        if status:
            time.sleep(self._done_queue_wait_seconds)

    def _polling(self):

        check_emtpy_times = 0

        while not self._stop.is_set():

            queue_not_empty_count = 0
            pooling_wait_seconds = 30

            for q in self.__LAUNCHER_QUEUE__.values():
                if q.length != 0:
                    queue_not_empty_count += 1

            if queue_not_empty_count == 0:
                pooling_wait_seconds = 3
                if self._pause.is_set():
                    check_emtpy_times = 0
                    if not self._task_model:
                        logger.info("Done! Ready to close thread...")
                        self._stop.set()
                elif check_emtpy_times > 2:
                    self.__DOING__ = {}
                    self._pause.set()
                else:
                    logger.info(
                        "check whether the task is complete, "
                        f"reset times {3 - check_emtpy_times}"
                    )
                    check_emtpy_times += 1
            elif self._pause.is_set():
                self._pause.clear()
                self._execute()
            else:
                logger.info(LogTemplate.launcher_air_polling.format(
                    task=self.task,
                    doing_len=len(self.__DOING__.keys()),
                    todo_len=self.__LAUNCHER_QUEUE__['todo'].length,
                    done_len=self.__LAUNCHER_QUEUE__['done'].length,
                    upload_len=self.__LAUNCHER_QUEUE__['upload'].length,
                ))

            time.sleep(pooling_wait_seconds)


