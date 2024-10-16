from typing import Generic, Type, TypeVar

import pydantic

DO = TypeVar("DO", bound="DependentObject")
DK = TypeVar("DK", bound="DependencyKwargs")


class Dependency(Generic[DO, DK]):
    def __init__(self, source: DO, meta: DK) -> None:
        self.source: DO = source
        self.meta = meta

    def __str__(self):
        return f"{str(self.source)}: {self.meta}"


class DependentObject(Generic[DO, DK]):

    def __init__(self, *, name: str, validator: Type[DK]):
        self._name = name
        self.validator: Type[DK] = validator
        self.dependencies: list[Dependency[DO, DK]] = []

    @property
    def name(self):
        return self._name

    def add_dependency(self, *, source: DO, meta_data: dict = {}):
        meta: DK = self.validator(**meta_data)
        self.dependencies.append(Dependency(source=source, meta=meta))


class DependencyKwargs(pydantic.BaseModel):
    pass


def topological_sort_dependency_tree(
    *, dependency_tree: dict[str, DependentObject]
) -> list[str]:
    """
    Fancy sort for dataset configurations in self._dataset_configs
    based on order of dependence.
    """
    # A list to store the sorted elements
    sorted_list: list[str] = []

    # A set to keep track of all visited nodes
    visited: set[str] = set()

    # A set to detect recursion and hence, cycles
    recursion_stack: set[str] = set()

    # Helper function for depth-first search
    def dfs(*, dependency_name: str):

        if dependency_name in recursion_stack:
            raise Exception(
                f"Circular dependency detected starting from {dependency_name}"
            )

        if dependency_name not in visited:

            visited.add(dependency_name)
            recursion_stack.add(dependency_name)

            current_obj = dependency_tree.get(dependency_name)
            if current_obj:
                for dependency in current_obj.dependencies:
                    dfs(dependency_name=dependency.source.name)

            recursion_stack.remove(dependency_name)
            sorted_list.append(dependency_name)

    # Perform DFS from each node
    for dependency_name in dependency_tree:
        if dependency_name not in visited:
            dfs(dependency_name=dependency_name)

    return sorted_list
