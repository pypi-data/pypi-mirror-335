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
class RadioType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COLOR_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    LABEL_POSITION_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    DISABLED_FIELD_NUMBER: builtins.int
    ON_RADIO_CHANGE_EVENT_HANDLER_ID_FIELD_NUMBER: builtins.int
    OPTIONS_FIELD_NUMBER: builtins.int
    color: builtins.str
    name: builtins.str
    label_position: builtins.str
    value: builtins.str
    disabled: builtins.bool
    on_radio_change_event_handler_id: builtins.str
    @property
    def options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___RadioOption]: ...
    def __init__(
        self,
        *,
        color: builtins.str | None = ...,
        name: builtins.str | None = ...,
        label_position: builtins.str | None = ...,
        value: builtins.str | None = ...,
        disabled: builtins.bool | None = ...,
        on_radio_change_event_handler_id: builtins.str | None = ...,
        options: collections.abc.Iterable[global___RadioOption] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["color", b"color", "disabled", b"disabled", "label_position", b"label_position", "name", b"name", "on_radio_change_event_handler_id", b"on_radio_change_event_handler_id", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["color", b"color", "disabled", b"disabled", "label_position", b"label_position", "name", b"name", "on_radio_change_event_handler_id", b"on_radio_change_event_handler_id", "options", b"options", "value", b"value"]) -> None: ...

global___RadioType = RadioType

@typing.final
class RadioOption(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    LABEL_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    label: builtins.str
    value: builtins.str
    def __init__(
        self,
        *,
        label: builtins.str | None = ...,
        value: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["label", b"label", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["label", b"label", "value", b"value"]) -> None: ...

global___RadioOption = RadioOption
