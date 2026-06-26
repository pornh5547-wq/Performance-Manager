import threading
from app.utils._pwsh import run, run_admin
from app.config import log

class WindowsRepair:
    @staticmethod
    def run_dism_scan(callback=None):
        def task():
            log("Starting DISM scan...")
            result = run_admin('DISM /Online /Cleanup-Image /ScanHealth')
            output = (result.stdout + result.stderr) if result else "Failed"
            log(f"DISM scan completed")
            if callback:
                callback("dism_scan", result is not None, output)
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def run_dism_restore(callback=None):
        def task():
            log("Starting DISM restore health...")
            result = run_admin('DISM /Online /Cleanup-Image /RestoreHealth')
            output = (result.stdout + result.stderr) if result else "Failed"
            log(f"DISM restore completed")
            if callback:
                callback("dism_restore", result is not None, output)
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def run_sfc_scan(callback=None):
        def task():
            log("Starting SFC scan...")
            result = run_admin('sfc /scannow')
            output = (result.stdout + result.stderr) if result else "Failed"
            log(f"SFC scan completed")
            if callback:
                callback("sfc", result is not None, output)
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def run_chkdsk(drive='C:', callback=None):
        def task():
            log(f"Starting CHKDSK on {drive}...")
            result = run_admin(f'chkdsk {drive} /f /r')
            output = (result.stdout + result.stderr) if result else "Failed"
            log(f"CHKDSK completed")
            if callback:
                callback("chkdsk", result is not None, output)
        threading.Thread(target=task, daemon=True).start()

class NetworkRepair:
    @staticmethod
    def flush_dns(callback=None):
        def task():
            log("Flushing DNS...")
            result = run_admin('ipconfig /flushdns')
            log(f"DNS flush completed")
            if callback:
                callback("dns_flush", result is not None, "")
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def reset_winsock(callback=None):
        def task():
            log("Resetting Winsock...")
            result = run_admin('netsh winsock reset')
            log(f"Winsock reset completed")
            if callback:
                callback("winsock", result is not None, "")
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def reset_ip(callback=None):
        def task():
            log("Resetting IP stack...")
            result = run_admin('netsh int ip reset')
            log(f"IP reset completed")
            if callback:
                callback("ip_reset", result is not None, "")
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def renew_ip(callback=None):
        def task():
            log("Releasing and renewing IP...")
            result = run_admin('ipconfig /release; ipconfig /renew')
            log(f"IP renew completed")
            if callback:
                callback("ip_renew", result is not None, "")
        threading.Thread(target=task, daemon=True).start()

    @staticmethod
    def reset_all(callback=None):
        def task():
            log("Running full network reset...")
            r = run_admin('ipconfig /flushdns; netsh winsock reset; netsh int ip reset; ipconfig /release; ipconfig /renew')
            ok = r is not None
            log(f"Full network reset completed")
            if callback:
                callback("network_reset_all", ok, "ok" if ok else "failed")
        threading.Thread(target=task, daemon=True).start()
