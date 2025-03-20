from .rasterops import DataCube
from .compute import Compute
from .intake import Intake
from .export import Export
# from rasterops.storage import PlainOlZarrStore
# from rasterops.api import API
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
        self._accessor_obj = None

    def __get__(self, obj, cls):
        if self._accessor_obj is None:
            self._accessor_obj = self._accessor(obj)

        return self._accessor_obj

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


register_datacube_accessor("compute")(Compute)
register_datacube_accessor("intake")(Intake)
register_datacube_accessor("export")(Export)
# register_datacube_accessor("api")(API)
# register_datacube_accessor("storage")(PlainOlZarrStore)

__all__ = ["DataCube"]
