Five functions in `itertools` can be substantially slowed when their input iterables generate data with lag. This might occur when the generator yields data being streamed from the internet, disk, or a multithreaded or multiprocessing workflow.

The most substantial slowdowns are in `permutations`, `combinations`, `combinations_with_replacement`, and `product`. These block the flow of execution until their input iterable(s) have completely finished being converted to a tuple. Example:

```
import time
import itertools
import nonblocking_itertools

def laggy_generator(iterable):
    for i in iterable:
        time.sleep(1)
        yield i

print("Testing itertools.combinations")
start = time.time()
data = laggy_generator(range(4))
for combo in itertools.combinations(data, 2):
    print("Seconds from start:", int(time.time() - start), "Combination:", combo)

print("Testing nonblocking_itertools.combinations")
start = time.time()
data = laggy_generator(range(4))
for combo in nonblocking_itertools.combinations(data, 2):
    print("Seconds from start:", time.time() - start, "Combination:", combo)
```

Output:

```
Testing itertools.combinations
Seconds from start: 4 Combination: (0, 1)
Seconds from start: 4 Combination: (0, 2)
Seconds from start: 4 Combination: (0, 3)
Seconds from start: 4 Combination: (1, 2)
Seconds from start: 4 Combination: (1, 3)
Seconds from start: 4 Combination: (2, 3)
Testing nonblocking_itertools.combinations
Seconds from start: 2 Combination: (0, 1)
Seconds from start: 3 Combination: (0, 2)
Seconds from start: 3 Combination: (1, 2)
Seconds from start: 4 Combination: (0, 3)
Seconds from start: 4 Combination: (1, 3)
Seconds from start: 4 Combination: (2, 3)
```

Notice that all results from itertools.combinations were printed after 4 seconds, while the results from nonblocking_itertools.combinations were printed as soon as it was possible to yield them, after 2 or 3 seconds. Note that nonblocking_itertools does not generally return results in the same order as the equivalent itertools methods.

The other improvement in nonblocking_itertools is with the `chain` method, for when iterables have some parallelizeable processing that is initiated only during iteration. The `itertools.chain` method only starts iterating through later iterables when the first is exhausted. That means it misses the opportunity to kick off parallel processing in the later iterables. By contrast, `nonblocking_itertools` initiates immediate and simultaneous multithreaded iteration through iterables to take advantage of opportunities for parallelization. Its output is identical to `itertools.chain`.

Example:

```
import time
import itertools
import nonblocking_itertools

def laggy_generator(iterable):
    for i in iterable:
        time.sleep(1)
        yield i

print("Testing itertools.chain")
start = time.time()
data1 = laggy_generator(range(2))
data2 = laggy_generator(range(2, 4))
for element in itertools.chain(data1, data2):
    print("Seconds from start:", int(time.time() - start), "Element:", element)

print("Testing nonblocking_itertools.chain")
start = time.time()
data1 = laggy_generator(range(2))
data2 = laggy_generator(range(2, 4))
for element in nonblocking_itertools.chain(data1, data2):
    print("Seconds from start:", int(time.time() - start), "Element:", element)
```

Output:

```
Testing itertools.chain
Seconds from start: 1 Element: 0
Seconds from start: 2 Element: 1
Seconds from start: 3 Element: 2
Seconds from start: 4 Element: 3
Testing nonblocking_itertools.chain
Seconds from start: 1 Element: 0
Seconds from start: 2 Element: 1
Seconds from start: 2 Element: 2
Seconds from start: 2 Element: 3
```

Notice that nonblocking_itertools.chain finishes after 2 seconds, while itertools.chain takes 4 seconds to finish.