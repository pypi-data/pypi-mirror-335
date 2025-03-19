# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonblocking_itertools']

package_data = \
{'': ['*']}

install_requires = \
['salish>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'nonblocking-itertools',
    'version': '0.1.2',
    'description': '',
    'long_description': 'Five functions in `itertools` can be substantially slowed when their input iterables generate data with lag. This might occur when the generator yields data being streamed from the internet, disk, or a multithreaded or multiprocessing workflow.\n\nThe most substantial slowdowns are in `permutations`, `combinations`, `combinations_with_replacement`, and `product`. These block the flow of execution until their input iterable(s) have completely finished being converted to a tuple. Example:\n\n```\nimport time\nimport itertools\nimport nonblocking_itertools\n\ndef laggy_generator(iterable):\n    for i in iterable:\n        time.sleep(1)\n        yield i\n\nprint("Testing itertools.combinations")\nstart = time.time()\ndata = laggy_generator(range(4))\nfor combo in itertools.combinations(data, 2):\n    print("Seconds from start:", int(time.time() - start), "Combination:", combo)\n\nprint("Testing nonblocking_itertools.combinations")\nstart = time.time()\ndata = laggy_generator(range(4))\nfor combo in nonblocking_itertools.combinations(data, 2):\n    print("Seconds from start:", time.time() - start, "Combination:", combo)\n```\n\nOutput:\n\n```\nTesting itertools.combinations\nSeconds from start: 4 Combination: (0, 1)\nSeconds from start: 4 Combination: (0, 2)\nSeconds from start: 4 Combination: (0, 3)\nSeconds from start: 4 Combination: (1, 2)\nSeconds from start: 4 Combination: (1, 3)\nSeconds from start: 4 Combination: (2, 3)\nTesting nonblocking_itertools.combinations\nSeconds from start: 2 Combination: (0, 1)\nSeconds from start: 3 Combination: (0, 2)\nSeconds from start: 3 Combination: (1, 2)\nSeconds from start: 4 Combination: (0, 3)\nSeconds from start: 4 Combination: (1, 3)\nSeconds from start: 4 Combination: (2, 3)\n```\n\nNotice that all results from itertools.combinations were printed after 4 seconds, while the results from nonblocking_itertools.combinations were printed as soon as it was possible to yield them, after 2 or 3 seconds. Note that nonblocking_itertools does not generally return results in the same order as the equivalent itertools methods.\n\nThe other improvement in nonblocking_itertools is with the `chain` method, for when iterables have some parallelizeable processing that is initiated only during iteration. The `itertools.chain` method only starts iterating through later iterables when the first is exhausted. That means it misses the opportunity to kick off parallel processing in the later iterables. By contrast, `nonblocking_itertools` initiates immediate and simultaneous multithreaded iteration through iterables to take advantage of opportunities for parallelization. Its output is identical to `itertools.chain`.\n\nExample:\n\n```\nimport time\nimport itertools\nimport nonblocking_itertools\n\ndef laggy_generator(iterable):\n    for i in iterable:\n        time.sleep(1)\n        yield i\n\nprint("Testing itertools.chain")\nstart = time.time()\ndata1 = laggy_generator(range(2))\ndata2 = laggy_generator(range(2, 4))\nfor element in itertools.chain(data1, data2):\n    print("Seconds from start:", int(time.time() - start), "Element:", element)\n\nprint("Testing nonblocking_itertools.chain")\nstart = time.time()\ndata1 = laggy_generator(range(2))\ndata2 = laggy_generator(range(2, 4))\nfor element in nonblocking_itertools.chain(data1, data2):\n    print("Seconds from start:", int(time.time() - start), "Element:", element)\n```\n\nOutput:\n\n```\nTesting itertools.chain\nSeconds from start: 1 Element: 0\nSeconds from start: 2 Element: 1\nSeconds from start: 3 Element: 2\nSeconds from start: 4 Element: 3\nTesting nonblocking_itertools.chain\nSeconds from start: 1 Element: 0\nSeconds from start: 2 Element: 1\nSeconds from start: 2 Element: 2\nSeconds from start: 2 Element: 3\n```\n\nNotice that nonblocking_itertools.chain finishes after 2 seconds, while itertools.chain takes 4 seconds to finish.',
    'author': 'Ben Skubi',
    'author_email': 'skubi@ohsu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
