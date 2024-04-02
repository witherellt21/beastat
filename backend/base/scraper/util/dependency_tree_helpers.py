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

    # def __str__(self):
    #     return self.name

    @property
    def name(self):
        return self._name

    def add_dependency(self, *, source: DO, meta_data: dict = {}):
        meta: DK = self.validator(**meta_data)
        self.dependencies.append(Dependency(source=source, meta=meta))


class DependencyKwargs(pydantic.BaseModel):
    pass


def topological_sort_dependency_tree(*, dependency_tree: dict[str, DependentObject]):
    """
    Fancy sort for dataset configurations in self._dataset_configs
    based on order of dependence.
    """
    # A list to store the sorted elements
    sorted_list = []

    # A set to keep track of all visited nodes
    visited = set()

    # A set to detect recursion and hence, cycles
    recursion_stack = set()

    # Helper function for depth-first search
    def dfs(*, dataset_name: str):
        if dataset_name in recursion_stack:
            raise Exception(
                f"Circular dependency detected starting from {dataset_name}"
            )
        if dataset_name not in visited:
            visited.add(dataset_name)
            recursion_stack.add(dataset_name)
            current_config = dependency_tree.get(dataset_name)
            if current_config:
                for dependency in current_config.dependencies:
                    dfs(dataset_name=dependency.source.name)

            recursion_stack.remove(dataset_name)
            sorted_list.append(dataset_name)

    # Perform DFS from each node
    for dataset_name in dependency_tree:
        if dataset_name not in visited:
            dfs(dataset_name=dataset_name)

    return sorted_list
