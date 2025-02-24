from typing import Any


try:
    import numpy as np

    def _handle_numpy_str(value):
        if isinstance(value, np.str_):
            return str(value)
        return value

    def _handle_numpy_array(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        return value

except ImportError:

    def _handle_numpy_str(value):
        return value

    def _handle_numpy_array(value):
        return value


class ValueHandler:
    def postprocess(self, value: Any) -> Any:
        if isinstance(value, list):
            return list(map(self.postprocess, value))
        elif isinstance(value, dict):
            return {
                self.postprocess(key): self.postprocess(value)
                for key, value in value.items()
            }
        else:
            return self.postprocess_atomic_value(value)

    def postprocess_atomic_value(self, value: Any) -> Any:
        value = _handle_numpy_array(value)
        if isinstance(value, list):
            return list(map(_handle_numpy_str, value))
        else:
            return _handle_numpy_str(value)
