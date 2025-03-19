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
class InputType(google.protobuf.message.Message):
    """Next id: 27"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DISABLED_FIELD_NUMBER: builtins.int
    ID_FIELD_NUMBER: builtins.int
    PLACEHOLDER_FIELD_NUMBER: builtins.int
    REQUIRED_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    READONLY_FIELD_NUMBER: builtins.int
    HIDE_REQUIRED_MARKER_FIELD_NUMBER: builtins.int
    COLOR_FIELD_NUMBER: builtins.int
    FLOAT_LABEL_FIELD_NUMBER: builtins.int
    APPEARANCE_FIELD_NUMBER: builtins.int
    SUBSCRIPT_SIZING_FIELD_NUMBER: builtins.int
    HINT_LABEL_FIELD_NUMBER: builtins.int
    LABEL_FIELD_NUMBER: builtins.int
    ON_INPUT_HANDLER_ID_FIELD_NUMBER: builtins.int
    ON_ENTER_HANDLER_ID_FIELD_NUMBER: builtins.int
    ON_BLUR_HANDLER_ID_FIELD_NUMBER: builtins.int
    ROWS_FIELD_NUMBER: builtins.int
    AUTOSIZE_FIELD_NUMBER: builtins.int
    MIN_ROWS_FIELD_NUMBER: builtins.int
    MAX_ROWS_FIELD_NUMBER: builtins.int
    ON_SHORTCUT_HANDLER_FIELD_NUMBER: builtins.int
    IS_TEXTAREA_FIELD_NUMBER: builtins.int
    IS_NATIVE_TEXTAREA_FIELD_NUMBER: builtins.int
    disabled: builtins.bool
    id: builtins.str
    placeholder: builtins.str
    required: builtins.bool
    type: builtins.str
    value: builtins.str
    readonly: builtins.bool
    hide_required_marker: builtins.bool
    color: builtins.str
    float_label: builtins.str
    appearance: builtins.str
    subscript_sizing: builtins.str
    hint_label: builtins.str
    label: builtins.str
    on_input_handler_id: builtins.str
    on_enter_handler_id: builtins.str
    on_blur_handler_id: builtins.str
    rows: builtins.int
    """Used for textarea only."""
    autosize: builtins.bool
    min_rows: builtins.int
    max_rows: builtins.int
    is_textarea: builtins.bool
    """Not exposed as public API."""
    is_native_textarea: builtins.bool
    @property
    def on_shortcut_handler(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ShortcutHandler]: ...
    def __init__(
        self,
        *,
        disabled: builtins.bool | None = ...,
        id: builtins.str | None = ...,
        placeholder: builtins.str | None = ...,
        required: builtins.bool | None = ...,
        type: builtins.str | None = ...,
        value: builtins.str | None = ...,
        readonly: builtins.bool | None = ...,
        hide_required_marker: builtins.bool | None = ...,
        color: builtins.str | None = ...,
        float_label: builtins.str | None = ...,
        appearance: builtins.str | None = ...,
        subscript_sizing: builtins.str | None = ...,
        hint_label: builtins.str | None = ...,
        label: builtins.str | None = ...,
        on_input_handler_id: builtins.str | None = ...,
        on_enter_handler_id: builtins.str | None = ...,
        on_blur_handler_id: builtins.str | None = ...,
        rows: builtins.int | None = ...,
        autosize: builtins.bool | None = ...,
        min_rows: builtins.int | None = ...,
        max_rows: builtins.int | None = ...,
        on_shortcut_handler: collections.abc.Iterable[global___ShortcutHandler] | None = ...,
        is_textarea: builtins.bool | None = ...,
        is_native_textarea: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["appearance", b"appearance", "autosize", b"autosize", "color", b"color", "disabled", b"disabled", "float_label", b"float_label", "hide_required_marker", b"hide_required_marker", "hint_label", b"hint_label", "id", b"id", "is_native_textarea", b"is_native_textarea", "is_textarea", b"is_textarea", "label", b"label", "max_rows", b"max_rows", "min_rows", b"min_rows", "on_blur_handler_id", b"on_blur_handler_id", "on_enter_handler_id", b"on_enter_handler_id", "on_input_handler_id", b"on_input_handler_id", "placeholder", b"placeholder", "readonly", b"readonly", "required", b"required", "rows", b"rows", "subscript_sizing", b"subscript_sizing", "type", b"type", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["appearance", b"appearance", "autosize", b"autosize", "color", b"color", "disabled", b"disabled", "float_label", b"float_label", "hide_required_marker", b"hide_required_marker", "hint_label", b"hint_label", "id", b"id", "is_native_textarea", b"is_native_textarea", "is_textarea", b"is_textarea", "label", b"label", "max_rows", b"max_rows", "min_rows", b"min_rows", "on_blur_handler_id", b"on_blur_handler_id", "on_enter_handler_id", b"on_enter_handler_id", "on_input_handler_id", b"on_input_handler_id", "on_shortcut_handler", b"on_shortcut_handler", "placeholder", b"placeholder", "readonly", b"readonly", "required", b"required", "rows", b"rows", "subscript_sizing", b"subscript_sizing", "type", b"type", "value", b"value"]) -> None: ...

global___InputType = InputType

@typing.final
class ShortcutHandler(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SHORTCUT_FIELD_NUMBER: builtins.int
    HANDLER_ID_FIELD_NUMBER: builtins.int
    handler_id: builtins.str
    @property
    def shortcut(self) -> global___Shortcut: ...
    def __init__(
        self,
        *,
        shortcut: global___Shortcut | None = ...,
        handler_id: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["handler_id", b"handler_id", "shortcut", b"shortcut"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["handler_id", b"handler_id", "shortcut", b"shortcut"]) -> None: ...

global___ShortcutHandler = ShortcutHandler

@typing.final
class Shortcut(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    KEY_FIELD_NUMBER: builtins.int
    SHIFT_FIELD_NUMBER: builtins.int
    CTRL_FIELD_NUMBER: builtins.int
    ALT_FIELD_NUMBER: builtins.int
    META_FIELD_NUMBER: builtins.int
    key: builtins.str
    shift: builtins.bool
    ctrl: builtins.bool
    alt: builtins.bool
    meta: builtins.bool
    def __init__(
        self,
        *,
        key: builtins.str | None = ...,
        shift: builtins.bool | None = ...,
        ctrl: builtins.bool | None = ...,
        alt: builtins.bool | None = ...,
        meta: builtins.bool | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["alt", b"alt", "ctrl", b"ctrl", "key", b"key", "meta", b"meta", "shift", b"shift"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["alt", b"alt", "ctrl", b"ctrl", "key", b"key", "meta", b"meta", "shift", b"shift"]) -> None: ...

global___Shortcut = Shortcut
