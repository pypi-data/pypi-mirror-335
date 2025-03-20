import inspect
from feature_set import FeatureSet
from feature import Feature
from feature_contracts import FEATURE_CONTRACTS

# Base class for feature providers
class FeatureProvider:
    def __init__(self):
        self.features = FeatureSet()
        self.dependencies: Dict[Feature, Feature] = {}

    def get_features(self) -> FeatureSet:
        return self.features

    def check_dependencies(self, available_features: FeatureSet) -> None:
        for feature, required in self.dependencies.items():
            if self.features.has_feature(feature) and not available_features.has_feature(required):
                raise ValueError(f"Feature {feature.name} requires {required.name}")

    def validate_implementation(self) -> None:
        for feature in Feature:
            if self.features.has_feature(feature):
                contract = FEATURE_CONTRACTS.get(feature, {})
                name = contract.get("name")
                kind = contract.get("kind")
                if not name or not kind:
                    continue
                if not hasattr(self, name):
                    raise ValueError(f"Provider for {feature.name} must implement {kind} '{name}'")
                attr = getattr(self, name)
                if kind == "attribute":
                    expected_type = contract.get("type")
                    if not isinstance(attr, expected_type):
                        raise ValueError(f"'{name}' for {feature.name} must be of type {expected_type.__name__}")
                elif kind == "method":
                    if not callable(attr):
                        raise ValueError(f"'{name}' for {feature.name} must be a method")
                    expected_sig = contract.get("signature")
                    actual_sig = inspect.signature(attr)
                    actual_params = {k: v for k, v in actual_sig.parameters.items() if k not in ('self', 'cls')}
                    for param_name, param in expected_sig.parameters.items():
                        if param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                            if param_name not in actual_params:
                                raise ValueError(f"Method '{name}' for {feature.name} must include parameter '{param_name}'")
                            actual_param = actual_params[param_name]
                            if actual_param.annotation != param.annotation:
                                raise ValueError(f"Method '{name}' for {feature.name} parameter '{param_name}' has wrong type")
                    has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in actual_params.values())
                    has_varkw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in actual_params.values())
                    if expected_sig.parameters.get("args") and not has_varargs:
                        raise ValueError(f"Method '{name}' for {feature.name} must accept *args")
                    if expected_sig.parameters.get("kwargs") and not has_varkw:
                        raise ValueError(f"Method '{name}' for {feature.name} must accept **kwargs")
                    if expected_sig.return_annotation != actual_sig.return_annotation:
                        raise ValueError(f"Method '{name}' for {feature.name} has wrong return type")