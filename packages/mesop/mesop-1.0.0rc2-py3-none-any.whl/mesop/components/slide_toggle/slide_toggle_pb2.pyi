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
class SlideToggleType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    LABEL_POSITION_FIELD_NUMBER: builtins.int
    REQUIRED_FIELD_NUMBER: builtins.int
    COLOR_FIELD_NUMBER: builtins.int
    DISABLED_FIELD_NUMBER: builtins.int
    DISABLE_RIPPLE_FIELD_NUMBER: builtins.int
    TAB_INDEX_FIELD_NUMBER: builtins.int
    CHECKED_FIELD_NUMBER: builtins.int
    HIDE_ICON_FIELD_NUMBER: builtins.int
    ON_SLIDE_TOGGLE_CHANGE_EVENT_HANDLER_ID_FIELD_NUMBER: builtins.int
    label_position: builtins.str
    required: builtins.bool
    color: builtins.str
    disabled: builtins.bool
    disable_ripple: builtins.bool
    tab_index: builtins.float
    checked: builtins.bool
    hide_icon: builtins.bool
    on_slide_toggle_change_event_handler_id: builtins.str
    def __init__(
        self,
        *,
        label_position: builtins.str | None = ...,
        required: builtins.bool | None = ...,
        color: builtins.str | None = ...,
        disabled: builtins.bool | None = ...,
        disable_ripple: builtins.bool | None = ...,
        tab_index: builtins.float | None = ...,
        checked: builtins.bool | None = ...,
        hide_icon: builtins.bool | None = ...,
        on_slide_toggle_change_event_handler_id: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["checked", b"checked", "color", b"color", "disable_ripple", b"disable_ripple", "disabled", b"disabled", "hide_icon", b"hide_icon", "label_position", b"label_position", "on_slide_toggle_change_event_handler_id", b"on_slide_toggle_change_event_handler_id", "required", b"required", "tab_index", b"tab_index"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["checked", b"checked", "color", b"color", "disable_ripple", b"disable_ripple", "disabled", b"disabled", "hide_icon", b"hide_icon", "label_position", b"label_position", "on_slide_toggle_change_event_handler_id", b"on_slide_toggle_change_event_handler_id", "required", b"required", "tab_index", b"tab_index"]) -> None: ...

global___SlideToggleType = SlideToggleType
