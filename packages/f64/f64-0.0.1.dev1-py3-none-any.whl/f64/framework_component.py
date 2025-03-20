from enum import Enum
from types import MethodType
from typing import List, Optional, Dict, Any, Union
import inspect
from functools import wraps
from dataclasses import dataclass
from functools import wraps
from types import MethodType
import inspect
from typing import List, Any
from functools import wraps

class FeatureDescriptor:
    def __init__(self, feature: Feature):
        self.feature = feature
        self.name = FEATURE_CONTRACTS[feature]["name"]

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._dependency_values.get(self.feature)

    def __set__(self, obj, value):
        obj._dependency_values[self.feature] = value
        for method_feature, dep_feature in obj._method_dependencies.items():
            if dep_feature == self.feature:
                method_name = FEATURE_CONTRACTS[method_feature]["name"]
                provider = obj._feature_map[method_feature]
                obj._bind_method(method_feature, method_name, provider)

class FrameworkComponent:
    def __init__(self, providers: List['FeatureProvider'], feature_selection: Optional[Dict[Feature, 'FeatureProvider']] = None, validate: bool = True):
        """
        Initialize the FrameworkComponent.

        Args:
            providers: List of FeatureProvider instances.
            feature_selection: Optional dict mapping Features to specific Providers to resolve overlaps.
            validate: Whether to validate provider implementations.
        """
        self.providers = providers
        self.features = FeatureSet()
        self._feature_map = {}
        self._dependency_values = {}
        self._method_dependencies = {}

        # Track features provided by each provider and detect overlaps
        feature_to_providers = {}
        for provider in providers:
            if validate:
                provider.validate_implementation()
            provider_features = provider.get_features()
            self.features = self.features.union(provider_features)
            for feature in Feature:
                if provider_features.has_feature(feature):
                    if feature not in feature_to_providers:
                        feature_to_providers[feature] = []
                    feature_to_providers[feature].append(provider)

        # Handle feature assignment with overlap detection
        for feature, providers_for_feature in feature_to_providers.items():
            if len(providers_for_feature) > 1:
                # Overlap detected
                if feature_selection and feature in feature_selection:
                    # Use explicit selection if provided
                    selected_provider = feature_selection.get(feature)
                    if selected_provider not in providers_for_feature:
                        raise ValueError(f"Selected provider {selected_provider.__class__.__name__} for {feature.name} not in available providers")
                    self._feature_map[feature] = selected_provider
                else:
                    # No selection provided, raise exception
                    provider_names = [p.__class__.__name__ for p in providers_for_feature]
                    raise ValueError(
                        f"Feature {feature.name} provided by multiple providers: {', '.join(provider_names)}. "
                        "Resolve by specifying 'feature_selection = { Feature."
                        f"{feature.name}: "+"<provider> }'"
                    )
            else:
                # No overlap, use the single provider
                self._feature_map[feature] = providers_for_feature[0]

        # Validate dependencies after feature mapping
        for provider in providers:
            provider.check_dependencies(self.features)

        # Initialize feature values
        for feature in Feature:
            if feature in self._feature_map:
                contract = FEATURE_CONTRACTS.get(feature, {})
                name = contract.get("name")
                kind = contract.get("kind")
                provider = self._feature_map[feature]
                
                if kind == "attribute":
                    value = getattr(provider, name)
                    self._dependency_values[feature] = value
                elif kind == "method":
                    dep_feature = provider.dependencies.get(feature)
                    if dep_feature:
                        self._method_dependencies[feature] = dep_feature
                    self._bind_method(feature, name, provider)

    def _bind_method(self, feature: 'Feature', method_name: str, provider: 'FeatureProvider') -> None:
        method = getattr(provider, method_name)
        dep_feature = provider.dependencies.get(feature)
        if dep_feature:
            sig = inspect.signature(method)
            param_names = tuple(p for p in sig.parameters if p not in ('self', 'cls'))
            dep_name = FEATURE_CONTRACTS[dep_feature]["name"]
            dep_value = self._dependency_values.get(dep_feature)
            bound_method = self._create_bound_method(feature, method, param_names, dep_name, dep_value)
        else:
            bound_method = MethodType(method, self)
        setattr(self, method_name, bound_method)

    def _create_bound_method(self, feature: 'Feature', method: Callable, param_names: tuple, dep_name: str, dep_value: Any) -> Callable:
        @wraps(method)
        def bound_method(self, *args, **kwargs):
            current_dep_value = self._dependency_values.get(self._method_dependencies.get(feature))
            if current_dep_value is not None:
                kwargs = {**kwargs, dep_name: current_dep_value}
            elif dep_name not in kwargs:
                raise ValueError(f"Required dependency '{dep_name}' not available")
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
            return method(*args, **filtered_kwargs)
        return MethodType(bound_method, self)

    def get_feature_value(self, feature: 'Feature') -> Any:
        if self.has_feature(feature):
            return self._dependency_values.get(feature)
        return None

    def has_feature(self, feature: 'Feature') -> bool:
        return self.features.has_feature(feature)

    def equals(self, featureset: 'FeatureSet') -> bool:
        return self.features.equals(featureset)

    def implements(self, featureset: 'FeatureSet') -> bool:
        return self.features.implements(featureset)

    def missing_features(self, featureset: 'FeatureSet') -> 'FeatureSet':
        return self.features.missing_features(featureset)

    def common_features(self, featureset: 'FeatureSet') -> 'FeatureSet':
        return self.features.common_features(featureset)
    
    def __str__(self) -> str:
        name = self.get_feature_value(Feature.ATTR_NAME) or "Unnamed"
        return f"FrameworkComponent(name={name}, features={self.features})"