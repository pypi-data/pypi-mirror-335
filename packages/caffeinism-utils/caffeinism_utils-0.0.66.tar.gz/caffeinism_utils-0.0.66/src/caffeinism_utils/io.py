from collections import deque


class PopIO:
    def __init__(self):
        self.deque = deque()
        self.closed = False

    def write(self, data):
        self.deque.append(data)

    def pop(self):
        while self.deque:
            yield self.deque.popleft()

    def pop_all(self):
        ret = []
        while self.deque:
            ret.append(self.deque.popleft())

        return b"".join(ret)

    def tell(self):
        pass

    def seekable(self):
        return False
