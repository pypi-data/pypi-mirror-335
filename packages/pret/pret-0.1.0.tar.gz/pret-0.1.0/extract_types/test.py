
import sys
from typing import Any, Union
from pret.render import stub_component

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

props_mapping = {
 "mui_theme": "muiTheme",
 "class_name": "className",
 "icon_class_name_left": "iconClassNameLeft",
 "icon_class_name_right": "iconClassNameRight",
 "icon_element_left": "iconElementLeft",
 "icon_element_right": "iconElementRight",
 "icon_style_right": "iconStyleRight",
 "icon_style_left": "iconStyleLeft",
 "on_left_icon_button_click": "onLeftIconButtonClick",
 "on_right_icon_button_click": "onRightIconButtonClick",
 "on_title_click": "onTitleClick",
 "show_menu_icon_button": "showMenuIconButton",
 "title_style": "titleStyle",
 "z_depth": "zDepth",
 "anchor_origin": "anchorOrigin",
 "data_source": "dataSource",
 "data_source_config": "dataSourceConfig",
 "disable_focus_ripple": "disableFocusRipple",
 "error_style": "errorStyle",
 "error_text": "errorText",
 "floating_label_text": "floatingLabelText",
 "full_width": "fullWidth",
 "hint_text": "hintText",
 "list_style": "listStyle",
 "max_search_results": "maxSearchResults",
 "menu_close_delay": "menuCloseDelay",
 "menu_props": "menuProps",
 "menu_style": "menuStyle",
 "on_blur": "onBlur",
 "on_focus": "onFocus",
 "on_key_down": "onKeyDown",
 "on_new_request": "onNewRequest",
 "on_update_input": "onUpdateInput",
 "open_on_focus": "openOnFocus",
 "popover_props": "popoverProps",
 "search_text": "searchText",
 "target_origin": "targetOrigin",
 "text_field_style": "textFieldStyle",
 "default_value": "defaultValue",
 "floating_label_fixed": "floatingLabelFixed",
 "floating_label_focus_style": "floatingLabelFocusStyle",
 "floating_label_shrink_style": "floatingLabelShrinkStyle",
 "floating_label_style": "floatingLabelStyle",
 "hint_style": "hintStyle",
 "input_style": "inputStyle",
 "multi_line": "multiLine",
 "on_change": "onChange",
 "on_key_up": "onKeyUp",
 "on_key_press": "onKeyPress",
 "rows_max": "rowsMax",
 "textarea_style": "textareaStyle",
 "underline_disabled_style": "underlineDisabledStyle",
 "underline_focus_style": "underlineFocusStyle",
 "underline_show": "underlineShow",
 "underline_style": "underlineStyle",
 "auto_focus": "autoFocus",
 "auto_complete": "autoComplete",
 "background_color": "backgroundColor",
 "on_click": "onClick",
 "badge_content": "badgeContent",
 "badge_style": "badgeStyle",
 "after_element_type": "afterElementType",
 "after_style": "afterStyle",
 "before_element_type": "beforeElementType",
 "before_style": "beforeStyle",
 "element_type": "elementType",
 "container_element": "containerElement",
 "default_checked": "defaultChecked",
 "suppress_content_editable_warning": "suppressContentEditableWarning",
 "suppress_hydration_warning": "suppressHydrationWarning",
 "access_key": "accessKey",
 "content_editable": "contentEditable",
 "context_menu": "contextMenu",
 "spell_check": "spellCheck",
 "tab_index": "tabIndex",
 "radio_group": "radioGroup",
 "auto_capitalize": "autoCapitalize",
 "auto_correct": "autoCorrect",
 "auto_save": "autoSave",
 "item_prop": "itemProp",
 "item_scope": "itemScope",
 "item_type": "itemType",
 "item_id": "itemID",
 "item_ref": "itemRef",
 "input_mode": "inputMode",
 "is_": "is",
 "checked_link": "checkedLink",
 "value_link": "valueLink",
 "aria_activedescendant": "aria-activedescendant",
 "aria_atomic": "aria-atomic",
 "aria_autocomplete": "aria-autocomplete",
 "aria_busy": "aria-busy",
 "aria_checked": "aria-checked",
 "aria_colcount": "aria-colcount",
 "aria_colindex": "aria-colindex",
 "aria_colspan": "aria-colspan",
 "aria_controls": "aria-controls",
 "aria_current": "aria-current",
 "aria_describedby": "aria-describedby",
 "aria_details": "aria-details",
 "aria_disabled": "aria-disabled",
 "aria_dropeffect": "aria-dropeffect",
 "aria_errormessage": "aria-errormessage",
 "aria_expanded": "aria-expanded",
 "aria_flowto": "aria-flowto",
 "aria_grabbed": "aria-grabbed",
 "aria_haspopup": "aria-haspopup",
 "aria_hidden": "aria-hidden",
 "aria_invalid": "aria-invalid",
 "aria_keyshortcuts": "aria-keyshortcuts",
 "aria_label": "aria-label",
 "aria_labelledby": "aria-labelledby",
 "aria_level": "aria-level",
 "aria_live": "aria-live",
 "aria_modal": "aria-modal",
 "aria_multiline": "aria-multiline",
 "aria_multiselectable": "aria-multiselectable",
 "aria_orientation": "aria-orientation",
 "aria_owns": "aria-owns",
 "aria_placeholder": "aria-placeholder",
 "aria_posinset": "aria-posinset",
 "aria_pressed": "aria-pressed",
 "aria_readonly": "aria-readonly",
 "aria_relevant": "aria-relevant",
 "aria_required": "aria-required",
 "aria_roledescription": "aria-roledescription",
 "aria_rowcount": "aria-rowcount",
 "aria_rowindex": "aria-rowindex",
 "aria_rowspan": "aria-rowspan",
 "aria_selected": "aria-selected",
 "aria_setsize": "aria-setsize",
 "aria_sort": "aria-sort",
 "aria_valuemax": "aria-valuemax",
 "aria_valuemin": "aria-valuemin",
 "aria_valuenow": "aria-valuenow",
 "aria_valuetext": "aria-valuetext",
 "dangerously_set_inner_html": "dangerouslySetInnerHTML",
 "on_copy": "onCopy",
 "on_copy_capture": "onCopyCapture",
 "on_cut": "onCut",
 "on_cut_capture": "onCutCapture",
 "on_paste": "onPaste",
 "on_paste_capture": "onPasteCapture",
 "on_composition_end": "onCompositionEnd",
 "on_composition_end_capture": "onCompositionEndCapture",
 "on_composition_start": "onCompositionStart",
 "on_composition_start_capture": "onCompositionStartCapture",
 "on_composition_update": "onCompositionUpdate",
 "on_composition_update_capture": "onCompositionUpdateCapture",
 "on_focus_capture": "onFocusCapture",
 "on_blur_capture": "onBlurCapture",
 "on_change_capture": "onChangeCapture",
 "on_before_input": "onBeforeInput",
 "on_before_input_capture": "onBeforeInputCapture",
 "on_input": "onInput",
 "on_input_capture": "onInputCapture",
 "on_reset": "onReset",
 "on_reset_capture": "onResetCapture",
 "on_submit": "onSubmit",
 "on_submit_capture": "onSubmitCapture",
 "on_invalid": "onInvalid",
 "on_invalid_capture": "onInvalidCapture",
 "on_load": "onLoad",
 "on_load_capture": "onLoadCapture",
 "on_error": "onError",
 "on_error_capture": "onErrorCapture",
 "on_key_down_capture": "onKeyDownCapture",
 "on_key_press_capture": "onKeyPressCapture",
 "on_key_up_capture": "onKeyUpCapture",
 "on_abort": "onAbort",
 "on_abort_capture": "onAbortCapture",
 "on_can_play": "onCanPlay",
 "on_can_play_capture": "onCanPlayCapture",
 "on_can_play_through": "onCanPlayThrough",
 "on_can_play_through_capture": "onCanPlayThroughCapture",
 "on_duration_change": "onDurationChange",
 "on_duration_change_capture": "onDurationChangeCapture",
 "on_emptied": "onEmptied",
 "on_emptied_capture": "onEmptiedCapture",
 "on_encrypted": "onEncrypted",
 "on_encrypted_capture": "onEncryptedCapture",
 "on_ended": "onEnded",
 "on_ended_capture": "onEndedCapture",
 "on_loaded_data": "onLoadedData",
 "on_loaded_data_capture": "onLoadedDataCapture",
 "on_loaded_metadata": "onLoadedMetadata",
 "on_loaded_metadata_capture": "onLoadedMetadataCapture",
 "on_load_start": "onLoadStart",
 "on_load_start_capture": "onLoadStartCapture",
 "on_pause": "onPause",
 "on_pause_capture": "onPauseCapture",
 "on_play": "onPlay",
 "on_play_capture": "onPlayCapture",
 "on_playing": "onPlaying",
 "on_playing_capture": "onPlayingCapture",
 "on_progress": "onProgress",
 "on_progress_capture": "onProgressCapture",
 "on_rate_change": "onRateChange",
 "on_rate_change_capture": "onRateChangeCapture",
 "on_resize": "onResize",
 "on_resize_capture": "onResizeCapture",
 "on_seeked": "onSeeked",
 "on_seeked_capture": "onSeekedCapture",
 "on_seeking": "onSeeking",
 "on_seeking_capture": "onSeekingCapture",
 "on_stalled": "onStalled",
 "on_stalled_capture": "onStalledCapture",
 "on_suspend": "onSuspend",
 "on_suspend_capture": "onSuspendCapture",
 "on_time_update": "onTimeUpdate",
 "on_time_update_capture": "onTimeUpdateCapture",
 "on_volume_change": "onVolumeChange",
 "on_volume_change_capture": "onVolumeChangeCapture",
 "on_waiting": "onWaiting",
 "on_waiting_capture": "onWaitingCapture",
 "on_aux_click": "onAuxClick",
 "on_aux_click_capture": "onAuxClickCapture",
 "on_click_capture": "onClickCapture",
 "on_context_menu": "onContextMenu",
 "on_context_menu_capture": "onContextMenuCapture",
 "on_double_click": "onDoubleClick",
 "on_double_click_capture": "onDoubleClickCapture",
 "on_drag": "onDrag",
 "on_drag_capture": "onDragCapture",
 "on_drag_end": "onDragEnd",
 "on_drag_end_capture": "onDragEndCapture",
 "on_drag_enter": "onDragEnter",
 "on_drag_enter_capture": "onDragEnterCapture",
 "on_drag_exit": "onDragExit",
 "on_drag_exit_capture": "onDragExitCapture",
 "on_drag_leave": "onDragLeave",
 "on_drag_leave_capture": "onDragLeaveCapture",
 "on_drag_over": "onDragOver",
 "on_drag_over_capture": "onDragOverCapture",
 "on_drag_start": "onDragStart",
 "on_drag_start_capture": "onDragStartCapture",
 "on_drop": "onDrop",
 "on_drop_capture": "onDropCapture",
 "on_mouse_down": "onMouseDown",
 "on_mouse_down_capture": "onMouseDownCapture",
 "on_mouse_enter": "onMouseEnter",
 "on_mouse_leave": "onMouseLeave",
 "on_mouse_move": "onMouseMove",
 "on_mouse_move_capture": "onMouseMoveCapture",
 "on_mouse_out": "onMouseOut",
 "on_mouse_out_capture": "onMouseOutCapture",
 "on_mouse_over": "onMouseOver",
 "on_mouse_over_capture": "onMouseOverCapture",
 "on_mouse_up": "onMouseUp",
 "on_mouse_up_capture": "onMouseUpCapture",
 "on_select": "onSelect",
 "on_select_capture": "onSelectCapture",
 "on_touch_cancel": "onTouchCancel",
 "on_touch_cancel_capture": "onTouchCancelCapture",
 "on_touch_end": "onTouchEnd",
 "on_touch_end_capture": "onTouchEndCapture",
 "on_touch_move": "onTouchMove",
 "on_touch_move_capture": "onTouchMoveCapture",
 "on_touch_start": "onTouchStart",
 "on_touch_start_capture": "onTouchStartCapture",
 "on_pointer_down": "onPointerDown",
 "on_pointer_down_capture": "onPointerDownCapture",
 "on_pointer_move": "onPointerMove",
 "on_pointer_move_capture": "onPointerMoveCapture",
 "on_pointer_up": "onPointerUp",
 "on_pointer_up_capture": "onPointerUpCapture",
 "on_pointer_cancel": "onPointerCancel",
 "on_pointer_cancel_capture": "onPointerCancelCapture",
 "on_pointer_enter": "onPointerEnter",
 "on_pointer_enter_capture": "onPointerEnterCapture",
 "on_pointer_leave": "onPointerLeave",
 "on_pointer_leave_capture": "onPointerLeaveCapture",
 "on_pointer_over": "onPointerOver",
 "on_pointer_over_capture": "onPointerOverCapture",
 "on_pointer_out": "onPointerOut",
 "on_pointer_out_capture": "onPointerOutCapture",
 "on_got_pointer_capture": "onGotPointerCapture",
 "on_got_pointer_capture_capture": "onGotPointerCaptureCapture",
 "on_lost_pointer_capture": "onLostPointerCapture",
 "on_lost_pointer_capture_capture": "onLostPointerCaptureCapture",
 "on_scroll": "onScroll",
 "on_scroll_capture": "onScrollCapture",
 "on_wheel": "onWheel",
 "on_wheel_capture": "onWheelCapture",
 "on_animation_start": "onAnimationStart",
 "on_animation_start_capture": "onAnimationStartCapture",
 "on_animation_end": "onAnimationEnd",
 "on_animation_end_capture": "onAnimationEndCapture",
 "on_animation_iteration": "onAnimationIteration",
 "on_animation_iteration_capture": "onAnimationIterationCapture",
 "on_transition_end": "onTransitionEnd",
 "on_transition_end_capture": "onTransitionEndCapture",
 "center_ripple": "centerRipple",
 "disable_keyboard_focus": "disableKeyboardFocus",
 "disable_touch_ripple": "disableTouchRipple",
 "focus_ripple_color": "focusRippleColor",
 "focus_ripple_opacity": "focusRippleOpacity",
 "keyboard_focused": "keyboardFocused",
 "on_keyboard_focus": "onKeyboardFocus",
 "touch_ripple_color": "touchRippleColor",
 "touch_ripple_opacity": "touchRippleOpacity",
 "hover_color": "hoverColor",
 "label_position": "labelPosition",
 "label_style": "labelStyle",
 "link_button": "linkButton",
 "ripple_color": "rippleColor",
 "button_style": "buttonStyle",
 "disabled_background_color": "disabledBackgroundColor",
 "disabled_label_color": "disabledLabelColor",
 "label_color": "labelColor",
 "overlay_style": "overlayStyle",
 "ripple_style": "rippleStyle",
 "disabled_color": "disabledColor",
 "icon_class_name": "iconClassName",
 "icon_style": "iconStyle",
 "hovered_style": "hoveredStyle",
 "tooltip_position": "tooltipPosition",
 "tooltip_styles": "tooltipStyles",
 "selected_index": "selectedIndex",
 "act_as_expander": "actAsExpander",
 "container_style": "containerStyle",
 "initially_expanded": "initiallyExpanded",
 "on_expand_change": "onExpandChange",
 "show_expandable_button": "showExpandableButton",
 "on_expanding": "onExpanding",
 "subtitle_color": "subtitleColor",
 "subtitle_style": "subtitleStyle",
 "text_style": "textStyle",
 "title_color": "titleColor",
 "open_icon": "openIcon",
 "close_icon": "closeIcon",
 "media_style": "mediaStyle",
 "overlay_container_style": "overlayContainerStyle",
 "overlay_content_style": "overlayContentStyle",
 "on_request_delete": "onRequestDelete",
 "delete_icon_style": "deleteIconStyle",
 "date_time_format": "DateTimeFormat",
 "auto_ok": "autoOk",
 "cancel_label": "cancelLabel",
 "default_date": "defaultDate",
 "dialog_container_style": "dialogContainerStyle",
 "disable_year_selection": "disableYearSelection",
 "first_day_of_week": "firstDayOfWeek",
 "format_date": "formatDate",
 "max_date": "maxDate",
 "min_date": "minDate",
 "ok_label": "okLabel",
 "on_dismiss": "onDismiss",
 "on_show": "onShow",
 "should_disable_date": "shouldDisableDate",
 "hide_calendar_date": "hideCalendarDate",
 "open_to_year_selection": "openToYearSelection",
 "initial_date": "initialDate",
 "on_accept": "onAccept",
 "action_focus": "actionFocus",
 "actions_container_class_name": "actionsContainerClassName",
 "actions_container_style": "actionsContainerStyle",
 "auto_detect_window_height": "autoDetectWindowHeight",
 "auto_scroll_body_content": "autoScrollBodyContent",
 "body_class_name": "bodyClassName",
 "body_style": "bodyStyle",
 "content_class_name": "contentClassName",
 "content_style": "contentStyle",
 "on_request_close": "onRequestClose",
 "overlay_class_name": "overlayClassName",
 "paper_class_name": "paperClassName",
 "paper_props": "paperProps",
 "reposition_on_update": "repositionOnUpdate",
 "title_class_name": "titleClassName",
 "container_class_name": "containerClassName",
 "disable_swipe_to_open": "disableSwipeToOpen",
 "on_request_change": "onRequestChange",
 "open_secondary": "openSecondary",
 "swipe_area_width": "swipeAreaWidth",
 "cell_height": "cellHeight",
 "action_icon": "actionIcon",
 "action_position": "actionPosition",
 "title_background": "titleBackground",
 "title_position": "titlePosition",
 "view_box": "viewBox",
 "cross_origin": "crossOrigin",
 "accent_height": "accentHeight",
 "alignment_baseline": "alignmentBaseline",
 "allow_reorder": "allowReorder",
 "arabic_form": "arabicForm",
 "attribute_name": "attributeName",
 "attribute_type": "attributeType",
 "auto_reverse": "autoReverse",
 "base_frequency": "baseFrequency",
 "baseline_shift": "baselineShift",
 "base_profile": "baseProfile",
 "calc_mode": "calcMode",
 "cap_height": "capHeight",
 "clip_path": "clipPath",
 "clip_path_units": "clipPathUnits",
 "clip_rule": "clipRule",
 "color_interpolation": "colorInterpolation",
 "color_interpolation_filters": "colorInterpolationFilters",
 "color_profile": "colorProfile",
 "color_rendering": "colorRendering",
 "content_script_type": "contentScriptType",
 "content_style_type": "contentStyleType",
 "diffuse_constant": "diffuseConstant",
 "dominant_baseline": "dominantBaseline",
 "edge_mode": "edgeMode",
 "enable_background": "enableBackground",
 "external_resources_required": "externalResourcesRequired",
 "fill_opacity": "fillOpacity",
 "fill_rule": "fillRule",
 "filter_res": "filterRes",
 "filter_units": "filterUnits",
 "flood_color": "floodColor",
 "flood_opacity": "floodOpacity",
 "font_family": "fontFamily",
 "font_size": "fontSize",
 "font_size_adjust": "fontSizeAdjust",
 "font_stretch": "fontStretch",
 "font_style": "fontStyle",
 "font_variant": "fontVariant",
 "font_weight": "fontWeight",
 "from_": "from",
 "glyph_name": "glyphName",
 "glyph_orientation_horizontal": "glyphOrientationHorizontal",
 "glyph_orientation_vertical": "glyphOrientationVertical",
 "glyph_ref": "glyphRef",
 "gradient_transform": "gradientTransform",
 "gradient_units": "gradientUnits",
 "horiz_adv_x": "horizAdvX",
 "horiz_origin_x": "horizOriginX",
 "image_rendering": "imageRendering",
 "in_": "in",
 "kernel_matrix": "kernelMatrix",
 "kernel_unit_length": "kernelUnitLength",
 "key_points": "keyPoints",
 "key_splines": "keySplines",
 "key_times": "keyTimes",
 "length_adjust": "lengthAdjust",
 "letter_spacing": "letterSpacing",
 "lighting_color": "lightingColor",
 "limiting_cone_angle": "limitingConeAngle",
 "marker_end": "markerEnd",
 "marker_height": "markerHeight",
 "marker_mid": "markerMid",
 "marker_start": "markerStart",
 "marker_units": "markerUnits",
 "marker_width": "markerWidth",
 "mask_content_units": "maskContentUnits",
 "mask_units": "maskUnits",
 "num_octaves": "numOctaves",
 "overline_position": "overlinePosition",
 "overline_thickness": "overlineThickness",
 "paint_order": "paintOrder",
 "path_length": "pathLength",
 "pattern_content_units": "patternContentUnits",
 "pattern_transform": "patternTransform",
 "pattern_units": "patternUnits",
 "pointer_events": "pointerEvents",
 "points_at_x": "pointsAtX",
 "points_at_y": "pointsAtY",
 "points_at_z": "pointsAtZ",
 "preserve_alpha": "preserveAlpha",
 "preserve_aspect_ratio": "preserveAspectRatio",
 "primitive_units": "primitiveUnits",
 "ref_x": "refX",
 "ref_y": "refY",
 "rendering_intent": "renderingIntent",
 "repeat_count": "repeatCount",
 "repeat_dur": "repeatDur",
 "required_extensions": "requiredExtensions",
 "required_features": "requiredFeatures",
 "shape_rendering": "shapeRendering",
 "specular_constant": "specularConstant",
 "specular_exponent": "specularExponent",
 "spread_method": "spreadMethod",
 "start_offset": "startOffset",
 "std_deviation": "stdDeviation",
 "stitch_tiles": "stitchTiles",
 "stop_color": "stopColor",
 "stop_opacity": "stopOpacity",
 "strikethrough_position": "strikethroughPosition",
 "strikethrough_thickness": "strikethroughThickness",
 "stroke_dasharray": "strokeDasharray",
 "stroke_dashoffset": "strokeDashoffset",
 "stroke_linecap": "strokeLinecap",
 "stroke_linejoin": "strokeLinejoin",
 "stroke_miterlimit": "strokeMiterlimit",
 "stroke_opacity": "strokeOpacity",
 "stroke_width": "strokeWidth",
 "surface_scale": "surfaceScale",
 "system_language": "systemLanguage",
 "table_values": "tableValues",
 "target_x": "targetX",
 "target_y": "targetY",
 "text_anchor": "textAnchor",
 "text_decoration": "textDecoration",
 "text_length": "textLength",
 "text_rendering": "textRendering",
 "underline_position": "underlinePosition",
 "underline_thickness": "underlineThickness",
 "unicode_bidi": "unicodeBidi",
 "unicode_range": "unicodeRange",
 "units_per_em": "unitsPerEm",
 "v_alphabetic": "vAlphabetic",
 "vector_effect": "vectorEffect",
 "vert_adv_y": "vertAdvY",
 "vert_origin_x": "vertOriginX",
 "vert_origin_y": "vertOriginY",
 "v_hanging": "vHanging",
 "v_ideographic": "vIdeographic",
 "view_target": "viewTarget",
 "v_mathematical": "vMathematical",
 "word_spacing": "wordSpacing",
 "writing_mode": "writingMode",
 "x_channel_selector": "xChannelSelector",
 "x_height": "xHeight",
 "xlink_actuate": "xlinkActuate",
 "xlink_arcrole": "xlinkArcrole",
 "xlink_href": "xlinkHref",
 "xlink_role": "xlinkRole",
 "xlink_show": "xlinkShow",
 "xlink_title": "xlinkTitle",
 "xlink_type": "xlinkType",
 "xml_base": "xmlBase",
 "xml_lang": "xmlLang",
 "xmlns_xlink": "xmlnsXlink",
 "xml_space": "xmlSpace",
 "y_channel_selector": "yChannelSelector",
 "zoom_and_pan": "zoomAndPan",
 "auto_generate_nested_indicator": "autoGenerateNestedIndicator",
 "initially_open": "initiallyOpen",
 "inner_div_style": "innerDivStyle",
 "inset_children": "insetChildren",
 "left_avatar": "leftAvatar",
 "left_checkbox": "leftCheckbox",
 "left_icon": "leftIcon",
 "nested_items": "nestedItems",
 "nested_level": "nestedLevel",
 "nested_list_style": "nestedListStyle",
 "on_nested_list_toggle": "onNestedListToggle",
 "primary_text": "primaryText",
 "primary_toggles_nested_list": "primaryTogglesNestedList",
 "right_avatar": "rightAvatar",
 "right_icon": "rightIcon",
 "right_icon_button": "rightIconButton",
 "right_toggle": "rightToggle",
 "secondary_text": "secondaryText",
 "secondary_text_lines": "secondaryTextLines",
 "auto_width": "autoWidth",
 "disable_auto_focus": "disableAutoFocus",
 "initially_keyboard_focused": "initiallyKeyboardFocused",
 "max_height": "maxHeight",
 "on_esc_key_down": "onEscKeyDown",
 "on_item_click": "onItemClick",
 "selected_menu_item_style": "selectedMenuItemStyle",
 "focus_state": "focusState",
 "menu_items": "menuItems",
 "click_close_delay": "clickCloseDelay",
 "icon_button_element": "iconButtonElement",
 "use_layer_for_click_away": "useLayerForClickAway",
 "icon_button": "iconButton",
 "menu_item_style": "menuItemStyle",
 "on_close": "onClose",
 "open_immediately": "openImmediately",
 "selection_renderer": "selectionRenderer",
 "auto_lock_scrolling": "autoLockScrolling",
 "transition_enabled": "transitionEnabled",
 "anchor_el": "anchorEl",
 "auto_close_when_off_screen": "autoCloseWhenOffScreen",
 "can_auto_position": "canAutoPosition",
 "inner_style": "innerStyle",
 "loading_color": "loadingColor",
 "drop_down_menu_props": "dropDownMenuProps",
 "select_field_root": "selectFieldRoot",
 "on_drag_stop": "onDragStop",
 "slider_style": "sliderStyle",
 "default_switched": "defaultSwitched",
 "input_type": "inputType",
 "on_parent_should_update": "onParentShouldUpdate",
 "on_switch": "onSwitch",
 "switch_element": "switchElement",
 "thumb_style": "thumbStyle",
 "track_style": "trackStyle",
 "enter_key_hint": "enterKeyHint",
 "form_action": "formAction",
 "form_enc_type": "formEncType",
 "form_method": "formMethod",
 "form_no_validate": "formNoValidate",
 "form_target": "formTarget",
 "max_length": "maxLength",
 "min_length": "minLength",
 "read_only": "readOnly",
 "checked_icon": "checkedIcon",
 "on_check": "onCheck",
 "unchecked_icon": "uncheckedIcon",
 "default_selected": "defaultSelected",
 "value_selected": "valueSelected",
 "default_toggled": "defaultToggled",
 "element_style": "elementStyle",
 "on_toggle": "onToggle",
 "thumb_switched_style": "thumbSwitchedStyle",
 "track_switched_style": "trackSwitchedStyle",
 "auto_hide_duration": "autoHideDuration",
 "on_action_click": "onActionClick",
 "icon_container_style": "iconContainerStyle",
 "active_step": "activeStep",
 "all_rows_selected": "allRowsSelected",
 "fixed_footer": "fixedFooter",
 "fixed_header": "fixedHeader",
 "footer_style": "footerStyle",
 "header_style": "headerStyle",
 "multi_selectable": "multiSelectable",
 "on_cell_click": "onCellClick",
 "on_cell_hover": "onCellHover",
 "on_cell_hover_exit": "onCellHoverExit",
 "on_row_hover": "onRowHover",
 "on_row_hover_exit": "onRowHoverExit",
 "on_row_selection": "onRowSelection",
 "wrapper_style": "wrapperStyle",
 "display_border": "displayBorder",
 "on_row_click": "onRowClick",
 "row_number": "rowNumber",
 "column_number": "columnNumber",
 "on_hover": "onHover",
 "on_hover_exit": "onHoverExit",
 "col_span": "colSpan",
 "row_span": "rowSpan",
 "adjust_for_checkbox": "adjustForCheckbox",
 "display_select_all": "displaySelectAll",
 "enable_select_all": "enableSelectAll",
 "on_select_all": "onSelectAll",
 "select_all_selected": "selectAllSelected",
 "tooltip_style": "tooltipStyle",
 "deselect_on_clickaway": "deselectOnClickaway",
 "display_row_checkbox": "displayRowCheckbox",
 "pre_scan_rows": "preScanRows",
 "show_row_hover": "showRowHover",
 "striped_rows": "stripedRows",
 "content_container_class_name": "contentContainerClassName",
 "content_container_style": "contentContainerStyle",
 "initial_selected_index": "initialSelectedIndex",
 "ink_bar_style": "inkBarStyle",
 "tab_item_container_style": "tabItemContainerStyle",
 "tab_template": "tabTemplate",
 "tab_template_style": "tabTemplateStyle",
 "on_active": "onActive",
 "default_time": "defaultTime",
 "dialog_body_style": "dialogBodyStyle",
 "dialog_style": "dialogStyle",
 "minutes_step": "minutesStep",
 "no_gutter": "noGutter",
 "first_child": "firstChild",
 "last_child": "lastChild",
 "on_click_away": "onClickAway",
 "enter_delay": "enterDelay",
 "transition_delay": "transitionDelay",
 "transition_duration": "transitionDuration",
 "component_click_away": "componentClickAway",
 "child_style": "childStyle",
 "max_scale": "maxScale",
 "min_scale": "minScale",
 "get_leave_direction": "getLeaveDirection",
 "horizontal_position": "horizontalPosition",
 "vertical_position": "verticalPosition",
 "abort_on_scroll": "abortOnScroll"
}

