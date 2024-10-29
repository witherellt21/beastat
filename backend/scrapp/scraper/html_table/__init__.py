from typing import Any, Literal, Optional, overload

import pandas as pd
from lib.dependency_trees import DependencyKwargs, DependentObject
from lib.pydantic_validator import PydanticValidatorMixin
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.exceptions import ColumnDoesNotExist, StageEmpty
from scrapp.tables import BaseTable
from scrapp.tables.base_table import AdvancedQuery

from .data_state_manager import DataStateManager


class DataframeControllerInheritance:
    """
    Gets inherited data from a source controller.
    """

    def __init__(
        self,
        source: "DataStateManager",
        fields: list[str],
        on_keys: dict[str, str],
    ) -> None:
        for field in fields:
            if field not in source.data_fields:
                raise ColumnDoesNotExist(field, source.data_fields)

        self.source: "DataStateManager" = source
        self.fields: list[str] = fields
        self.on_keys: dict[str, str] = on_keys

    def __str__(self) -> str:
        return f"{self.__class__.__name__} :: {self.fields} from {self.source}"

    def is_ready(self):
        return not self.source.commits.empty

    def perform(self):
        """
        Perform the inheritance operation to get a new dataframe consisting
        of the requested field and keys to merge on.
        """
        if not self.source.commits.empty:
            fields = [*self.on_keys.keys(), *self.fields]
            data = self.source.commits[fields]

            data = data.rename(columns=self.on_keys)
            data = data.rename(columns={col: f"inherited_{col}" for col in self.fields})

            return data

        else:
            raise StageEmpty(
                f"Inherited data source '{self.source}' while attempting to resolve inheritances for {self}."
            )


class DataframeController(
    DependentObject["DataframeController", DependencyKwargs], PydanticValidatorMixin
):
    """
    Controls the validation and saving of pandas dataframes.
    """

    @overload
    def __init__(
        self,
        name: str,
        serializer: BaseDataframeValidator,
        *,
        data_manager: Optional[DataStateManager],
    ) -> None: ...

    @overload
    def __init__(
        self,
        name: str,
        serializer: BaseDataframeValidator,
        *,
        db_table: Optional[BaseTable],
    ) -> None: ...

    def __init__(
        self,
        name: str,
        serializer: BaseDataframeValidator,
        *,
        data_manager: Optional[DataStateManager] = None,
        db_table: Optional[BaseTable] = None,
    ):
        super().__init__(name=name, validator=DependencyKwargs)

        self.__data_manager: DataStateManager
        self.__serializer: BaseDataframeValidator = serializer
        self.__inheritances: list[DataframeControllerInheritance] = []

        self.status: Literal["downloaded", "cached"] = "downloaded"

        if data_manager and isinstance(data_manager, DataStateManager):
            self.__data_manager = data_manager
        elif db_table:
            self.__data_manager = DataStateManager(
                db_table,
                self.__serializer.get_fields(),
                extraneous_fields=self.__serializer.get_post_validated_fields(),
            )
        else:
            raise Exception(
                "Either the 'data_manager' or the 'db_table' argument must be provided."
            )

    def __str__(self):
        return self.name

    # def add_inheritance(
    #     self,
    #     source: "DataStateManager",
    #     fields: list[str],
    # ):
    #     """
    #     Add an inheritance to the table so that it can import foreign data from another webpage/table.

    #     """
    #     self.__inheritances.append(DataframeControllerInheritance(source, fields))

    @property
    def data(self):
        return self.__data_manager

    @property
    def serializer(self):
        return self.__serializer

    @serializer.setter
    def serializer(self, serializer: BaseDataframeValidator):
        self.__serializer = serializer
        self.__data_manager.data_fields = serializer.get_fields()

    @property
    def inheritances(self):
        return self.__inheritances

    def is_cached(self):
        return self.status == "cached"

    def set_cached(self):
        # TODO: There is a better design out there
        self.status = "cached"

    def load_from_cache(self, db_query: AdvancedQuery | None):
        """
        Load the cached data from the database and fix the data_source
        attribute accordingly.
        """
        data = self.data.db_table.filter_records_advanced(db_query)

        if not data.empty:
            self.__data_manager.add(data)
            self.status = "cached"

        else:
            self.status = "downloaded"  # TODO: Should this be done here?

    def add_dependency(
        self,
        *,
        source: "DataframeController",
    ):
        return super().add_dependency(source=source, meta_data={})

    def check_dependencies(self):
        for dependency in self.dependencies:
            if dependency.source.status != "cached":
                return False

        return True

    def ready_for_save(self):
        """
        1. Have all dependencies been saved to the database?
        2. Is there committed data to be saved?
        """
        return not self.data.commits.empty and self.check_dependencies()

    # def attempt_save(self, *, raise_exception: bool = False):
    #     """
    #     Try to postprocess the current staged data and save it if successful.
    #     """
    #     try:
    #         self.resolve_inheritances()

    #         self.__data_manager.commit(persist_data=True)

    #     except StageEmpty as e:
    #         if raise_exception:
    #             raise e

    #     if self.ready_for_save():
    #         self.data.push()
    #         self.status = "cached"

    # def resolve_inheritances(self):
    #     """
    #     Perform inheritances to draw data from external data sources.
    #     """
    #     for inheritance in self.inheritances:
    #         data = inheritance.perform(self.__data_manager.primary_keys)

    #         data = self.__serializer.post_validate(data)

    #         self.__data_manager.update(data)

    def save(self, *, persist_data: bool = False):
        self.__data_manager.push(persist_data=persist_data)

        self.status = "cached"

    # def postprocess(self, *, persist_data: bool = False):
    #     self.resolve_inheritances()

    #     self.__data_manager.commit(persist_data=persist_data)

    def preprocess(self, df: pd.DataFrame, additional_fields: dict[str, Any] = {}):
        """
        Validate the incoming data and update the data manager with
        the resulting data.
        """
        # TODO: Currently, DataframeSerializers do not support multi-indexing
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.map("_".join).str.strip("_")

        data = self.__serializer.validate(df, additional_fields)

        self.__data_manager.add(data)
