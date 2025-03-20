from collections.abc import ItemsView, Iterator, KeysView, ValuesView

import pydantic


class ListOf[T](pydantic.RootModel[list[T]]):
    """
    Pydantic RootModel for representing a list of other models.
    """

    def __iter__(self) -> Iterator[T]:  # type:ignore[override]
        return iter(self.root)

    def __getitem__(self, item: int) -> T:
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)


class DictOf[K, V](pydantic.RootModel[dict[K, V]]):
    """
    Pydantic RootModel for representing a dict
    """

    def __getitem__(self, key: K) -> V:
        return self.root[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.root[key] = value

    def __delitem__(self, key: K) -> None:
        del self.root[key]

    def __contains__(self, key: K) -> bool:
        return key in self.root

    def __iter__(self) -> Iterator[K]:  # type:ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def keys(self) -> KeysView[K]:
        return self.root.keys()

    def values(self) -> ValuesView[V]:
        return self.root.values()

    def items(self) -> ItemsView[K, V]:
        return self.root.items()

    def get(self, key: K, default: V | None = None) -> V | None:
        return self.root.get(key, default)

    def setdefault(self, key: K, default: V) -> V:
        return self.root.setdefault(key, default)

    def update(self, other: dict[K, V]) -> None:
        self.root.update(other)

    def pop(self, key: K, default: V | None = None) -> V | None:
        return self.root.pop(key, default)

    def popitem(self) -> tuple[K, V]:
        return self.root.popitem()

    def clear(self) -> None:
        self.root.clear()
