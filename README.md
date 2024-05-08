# Idle Defense Save Finder
A simple app with a simple [GUI](https://customtkinter.tomschimansky.com/) to find your most recent save code for the [Idle Defense](https://vrchat.com/home/world/wrld_f18613e0-eca8-45ee-b3a8-50ce482b35de) game on [VRChat](https://hello.vrchat.com).

- Will grab the most recent save code, useful if your game crashed, isn't open, you're lazy, etc.
- Detects if you've disconnected and will grab the most recent save file before it

## Download
Head to the [Releases](https://github.com/MissingNO123/IdleDefenseLogParser/releases/latest) section and download the .exe file

## Building
A `build.bat` is included for Windows. The executable is confirmed to run under Wine on Linux, though the VRChat Appdata directory folder will need to be manually specified.
e.g.: 
```bash
IdleSaver.exe -l {SteamLibrary}/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/
```

Otherwise, just use it as normal through Python:
```bash
python run.py
```