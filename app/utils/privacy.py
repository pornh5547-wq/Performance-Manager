import subprocess
import os
from app.utils._pwsh import run_admin, run

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

def get_privacy_status():
    status = {}
    try:
        r = run('Get-Service DiagTrack | Select-Object -ExpandProperty Status')
        status["telemetry_service"] = r.stdout.strip() if r and r.stdout else "Unknown"
    except:
        status["telemetry_service"] = "Unknown"
    try:
        r = run('Get-Service DmwAppPushService | Select-Object -ExpandProperty Status')
        status["push_service"] = r.stdout.strip() if r and r.stdout else "Unknown"
    except:
        status["push_service"] = "Unknown"
    try:
        r = run('Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name AllowTelemetry -ErrorAction SilentlyContinue | Select-Object -ExpandProperty AllowTelemetry')
        val = r.stdout.strip() if r and r.stdout else ""
        status["telemetry_level"] = val if val else "Not Set"
    except:
        status["telemetry_level"] = "Unknown"
    try:
        path = os.path.join(os.environ.get('LOCALAPPDATA',''),'PMTelemetryBlock')
        status["hosts_blocked"] = os.path.exists(path)
    except:
        status["hosts_blocked"] = False
    return status

def block_telemetry():
    results = []
    try:
        cmd = '''
Set-Service DiagTrack -StartupType Disabled -ErrorAction SilentlyContinue; Stop-Service DiagTrack -Force -ErrorAction SilentlyContinue;
Set-Service DmwAppPushService -StartupType Disabled -ErrorAction SilentlyContinue; Stop-Service DmwAppPushService -Force -ErrorAction SilentlyContinue;
$null = New-Item -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Force;
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name AllowTelemetry -Value 0 -ErrorAction SilentlyContinue;
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name AllowCortana -Value 0 -Type DWord -ErrorAction SilentlyContinue;
New-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" -Name AllowTelemetry -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue
'''
        r = run_admin(cmd)
        ok = r is not None
        results = [
            ("DiagTrack Service", "Disabled" if ok else "Failed"),
            ("Push Service", "Disabled" if ok else "Failed"),
            ("Telemetry Level", "Set to 0" if ok else "Failed"),
            ("Cortana", "Disabled" if ok else "Failed"),
            ("DataCollection Policy", "Set" if ok else "Failed"),
        ]
    except:
        results = [
            ("DiagTrack Service", "Error"),
            ("Push Service", "Error"),
            ("Telemetry Level", "Error"),
            ("Cortana", "Error"),
            ("DataCollection Policy", "Error"),
        ]
    hosts_blocked = _block_telemetry_hosts()
    results.append(("Telemetry Hosts", "Blocked" if hosts_blocked else "Failed"))
    marker = os.path.join(os.environ.get('LOCALAPPDATA',''),'PMTelemetryBlock')
    try:
        open(marker, 'a').close()
    except:
        pass
    return results

def unblock_telemetry():
    results = []
    try:
        cmd = '''
Set-Service DiagTrack -StartupType Manual -ErrorAction SilentlyContinue; Start-Service DiagTrack -ErrorAction SilentlyContinue;
Set-Service DmwAppPushService -StartupType Manual -ErrorAction SilentlyContinue; Start-Service DmwAppPushService -ErrorAction SilentlyContinue;
Remove-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name AllowTelemetry -ErrorAction SilentlyContinue;
Remove-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name AllowCortana -ErrorAction SilentlyContinue
'''
        r = run_admin(cmd)
        ok = r is not None
        results = [
            ("DiagTrack Service", "Enabled" if ok else "Failed"),
            ("Push Service", "Enabled" if ok else "Failed"),
            ("Telemetry Level", "Reset" if ok else "Failed"),
            ("Cortana", "Enabled" if ok else "Failed"),
        ]
    except:
        results = [
            ("DiagTrack Service", "Error"),
            ("Push Service", "Error"),
            ("Telemetry Level", "Error"),
            ("Cortana", "Error"),
        ]
    hosts_file = os.path.join(os.environ.get('SystemRoot','C:\\Windows'),'System32','drivers','etc','hosts')
    _remove_telemetry_hosts(hosts_file)
    results.append(("Telemetry Hosts", "Unblocked"))
    marker = os.path.join(os.environ.get('LOCALAPPDATA',''),'PMTelemetryBlock')
    try:
        if os.path.exists(marker):
            os.remove(marker)
    except:
        pass
    return results

TELEMETRY_DOMAINS = [
    "vortex.data.microsoft.com",
    "vortex-win.data.microsoft.com",
    "telemetry.microsoft.com",
    "telemetry.remote.microsoft.com",
    "watson.telemetry.microsoft.com",
    "oca.telemetry.microsoft.com",
    "sqm.telemetry.microsoft.com",
    "settings-win.data.microsoft.com",
    "settings-sandbox.data.microsoft.com",
    "diagnostics.support.microsoft.com",
    "corp.sts.microsoft.com",
    "statsfe2.ws.microsoft.com",
    "statsfe1.ws.microsoft.com",
    "redir.metaservices.microsoft.com",
    "choice.microsoft.com",
    "choice.microsoft.com.nsatc.net",
    "app.powerbi.com",
    "ctldl.windowsupdate.com",
    "au.download.windowsupdate.com",
    "download.windowsupdate.com",
    "ntservicepack.microsoft.com",
    "ecn.deviceservices.microsoft.com",
    "defender.microsoft.com",
    "data.microsoft.com",
]

def _block_telemetry_hosts():
    try:
        hosts_file = os.path.join(os.environ.get('SystemRoot','C:\\Windows'),'System32','drivers','etc','hosts')
        if not os.path.exists(hosts_file):
            return False
        with open(hosts_file, 'r') as f:
            content = f.read()
        added = 0
        with open(hosts_file, 'a') as f:
            for domain in TELEMETRY_DOMAINS:
                line = f"127.0.0.1 {domain}"
                if line not in content:
                    f.write(f"\n{line}")
                    added += 1
            for domain in TELEMETRY_DOMAINS:
                line = f"::1 {domain}"
                if line not in content:
                    f.write(f"\n{line}")
                    added += 1
        return True
    except:
        return False

def _remove_telemetry_hosts(hosts_file):
    try:
        if not os.path.exists(hosts_file):
            return
        with open(hosts_file, 'r') as f:
            lines = f.readlines()
        with open(hosts_file, 'w') as f:
            for line in lines:
                stripped = line.strip()
                if not any(domain in stripped for domain in TELEMETRY_DOMAINS):
                    f.write(line)
    except:
        pass
