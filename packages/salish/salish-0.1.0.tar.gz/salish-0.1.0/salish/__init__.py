from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import *
from dataclasses import dataclass, field
from collections import deque
import time

@dataclass
class ChannelIterator:
    channel: "Channel"
    index: int = 0

    def __next__(self):
        while not self.channel.satisfied(self.index):
            if len(self.channel) > self.index:
                result = self.channel.collected[self.index]
                self.index += 1
                return result
        raise StopIteration

@dataclass
class ReactiveBinding:
    channel: "Channel"
    on_collect: Callable
    on_stop_iteration: Callable
    max_workers: int
    index: int = 0
    thread: Thread = None

    def __post_init__(self):
        self.thread = Thread(target = self.receive, args = [])
        self.thread.start()
    
    def receive(self):
        with ThreadPoolExecutor(max_workers = self.max_workers) as executor:
            deque(executor.map(self.on_collect, self.channel))
        if self.on_stop_iteration:
            self.on_stop_iteration()
    
    def join(self):
        self.thread.join()

@dataclass
class Bind:
    method: Callable
    how: str = None

@dataclass
class Caller:
    bound: Callable | Bind
    collected: List[Any] = field(default_factory=list)
    complete: bool = False
    index: int = 0

    def collect(self, item):
        if isinstance(self.bound, Callable):
            self.collected.append(self.bound(item))
        elif isinstance(self.bound, Bind):
            if not self.bound.how:
                self.collected.append(self.bound.method(item))
            elif self.bound.how == "*":
                self.collected.append(self.bound.method(*item))
            elif self.bound.how == "**":
                self.collected.append(self.bound.method(**item))

    def stop_iteration(self):
        self.complete = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.collected):
            if self.complete:
                raise StopIteration
            while self.index >= len(self.collected) and not self.complete:
                time.sleep(.01)
        if self.index < len(self.collected):
            result = self.collected[self.index]
            self.index += 1
        elif self.complete:
            raise StopIteration

        return result

@dataclass
class Channel:
    source: Iterable[Any]
    collected: List[Any] = field(default_factory=list)
    wait: bool = False
    exhausted: bool = False
    _receiver: Thread = None
    _bound: List[ReactiveBinding] = field(default_factory=list)


    def __post_init__(self):
        self._receiver = Thread(target=self.start, args=[])
        if not self.wait:
            self._receiver.start()
    
    def start(self):
        self.exhausted = False
        self.collected = []
        for s in self.source:
            self.collected.append(s)
        self.exhausted = True
    
    def bind(self, on_collect: Callable, on_stop_iteration: Callable | None = None, max_workers: int | None = None):
        binding = ReactiveBinding(channel = self, on_collect = on_collect, on_stop_iteration = on_stop_iteration, max_workers = max_workers)
        self._bound.append(binding)
        return self
    
    def satisfied(self, index: int) -> bool:
        return self.exhausted and index >= len(self.collected)

    def __len__(self) -> int:
        return len(self.collected)
    
    def __iter__(self) -> ChannelIterator:
        return ChannelIterator(self)
    
    def __or__(self, arg: Callable | Bind):
        bound = Bind(arg) if isinstance(arg, Callable) else arg
        
        if bound.how == "collect":
            return Channel(bound.method(self))
        else:
            caller = Caller(bound)
            self.bind(caller.collect, caller.stop_iteration)
            return Channel(caller)
        

    def __and__(self, other: Generator):
        return Channel(other(self))

    def join(self):
        if self._receiver:
            self._receiver.join()
        [bound.join() for bound in self._bound]