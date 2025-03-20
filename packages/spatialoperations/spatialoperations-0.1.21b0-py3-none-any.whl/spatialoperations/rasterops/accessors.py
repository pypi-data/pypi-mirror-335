from .rasterops import DataCube
import warnings

class AccessorRegistrationWarning(Warning):
    """Warning for when an accessor is being registered that overrides a preexisting attribute."""
    pass


class _CachedAccessor:
    """
    Custom property-like object for caching accessors.
    """
    def __init__(self, name, accessor):
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            return self._accessor

        # Create an accessor instance and cache it on the object
        accessor_obj = self._accessor(obj)
        # Use the accessor's class name for caching
        cache_name = f"_{self._accessor.__name__}"
        setattr(obj, cache_name, accessor_obj)
        return accessor_obj


def register_datacube_accessor(name):
    """
    Register a custom accessor for DataCube objects.
    
    Parameters
    ----------
    name : str
        Name under which the accessor should be registered. A warning is issued
        if this name conflicts with a preexisting attribute.
        
    Returns
    -------
    callable
        A decorator that registers the accessor class.
    """
    def decorator(accessor):
        if hasattr(DataCube, name):
            warnings.warn(
                f"registration of accessor {accessor!r} under name {name!r} for DataCube is "
                "overriding a preexisting attribute with the same name.",
                AccessorRegistrationWarning,
                stacklevel=2,
            )
        setattr(DataCube, name, _CachedAccessor(name, accessor))
        return accessor

    return decorator
