from enum import Enum
from types import MethodType
from typing import List, Optional, Dict, Any, Union
import inspect
from functools import wraps
from dataclasses import dataclass
from functools import wraps
from types import MethodType

# Define 64 unique features
class Feature(Enum):
    ATTR_NAME = 0     # Bit 0 (property: name)
    ATTR_ID = 1       # Bit 1 (property: id)
    METHOD_START = 2  # Bit 2 (method: start)
    METHOD_STOP = 3   # Bit 3 (method: stop)
    ATTR_CONFIG = 4   # Bit 4 (property: config)
    METHOD_LOG = 5    # Bit 5 (method: log, depends on ATTR_CONFIG)
    # ... Expand to 64 (0–63)
    ATTR_Z = 63       # Bit 63