@stub_component("ThemeWrapper", props_mapping)
def theme_wrapper(*children, theme: Any):
    ...

@stub_component("MuiThemeProvider", props_mapping)
def mui_theme_provider(*children, mui_theme: Any):
    ...

@stub_component("AppBar", props_mapping)
def app_bar(*children, class_name: str, icon_class_name_left: str, icon_class_name_right: str, icon_element_left: Any, icon_element_right: Any, icon_style_right: Any, icon_style_left: Any, on_left_icon_button_click: Any, on_right_icon_button_click: Any, on_title_click: Any, show_menu_icon_button: bool, style: Any, title: Union[str, int, float, Any, Literal[False, True]], title_style: Any, z_depth: Union[int, float]):
    ...

@stub_component("AppCanvas", props_mapping)
def app_canvas(*children, ):
    ...

@stub_component("AutoComplete", props_mapping)
def auto_complete(*children, anchor_origin: Any, animated: bool, animation: Any, data_source: Any, data_source_config: Any, disable_focus_ripple: bool, error_style: Any, error_text: Union[str, int, float, Any, Literal[False, True]], filter: Any, floating_label_text: Union[str, int, float, Any, Literal[False, True]], full_width: bool, hint_text: Union[str, int, float, Any, Literal[False, True]], list_style: Any, max_search_results: Union[int, float], menu_close_delay: Union[int, float], menu_props: Any, menu_style: Any, on_blur: Any, on_focus: Any, on_key_down: Any, on_new_request: Any, on_update_input: Any, open: bool, open_on_focus: bool, popover_props: Any, search_text: str, style: Any, target_origin: Any, text_field_style: Any, class_name: str, default_value: Any, disabled: bool, floating_label_fixed: bool, floating_label_focus_style: Any, floating_label_shrink_style: Any, floating_label_style: Any, hint_style: Any, id: str, input_style: Any, multi_line: bool, name: str, on_change: Any, on_key_up: Any, on_key_press: Any, required: bool, rows: Union[int, float], rows_max: Union[int, float], textarea_style: Any, type: str, underline_disabled_style: Any, underline_focus_style: Any, underline_show: bool, underline_style: Any, value: Any, auto_focus: bool, min: Union[int, float], max: Union[int, float], maxlength: str, minlength: str, step: Union[int, float], auto_complete: str, placeholder: str, title: str):
    ...

