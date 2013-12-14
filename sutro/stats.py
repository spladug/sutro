import contextlib
import socket
import time


MS_PER_SEC = 1000.0


class StatsClient(object):
    def __init__(self, hostname, port):
        if hostname:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dest = (hostname, port)
        else:
            self.socket = None
            self.dest = None

    @contextlib.contextmanager
    def timer(self, key):
        start = time.time()
        yield
        stop = time.time()

        elapsed_ms = (stop - start) * MS_PER_SEC
        self._send("%s:%d|ms" % (key, round(elapsed_ms)))

    def increment(self, key, count=1):
        self._send("%s:%d|c" % (key, count))

    def _send(self, message):
        if self.socket:
            self.socket.sendto(message + "\n", self.dest)
