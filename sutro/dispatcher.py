import gevent.queue


class MessageDispatcher(object):
    def __init__(self, stats):
        self.consumers = {}
        self.stats = stats

    def on_message_received(self, namespace, message):
        consumers = self.consumers.get(namespace, [])

        with self.stats.timer("sutro.dispatch"):
            for consumer in consumers:
                consumer.put(message)

    def listen(self, namespace):
        queue = gevent.queue.Queue()
        self.consumers.setdefault(namespace, []).append(queue)

        try:
            while True:
                yield queue.get(block=True)
        finally:
            self.consumers[namespace].remove(queue)
            if not self.consumers[namespace]:
                del self.consumers[namespace]
