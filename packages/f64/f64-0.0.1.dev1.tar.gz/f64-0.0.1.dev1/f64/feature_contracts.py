import inspect
from feature import Feature

FEATURE_CONTRACTS = {
    Feature.ATTR_NAME: {"name": "name", "kind": "attribute", "type": str},
    Feature.ATTR_ID: {"name": "id", "kind": "attribute", "type": int},
    Feature.METHOD_START: {
        "name": "start",
        "kind": "method",
        "signature": inspect.Signature(
            parameters=[
                inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
                inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)
            ],
            return_annotation=str
        )
    },
    Feature.METHOD_STOP: {
        "name": "stop",
        "kind": "method",
        "signature": inspect.Signature(
            parameters=[
                inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
                inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)
            ],
            return_annotation=str
        )
    },
    Feature.ATTR_CONFIG: {"name": "config", "kind": "attribute", "type": dict},
    Feature.METHOD_LOG: {
        "name": "log",
        "kind": "method",
        "signature": inspect.Signature(
            parameters=[
                inspect.Parameter("message", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
                inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
                inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)
            ],
            return_annotation=None
        )
    },
}