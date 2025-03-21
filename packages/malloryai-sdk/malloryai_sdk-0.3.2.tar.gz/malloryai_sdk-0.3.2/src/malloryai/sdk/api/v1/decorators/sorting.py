from typing import Callable, Any, Optional
from functools import wraps
from inspect import signature, iscoroutinefunction
from pydantic import BaseModel, Field, ValidationError, create_model


class SortParams(BaseModel):
    """Pydantic model for sorting validation."""

    sort: str = Field(..., pattern="^(name|created_at|updated_at)$")
    order: str = Field(..., pattern="^(asc|desc)$")

    model_config = {"extra": "ignore"}


def validate_sorting(
    func: Optional[Callable] = None, *, sort_pattern: Optional[str] = None
) -> Callable:
    """
    Decorator to validate and inject sorting parameters.
    Works with both sync and async functions.

    Usage without override:
      @validate_sorting
      def list_exploits(..., sort: str = "created_at", order: str = "desc"):
          ...

      @validate_sorting
      async def list_exploits_async(..., sort: str = "created_at", order: str = "desc"):
          ...

    Or with override:
      @validate_sorting(sort_pattern="^(url|authors|maturity|created_at|updated_at)$")
      def list_exploits(..., sort: str = "created_at", order: str = "desc"):
          ...
    """

    def decorator(f: Callable) -> Callable:
        is_async = iscoroutinefunction(f)

        @wraps(f)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            validated_kwargs = _validate_params(f, kwargs, sort_pattern)
            return await f(*args, **validated_kwargs)

        @wraps(f)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            validated_kwargs = _validate_params(f, kwargs, sort_pattern)
            return f(*args, **validated_kwargs)

        return async_wrapper if is_async else sync_wrapper

    # Allow the decorator to be used with or without arguments
    if func is not None and callable(func):
        return decorator(func)
    return decorator


def _validate_params(func: Callable, kwargs: dict, sort_pattern: Optional[str]) -> dict:
    """Helper function to validate sorting parameters."""
    # Retrieve function signature and merge default values with provided kwargs
    sig = signature(func)
    defaults = {
        name: param.default
        for name, param in sig.parameters.items()
        if param.default is not param.empty
    }
    params = defaults.copy()
    params.update(kwargs)

    # Decide which model to use
    if sort_pattern is None:
        model_cls = SortParams
    else:
        # Use a configuration dictionary as expected in Pydantic v2
        config_dict = {"extra": "ignore"}
        model_cls = create_model(
            "SortParamsCustom",
            sort=(str, Field(..., pattern=sort_pattern)),
            order=(str, Field(..., pattern="^(asc|desc)$")),
            __config__=config_dict,
        )

    try:
        sort_params = model_cls(sort=params["sort"], order=params["order"])
        # Update kwargs with the validated values
        kwargs.update(sort_params.model_dump(exclude_unset=True))
    except (ValidationError, KeyError) as e:
        raise ValueError(f"Invalid or missing sorting parameters: {e}")

    return kwargs
