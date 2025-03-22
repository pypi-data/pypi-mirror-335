from __future__ import annotations

from collections import UserDict
from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from datetime import UTC, datetime, timedelta
from typing import Any, Self, override

_KT = Any
_VT = Any


class TTLDict(UserDict):
    def __init__(
        self,
        ttl: timedelta,
        other: Mapping[_KT, _VT] | Iterable[tuple[_KT, _VT]] | None = None,
        /,
        **kwargs: _VT,
    ) -> None:
        self.__ttl: timedelta = ttl

        self.expiries: dict[_KT, datetime] = {}

        # Must be at the end of __init__ as it calls self.update which needs self.__ttl
        super().__init__(other, **kwargs)

    def cleanup(self) -> None:
        now: datetime = datetime.now(UTC)

        expired_keys: list[_KT] = []
        for key, expiry in self.expiries.items():
            # As dict is iterated by insert order, the newer ones are iterated later
            if now < expiry:
                break

            expired_keys.append(key)

        for key in expired_keys:
            del self.expiries[key]
            del self.data[key]

    def cleanup_by_key(self, key: _KT) -> bool:
        now: datetime = datetime.now(UTC)

        if key not in self.expiries:
            return False

        if self.expiries[key] <= now:
            del self.expiries[key]
            del self.data[key]

            return False

        return True

    @override
    def __len__(self) -> int:
        self.cleanup()
        return super().__len__()

    @override
    def __contains__(self, key: _KT) -> bool:
        return self.cleanup_by_key(key)

    @override
    def get(self, key: _KT, default: _VT | None = None) -> _VT | None:
        self.cleanup_by_key(key)
        return super().get(key, default)

    @override
    def __getitem__(self, key: _KT) -> _VT:
        self.cleanup_by_key(key)
        return super().__getitem__(key)

    @override
    def __iter__(self) -> Iterator[_KT]:
        self.cleanup()
        return super().__iter__()

    @override
    def clear(self) -> None:
        self.expiries.clear()
        super().clear()

    @override
    def pop(self, key: _KT, default: _VT | None = None) -> _VT | None:
        if not self.expiries.pop(key):
            return default

        return super().pop(key, default)

    @override
    def popitem(self) -> tuple[_KT, _VT]:
        self.cleanup()

        key, value = super().popitem()
        self.expiries.pop(key)

        return (key, value)

    @override
    def __delitem__(self, key: _KT) -> None:
        del self.expiries[key]
        super().__delitem__(key)

    @override
    def __setitem__(self, key: _KT, value: _VT) -> None:
        self.expiries[key] = datetime.now(UTC) + self.__ttl
        super().__setitem__(key, value)

    @override
    def setdefault(self, key: _KT, default: _VT | None = None) -> None:
        self.expiries[key] = datetime.now(UTC) + self.__ttl
        super().setdefault(key, default)

    @override
    def update(
        self,
        other: Mapping[_KT, _VT] | Iterable[tuple[_KT, _VT]] | None,
        /,
        **kwargs: _VT,
    ) -> None:
        expiry: datetime = datetime.now(UTC) + self.__ttl
        other_ttl_dict: bool = isinstance(other, TTLDict)

        if isinstance(other, Mapping):
            for key, value in other.items():
                self.expiries[key] = other.expiries[key] if other_ttl_dict else expiry
                self.data[key] = value
        elif isinstance(other, Iterable):
            for key, value in other:
                self.expiries[key] = expiry
                self.data[key] = value

        for key, value in kwargs.items():
            self.expiries[key] = expiry
            self.data[key] = value

    @override
    def copy(self) -> TTLDict:
        return TTLDict(self.__ttl, self)

    @override
    def __or__(self, other: Mapping[_KT, _VT]) -> TTLDict:
        d: TTLDict = self.copy()
        d.update(other)

        return d

    @override
    def __ior__(self, other: Mapping[_KT, _VT]) -> Self:
        self.update(other)
        return self

    @override
    def __repr__(self) -> str:
        self.cleanup()
        return super().__repr__()

    @override
    def keys(self) -> KeysView:
        self.cleanup()
        return super().keys()

    @override
    def values(self) -> ValuesView:
        self.cleanup()
        return super().values()

    @override
    def items(self) -> ItemsView:
        self.cleanup()
        return super().items()
