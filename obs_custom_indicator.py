#! /usr/bin/python -I -S
"""OBS Custom Indicator:
    Display on-screen indicators for recording and live streaming status.

    Copyright (c) 2025 eka.

    OBS Custom Indicator is released under the MIT License.
"""


from datetime import datetime
from logging import basicConfig, getLogger, DEBUG, INFO
import obspython as obs
import threading
from tkinter import messagebox

from bin.indicator import Color, Duration, Indicator, Size
from bin.translation import install_language, languages


# ==============================
def script_description() -> str:
    return (
        'Display on-screen indicators for recording and live streaming status.'
    )


# ==============================
class Controller:
    develop_mode = False
    indicator = None


# ==============================
class Status:
    record_started = False
    stream_started = False
    reloaded = False


# ==============================
def script_defaults(settings):
    """Default settings."""
    obs.obs_data_set_default_string(settings, 'Language', 'en-US')
    obs.obs_data_set_default_string(settings, 'Size', 'Medium')
    obs.obs_data_set_default_string(settings, 'Position', 'NW')
    obs.obs_data_set_default_string(settings, 'RecordingColor', 'Red')
    obs.obs_data_set_default_string(settings, 'StreamingColor', 'Green')
    obs.obs_data_set_default_string(settings, 'Duration', 'Always')


# ==============================
def properties(settings) -> dict:
    return {
        'Size': obs.obs_data_get_string(settings, 'Size'),
        'Position': obs.obs_data_get_string(settings, 'Position'),
        'RecordingColor': obs.obs_data_get_string(settings, 'RecordingColor'),
        'StreamingColor': obs.obs_data_get_string(settings, 'StreamingColor'),
        'Duration': obs.obs_data_get_string(settings, 'Duration'),
    }


# ==============================
def script_properties():
    """Defines and displays properties in the UI."""
    props = obs.obs_properties_create()
    _list_format = (obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    _oid = obs.obs_properties_add_list(
        props, 'Language', _('Language'), *_list_format,
    )

    for i in languages():
        obs.obs_property_list_add_string(_oid, *i)

    _oid = obs.obs_properties_add_list(props, 'Size', _('Size'), *_list_format)

    for i in [[_(k.name.capitalize()), k.name] for k in Size]:
        obs.obs_property_list_add_string(_oid, *i)

    _oid = obs.obs_properties_add_list(
        props, 'Position', _('Position'), *_list_format,
    )

    for i in [[_(k), k] for k in ('NW', 'NE', 'SW', 'SE')]:
        obs.obs_property_list_add_string(_oid, *i)

    _oid = obs.obs_properties_add_list(
        props, 'RecordingColor', _('RecordingColor'), *_list_format,
    )
    _color_options = [[_(i.name.capitalize()), i.name] for i in Color]

    for i in _color_options:
        obs.obs_property_list_add_string(_oid, *i)

    _oid = obs.obs_properties_add_list(
        props, 'StreamingColor', _('StreamingColor'), *_list_format,
    )

    for i in _color_options:
        obs.obs_property_list_add_string(_oid, *i)

    _oid = obs.obs_properties_add_list(
        props, 'Duration', _('Duration'), *_list_format,
    )

    for i in [[_(k.name.capitalize()), k.name] for k in Duration]:
        obs.obs_property_list_add_string(_oid, *i)

    return props


# ==============================
def script_update(settings):
    """Triggered on startup and when settings are modified."""
    if _indicator := Controller.indicator:
        getLogger(__name__).debug(f'Update indicator settings.')
        install_language(obs.obs_data_get_string(settings, 'Language'))
        _indicator.load_settings(properties(settings))
        _indicator.update_requested = True


# ==============================
def script_load(settings):
    """Triggered on startup, default button press, or reload button press."""
    if (_len := len(threading.enumerate())) > 1:
        getLogger(__name__).debug(f'Script reloaded. (Threads: {_len})')
        messagebox.showinfo(
            'OBS Custom Indicator', _('Script reloaded. Please restart OBS.'),
        )
        return

    start_logging()
    _logger = getLogger(__name__)
    _logger.debug(f'Script loading.')
    install_language(obs.obs_data_get_string(settings, 'Language'))
    obs.obs_frontend_add_event_callback(on_event)

    _thread = threading.Thread(
        target=create_indicator, args=(settings,), daemon=True,
    )
    _thread.start()
    _logger.debug('Script loaded successfully.')


# ==============================
def create_indicator(settings):
    _logger = getLogger(__name__)
    _logger.debug(f'Creating indicator.')

    try:
        Controller.indicator = Indicator(properties(settings), Status)
    except Exception as err:
        _logger.debug(f'{err.__class__.__name__}: {err}')
    else:
        _logger.debug(f'Indicator created successfully.')
        Controller.indicator.mainloop()


# ==============================
def script_unload():
    """Triggered on shutdown, default button press, or reload button press."""
    getLogger(__name__).debug(f'Script unloaded.')
    Status.reloaded = True


# ==============================
def on_event(event):
    _logger = getLogger(__name__)

    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        _logger.debug(f'Recording started.')
        Status.record_started = True
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        _logger.debug(f'Recording stopped.')
        Status.record_started = False
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_PAUSED:
        _logger.debug(f'Recording paused.')
        Status.record_started = False
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_UNPAUSED:
        _logger.debug(f'Recording unpaused.')
        Status.record_started = True
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        _logger.debug(f'Streaming started.')
        Status.stream_started = True
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        _logger.debug(f'Streaming stopped.')
        Status.stream_started = False


# ==============================
def start_logging():
    if Controller.develop_mode:
        basicConfig(
            level=DEBUG,
            format='{levelname:<8}: <{name}, line {lineno}>  {message}',
            style='{',
        )
    else:
        basicConfig(level=INFO, format='{message}', style='{')

    getLogger(__name__).debug(f'Start logging. ({datetime.now()})')
