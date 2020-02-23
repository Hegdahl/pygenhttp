'''
Provides Loop, an object used to run generators concurrently.
'''
from typing import Union, Generator, Iterable, Callable
import time
from numbers import Number

def sleep(seconds: Number) -> None:
    '''Wait for seconds.'''
    wake_time = time.time() + seconds
    while time.time() < wake_time:
        yield

def call_later(seconds: Number, func: Callable, *args, **kwargs) -> None:
    '''Call a function after waiting seconds.'''
    yield from sleep(seconds)
    func(*args, **kwargs)

def schedule(*gens: Union[Generator, Callable]):
    '''Yield through generators sequentially.'''
    for gen in gens:
        if callable(gen):
            gen()
        else:
            yield from gen

class Loop:
    '''
    Used to run generators concurrently.
    '''
    ACTIVE = None

    def __init__(self):
        self.queue = []

    def start(self) -> None:
        '''Runs the loop until there is nothing left in the queue.'''
        if Loop.ACTIVE is not None:
            raise RuntimeError('A loop is already running.')
        Loop.ACTIVE = self
        while self.queue:
            for idx, gen in reversed(tuple(enumerate(self.queue))):
                try:
                    next(gen)
                except StopIteration:
                    self.queue.pop(idx)
        Loop.ACTIVE = None

    def enqueue(self, gen: Generator) -> None:
        '''Adds a gen to the queue.'''
        self.queue.append(gen)
