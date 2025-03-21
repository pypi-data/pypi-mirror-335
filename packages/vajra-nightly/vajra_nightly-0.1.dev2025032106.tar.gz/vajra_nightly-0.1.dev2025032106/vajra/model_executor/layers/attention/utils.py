"""Utils for attention"""

from typing import Callable

from vajra.model_executor.utils import ReturnType


def check_metadata_initialized(
    func: Callable[..., ReturnType],
) -> Callable[..., ReturnType]:
    """
    Decorator that ensures metadata is initialized for non-native execution before executing the function.
    """

    def wrapper(self, *args, **kwargs):
        assert (
            self.is_metadata_initialized or self.use_native_execution_backend
        ), "Metadata is not initialized for non-native execution."
        return func(self, *args, **kwargs)

    return wrapper
