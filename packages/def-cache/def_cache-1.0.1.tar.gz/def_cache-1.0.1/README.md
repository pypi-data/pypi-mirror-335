## def-cache

<p align="center">
  <a href="https://pypi.org/project/def-cache"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/def-cache" /></a>
  <a href="https://pypi.org/project/def-cache"><img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/def-cache" /></a>
<br/>
</p>

`def-cache` is a python package that can be used as a method decorator to case their results.

Even though it can be used for any python method, it's aim is to be used in computational heavy methods,
that do not need to be executed constantly and can be cached (eg: model training, heavy calculation tasks, etc)

Currently, the backend supported is `fs` (file-system) and the results of the cached method are stored in files

### Installation

As `def-cache` is a python package it can be installed directly using pip:

```bash
python -m pip install def-cache
```

Alternatively one can use the source code directly.

### Usage

Upon installation one can directly use the decorator on the methods that need to be cached.

A base usage example can be found below:

```python
from def_cache import decorator

"""
The decorator below will cache the results of method: add for 60s in a file stored in the tmp relative path
"""


@decorator.cache(ttl=60, backend='fs', storage='tmp')
def add(x, y):
    return x + y


# this will not be called from cache
print(add(1, 2))

# this will be retrieved from cache
print(add(1, 2))
```

Example are also present in the [examples](/examples) directory.

### Future Extensions

In the future we plan on adding storage engine support for the decorator, but of course would welcome any suggestions.
