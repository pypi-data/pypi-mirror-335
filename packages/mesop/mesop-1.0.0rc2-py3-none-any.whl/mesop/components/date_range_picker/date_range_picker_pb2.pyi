"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import google.protobuf.descriptor
import google.protobuf.message
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class DateRangePickerType(google.protobuf.message.Message):
    """Next ID: 16"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    START_DATE_FIELD_NUMBER: builtins.int
    END_DATE_FIELD_NUMBER: builtins.int
    PLACEHOLDER_START_DATE_FIELD_NUMBER: builtins.int
    PLACEHOLDER_END_DATE_FIELD_NUMBER: builtins.int
    DISABLED_FIELD_NUMBER: builtins.int
    REQUIRED_FIELD_NUMBER: builtins.int
    READONLY_FIELD_NUMBER: builtins.int
    HIDE_REQUIRED_MARKER_FIELD_NUMBER: builtins.int
    COLOR_FIELD_NUMBER: builtins.int
    FLOAT_LABEL_FIELD_NUMBER: builtins.int
    APPEARANCE_FIELD_NUMBER: builtins.int
    SUBSCRIPT_SIZING_FIELD_NUMBER: builtins.int
    HINT_LABEL_FIELD_NUMBER: builtins.int
    LABEL_FIELD_NUMBER: builtins.int
    ON_CHANGE_HANDLER_ID_FIELD_NUMBER: builtins.int
    start_date: builtins.str
    end_date: builtins.str
    placeholder_start_date: builtins.str
    placeholder_end_date: builtins.str
    disabled: builtins.bool
    required: builtins.bool
    readonly: builtins.bool
    hide_required_marker: builtins.bool
    color: builtins.str
    float_label: builtins.str
    appearance: builtins.str
    subscript_sizing: builtins.str
    hint_label: builtins.str
    label: builtins.str
    on_change_handler_id: builtins.str
    def __init__(
        self,
        *,
        start_date: builtins.str | None = ...,
        end_date: builtins.str | None = ...,
        placeholder_start_date: builtins.str | None = ...,
        placeholder_end_date: builtins.str | None = ...,
        disabled: builtins.bool | None = ...,
        required: builtins.bool | None = ...,
        readonly: builtins.bool | None = ...,
        hide_required_marker: builtins.bool | None = ...,
        color: builtins.str | None = ...,
        float_label: builtins.str | None = ...,
        appearance: builtins.str | None = ...,
        subscript_sizing: builtins.str | None = ...,
        hint_label: builtins.str | None = ...,
        label: builtins.str | None = ...,
        on_change_handler_id: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["appearance", b"appearance", "color", b"color", "disabled", b"disabled", "end_date", b"end_date", "float_label", b"float_label", "hide_required_marker", b"hide_required_marker", "hint_label", b"hint_label", "label", b"label", "on_change_handler_id", b"on_change_handler_id", "placeholder_end_date", b"placeholder_end_date", "placeholder_start_date", b"placeholder_start_date", "readonly", b"readonly", "required", b"required", "start_date", b"start_date", "subscript_sizing", b"subscript_sizing"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["appearance", b"appearance", "color", b"color", "disabled", b"disabled", "end_date", b"end_date", "float_label", b"float_label", "hide_required_marker", b"hide_required_marker", "hint_label", b"hint_label", "label", b"label", "on_change_handler_id", b"on_change_handler_id", "placeholder_end_date", b"placeholder_end_date", "placeholder_start_date", b"placeholder_start_date", "readonly", b"readonly", "required", b"required", "start_date", b"start_date", "subscript_sizing", b"subscript_sizing"]) -> None: ...

global___DateRangePickerType = DateRangePickerType
