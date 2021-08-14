from contextlib import AbstractContextManager
from threading import Timer
from _thread import interrupt_main
from sys import stderr


class ContextTimeoutError(Exception):
    def __init__(self, ctx: 'TimeoutContext'):
        self.ctx: 'TimeoutContext' = ctx
        super().__init__(f'TimeoutContext with delay {ctx.delay} has been timed out.')


class TimeoutContext(AbstractContextManager):
    __slots__ = ('delay', 'timer')

    def __init__(self, delay: int):
        self.delay = delay
        self.timer = Timer(self.delay, self._timeout_callback, args=tuple())

    def _timeout_callback(self):
        print(f'TimeoutContext timed out over delay {self.delay} seconds', file=stderr)
        interrupt_main()

    def __enter__(self):
        self.timer.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is KeyboardInterrupt:
            raise ContextTimeoutError(self)
        else:
            self.timer.cancel()
            return False


if __name__ == '__main__':
    # sample test code.
    # sh > python timeout.py
    # to test TimeoutContext.
    print('Not timed out.')
    with TimeoutContext(5) as ctx:
        for i in range(5):
            print(f'Loop : {i}')

    print('Timed out')
    with TimeoutContext(1) as ctx:
        for i in range(1000000):
            print(f'Looping {i} times.')
