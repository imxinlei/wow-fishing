# WOW-FISHING
Fishing bot for world of warcraft, detecting cursor change to find hook, monitoring sound to trigger fishing.

# Prerequisities
- OS: Windows Vista / 7 / 8 / 10
- python3.x

# Environment
```ps
python3 -m venv .venv

pip install -r requirements.txt
# or using a mirror
pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
```

# Compile
WOW-FISHING uses WASAPI to monitoring game audio, which is implemented in C++. Compiling is needed before running python script.
```ps
cl.exe /LD .\wasapi\wasapi.cpp /link Ole32.Lib
```

# Run
Enter python virtual environment
```ps
.\.venv\Scripts\Activate.ps1
```

Run fishing script:
```ps
python .\fishingWasapi.py
```
