# Attendance System
A QR-based attendance system that tracks student logs sent to Google Sheets using Python libraries and QR scanner device.

## Setup
1. Download and install **Python and **Git:
    - [Python 3.12.10](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)
    - [Git](https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe) or watch this video [How to Install Git & Use Git in Visual Studio Code](https://youtu.be/3Tsaxxv9sls?t=43)
2. Create a project folder > project_name
    - For example:\
    > C:\Users\Dan\Attendance_System <br/>
    or the directory of your project folder.
3. Open Visual Studio Code and select
    > File <br/>
    and <br/>
    > Open Folder. <br/>
    Then, select your created project folder.
4. Open Terminal and copy and paste this using
    - PowerShell:
    ```powershell
    git clone https://github.com/danclangcoder/attendance-system.git
    python3.12 -m venv .venv
    .venv/Scripts/Activate.ps1
    pip install -r requirements.txt
    ```
    - or Command Prompt:
    ```cmd
    python3.12 -m venv .venv
    .venv/Scripts/activate.bat
    pip install -r requirements.txt
    ```

## When updating code, simply run these commands on your VS Code Terminal
**For example when updating a single file:
```powershell
git init
git pull origin master
git add qr_scanner.py
git commit -m "Added new function"
git push origin master
```