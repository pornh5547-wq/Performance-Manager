import subprocess
import ctypes
import os

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run(cmd, timeout=30, shell=False):
    try:
        if shell:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                  startupinfo=SI, creationflags=NO_WINDOW, shell=True)
        return subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                              capture_output=True, text=True, timeout=timeout,
                              startupinfo=SI, creationflags=NO_WINDOW)
    except:
        return None

def run_admin(cmd, timeout=120):
    try:
        if _is_admin():
            return subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                                  capture_output=True, text=True, timeout=timeout,
                                  startupinfo=SI, creationflags=NO_WINDOW)
        full = f'Start-Process PowerShell -Verb RunAs -WindowStyle Hidden -PassThru -Wait -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command "{cmd}"\''
        result = subprocess.run(['powershell', '-NoProfile', '-Command', full],
                                capture_output=True, text=True, timeout=timeout,
                                startupinfo=SI, creationflags=NO_WINDOW)
        return result
    except subprocess.TimeoutExpired:
        return None
    except:
        return None
