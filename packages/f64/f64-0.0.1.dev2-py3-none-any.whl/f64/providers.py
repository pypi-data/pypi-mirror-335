from dataclasses import dataclass
from feature_provider import FeatureProvider
from feature import Feature

# Feature providers using dataclasses
@dataclass
class NameProvider(FeatureProvider):
    name: str

    def __post_init__(self):
        super().__init__()
        self.features.enable_feature(Feature.ATTR_NAME)
        self.validate_implementation()

@dataclass
class ConfigProvider(FeatureProvider):
    config: dict = None

    def __post_init__(self):
        super().__init__()
        self.features.enable_feature(Feature.ATTR_CONFIG)
        self.config = self.config or {}
        self.validate_implementation()

class StartableProvider(FeatureProvider):
    def __init__(self):
        super().__init__()
        self.features.enable_feature(Feature.METHOD_START)
        self.validate_implementation()

    def start(self, *args, **kwargs) -> str:
        return "Started"

class ConfigLoggingProvider(FeatureProvider):
    def __init__(self):
        super().__init__()
        self.features.enable_feature(Feature.METHOD_LOG)
        self.dependencies[Feature.METHOD_LOG] = Feature.ATTR_CONFIG
        self._log_buffer = []
        self.validate_implementation()

    def log(self, message: str, *args, config: dict = None, **kwargs) -> None:
        if not config:
            raise ValueError("Logging requires config")
        level = config.get("log_level", "INFO")
        msg = f"[{level}] {message}"
        self._log_buffer.append(msg)
        print(msg)

class SimpleLoggingProvider(FeatureProvider):
    def __init__(self):
        super().__init__()
        self.features.enable_feature(Feature.METHOD_LOG)
        self.validate_implementation()

    def log(self, message: str, *args, **kwargs) -> None:
        print(f"[SIMPLE] {message}")

class TimestampLoggingProvider(FeatureProvider):
    def __init__(self):
        super().__init__()
        self.features.enable_feature(Feature.METHOD_LOG)
        self.dependencies[Feature.METHOD_LOG] = Feature.ATTR_NAME
        self.validate_implementation()

    def log(self, message: str, *args, name: str = None, **kwargs) -> None:
        if not name:
            raise ValueError("Timestamp logging requires name")
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {name}: {message}")