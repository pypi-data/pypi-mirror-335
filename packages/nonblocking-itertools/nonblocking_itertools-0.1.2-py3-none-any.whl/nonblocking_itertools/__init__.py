from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import *
from dataclasses import dataclass, field
from collections import deque
import time
import itertools
from functools import partial
from salish import *

def combinations(iterable: Iterable, r: int):
    channel = Channel(iterable)
    for i, n in enumerate(channel):
        collected = channel.collected[:i]
        combinations = itertools.combinations(collected, r-1)
        for combination in combinations:
            yield tuple([*combination, n])

def combinations_with_replacement(iterable: Iterable, r: int):
    channel = Channel(iterable)
    for i, n in enumerate(channel):
        for _r in range(0, r):
            collected = channel.collected[:i]
            combinations = itertools.combinations_with_replacement(collected, _r)
            for combination in combinations:
                repeat = (r - _r)
                repeated = [n]*repeat
                yield tuple([*combination, *repeated])

def permutations(iterable: Iterable, r = None):
    channel = Channel(iterable)
    for i, n in enumerate(channel):
        collected = channel.collected[:i]
        combinations = itertools.combinations(collected, r - 1)
        for combinations in combinations:
            yield from itertools.permutations([*combinations, n], r)

def product(*iterables: List[Iterable]):
    @dataclass
    class Collection:
        count: int
        iterables_count: int
        collection = {}
        complete = 0
        generators = []

        def __post_init__(self):
            self.iterables_count = self.count

        def collect(self, value, i):
            self.collection.setdefault(i, [])
            self.collection[i].append(value)
            if len(self.collection) == self.iterables_count:
                iterables = list(self.collection.values())
                iterables[i] = [value]
                self.generators.append(itertools.product(*iterables))
        
        def stop_iteration(self):
            self.count -= 1
        
        def items(self):
            while not self.complete and not self.generators:
                time.sleep(.01)
            if not self.complete and self.generators:
                yield from itertools.chain(*self.generators)



    collection = Collection(len(iterables), len(iterables))
    channels = [Channel(it).bind(partial(collection.collect, i=i), collection.stop_iteration) for i, it in enumerate(iterables)]
    yield from collection.items()

def chain(*iterables: List[Iterable]):
    channels = [Channel(it) for it in iterables]
    yield from itertools.chain.from_iterable(channels)

def roundrobin(*iterables: List[Iterable]):
    @dataclass
    class Collection:
        count: int
        collection: List[Any] = field(default_factory = list)
        index = 0

        def collect(self, item):
            self.collection.append(item)
        
        def stop_iteration(self):
            self.count -= 1

        def __iter__(self):
            while self.count > 0 or self.index < len(self.collection):
                while self.index >= len(self.collection) and self.count > 0:
                    continue
                if self.index < len(self.collection):
                    result = self.collection[self.index]
                    self.index += 1
                    yield result


    collection = Collection(len(iterables))
    [Channel(it).bind(collection.collect, collection.stop_iteration) for it in iterables]
    yield from collection