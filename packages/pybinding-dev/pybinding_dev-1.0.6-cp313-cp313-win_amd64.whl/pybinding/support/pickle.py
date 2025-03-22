"""Utility functions for getting data to/from files"""
import gzip
import os
import pathlib
import pickle

from pathlib import Path
from ..utils.misc import decorator_decorator
from typing import Union

__all__ = ['pickleable', 'save', 'load', 'normalize']


def normalize(file: Union[str, Path]) -> str:
    """Convenience function to support path objects."""
    if 'Path' in type(file).__name__:
        return str(file)
    else:
        return file


def _add_extension(file: Union[str, Path]) -> Union[str, Path]:
    """Append '.pbz' if the file has no extension
    
    Examples
    --------
    >>> _add_extension("plain")
    'plain.pbz'
    >>> _add_extension("has_one.ext")
    'has_one.ext'
    """
    if not isinstance(file, str):
        return file

    path = pathlib.Path(file)
    if not path.suffix:
        return str(path.with_suffix(".pbz"))
    else:
        return file


def save(obj, file: Union[str, Path]) -> None:
    """Save an object to a compressed file

    Essentially, this is just a wrapper for :func:`pickle.dump()` with a few conveniences,
    like default pickle protocol 4 and gzip compression. The '.pbz' extension will be added
    if file has none.

    Parameters
    ----------
    obj : Any
        Object to be saved.
    file : Union[str, pathlib.Path]
        May be a `str`, a `pathlib` object or a file object created with `open()`.
    """
    file = _add_extension(normalize(file))
    with gzip.open(file, 'wb') as f:
        pickle.dump(obj, f, protocol=4)


def load(file: Union[str, Path]):
    """Load an object from a compressed file

    Wraps :func:`pickle.load()` with the same conveniences as :func:`pb.save() <save>`.

    Parameters
    ----------
    file : Union[str, pathlib.Path]
        May be a `str`, a `pathlib` object or a file object created with `open()`.
    """
    file = normalize(file)
    file_ext = _add_extension(file)
    if isinstance(file, str) and not os.path.exists(file) and os.path.exists(file_ext):
        file = file_ext

    with gzip.open(file, 'rb') as f:
        return pickle.load(f)


@decorator_decorator
def pickleable(props: str = "", version: int = 0) -> callable:
    props = props.split()

    def getstate(self):
        state = dict(version=version, dict=self.__dict__)
        if props:
            state["props"] = {name: getattr(self, name) for name in props}
        return state

    def setstate(self, state):
        if "version" not in state:
            self.__dict__.update(state)
            return

        if state["version"] != version:
            raise RuntimeError("Can't create class {} v{} from incompatible data v{}".format(
                type(self), version, state["version"]
            ))

        self.__dict__.update(state["dict"])
        props_state = {name: value for name, value in state.get("props", {})
                       if name in props}
        for name, value in props_state:
            setattr(self, name, value)

    def decorator(cls):
        cls.__getstate__ = getstate
        cls.__setstate__ = setstate
        return cls

    return decorator
