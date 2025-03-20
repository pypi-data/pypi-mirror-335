import time
from feature import Feature
from feature_set import FeatureSet
from providers import ConfigLoggingProvider

features = set(Feature)
start = time.perf_counter_ns()
fs = FeatureSet(features)
end = time.perf_counter_ns()
print(f"Setup FeatureSet with 64 features: {end - start} ns")


provider = ConfigLoggingProvider()
start = time.perf_counter_ns()
provider.validate_implementation()
end = time.perf_counter_ns()
print(f"Validation for ConfigLoggingProvider: {end - start} ns")

