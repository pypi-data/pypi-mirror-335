from enum import Enum
from types import MethodType
from typing import List, Optional, Dict, Any, Union
import inspect
from functools import wraps
from dataclasses import dataclass
from functools import wraps
from types import MethodType

from feature import Feature

from enum import Enum
from typing import Set

class FeatureSet:
    MAX_BITS = 64
    ALL_BITS = (1 << MAX_BITS) - 1

    def __init__(self, initial_features: Set[Feature] = None):
        self.mask = 0
        if initial_features:
            for feature in initial_features:
                self.enable_feature(feature)

    def enable_feature(self, feature: Feature) -> None:
        if feature.value >= self.MAX_BITS:
            raise ValueError(f"Feature index {feature.value} exceeds 64-bit limit")
        self.mask |= (1 << feature.value)

    def has_feature(self, feature: Feature) -> bool:
        return bool(self.mask & (1 << feature.value))

    def union(self, other: 'FeatureSet') -> 'FeatureSet':
        result = FeatureSet()
        result.mask = self.mask | other.mask
        return result

    def intersection(self, other: 'FeatureSet') -> 'FeatureSet':
        result = FeatureSet()
        result.mask = self.mask & other.mask
        return result

    # New comparison methods
    def equals(self, other: 'FeatureSet') -> bool:
        """Check if this mask is identical to another."""
        return self.mask == other.mask

    def implements(self, other: 'FeatureSet') -> bool:
        """Check if this mask implements all features of another mask."""
        return (self.mask & other.mask) == other.mask

    def missing_features(self, other: 'FeatureSet') -> 'FeatureSet':
        """Return a FeatureSet of features in other that are not in self."""
        result = FeatureSet()
        result.mask = other.mask & ~self.mask
        return result

    def common_features(self, other: 'FeatureSet') -> 'FeatureSet':
        """Return a FeatureSet of features present in both masks."""
        return self.intersection(other)

    def list_features(self) -> list:
        features = [f.name for f in Feature if self.has_feature(f)]
        return features
    
    def __str__(self) -> str:
        features = ", ".join(f.name for f in Feature if self.has_feature(f))
        return f"FeatureSet(features=[{features}])"