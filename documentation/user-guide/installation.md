## Installation

This is a Python 3.8+ package.

The package can be installed with pip.

```bash
pip install jetblack-serialization
```

It has dependencies on the following packages:

* [typing-extensions](https://github.com/python/typing/tree/master/typing_extensions)
* [typing_inspect](https://github.com/ilevkivskyi/typing_inspect)

By default, the dependencies for YAML and XML are not installed.

To install the dependencies for XML
([`lxml`](https://lxml.de/)).

```bash
pip install jetblack-serialization[xml]
```

To install the dependencies for YAML ([`PyYAML`](https://github.com/yaml/pyyaml)).

```bash
pip install jetblack-serialization[yaml]
```

To install the dependencies for all.

```bash
pip install jetblack-serialization[all]
```
