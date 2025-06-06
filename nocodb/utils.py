from threading import Thread


class CustomThread(Thread):
    """
    Custom class to catch return value of threads.
    from: https://medium.com/@birenmer/threading-the-needle-returning-values-from-python-threads-with-ease-ace21193c148
    """

    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None
    ):
        # Initializing the Thread class
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    # Overriding the Thread.run function
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return
