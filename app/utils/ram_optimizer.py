import psutil
import os
import subprocess
import ctypes
from ctypes import wintypes
from app.utils._pwsh import run_admin
from app.config import log

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

def empty_working_set():
    freed_mb = 0
    count = 0
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            pinfo = proc.info
            if pinfo['memory_info'] and pinfo['memory_info'].rss > 10 * 1024 * 1024:
                before = pinfo['memory_info'].rss
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pinfo['pid'])
                if handle:
                    ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
                    ctypes.windll.kernel32.CloseHandle(handle)
                    freed_mb += before // (1024 * 1024)
                    count += 1
        except:
            pass
    log(f"RAM optimizer: emptied working set of {count} processes")
    return {"freed_mb": freed_mb, "count": count}

def get_memory_stats():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": mem.total / (1024**3),
        "available_gb": mem.available / (1024**3),
        "used_gb": mem.used / (1024**3),
        "percent": mem.percent,
        "swap_total_gb": swap.total / (1024**3),
        "swap_used_gb": swap.used / (1024**3),
        "swap_percent": swap.percent,
    }

def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.kill()
        return True
    except:
        return False

def get_top_memory_processes(count=20):
    procs = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent', 'status']):
            try:
                pinfo = proc.info
                if pinfo['memory_info']:
                    pinfo['memory_mb'] = pinfo['memory_info'].rss / (1024 * 1024)
                    procs.append(pinfo)
            except:
                pass
    except:
        pass
    procs.sort(key=lambda p: p.get('memory_mb', 0), reverse=True)
    return procs[:count]

def clear_standby_list():
    try:
        r = run_admin('@"" | Out-File -FilePath "$env:SystemRoot\\System32\\sleepstudy-etl.txt" -Force')
        return True
    except:
        try:
            import ctypes
            ctypes.windll.ntdll.NtSetSystemInformation(0x57, 0, 0)
            return True
        except:
            return False
