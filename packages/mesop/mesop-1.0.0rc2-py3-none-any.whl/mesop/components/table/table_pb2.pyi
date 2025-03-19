"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class TableClickEvent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ROW_INDEX_FIELD_NUMBER: builtins.int
    COL_INDEX_FIELD_NUMBER: builtins.int
    row_index: builtins.int
    col_index: builtins.int
    def __init__(
        self,
        *,
        row_index: builtins.int | None = ...,
        col_index: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["col_index", b"col_index", "row_index", b"row_index"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["col_index", b"col_index", "row_index", b"row_index"]) -> None: ...

global___TableClickEvent = TableClickEvent

@typing.final
class TableRow(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    INDEX_FIELD_NUMBER: builtins.int
    CELL_VALUES_FIELD_NUMBER: builtins.int
    index: builtins.int
    """Pandas Index."""
    @property
    def cell_values(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]:
        """Column values are stored as a list corresponding to the `displayed_columns`
        field.

        This is done because the Pandas may change the column name in certain situations
        such as:

        - Naming a column `Index` which conflicts with the special Pandas `Index` column.
        - Naming a column with spaces, such as "Date Time"
        """

    def __init__(
        self,
        *,
        index: builtins.int | None = ...,
        cell_values: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["index", b"index"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["cell_values", b"cell_values", "index", b"index"]) -> None: ...

global___TableRow = TableRow

@typing.final
class TableHeader(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STICKY_FIELD_NUMBER: builtins.int
    sticky: builtins.bool
    def __init__(
        self,
        *,
        sticky: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["sticky", b"sticky"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["sticky", b"sticky"]) -> None: ...

global___TableHeader = TableHeader

@typing.final
class TableColumn(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STICKY_FIELD_NUMBER: builtins.int
    sticky: builtins.bool
    def __init__(
        self,
        *,
        sticky: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["sticky", b"sticky"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["sticky", b"sticky"]) -> None: ...

global___TableColumn = TableColumn

@typing.final
class TableType(google.protobuf.message.Message):
    """Next ID: 6"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class ColumnsEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        @property
        def value(self) -> global___TableColumn: ...
        def __init__(
            self,
            *,
            key: builtins.str | None = ...,
            value: global___TableColumn | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["key", b"key", "value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["key", b"key", "value", b"value"]) -> None: ...

    DISPLAYED_COLUMNS_FIELD_NUMBER: builtins.int
    DATA_SOURCE_FIELD_NUMBER: builtins.int
    ON_TABLE_CLICK_EVENT_HANDLER_ID_FIELD_NUMBER: builtins.int
    HEADER_FIELD_NUMBER: builtins.int
    COLUMNS_FIELD_NUMBER: builtins.int
    on_table_click_event_handler_id: builtins.str
    @property
    def displayed_columns(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def data_source(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TableRow]: ...
    @property
    def header(self) -> global___TableHeader: ...
    @property
    def columns(self) -> google.protobuf.internal.containers.MessageMap[builtins.str, global___TableColumn]: ...
    def __init__(
        self,
        *,
        displayed_columns: collections.abc.Iterable[builtins.str] | None = ...,
        data_source: collections.abc.Iterable[global___TableRow] | None = ...,
        on_table_click_event_handler_id: builtins.str | None = ...,
        header: global___TableHeader | None = ...,
        columns: collections.abc.Mapping[builtins.str, global___TableColumn] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["header", b"header", "on_table_click_event_handler_id", b"on_table_click_event_handler_id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["columns", b"columns", "data_source", b"data_source", "displayed_columns", b"displayed_columns", "header", b"header", "on_table_click_event_handler_id", b"on_table_click_event_handler_id"]) -> None: ...

global___TableType = TableType
