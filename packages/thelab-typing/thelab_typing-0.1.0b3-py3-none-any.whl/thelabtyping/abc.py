from collections.abc import Iterator

import pydantic


class ListOf[T: pydantic.BaseModel](pydantic.RootModel[list[T]]):
    """
    Pydantic RootModel for representing a list of other models.
    """

    def __iter__(self) -> Iterator[T]:  # type:ignore[override]
        return iter(self.root)

    def __getitem__(self, item: int) -> T:
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)
