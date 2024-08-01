## Installation

This is a Python 3.8+ package.

The package can be installed with pip.

```bash
pip install jetblack-serialization
```

By default the dependencies for XML serialization (`lxml`) are not installed.
To add the optional packages for XML use the following.

```bash
pip install jetblack-serialization[xml]
```

It has dependencies on the following packages:

* [lxml](https://lxml.de/)
* [typing-extensions](https://github.com/python/typing/tree/master/typing_extensions)
* [typing_inspect](https://github.com/ilevkivskyi/typing_inspect)
