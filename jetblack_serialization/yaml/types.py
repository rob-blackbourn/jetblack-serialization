"""Types for YAML serialization"""

from typing import Union

import yaml

_Dumper = Union[
    yaml.BaseDumper,
    yaml.Dumper,
    yaml.SafeDumper
]
_Loader = Union[
    yaml.Loader,
    yaml.BaseLoader,
    yaml.FullLoader,
    yaml.SafeLoader,
    yaml.UnsafeLoader
]
