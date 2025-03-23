"""Store and modify global app state in JSON (Python dictionary) to re-render front-end components."""

from collections.abc import Callable, Hashable, Iterable, MutableMapping
from typing import Any, overload
from unittest.mock import call

__version__ = '0.0.3'


class State(dict):
    def __init__(self, json_state: dict | list, *args, **kwargs) -> None:
        self.on_change_callbacks = {}
        super().__init__(json_state, *args, **kwargs)

    def callbacks(self, key: str) -> list[Callable]:
        self.on_change_callbacks.setdefault(key, [])
        return self.on_change_callbacks[key]

    def pop(
        self, key: Any, default: Any | None = None, /, *args, **kwargs
    ) -> Any | None:
        if key not in self:
            return super().pop(key, default, *args, **kwargs)

        old_value = self[key]
        result = super().pop(key, default, *args, **kwargs)
        for callback in self.on_change_callbacks[key]:
            callback(old_value=old_value, action='remove')
        return result

    def popitem(self) -> tuple[Any, Any]:
        result = super().popitem()
        if result:
            key = result[0]
            old_value = result[1]
            for callback in self.on_change_callbacks[key]:
                callback(old_value=old_value, action='remove')
        return result

    def clear(self) -> None:
        for key in self:
            for callback in self.on_change_callbacks[key]:
                callback(old_value=self[key], action='remove')
        return super().clear()

    @overload
    def update(self, arg: MutableMapping[Hashable, Any], /, **kwargs: Any) -> None: ...

    @overload
    def update(self, arg: Iterable[tuple[Hashable, Any]], /, **kwargs: Any) -> None: ...

    @overload
    def update(self, /, **kwargs: Any) -> None: ...

    def update(self, arg: Any = None, /, **kwargs: Any) -> None:  # type: ignore
        if hasattr(arg, 'keys'):
            for key in arg:
                # TODO: do not send update callbacks if old and new values are the same.
                new_value = arg[key]
                callback_kwargs = None
                if key in self:
                    old_value = self[key]
                    if old_value != new_value:
                        callback_kwargs = {
                            'new_value': new_value,
                            'old_value': old_value,
                            'action': 'update',
                        }
                else:
                    callback_kwargs = {
                        'new_value': new_value,
                        'action': 'create',
                    }

                if callback_kwargs:
                    for callback in self.on_change_callbacks[key]:
                        callback(**callback_kwargs)

            return super().update(arg, **kwargs)
        if arg:
            for key, value in arg:
                new_value = value
                callback_kwargs = None
                if key in self:
                    old_value = self[key]
                    if old_value != new_value:
                        callback_kwargs = {
                            'new_value': new_value,
                            'old_value': old_value,
                            'action': 'update',
                        }
                else:
                    callback_kwargs = {
                        'new_value': new_value,
                        'action': 'create',
                    }

                if callback_kwargs:
                    for callback in self.on_change_callbacks[key]:
                        callback(**callback_kwargs)
            return super().update(arg, **kwargs)
        for key, value in kwargs.items():
            new_value = value
            callback_kwargs = None
            if key in self:
                old_value = self[key]
                if old_value != new_value:
                    callback_kwargs = {
                        'new_value': new_value,
                        'old_value': old_value,
                        'action': 'update',
                    }
            else:
                callback_kwargs = {
                    'new_value': new_value,
                    'action': 'create',
                }

            if callback_kwargs:
                for callback in self.on_change_callbacks[key]:
                    callback(**callback_kwargs)

        return super().update(kwargs, **kwargs)

    def setdefault(self, key, default: Any | None = None, /) -> Any | None:
        callback_kwargs = None
        if key not in self:
            callback_kwargs = {
                'action': 'create',
            }

        result = super().setdefault(key, default)

        if callback_kwargs:
            for callback in self.on_change_callbacks[key]:
                callback(new_value=result, **callback_kwargs)

        return result

    def __setitem__(self, key: Any, value: Any, /, *args, **kwargs) -> None:
        callback_kwargs = None
        new_value = value
        if key in self:
            old_value = self[key]
            if old_value != new_value:
                callback_kwargs = {
                    'new_value': new_value,
                    'old_value': self[key],
                    'action': 'update',
                }
        else:
            callback_kwargs = {
                'new_value': new_value,
                'action': 'create',
            }

        result = super().__setitem__(key, value, *args, **kwargs)

        if callback_kwargs:
            for callback in self.on_change_callbacks[key]:
                callback(**callback_kwargs)

        return result

    def __delitem__(self, key: Any, /) -> None:
        if key not in self:
            return super().__delitem__(key)

        old_value = self[key]
        result = super().__delitem__(key)
        for callback in self.on_change_callbacks[key]:
            callback(old_value=old_value, action='remove')
        return result
