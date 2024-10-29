from shlex import join
from typing import Iterable

import numpy as np
import pandas as pd
from scrapp.core.dataframes import safe_concat
from scrapp.core.exceptions import (
    ColumnDoesNotExist,
    DataInsertionError,
    DataStagingError,
    StageEmpty,
    concatenate_exceptions,
)
from scrapp.tables import BaseTable


class DataStateManager:

    def __init__(
        self,
        db_table: BaseTable,
        data_fields: Iterable[str],
        extraneous_fields: Iterable[str] = [],
        primary_keys: list[str] = [],
    ) -> None:
        self.__db_table: BaseTable = db_table
        self.__data_fields: set[str] = set(data_fields)
        self.__model_fields: list[str] = list(db_table.serializer_class.model_fields)
        self.__extraneous_fields: set[str] = set(extraneous_fields)
        self.__base_fields = self.__data_fields - self.__extraneous_fields
        self.__primary_keys: list[str] = primary_keys or db_table.PKS

        self.__committed_data: pd.DataFrame = pd.DataFrame(
            columns=list(self.__data_fields)
        )
        self.__staged_data: pd.DataFrame = pd.DataFrame(
            columns=list(self.__base_fields)
        )

    def __str__(self):
        return str(self.__staged_data)

    @property
    def data_fields(self):
        return self.__data_fields

    @data_fields.setter
    def data_fields(self, value: set[str]):
        self.__data_fields = value
        self.__base_fields = self.__data_fields - self.__extraneous_fields

    @property
    def base_fields(self):
        return self.__data_fields

    @property
    def primary_keys(self):
        return self.__primary_keys

    @property
    def db_table(self):
        return self.__db_table

    @db_table.setter
    def db_table(self, db_table: BaseTable):
        self.__db_table = db_table

    @property
    def stage(self):
        return self.__staged_data

    @property
    def commits(self):
        return self.__committed_data

    def copy(self) -> pd.DataFrame:
        return self.__staged_data.copy()

    def reset(self) -> None:
        self.__staged_data = pd.DataFrame(columns=list(self.__data_fields))

    def unstage(self) -> None:
        self.__committed_data = pd.DataFrame(columns=list(self.__data_fields))

    def add(self, data: pd.DataFrame) -> None:
        """
        Add data to the stack. Outer joins new records into the bottom of the table
        filling all required fields and keeping additional fields.
        """
        exceptions: list[Exception] = []
        for column in self.__primary_keys:
            if column not in data.columns:
                exceptions.append(ColumnDoesNotExist(column, data.columns.to_list()))

        if exceptions:
            raise DataInsertionError(concatenate_exceptions(exceptions))

        # Concatenate all independent columns
        # self.__staged_data = safe_concat(
        #     self.__staged_data.set_index(self.__primary_keys),
        #     data.set_index(self.__primary_keys),
        #     axis=1,
        #     join="outer",
        # ).reset_index()
        self.__staged_data = safe_concat(self.__staged_data, data, join="inner")

        exceptions: list[Exception] = []
        for column in self.__base_fields:
            if column not in self.__staged_data.columns:
                exceptions.append(ColumnDoesNotExist(column, data.columns.to_list()))

        if exceptions:
            self.reset()
            raise DataInsertionError(concatenate_exceptions(exceptions))

    def update(self, data: pd.DataFrame):
        """
        Update the staged data to include new columns. Inner joins new data with
        the existing data based on the index column(s).
        """
        self.__staged_data = safe_concat(
            self.__staged_data.set_index(self.__primary_keys),
            data.set_index(self.__primary_keys),
            axis=1,
            join="inner",
        ).reset_index()

    def commit(self, *, persist_data: bool = False) -> None:
        """
        Moves data to the stage. Inner joins existing data to the staged data keeping
        only the required columns.
        """
        exceptions: list[Exception] = []
        for column in self.__data_fields:
            if column not in self.__staged_data:
                # raise Exception(f"{column} not present in the added data.")
                exceptions.append(
                    ColumnDoesNotExist(column, self.__staged_data.columns.to_list())
                )

        if exceptions:
            raise DataStagingError(concatenate_exceptions(exceptions))

        self.__committed_data = safe_concat(
            self.__committed_data, self.__staged_data, join="inner"
        )

        # Reset the data if not being persisted
        if not persist_data:
            self.reset()

    def push(self, *, persist_data: bool = False) -> pd.DataFrame:
        """
        Save the data for the dataset and any nested datasets.
        """
        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        if self.__committed_data.empty:
            if self.__staged_data.empty:
                raise StageEmpty(
                    "There is no staged data to push. First stage data using 'add'. Then, commit it using 'commit'."
                )
            else:
                raise StageEmpty(
                    "There is no staged data to push. Run 'commit' to add commit staged data for push."
                )

        data = self.__committed_data.copy()

        # Empty the stage because if the save fails, we won't be running
        # it again.
        if not persist_data:
            self.unstage()

        data = data.fillna(np.nan).replace([np.nan], [None])

        db_table_meta = getattr(self.db_table.model_class, "_meta", None)

        if db_table_meta and db_table_meta.primary_key.name in list(data.columns):
            data = data.set_index(db_table_meta.primary_key.name)

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index

            self.__db_table.update_or_insert_record(data=row_data)

        return data
