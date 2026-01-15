# Attendance System
A QR-based attendance system that tracks student logs sent to Google Sheets using Python libraries and QR scanner device.

## Features
- QR-based Attendance Logging
- Google Sheets Automation
- Plug-and-Play
- SHA256 Signing

## Back End
- Python version 3.12
- PySerial Python Library for Hardware Inferfacing
- Google Sheets API and Google Drive API
- SHA256 Hashing Algorithm

## Front End
- Tkinter Built-in Python GUI Library

## How It Works
**QR Registration**
1. Scan ID
2. Generate unique signed key via SHA256
3. Store key with student number

**Attendance Logging**
1. Scan ID
2. App will search from Google Sheets
3. App verifies student
4. Display feedback on Graphical User Interface (GUI)

    > name, student number, timestamp, status(present/late)

5. Instructors/teachers can check their Google Sheets spreadsheet file and verify student logs. Then, mark students ABSENT that did not scan.

## Setup
1. Download and install **Python** and **Git**:
    - [Python 3.12.10](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)
    - [Git](https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe) or watch this video [How to Install Git & Use Git in Visual Studio Code](https://youtu.be/3Tsaxxv9sls?t=43)

2. Create a project folder. For example

    > C:\Users\Dan\Python_Projects

    or use an existing directory of your project.

3. To clone this project, open **Windows Terminal** and go to your project directory by copying this command:
    via **PowerShell** or **Command Prompt**:
    ```cmd
    cd Python_Projects
    git clone https://github.com/danclangcoder/attendance-system.git
    ```
    You will see something like this:
    ![Cloning process](screenshots/cloning-process-screenshot.png)

4. Open **Visual Studio Code** and select:
    > File

    and

    > Open Folder

    Then, select your attendance-system folder.

5. Open Terminal and create a virtual environment and activate:
    ```powershell
    python3.12 -m venv .venv
    .venv/Scripts/Activate.ps1
    ```

6. Once activated, your terminal will look like this:
    ![Virtual environment activated](screenshots/terminal-screenshot.png)

7. Next, select the correct Python interpreter (.venv) by using VS Code commands:
    **Ctrl + Shift + P**.</br>

    Then, type interpreter and select

    > Python: Select Interpreter

    Then, click the Python 3.12.10 (.venv) interpreter.
    ![Interpreter select](screenshots/select-interpreter-screenshot.png)

8. Install the packages listed in requirements.txt file by copy and paste on your VS Code Terminal:
    ```powershell
    pip install -r requirements.txt
    ```

## When updating code, simply run these commands on your VS Code Terminal
For example when updating a **single file**:
```powershell
git pull origin master
git add qr_scanner.py
git commit -m "Added new function"
git push origin master
```
When creating new file or folder:
```powershell
git pull origin master
git add .
git commit -m "Enter short description"
git push origin master
```

When moving files or folders do this:
```powershell
git pull origin master
git add -A
git commit -m "Enter short description"
git push origin master
```