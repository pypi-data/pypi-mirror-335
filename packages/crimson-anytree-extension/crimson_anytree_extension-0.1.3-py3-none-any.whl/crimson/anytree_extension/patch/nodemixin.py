from typing import Generic, TypeVar, Tuple, Optional, Iterator
from anytree import NodeMixin

T = TypeVar("T")


class NodeMixinTyped(NodeMixin, Generic[T]):
    @property
    def children(self) -> Tuple[T, ...]:
        return super().children

    @property
    def parent(self) -> Optional[T]:
        return super().parent

    @parent.setter
    def parent(self, value: Optional[T]):
        super(NodeMixinTyped, type(self)).parent.fset(self, value)

    @property
    def path(self) -> Tuple[T, ...]:
        return super().path

    @property
    def ancestors(self) -> Tuple[T, ...]:
        return super().ancestors

    @property
    def descendants(self) -> Tuple[T, ...]:
        return super().descendants

    @property
    def root(self) -> T:
        return super().root

    @property
    def siblings(self) -> Tuple[T, ...]:
        return super().siblings

    @property
    def leaves(self) -> Tuple[T, ...]:
        return super().leaves

    def iter_path_reverse(self) -> Iterator[T]:
        return super().iter_path_reverse()
