#! /usr/bin/python -I -S
"""The indicator module manages the appearance of indicators."""


from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto, unique
from logging import getLogger
from pathlib import Path
import tkinter as tk


# ==============================
class Icon:
    RECORD_STARTED_GREEN = 'record_started_green.png'
    RECORD_STARTED_RED = 'record_started_red.png'
    RECORD_STOPPED = 'record_stopped.png'
    STREAM_STARTED_GREEN = 'stream_started_green.png'
    STREAM_STARTED_RED = 'stream_started_red.png'
    STREAM_STOPPED = 'stream_stopped.png'


# ==============================
@unique
class Color(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()

    # ------------------------------
    @classmethod
    def get(cls, name: str, /):
        if _member := cls.__members__.get(name.upper()):
            return _member.value
        else:
            return cls.RED.value


# ==============================
@unique
class Size(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()

    # ------------------------------
    @classmethod
    def get(cls, name: str, /):
        if _member := cls.__members__.get(name.upper()):
            return _member.value
        else:
            return cls.MEDIUM.value


# ==============================
@unique
class Duration(IntEnum):
    ALWAYS = -1
    SEC3 = 3
    SEC1 = 1

    # ------------------------------
    @classmethod
    def get(cls, name: str, /):
        if _member := cls.__members__.get(name.upper()):
            return _member.value
        else:
            return cls.ALWAYS.value


# ==============================
class Indicator(tk.Tk):
    """Always-on-top indicator on the screen.

        Args:
            current_settings: A dictionary containing the current settings.
            status: A class to dynamically maintain the state of OBS.

        Variables:
            offset: Offset distance from the screen edges in pixels.
            size: Indicator size.
            position: On-screen position (NW/NE/SW/SE).
            record_color: Recording indicator color.
            stream_color: Streaming indicator color.
            duration: Duration of display.
            update_requested: Update display settings during monitoring
                                (True/False).
    """
    def __init__(self, /, current_settings: dict, status):
        super().__init__(None)
        self.load_settings(current_settings)
        self.status = status
        self.last_status = []

        _bg_color = '#888'
        self.configure(background=_bg_color)
        self.attributes('-transparentcolor', _bg_color)
        self.wm_attributes('-topmost', True)
        self.update_idletasks()
        self.overrideredirect(True)

        self.record_label = tk.Label(self, background=_bg_color)
        self.stream_label = tk.Label(self, background=_bg_color)
        self.record_label.grid(column=0, row=0)
        self.stream_label.grid(column=1, row=0)

        self.timer = timedelta()
        self.updated_time = datetime.now()
        self.skip_update = False
        self.update_requested = True
        self.on_update()

    # ------------------------------
    def load_settings(self, /, current_settings: dict):
        getLogger(__name__).debug(f'Indicator: {current_settings=}')
        self.offset = 8
        self.size = Size.get(current_settings['Size'])
        self.position = current_settings['Position']
        self.record_color = Color.get(current_settings['RecordingColor'])
        self.stream_color = Color.get(current_settings['StreamingColor'])
        self.duration = Duration.get(current_settings['Duration'])

    # ------------------------------
    def on_update(self, /, delay_ms=125):
        if self.status.reloaded:
            getLogger(__name__).debug(f'Stop indicator.')
            self.withdraw()
            return

        if self.update_requested:
            getLogger(__name__).debug(f'Update requested.')
            self.update_requested = False
            self.last_status = []
            self.update_settings()

        if self.skip_update:
#            getLogger(__name__).debug(f'Skip update.')
            self.after(delay_ms * 4, self.on_update)
            return

        if (self.timer.seconds
                and self.updated_time + self.timer < datetime.now()):
            getLogger(__name__).debug(f'Hide via timer.')
            self.timer = timedelta()
            self.withdraw()
            self.after(delay_ms, self.on_update)
            return

        _current = [self.status.record_started, self.status.stream_started]

        if _current == self.last_status:
            self.after(delay_ms, self.on_update)
            return
        else:
            getLogger(__name__).debug(f'Different status. {_current}')
            self.last_status = _current

        if self.status.record_started:
            self.record_label.configure(image=self.record_started_icon)
        else:
            self.record_label.configure(image=self.record_stopped_icon)

        if self.status.stream_started:
            self.stream_label.configure(image=self.stream_started_icon)
        else:
            self.stream_label.configure(image=self.stream_stopped_icon)

        if self.state() != 'normal':
            self.deiconify()

        self.timer = timedelta(seconds=max(0, self.duration))
        self.updated_time = datetime.now()
        self.after(delay_ms, self.on_update)

    # ------------------------------
    def update_settings(self):
        self.set_icon_data()
        self.set_geometry()

        _columns = bool(self.record_color) + bool(self.stream_color)
        self.skip_update = (_columns == 0 or self.duration == 0)

        if self.skip_update:
            self.withdraw()
        else:
            self.deiconify()

    # ------------------------------
    def set_icon_data(self):
        _logger = getLogger(__name__)
        _logger.debug(f'Set icon data.')
        _path = Path(__file__).parent.joinpath('image').joinpath

        if self.record_color == Color.GREEN.value:
            self.record_started_icon = tk.PhotoImage(
                file=_path(Icon.RECORD_STARTED_GREEN),
            )
        else:
            self.record_started_icon = tk.PhotoImage(
                file=_path(Icon.RECORD_STARTED_RED),
            )

        self.record_stopped_icon = tk.PhotoImage(
            file=_path(Icon.RECORD_STOPPED),
        )

        if self.stream_color == Color.GREEN.value:
            self.stream_started_icon = tk.PhotoImage(
                file=_path(Icon.STREAM_STARTED_GREEN),
            )
        else:
            self.stream_started_icon = tk.PhotoImage(
                file=_path(Icon.STREAM_STARTED_RED),
            )

        self.stream_stopped_icon = tk.PhotoImage(
            file=_path(Icon.STREAM_STOPPED),
        )

        if self.size == Size.SMALL.value:
            _factor = 4
        elif self.size == Size.MEDIUM.value:
            _factor = 2
        else:
            _logger.debug(f'Using icon at original size.')
            return

        _logger.debug(f'Scaling down icon: {_factor=}')
        self.record_started_icon = self.record_started_icon.subsample(_factor)
        self.record_stopped_icon = self.record_stopped_icon.subsample(_factor)
        self.stream_started_icon = self.stream_started_icon.subsample(_factor)
        self.stream_stopped_icon = self.stream_stopped_icon.subsample(_factor)

    # ------------------------------
    def set_geometry(self):
        _logger = getLogger(__name__)
        _logger.debug(f'Set geometry: {self.position=}')
        _w_record = _h_record = _w_stream = _h_stream = 0
        _columns = 0

        if self.record_color == Color.NONE.value:
            self.record_label.grid_remove()
        else:
            _w_record = self.record_started_icon.width()
            _h_record = self.record_started_icon.height()
            self.record_label.grid()
            _columns += 1

        if self.stream_color == Color.NONE.value:
            self.stream_label.grid_remove()
        else:
            _w_stream = self.stream_started_icon.width()
            _h_stream = self.stream_started_icon.height()
            self.stream_label.grid()
            _columns += 1

        _width = _w_record + _w_stream + 4 * _columns
        _height = max(_h_record, _h_stream) + 4

        if 'E' in self.position:
            _posx = self.winfo_screenwidth() - self.offset - _width
        else:
            _posx = self.offset

        if 'S' in self.position:
            _posy = self.winfo_screenheight() - self.offset - _height
        else:
            _posy = self.offset

        _logger.debug(f'{_width}x{_height}+{_posx}+{_posy}')
        self.geometry(f'{_width}x{_height}+{_posx}+{_posy}')
