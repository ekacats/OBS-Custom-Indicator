# OBS-Custom-Indicator
Display on-screen indicators for recording and live streaming status.


## Dependencies
This software is designed to run on Windows and relies on the following dependencies:
- [OBS Studio](https://obsproject.com/)
- [Python](https://www.python.org/)


## Usage
To use Python scripts with OBS Studio, follow these steps:

1. Python Installation<br>
	Download and install Python 3.12 from the official website: [python.org](https://www.python.org/downloads/windows/). If OBS Studio supports a newer version of Python in the future, you may use that version instead.
	Since this software uses tkinter, please make sure to check the **tcl/tk and IDLE** option during the installation process.

2. Register Python in OBS Studio<br>
	Open OBS Studio and navigate to **Tools** menu -> **Scripts** option -> **Python Settings** tab. Specify the Python installation folder to register Python in OBS. For detailed instructions, please consult the [OBS Python/Lua Scripting](https://docs.obsproject.com/scripting).

3. Specify the Python Script<br>
	Specify the path to **obs_custom_indicator.py** file in **Scripts** tab.

4. Customize Indicators<br>
	You can customize the appearance of the indicators (**size**, **position**, **color**, etc.) by modifying the script properties. After modifying the display language for script properties, restart OBS Studio to apply the changes.


## License
This software is released under the MIT License, see LICENSE.

This software uses [Material Symbols](https://fonts.google.com/icons) for icons. Material Symbols are licensed under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
The icons have been modified by changing their colors.
