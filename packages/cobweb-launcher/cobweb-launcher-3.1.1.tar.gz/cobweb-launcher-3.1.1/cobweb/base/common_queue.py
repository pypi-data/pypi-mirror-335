from collections import deque


class Queue:

    def __init__(self):
        self._queue = deque()

    @property
    def length(self) -> int:
        return len(self._queue)

    def push(self, data, left: bool = False, direct_insertion: bool = False):
        try:
            if not data:
                return None
            if not direct_insertion and any(isinstance(data, t) for t in (list, tuple)):
                self._queue.extendleft(data) if left else self._queue.extend(data)
            else:
                self._queue.appendleft(data) if left else self._queue.append(data)
        except AttributeError:
            pass

    def pop(self, left: bool = True):
        try:
            return self._queue.popleft() if left else self._queue.pop()
        except IndexError:
            return None
        except AttributeError:
            return None