@stub_component("Avatar", props_mapping)
def avatar(*children, background_color: str, class_name: str, color: str, icon: Any, size: Union[int, float], src: str, style: Any, on_click: Any):
    ...

@stub_component("Badge", props_mapping)
def badge(*children, badge_content: Union[str, int, float, Any, Literal[False, True]], badge_style: Any, class_name: str, primary: bool, secondary: bool, style: Any):
    ...

@stub_component("BeforeAfterWrapper", props_mapping)
def before_after_wrapper(*children, after_element_type: str, after_style: Any, before_element_type: str, before_style: Any, element_type: str, style: Any):
    ...

@stub_component("EnhancedButton", props_mapping)
def enhanced_button(*children, container_element: Union[str, int, float, Any, Literal[False, True]], disabled: bool, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], style: Any, tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_keyboard_focus: Any, target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str):
    ...

@stub_component("FlatButton", props_mapping)
def flat_button(*children, background_color: str, class_name: str, disabled: bool, full_width: bool, hover_color: str, icon: Union[str, int, float, Any, Literal[False, True]], label: Union[str, int, float, Any, Literal[False, True]], label_position: Literal["before", "after"], label_style: Any, link_button: bool, on_keyboard_focus: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_touch_start: Any, primary: bool, ripple_color: str, secondary: bool, style: Any, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("RaisedButton", props_mapping)
def raised_button(*children, background_color: str, button_style: Any, class_name: str, disabled: bool, disabled_background_color: str, disabled_label_color: str, full_width: bool, icon: Union[str, int, float, Any, Literal[False, True]], label: Union[str, int, float, Any, Literal[False, True]], label_color: str, label_position: Literal["before", "after"], label_style: Any, link_button: bool, on_mouse_down: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_up: Any, on_touch_end: Any, on_touch_start: Any, overlay_style: Any, primary: bool, ripple_style: Any, secondary: bool, style: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_key_down: Any, on_key_up: Any, on_click: Any, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("FloatingActionButton", props_mapping)
def floating_action_button(*children, background_color: str, class_name: str, disabled: bool, disabled_color: str, icon_class_name: str, icon_style: Any, mini: bool, on_mouse_down: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_up: Any, on_touch_end: Any, on_touch_start: Any, secondary: bool, style: Any, z_depth: Union[int, float], default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_keyboard_focus: Any, target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("IconButton", props_mapping)
def icon_button(*children, class_name: str, disable_touch_ripple: bool, disabled: bool, hovered_style: Any, icon_class_name: str, icon_style: Any, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_out: Any, style: Any, tooltip: Union[str, int, float, Any, Literal[False, True]], tooltip_position: Literal["bottom-center", "bottom-left", "bottom-right", "top-center", "top-left", "top-right"], tooltip_styles: Any, touch: bool, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus_capture: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("BottomNavigation", props_mapping)
def bottom_navigation(*children, class_name: str, selected_index: Union[int, float], style: Any):
    ...

@stub_component("BottomNavigationItem", props_mapping)
def bottom_navigation_item(*children, class_name: str, icon: Union[str, int, float, Any, Literal[False, True]], label: Union[str, int, float, Any, Literal[False, True]], center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_key_down: Any, on_key_up: Any, on_click: Any, style: Any, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("Card", props_mapping)
def card(*children, class_name: str, act_as_expander: bool, container_style: Any, expandable: bool, expanded: bool, initially_expanded: bool, on_expand_change: Any, show_expandable_button: bool, style: Any):
    ...

@stub_component("CardActions", props_mapping)
def card_actions(*children, act_as_expander: bool, expandable: bool, show_expandable_button: bool, style: Any, class_name: str):
    ...

@stub_component("CardExpandable", props_mapping)
def card_expandable(*children, expanded: bool, on_expanding: Any, style: Any):
    ...

@stub_component("CardHeader", props_mapping)
def card_header(*children, act_as_expander: bool, avatar: Union[str, int, float, Any, Literal[False, True]], expandable: bool, show_expandable_button: bool, style: Any, subtitle: Union[str, int, float, Any, Literal[False, True]], subtitle_color: str, subtitle_style: Any, text_style: Any, title: Union[str, int, float, Any, Literal[False, True]], title_color: str, title_style: Any, class_name: str, open_icon: Union[str, int, float, Any, Literal[False, True]], close_icon: Union[str, int, float, Any, Literal[False, True]], icon_style: Any):
    ...

@stub_component("CardMedia", props_mapping)
def card_media(*children, act_as_expander: bool, expandable: bool, media_style: Any, overlay: Union[str, int, float, Any, Literal[False, True]], overlay_container_style: Any, overlay_content_style: Any, overlay_style: Any, style: Any):
    ...

@stub_component("CardText", props_mapping)
def card_text(*children, act_as_expander: bool, color: str, expandable: bool, style: Any, class_name: str):
    ...

@stub_component("CardTitle", props_mapping)
def card_title(*children, act_as_expander: bool, expandable: bool, show_expandable_button: bool, style: Any, subtitle: Union[str, int, float, Any, Literal[False, True]], subtitle_color: str, subtitle_style: Any, title: Union[str, int, float, Any, Literal[False, True]], title_color: str, title_style: Any):
    ...

@stub_component("Chip", props_mapping)
def chip(*children, background_color: str, class_name: str, container_element: Union[str, int, float, Any, Literal[False, True]], label_color: str, label_style: Any, on_click: Any, on_request_delete: Any, style: Any, delete_icon_style: Any):
    ...

@stub_component("DatePicker", props_mapping)
def date_picker(*children, date_time_format: Any, auto_ok: bool, cancel_label: Union[str, int, float, Any, Literal[False, True]], container: Literal["dialog", "inline"], default_date: Any, dialog_container_style: Any, disable_year_selection: bool, disabled: bool, first_day_of_week: Union[int, float], format_date: Any, locale: str, max_date: Any, min_date: Any, mode: Literal["portrait", "landscape"], ok_label: Union[str, int, float, Any, Literal[False, True]], on_change: Any, on_dismiss: Any, on_focus: Any, on_show: Any, on_click: Any, should_disable_date: Any, style: Any, text_field_style: Any, value: Any, class_name: str, default_value: str, error_style: Any, error_text: Union[str, int, float, Any, Literal[False, True]], floating_label_style: Any, floating_label_text: Union[str, int, float, Any, Literal[False, True]], full_width: bool, hide_calendar_date: bool, hint_style: Any, hint_text: Union[str, int, float, Any, Literal[False, True]], id: str, input_style: Any, on_blur: Any, on_key_down: Any, open_to_year_selection: bool, rows: Union[int, float], rows_max: Union[int, float], name: str, type: str, underline_disabled_style: Any, underline_focus_style: Any, underline_show: bool, underline_style: Any, utils: Any):
    ...

@stub_component("DatePickerDialog", props_mapping)
def date_picker_dialog(*children, date_time_format: Any, animation: Any, auto_ok: bool, cancel_label: Union[str, int, float, Any, Literal[False, True]], container: Literal["dialog", "inline"], disable_year_selection: bool, first_day_of_week: Union[int, float], initial_date: Any, locale: str, max_date: Any, min_date: Any, mode: Literal["portrait", "landscape"], ok_label: Union[str, int, float, Any, Literal[False, True]], on_accept: Any, on_dismiss: Any, on_show: Any, should_disable_date: Any, style: Any, utils: Any):
    ...

@stub_component("Dialog", props_mapping)
def dialog(*children, ref: Any, actions: Any, action_focus: str, actions_container_class_name: str, actions_container_style: Any, auto_detect_window_height: bool, auto_scroll_body_content: bool, body_class_name: str, body_style: Any, class_name: str, content_class_name: str, content_style: Any, modal: bool, on_request_close: Any, open: bool, overlay_class_name: str, overlay_style: Any, paper_class_name: str, paper_props: Any, reposition_on_update: bool, style: Any, title: Union[str, int, float, Any, Literal[False, True]], title_class_name: str, title_style: Any, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("Divider", props_mapping)
def divider(*children, class_name: str, inset: bool, style: Any):
    ...

@stub_component("Drawer", props_mapping)
def drawer(*children, class_name: str, container_class_name: str, container_style: Any, disable_swipe_to_open: bool, docked: bool, on_request_change: Any, open: bool, open_secondary: bool, overlay_class_name: str, overlay_style: Any, style: Any, swipe_area_width: Union[int, float], width: Any, z_depth: Union[int, float]):
    ...

@stub_component("GridList", props_mapping)
def grid_list(*children, cell_height: Union[int, float, Literal["auto"]], cols: Union[int, float], padding: Union[int, float], style: Any):
    ...

@stub_component("GridTile", props_mapping)
def grid_tile(*children, action_icon: Any, action_position: Literal["left", "right"], cols: Union[int, float], container_element: Any, rows: Union[int, float], style: Any, subtitle: Union[str, int, float, Any, Literal[False, True]], subtitle_style: Any, title: Union[str, int, float, Any, Literal[False, True]], title_background: str, title_position: Literal["top", "bottom"], title_style: Any, on_click: Any):
    ...

@stub_component("FontIcon", props_mapping)
def font_icon(*children, ref: Any, color: str, hover_color: str, on_mouse_enter: Any, on_mouse_leave: Any, style: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("SvgIcon", props_mapping)
def svg_icon(*children, ref: Any, color: str, hover_color: str, on_mouse_enter: Any, on_mouse_leave: Any, style: Any, view_box: str, class_name: str, height: Any, id: str, lang: str, max: Any, media: str, method: str, min: Any, name: str, target: str, type: str, width: Any, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], tab_index: Union[int, float], cross_origin: Literal["", "anonymous", "use-credentials"], accent_height: Any, accumulate: Literal["none", "sum"], additive: Literal["sum", "replace"], alignment_baseline: Literal["inherit", "auto", "baseline", "before-edge", "text-before-edge", "middle", "central", "after-edge", "text-after-edge", "ideographic", "alphabetic", "hanging", "mathematical"], allow_reorder: Literal["yes", "no"], alphabetic: Any, amplitude: Any, arabic_form: Literal["initial", "medial", "terminal", "isolated"], ascent: Any, attribute_name: str, attribute_type: str, auto_reverse: Literal[False, True, "true", "false"], azimuth: Any, base_frequency: Any, baseline_shift: Any, base_profile: Any, bbox: Any, begin: Any, bias: Any, by: Any, calc_mode: Any, cap_height: Any, clip: Any, clip_path: str, clip_path_units: Any, clip_rule: Any, color_interpolation: Any, color_interpolation_filters: Literal["inherit", "auto", "sRGB", "linearRGB"], color_profile: Any, color_rendering: Any, content_script_type: Any, content_style_type: Any, cursor: Any, cx: Any, cy: Any, d: str, decelerate: Any, descent: Any, diffuse_constant: Any, direction: Any, display: Any, divisor: Any, dominant_baseline: Any, dur: Any, dx: Any, dy: Any, edge_mode: Any, elevation: Any, enable_background: Any, end: Any, exponent: Any, external_resources_required: Literal[False, True, "true", "false"], fill: str, fill_opacity: Any, fill_rule: Literal["inherit", "nonzero", "evenodd"], filter: str, filter_res: Any, filter_units: Any, flood_color: Any, flood_opacity: Any, focusable: Literal[False, True, "true", "false", "auto"], font_family: str, font_size: Any, font_size_adjust: Any, font_stretch: Any, font_style: Any, font_variant: Any, font_weight: Any, format: Any, fr: Any, from_: Any, fx: Any, fy: Any, g1: Any, g2: Any, glyph_name: Any, glyph_orientation_horizontal: Any, glyph_orientation_vertical: Any, glyph_ref: Any, gradient_transform: str, gradient_units: str, hanging: Any, horiz_adv_x: Any, horiz_origin_x: Any, href: str, ideographic: Any, image_rendering: Any, in2: Any, in_: str, intercept: Any, k1: Any, k2: Any, k3: Any, k4: Any, k: Any, kernel_matrix: Any, kernel_unit_length: Any, kerning: Any, key_points: Any, key_splines: Any, key_times: Any, length_adjust: Any, letter_spacing: Any, lighting_color: Any, limiting_cone_angle: Any, local: Any, marker_end: str, marker_height: Any, marker_mid: str, marker_start: str, marker_units: Any, marker_width: Any, mask: str, mask_content_units: Any, mask_units: Any, mathematical: Any, mode: Any, num_octaves: Any, offset: Any, opacity: Any, operator: Any, order: Any, orient: Any, orientation: Any, origin: Any, overflow: Any, overline_position: Any, overline_thickness: Any, paint_order: Any, panose1: Any, path: str, path_length: Any, pattern_content_units: str, pattern_transform: Any, pattern_units: str, pointer_events: Any, points: str, points_at_x: Any, points_at_y: Any, points_at_z: Any, preserve_alpha: Literal[False, True, "true", "false"], preserve_aspect_ratio: str, primitive_units: Any, r: Any, radius: Any, ref_x: Any, ref_y: Any, rendering_intent: Any, repeat_count: Any, repeat_dur: Any, required_extensions: Any, required_features: Any, restart: Any, result: str, rotate: Any, rx: Any, ry: Any, scale: Any, seed: Any, shape_rendering: Any, slope: Any, spacing: Any, specular_constant: Any, specular_exponent: Any, speed: Any, spread_method: str, start_offset: Any, std_deviation: Any, stemh: Any, stemv: Any, stitch_tiles: Any, stop_color: str, stop_opacity: Any, strikethrough_position: Any, strikethrough_thickness: Any, string: Any, stroke: str, stroke_dasharray: Any, stroke_dashoffset: Any, stroke_linecap: Literal["inherit", "butt", "round", "square"], stroke_linejoin: Literal["inherit", "round", "miter", "bevel"], stroke_miterlimit: Any, stroke_opacity: Any, stroke_width: Any, surface_scale: Any, system_language: Any, table_values: Any, target_x: Any, target_y: Any, text_anchor: str, text_decoration: Any, text_length: Any, text_rendering: Any, to: Any, transform: str, u1: Any, u2: Any, underline_position: Any, underline_thickness: Any, unicode: Any, unicode_bidi: Any, unicode_range: Any, units_per_em: Any, v_alphabetic: Any, values: str, vector_effect: Any, version: str, vert_adv_y: Any, vert_origin_x: Any, vert_origin_y: Any, v_hanging: Any, v_ideographic: Any, view_target: Any, visibility: Any, v_mathematical: Any, widths: Any, word_spacing: Any, writing_mode: Any, x1: Any, x2: Any, x: Any, x_channel_selector: str, x_height: Any, xlink_actuate: str, xlink_arcrole: str, xlink_href: str, xlink_role: str, xlink_show: str, xlink_title: str, xlink_type: str, xml_base: str, xml_lang: str, xmlns: str, xmlns_xlink: str, xml_space: str, y1: Any, y2: Any, y: Any, y_channel_selector: str, z: Any, zoom_and_pan: str, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("List", props_mapping)
def list(*children, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], style: Any, tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("ListItem", props_mapping)
def list_item(*children, auto_generate_nested_indicator: bool, disable_keyboard_focus: bool, disabled: bool, hover_color: str, initially_open: bool, inner_div_style: Any, inset_children: bool, left_avatar: Any, left_checkbox: Any, left_icon: Any, nested_items: Any, nested_level: Union[int, float], nested_list_style: Any, on_keyboard_focus: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_nested_list_toggle: Any, on_touch_start: Any, on_click: Any, open: bool, primary_text: Union[str, int, float, Any, Literal[False, True]], primary_toggles_nested_list: bool, right_avatar: Any, right_icon: Any, right_icon_button: Any, right_toggle: Any, secondary_text: Union[str, int, float, Any, Literal[False, True]], secondary_text_lines: Union[int, float], style: Any, value: Any, container_element: Union[str, int, float, Any, Literal[False, True]], default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str):
    ...

@stub_component("Menu", props_mapping)
def menu(*children, auto_width: bool, desktop: bool, disable_auto_focus: bool, initially_keyboard_focused: bool, list_style: Any, max_height: Union[int, float], multiple: bool, on_change: Any, on_esc_key_down: Any, on_item_click: Any, on_key_down: Any, selected_menu_item_style: Any, style: Any, value: Any, value_link: Any, width: Any):
    ...

@stub_component("MenuItem", props_mapping)
def menu_item(*children, animation: Any, checked: bool, desktop: bool, disabled: bool, focus_state: str, inner_div_style: Any, inset_children: bool, label: Union[str, int, float, Any, Literal[False, True]], left_icon: Any, menu_items: Union[str, int, float, Any, Literal[False, True]], on_click: Any, primary_text: Union[str, int, float, Any, Literal[False, True]], right_icon: Any, secondary_text: Union[str, int, float, Any, Literal[False, True]], style: Any, container_element: Union[str, int, float, Any, Literal[False, True]], auto_generate_nested_indicator: bool, disable_keyboard_focus: bool, hover_color: str, initially_open: bool, left_avatar: Any, left_checkbox: Any, nested_items: Any, nested_level: Union[int, float], nested_list_style: Any, on_keyboard_focus: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_nested_list_toggle: Any, on_touch_start: Any, open: bool, primary_toggles_nested_list: bool, right_avatar: Any, right_icon_button: Any, right_toggle: Any, secondary_text_lines: Union[int, float], value: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any, center_ripple: bool, disable_focus_ripple: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str):
    ...

@stub_component("IconMenu", props_mapping)
def icon_menu(*children, anchor_origin: Any, animated: bool, animation: Any, class_name: str, click_close_delay: Union[int, float], icon_button_element: Any, icon_style: Any, menu_style: Any, on_click: Any, on_item_click: Any, on_keyboard_focus: Any, on_mouse_down: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_up: Any, on_request_change: Any, open: bool, target_origin: Any, use_layer_for_click_away: bool, auto_width: bool, desktop: bool, disable_auto_focus: bool, initially_keyboard_focused: bool, list_style: Any, max_height: Union[int, float], multiple: bool, on_change: Any, style: Any, value: Any):
    ...

@stub_component("DropDownMenu", props_mapping)
def drop_down_menu(*children, anchor_origin: Any, animated: bool, animation: Any, class_name: str, disabled: bool, icon_button: Union[str, int, float, Any, Literal[False, True]], icon_style: Any, label_style: Any, list_style: Any, max_height: Union[int, float], menu_item_style: Any, menu_style: Any, multiple: bool, on_change: Any, on_close: Any, open_immediately: bool, selected_menu_item_style: Any, selection_renderer: Any, style: Any, target_origin: Any, underline_style: Any, value: Any):
    ...

@stub_component("Overlay", props_mapping)
def overlay(*children, ref: Any, auto_lock_scrolling: bool, show: bool, transition_enabled: bool, on_click: Any):
    ...

@stub_component("Paper", props_mapping)
def paper(*children, ref: Any, circle: bool, rounded: bool, style: Any, transition_enabled: bool, z_depth: Union[int, float], width: Any, height: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("Popover", props_mapping)
def popover(*children, anchor_el: Any, anchor_origin: Any, animated: bool, animation: Any, auto_close_when_off_screen: bool, can_auto_position: bool, class_name: str, on_request_close: Any, open: bool, style: Any, target_origin: Any, use_layer_for_click_away: bool, z_depth: Union[int, float]):
    ...

@stub_component("PopoverAnimationVertical", props_mapping)
def popover_animation_vertical(*children, class_name: str, target_origin: Any, z_depth: Union[int, float], open: bool, style: Any):
    ...

@stub_component("PopoverAnimationDefault", props_mapping)
def popover_animation_default(*children, class_name: str, target_origin: Any, z_depth: Union[int, float], open: bool, style: Any):
    ...

@stub_component("CircularProgress", props_mapping)
def circular_progress(*children, color: str, inner_style: Any, max: Union[int, float], min: Union[int, float], mode: Literal["determinate", "indeterminate"], size: Union[int, float], style: Any, thickness: Union[int, float], value: Union[int, float]):
    ...

@stub_component("LinearProgress", props_mapping)
def linear_progress(*children, color: str, max: Union[int, float], min: Union[int, float], mode: Literal["determinate", "indeterminate"], style: Any, value: Union[int, float]):
    ...

@stub_component("RefreshIndicator", props_mapping)
def refresh_indicator(*children, color: str, left: Union[int, float], loading_color: str, percentage: Union[int, float], size: Union[int, float], status: Literal["ready", "loading", "hide"], style: Any, top: Union[int, float]):
    ...

@stub_component("SelectField", props_mapping)
def select_field(*children, auto_width: bool, disabled: bool, drop_down_menu_props: Any, error_style: Any, error_text: Union[str, int, float, Any, Literal[False, True]], floating_label_fixed: bool, floating_label_style: Any, floating_label_text: Union[str, int, float, Any, Literal[False, True]], full_width: bool, hint_style: Any, hint_text: Union[str, int, float, Any, Literal[False, True]], icon_style: Any, id: str, name: str, label_style: Any, multiple: bool, on_blur: Any, on_change: Any, on_focus: Any, select_field_root: Any, selection_renderer: Any, style: Any, underline_disabled_style: Any, underline_focus_style: Any, underline_style: Any, value: Any, class_name: str, max_height: Union[int, float], menu_style: Any, list_style: Any, menu_item_style: Any, selected_menu_item_style: Any, open_immediately: bool):
    ...

@stub_component("Slider", props_mapping)
def slider(*children, axis: Literal["x", "x-reverse", "y", "y-reverse"], default_value: Union[int, float], description: str, disable_focus_ripple: bool, disabled: bool, error: str, max: Union[int, float], min: Union[int, float], name: str, on_blur: Any, on_change: Any, on_drag_start: Any, on_drag_stop: Any, on_focus: Any, required: bool, slider_style: Any, step: Union[int, float], style: Any, value: Union[int, float]):
    ...

@stub_component("EnhancedSwitch", props_mapping)
def enhanced_switch(*children, class_name: str, default_switched: bool, disable_focus_ripple: bool, disable_touch_ripple: bool, disabled: bool, icon_style: Any, id: str, input_style: Any, input_type: str, label_position: str, label_style: Any, name: str, on_blur: Any, on_focus: Any, on_mouse_down: Any, on_mouse_leave: Any, on_mouse_up: Any, on_parent_should_update: Any, on_switch: Any, on_touch_end: Any, on_touch_start: Any, required: bool, ripple_color: str, ripple_style: Any, style: Any, switch_element: Any, switched: bool, thumb_style: Any, track_style: Any, value: str, ref: Any, label: Union[str, int, float, Any, Literal[False, True]], accept: str, alt: str, auto_complete: str, capture: Literal[False, True, "user", "environment"], checked: bool, cross_origin: Literal["", "anonymous", "use-credentials"], enter_key_hint: Literal["search", "enter", "done", "go", "next", "previous", "send"], form: str, form_action: str, form_enc_type: str, form_method: str, form_no_validate: bool, form_target: str, height: Any, list: str, max: Any, max_length: Union[int, float], min: Any, min_length: Union[int, float], multiple: bool, pattern: str, placeholder: str, read_only: bool, size: Union[int, float], src: str, step: Any, type: Union[Any, Literal["number", "button", "checkbox", "radio", "search", "text", "tel", "url", "email", "date", "time", "color", "datetime-local", "file", "hidden", "image", "month", "password", "range", "reset", "submit", "week"]], width: Any, on_change: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, lang: str, nonce: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus_capture: Any, on_blur_capture: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("Checkbox", props_mapping)
def checkbox(*children, checked: bool, checked_icon: Any, default_checked: bool, disabled: bool, icon_style: Any, label_position: Literal["left", "right"], label_style: Any, on_check: Any, style: Any, unchecked_icon: Any, value_link: Any, input_style: Any, ref: Any, label: Union[str, int, float, Any, Literal[False, True]], accept: str, alt: str, auto_complete: str, capture: Literal[False, True, "user", "environment"], cross_origin: Literal["", "anonymous", "use-credentials"], enter_key_hint: Literal["search", "enter", "done", "go", "next", "previous", "send"], form: str, form_action: str, form_enc_type: str, form_method: str, form_no_validate: bool, form_target: str, height: Any, list: str, max: Any, max_length: Union[int, float], min: Any, min_length: Union[int, float], multiple: bool, name: str, pattern: str, placeholder: str, read_only: bool, required: bool, size: Union[int, float], src: str, step: Any, type: Union[Any, Literal["number", "button", "checkbox", "radio", "search", "text", "tel", "url", "email", "date", "time", "color", "datetime-local", "file", "hidden", "image", "month", "password", "range", "reset", "submit", "week"]], value: Any, width: Any, on_change: Any, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("RadioButton", props_mapping)
def radio_button(*children, checked_icon: Any, disabled: bool, icon_style: Any, input_style: Any, label_style: Any, on_check: Any, style: Any, unchecked_icon: Any, value: Any, ref: Any, label: Union[str, int, float, Any, Literal[False, True]], accept: str, alt: str, auto_complete: str, capture: Literal[False, True, "user", "environment"], checked: bool, cross_origin: Literal["", "anonymous", "use-credentials"], enter_key_hint: Literal["search", "enter", "done", "go", "next", "previous", "send"], form: str, form_action: str, form_enc_type: str, form_method: str, form_no_validate: bool, form_target: str, height: Any, list: str, max: Any, max_length: Union[int, float], min: Any, min_length: Union[int, float], multiple: bool, name: str, pattern: str, placeholder: str, read_only: bool, required: bool, size: Union[int, float], src: str, step: Any, type: Union[Any, Literal["number", "button", "checkbox", "radio", "search", "text", "tel", "url", "email", "date", "time", "color", "datetime-local", "file", "hidden", "image", "month", "password", "range", "reset", "submit", "week"]], width: Any, on_change: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("RadioButtonGroup", props_mapping)
def radio_button_group(*children, class_name: str, default_selected: Any, label_position: Literal["left", "right"], name: str, on_change: Any, style: Any, value_selected: Any):
    ...

@stub_component("Toggle", props_mapping)
def toggle(*children, default_toggled: bool, disabled: bool, element_style: Any, icon_style: Any, input_style: Any, label: Union[str, int, float, Any, Literal[False, True]], label_position: Literal["left", "right"], label_style: Any, on_toggle: Any, ripple_style: Any, style: Any, thumb_style: Any, thumb_switched_style: Any, track_switched_style: Any, toggled: bool, track_style: Any, value_link: Any, ref: Any, accept: str, alt: str, auto_complete: str, capture: Literal[False, True, "user", "environment"], checked: bool, cross_origin: Literal["", "anonymous", "use-credentials"], enter_key_hint: Literal["search", "enter", "done", "go", "next", "previous", "send"], form: str, form_action: str, form_enc_type: str, form_method: str, form_no_validate: bool, form_target: str, height: Any, list: str, max: Any, max_length: Union[int, float], min: Any, min_length: Union[int, float], multiple: bool, name: str, pattern: str, placeholder: str, read_only: bool, required: bool, size: Union[int, float], src: str, step: Any, type: Union[Any, Literal["number", "button", "checkbox", "radio", "search", "text", "tel", "url", "email", "date", "time", "color", "datetime-local", "file", "hidden", "image", "month", "password", "range", "reset", "submit", "week"]], value: Any, width: Any, on_change: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("Snackbar", props_mapping)
def snackbar(*children, action: Union[str, int, float, Any, Literal[False, True]], auto_hide_duration: Union[int, float], body_style: Any, class_name: str, content_style: Any, message: Union[str, int, float, Any, Literal[False, True]], on_action_click: Any, on_request_close: Any, open: bool, style: Any):
    ...

@stub_component("Step", props_mapping)
def step(*children, active: bool, completed: bool, disabled: bool, style: Any):
    ...

@stub_component("StepButton", props_mapping)
def step_button(*children, active: bool, completed: bool, disabled: bool, icon: Union[str, int, float, Any, Literal[False, True]], on_mouse_enter: Any, on_mouse_leave: Any, on_touch_start: Any, style: Any, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_key_down: Any, on_key_up: Any, on_click: Any, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("StepContent", props_mapping)
def step_content(*children, active: bool, last: bool, style: Any):
    ...

@stub_component("StepLabel", props_mapping)
def step_label(*children, active: bool, completed: bool, disabled: bool, icon: Union[str, int, float, Any, Literal[False, True]], icon_container_style: Any, style: Any):
    ...

@stub_component("Stepper", props_mapping)
def stepper(*children, active_step: Union[int, float], linear: bool, orientation: Literal["horizontal", "vertical"], style: Any):
    ...

@stub_component("Subheader", props_mapping)
def subheader(*children, inset: bool, style: Any):
    ...

@stub_component("Table", props_mapping)
def table(*children, all_rows_selected: bool, body_style: Any, class_name: str, fixed_footer: bool, fixed_header: bool, footer_style: Any, header_style: Any, height: str, multi_selectable: bool, on_cell_click: Any, on_cell_hover: Any, on_cell_hover_exit: Any, on_row_hover: Any, on_row_hover_exit: Any, on_row_selection: Any, selectable: bool, style: Any, wrapper_style: Any):
    ...

@stub_component("TableRow", props_mapping)
def table_row(*children, class_name: str, display_border: bool, hoverable: bool, hovered: bool, on_cell_click: Any, on_cell_hover: Any, on_cell_hover_exit: Any, on_row_click: Any, on_row_hover: Any, on_row_hover_exit: Any, row_number: Union[int, float], selectable: bool, selected: bool, striped: bool, style: Any):
    ...

@stub_component("TableRowColumn", props_mapping)
def table_row_column(*children, class_name: str, column_number: Union[int, float], hoverable: bool, key: str, on_click: Any, on_hover: Any, on_hover_exit: Any, style: Any, col_span: Union[int, float], row_span: Union[int, float]):
    ...

@stub_component("TableHeader", props_mapping)
def table_header(*children, adjust_for_checkbox: bool, class_name: str, display_select_all: bool, enable_select_all: bool, on_select_all: Any, select_all_selected: bool, style: Any):
    ...

@stub_component("TableHeaderColumn", props_mapping)
def table_header_column(*children, class_name: str, column_number: Union[int, float], key: str, on_click: Any, style: Any, tooltip: str, tooltip_style: Any, col_span: Union[int, float], row_span: Union[int, float]):
    ...

@stub_component("TableBody", props_mapping)
def table_body(*children, all_rows_selected: bool, class_name: str, deselect_on_clickaway: bool, display_row_checkbox: bool, multi_selectable: bool, on_cell_click: Any, on_cell_hover: Any, on_cell_hover_exit: Any, on_row_hover: Any, on_row_hover_exit: Any, on_row_selection: Any, pre_scan_rows: bool, selectable: bool, show_row_hover: bool, striped_rows: bool, style: Any):
    ...

@stub_component("TableFooter", props_mapping)
def table_footer(*children, adjust_for_checkbox: bool, class_name: str, style: Any):
    ...

@stub_component("Tabs", props_mapping)
def tabs(*children, class_name: str, content_container_class_name: str, content_container_style: Any, initial_selected_index: Union[int, float], ink_bar_style: Any, on_change: Any, style: Any, tab_item_container_style: Any, tab_template: Any, tab_template_style: Any, value: Any):
    ...

@stub_component("Tab", props_mapping)
def tab(*children, button_style: Any, class_name: str, icon: Union[str, int, float, Any, Literal[False, True]], label: Union[str, int, float, Any, Literal[False, True]], on_active: Any, style: Any, value: Any, disabled: bool, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_key_down: Any, on_key_up: Any, on_click: Any, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("TextField", props_mapping)
def text_field(*children, class_name: str, default_value: Any, disabled: bool, error_style: Any, error_text: Union[str, int, float, Any, Literal[False, True]], floating_label_fixed: bool, floating_label_focus_style: Any, floating_label_shrink_style: Any, floating_label_style: Any, floating_label_text: Union[str, int, float, Any, Literal[False, True]], full_width: bool, hint_style: Any, hint_text: Union[str, int, float, Any, Literal[False, True]], id: str, input_style: Any, multi_line: bool, name: str, on_blur: Any, on_change: Any, on_focus: Any, on_key_down: Any, on_key_up: Any, on_key_press: Any, required: bool, rows: Union[int, float], rows_max: Union[int, float], style: Any, textarea_style: Any, type: str, underline_disabled_style: Any, underline_focus_style: Any, underline_show: bool, underline_style: Any, value: Any, auto_focus: bool, min: Union[int, float], max: Union[int, float], maxlength: str, minlength: str, step: Union[int, float], auto_complete: str, placeholder: str, title: str):
    ...

@stub_component("TimePicker", props_mapping)
def time_picker(*children, auto_ok: bool, cancel_label: Union[str, int, float, Any, Literal[False, True]], default_time: Any, dialog_body_style: Any, dialog_style: Any, disabled: bool, format: Literal["ampm", "24hr"], minutes_step: Union[int, float], ok_label: Union[str, int, float, Any, Literal[False, True]], on_change: Any, on_dismiss: Any, on_focus: Any, on_show: Any, on_click: Any, pedantic: bool, style: Any, text_field_style: Any, value: Any, class_name: str, default_value: Any, error_style: Any, error_text: Union[str, int, float, Any, Literal[False, True]], floating_label_fixed: bool, floating_label_focus_style: Any, floating_label_style: Any, floating_label_text: Union[str, int, float, Any, Literal[False, True]], full_width: bool, hint_style: Any, hint_text: Union[str, int, float, Any, Literal[False, True]], id: str, input_style: Any, multi_line: bool, name: str, on_blur: Any, on_key_down: Any, rows: Union[int, float], rows_max: Union[int, float], textarea_style: Any, type: str, underline_disabled_style: Any, underline_focus_style: Any, underline_show: bool, underline_style: Any):
    ...

@stub_component("Toolbar", props_mapping)
def toolbar(*children, class_name: str, no_gutter: bool, style: Any):
    ...

@stub_component("ToolbarGroup", props_mapping)
def toolbar_group(*children, class_name: str, first_child: bool, float: Literal["left", "right"], last_child: bool, style: Any):
    ...

@stub_component("ToolbarSeparator", props_mapping)
def toolbar_separator(*children, class_name: str, style: Any):
    ...

@stub_component("ToolbarTitle", props_mapping)
def toolbar_title(*children, ref: Any, class_name: str, style: Any, text: str, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, placeholder: str, slot: str, spell_check: Literal[False, True, "true", "false"], tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("AppCanvas", props_mapping)
def app_canvas(*children, ref: Any):
    ...

@stub_component("AutoLockScrolling", props_mapping)
def auto_lock_scrolling(*children, ref: Any, lock: bool):
    ...

@stub_component("BeforeAfterWrapper", props_mapping)
def before_after_wrapper(*children, ref: Any, after_element_type: str, after_style: Any, before_element_type: str, before_style: Any, element_type: str, style: Any):
    ...

@stub_component("CircleRipple", props_mapping)
def circle_ripple(*children, ref: Any, aborted: bool, color: str, opacity: Union[int, float], style: Any):
    ...

@stub_component("ClearFix", props_mapping)
def clear_fix(*children, ref: Any, style: Any):
    ...

@stub_component("ClickAwayListener", props_mapping)
def click_away_listener(*children, ref: Any, on_click_away: Any):
    ...

@stub_component("EnhancedButton", props_mapping)
def enhanced_button(*children, center_ripple: bool, disable_focus_ripple: bool, disable_keyboard_focus: bool, disable_touch_ripple: bool, focus_ripple_color: str, focus_ripple_opacity: Union[int, float], href: str, keyboard_focused: bool, on_blur: Any, on_focus: Any, on_keyboard_focus: Any, on_key_down: Any, on_key_up: Any, on_click: Any, style: Any, tab_index: Union[int, float], target: str, touch_ripple_color: str, touch_ripple_opacity: Union[int, float], type: str, container_element: Union[str, int, float, Any, Literal[False, True]]):
    ...

@stub_component("EnhancedSwitch", props_mapping)
def enhanced_switch(*children, ref: Any, label: Union[str, int, float, Any, Literal[False, True]], accept: str, alt: str, auto_complete: str, capture: Literal[False, True, "user", "environment"], checked: bool, cross_origin: Literal["", "anonymous", "use-credentials"], disabled: bool, enter_key_hint: Literal["search", "enter", "done", "go", "next", "previous", "send"], form: str, form_action: str, form_enc_type: str, form_method: str, form_no_validate: bool, form_target: str, height: Any, list: str, max: Any, max_length: Union[int, float], min: Any, min_length: Union[int, float], multiple: bool, name: str, pattern: str, placeholder: str, read_only: bool, required: bool, size: Union[int, float], src: str, step: Any, type: Union[Any, Literal["number", "button", "checkbox", "radio", "search", "text", "tel", "url", "email", "date", "time", "color", "datetime-local", "file", "hidden", "image", "month", "password", "range", "reset", "submit", "week"]], value: Any, width: Any, on_change: Any, default_checked: bool, default_value: Any, suppress_content_editable_warning: bool, suppress_hydration_warning: bool, access_key: str, auto_focus: bool, class_name: str, content_editable: Literal[False, True, "true", "false", "inherit"], context_menu: str, dir: str, draggable: Literal[False, True, "true", "false"], hidden: bool, id: str, lang: str, nonce: str, slot: str, spell_check: Literal[False, True, "true", "false"], style: Any, tab_index: Union[int, float], title: str, translate: Literal["yes", "no"], radio_group: str, role: Union[Any, Literal["alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"]], about: str, content: str, datatype: str, inlist: Any, prefix: str, property: str, rel: str, resource: str, rev: str, typeof: str, vocab: str, auto_capitalize: str, auto_correct: str, auto_save: str, color: str, item_prop: str, item_scope: bool, item_type: str, item_id: str, item_ref: str, results: Union[int, float], security: str, unselectable: Literal["on", "off"], input_mode: Literal["none", "search", "text", "tel", "url", "email", "numeric", "decimal"], is_: str, checked_link: Any, value_link: Any, aria_activedescendant: str, aria_atomic: Literal[False, True, "true", "false"], aria_autocomplete: Literal["list", "none", "inline", "both"], aria_busy: Literal[False, True, "true", "false"], aria_checked: Literal[False, True, "true", "false", "mixed"], aria_colcount: Union[int, float], aria_colindex: Union[int, float], aria_colspan: Union[int, float], aria_controls: str, aria_current: Literal[False, True, "true", "false", "page", "step", "location", "date", "time"], aria_describedby: str, aria_details: str, aria_disabled: Literal[False, True, "true", "false"], aria_dropeffect: Literal["link", "none", "copy", "execute", "move", "popup"], aria_errormessage: str, aria_expanded: Literal[False, True, "true", "false"], aria_flowto: str, aria_grabbed: Literal[False, True, "true", "false"], aria_haspopup: Literal[False, True, "true", "false", "dialog", "grid", "listbox", "menu", "tree"], aria_hidden: Literal[False, True, "true", "false"], aria_invalid: Literal[False, True, "true", "false", "grammar", "spelling"], aria_keyshortcuts: str, aria_label: str, aria_labelledby: str, aria_level: Union[int, float], aria_live: Literal["off", "assertive", "polite"], aria_modal: Literal[False, True, "true", "false"], aria_multiline: Literal[False, True, "true", "false"], aria_multiselectable: Literal[False, True, "true", "false"], aria_orientation: Literal["horizontal", "vertical"], aria_owns: str, aria_placeholder: str, aria_posinset: Union[int, float], aria_pressed: Literal[False, True, "true", "false", "mixed"], aria_readonly: Literal[False, True, "true", "false"], aria_relevant: Literal["text", "additions", "additions removals", "additions text", "all", "removals", "removals additions", "removals text", "text additions", "text removals"], aria_required: Literal[False, True, "true", "false"], aria_roledescription: str, aria_rowcount: Union[int, float], aria_rowindex: Union[int, float], aria_rowspan: Union[int, float], aria_selected: Literal[False, True, "true", "false"], aria_setsize: Union[int, float], aria_sort: Literal["none", "ascending", "descending", "other"], aria_valuemax: Union[int, float], aria_valuemin: Union[int, float], aria_valuenow: Union[int, float], aria_valuetext: str, dangerously_set_inner_html: Any, on_copy: Any, on_copy_capture: Any, on_cut: Any, on_cut_capture: Any, on_paste: Any, on_paste_capture: Any, on_composition_end: Any, on_composition_end_capture: Any, on_composition_start: Any, on_composition_start_capture: Any, on_composition_update: Any, on_composition_update_capture: Any, on_focus: Any, on_focus_capture: Any, on_blur: Any, on_blur_capture: Any, on_change_capture: Any, on_before_input: Any, on_before_input_capture: Any, on_input: Any, on_input_capture: Any, on_reset: Any, on_reset_capture: Any, on_submit: Any, on_submit_capture: Any, on_invalid: Any, on_invalid_capture: Any, on_load: Any, on_load_capture: Any, on_error: Any, on_error_capture: Any, on_key_down: Any, on_key_down_capture: Any, on_key_press: Any, on_key_press_capture: Any, on_key_up: Any, on_key_up_capture: Any, on_abort: Any, on_abort_capture: Any, on_can_play: Any, on_can_play_capture: Any, on_can_play_through: Any, on_can_play_through_capture: Any, on_duration_change: Any, on_duration_change_capture: Any, on_emptied: Any, on_emptied_capture: Any, on_encrypted: Any, on_encrypted_capture: Any, on_ended: Any, on_ended_capture: Any, on_loaded_data: Any, on_loaded_data_capture: Any, on_loaded_metadata: Any, on_loaded_metadata_capture: Any, on_load_start: Any, on_load_start_capture: Any, on_pause: Any, on_pause_capture: Any, on_play: Any, on_play_capture: Any, on_playing: Any, on_playing_capture: Any, on_progress: Any, on_progress_capture: Any, on_rate_change: Any, on_rate_change_capture: Any, on_resize: Any, on_resize_capture: Any, on_seeked: Any, on_seeked_capture: Any, on_seeking: Any, on_seeking_capture: Any, on_stalled: Any, on_stalled_capture: Any, on_suspend: Any, on_suspend_capture: Any, on_time_update: Any, on_time_update_capture: Any, on_volume_change: Any, on_volume_change_capture: Any, on_waiting: Any, on_waiting_capture: Any, on_aux_click: Any, on_aux_click_capture: Any, on_click: Any, on_click_capture: Any, on_context_menu: Any, on_context_menu_capture: Any, on_double_click: Any, on_double_click_capture: Any, on_drag: Any, on_drag_capture: Any, on_drag_end: Any, on_drag_end_capture: Any, on_drag_enter: Any, on_drag_enter_capture: Any, on_drag_exit: Any, on_drag_exit_capture: Any, on_drag_leave: Any, on_drag_leave_capture: Any, on_drag_over: Any, on_drag_over_capture: Any, on_drag_start: Any, on_drag_start_capture: Any, on_drop: Any, on_drop_capture: Any, on_mouse_down: Any, on_mouse_down_capture: Any, on_mouse_enter: Any, on_mouse_leave: Any, on_mouse_move: Any, on_mouse_move_capture: Any, on_mouse_out: Any, on_mouse_out_capture: Any, on_mouse_over: Any, on_mouse_over_capture: Any, on_mouse_up: Any, on_mouse_up_capture: Any, on_select: Any, on_select_capture: Any, on_touch_cancel: Any, on_touch_cancel_capture: Any, on_touch_end: Any, on_touch_end_capture: Any, on_touch_move: Any, on_touch_move_capture: Any, on_touch_start: Any, on_touch_start_capture: Any, on_pointer_down: Any, on_pointer_down_capture: Any, on_pointer_move: Any, on_pointer_move_capture: Any, on_pointer_up: Any, on_pointer_up_capture: Any, on_pointer_cancel: Any, on_pointer_cancel_capture: Any, on_pointer_enter: Any, on_pointer_enter_capture: Any, on_pointer_leave: Any, on_pointer_leave_capture: Any, on_pointer_over: Any, on_pointer_over_capture: Any, on_pointer_out: Any, on_pointer_out_capture: Any, on_got_pointer_capture: Any, on_got_pointer_capture_capture: Any, on_lost_pointer_capture: Any, on_lost_pointer_capture_capture: Any, on_scroll: Any, on_scroll_capture: Any, on_wheel: Any, on_wheel_capture: Any, on_animation_start: Any, on_animation_start_capture: Any, on_animation_end: Any, on_animation_end_capture: Any, on_animation_iteration: Any, on_animation_iteration_capture: Any, on_transition_end: Any, on_transition_end_capture: Any):
    ...

@stub_component("ExpandTransition", props_mapping)
def expand_transition(*children, ref: Any, enter_delay: Union[int, float], loading: bool, open: bool, style: Any, transition_delay: Union[int, float], transition_duration: Union[int, float]):
    ...

@stub_component("ExpandTransitionChild", props_mapping)
def expand_transition_child(*children, ref: Any, enter_delay: Union[int, float], style: Any, transition_delay: Union[int, float], transition_duration: Union[int, float]):
    ...

@stub_component("FocusRipple", props_mapping)
def focus_ripple(*children, ref: Any, color: str, inner_style: Any, opacity: Union[int, float], show: bool, style: Any):
    ...

@stub_component("Overlay", props_mapping)
def overlay(*children, ref: Any, auto_lock_scrolling: bool, show: bool, style: Any, transition_enabled: bool, on_click: Any):
    ...

@stub_component("RenderToLayer", props_mapping)
def render_to_layer(*children, ref: Any, component_click_away: Any, open: bool, render: Any, use_layer_for_click_away: bool):
    ...

@stub_component("ScaleIn", props_mapping)
def scale_in(*children, ref: Any, child_style: Any, enter_delay: Union[int, float], max_scale: Union[int, float], min_scale: Union[int, float]):
    ...

@stub_component("ScaleInChild", props_mapping)
def scale_in_child(*children, ref: Any, enter_delay: Union[int, float], max_scale: Union[int, float], min_scale: Union[int, float], style: Any):
    ...

@stub_component("SlideIn", props_mapping)
def slide_in(*children, ref: Any, child_style: Any, direction: Literal["left", "right", "up", "down"], enter_delay: Union[int, float], style: Any):
    ...

@stub_component("SlideInChild", props_mapping)
def slide_in_child(*children, ref: Any, direction: str, enter_delay: Union[int, float], get_leave_direction: Any, style: Any):
    ...

@stub_component("Tooltip", props_mapping)
def tooltip(*children, ref: Any, class_name: str, horizontal_position: Literal["left", "right", "center"], label: Any, show: bool, style: Any, touch: bool, vertical_position: Literal["top", "bottom", "center"]):
    ...

@stub_component("TouchRipple", props_mapping)
def touch_ripple(*children, ref: Any, abort_on_scroll: bool, center_ripple: bool, color: str, opacity: Union[int, float], style: Any):
    ...
