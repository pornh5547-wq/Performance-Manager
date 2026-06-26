import json
from app.utils._pwsh import run, run_admin

BLOATWARE_LIST = [
    "Microsoft.3DBuilder", "Microsoft.BingWeather", "Microsoft.BingNews",
    "Microsoft.BingSports", "Microsoft.BingFinance", "Microsoft.GetHelp",
    "Microsoft.Getstarted", "Microsoft.Messaging", "Microsoft.Microsoft3DViewer",
    "Microsoft.MicrosoftOfficeHub", "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.MixedReality.Portal", "Microsoft.Office.OneNote",
    "Microsoft.OneConnect", "Microsoft.People", "Microsoft.Print3D",
    "Microsoft.SkypeApp", "Microsoft.Wallet", "Microsoft.WindowsAlarms",
    "Microsoft.WindowsCamera", "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps", "Microsoft.WindowsSoundRecorder",
    "Microsoft.XboxApp", "Microsoft.XboxGameCallableUI", "Microsoft.XboxGamingOverlay",
    "Microsoft.XboxIdentityProvider", "Microsoft.XboxSpeechToTextOverlay",
    "Microsoft.Xbox.TCUI", "Microsoft.YourPhone", "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo", "Microsoft.Advertising.Xaml",
    "Microsoft.MSPaint", "Microsoft.Todos", "Microsoft.PowerAutomateDesktop",
    "Microsoft.Windows.DevHome", "Microsoft.Whiteboard",
    "SpotifyAB.SpotifyMusic", "Disney.37853FC22B2CE", "Facebook.Facebook",
    "Instagram.Instagram", "TikTok.TikTok", "Netflix.Netflix",
    "Clipchamp.Clipchamp", "Microsoft.549981C3F5F10", "Microsoft.AsyncTextService",
    "Microsoft.Copilot", "Microsoft.FamilySafety", "Microsoft.GamingApp",
    "Microsoft.MicrosoftJournal", "Microsoft.MixedReality",
    "Microsoft.Office.Sway", "Microsoft.OutlookForWindows",
    "Microsoft.StorePurchaseApp", "Microsoft.WidgetPlatformRuntime",
    "Microsoft.Windows.Calculator", "Microsoft.Windows.Photos",
    "Microsoft.windowscommunicationsapps",
    "Microsoft.WindowsNotepad", "Microsoft.WindowsVoiceRecorder",
    "Microsoft.XboxGamingOverlay_Secure",
    "MicrosoftCorporationII.MicrosoftFamily", "MicrosoftWindows.CrossDevice",
    "MicrosoftWindows.UndockedDevKit",
]

def list_installed_bloatware():
    cmd = 'Get-AppxPackage -AllUsers | Select-Object Name, PackageFullName, InstallLocation | ConvertTo-Json'
    result = run(cmd)
    installed = []
    seen = set()
    if result and result.stdout.strip():
        try:
            packages = json.loads(result.stdout)
            if isinstance(packages, dict):
                packages = [packages]
            for pkg in packages:
                name = pkg.get("Name", "")
                if name in BLOATWARE_LIST and name not in seen:
                    seen.add(name)
                    installed.append(pkg)
        except:
            pass
    cmd2 = 'Get-AppxProvisionedPackage -Online | Select-Object DisplayName, PackageName | ConvertTo-Json'
    result2 = run(cmd2, timeout=30)
    if result2 and result2.stdout.strip():
        try:
            prov_pkgs = json.loads(result2.stdout)
            if isinstance(prov_pkgs, dict):
                prov_pkgs = [prov_pkgs]
            for pkg in prov_pkgs:
                name = pkg.get("DisplayName", "")
                if name in BLOATWARE_LIST and name not in seen:
                    seen.add(name)
                    installed.append({
                        "Name": name,
                        "PackageFullName": pkg.get("PackageName", ""),
                        "InstallLocation": "",
                        "Provisioned": True,
                    })
        except:
            pass
    return installed

def uninstall_package(full_name, provisioned=False):
    if provisioned:
        r = run_admin(f'Get-AppxProvisionedPackage -Online | Where-Object {{$_.PackageName -eq "{full_name}"}} | Remove-AppxProvisionedPackage -AllUsers')
    else:
        r = run_admin(f'Get-AppxPackage "{full_name}" | Remove-AppxPackage -AllUsers')
    if r is None:
        return False
    return r.returncode == 0 or (r.stdout and "success" in r.stdout.lower())

def uninstall_all():
    results = []
    for pkg in list_installed_bloatware():
        name = pkg.get("Name", "Unknown")
        full = pkg.get("PackageFullName", "")
        if not full:
            results.append({"name": name, "success": False})
            continue
        ok1 = uninstall_package(full, provisioned=False)
        ok2 = uninstall_package(full, provisioned=True)
        results.append({"name": name, "success": ok1 or ok2})
    return results

def reinstall_package(name):
    cmd = f'Get-AppxPackage -AllUsers | Where-Object {{$_.Name -eq "{name}"}} | Format-List PackageFullName'
    result = run(cmd)
    if result and result.stdout.strip():
        full_name = result.stdout.strip().split('\n')[0].split(':')[-1].strip()
        if full_name:
            r = run_admin(f'Add-AppxPackage -Register "$(Get-AppxPackage -AllUsers | Where-Object {{$_.Name -eq "{name}"}} | Select-Object -ExpandProperty InstallLocation)\\AppxManifest.xml" -DisableDevelopmentMode')
            return r is not None and r.returncode == 0
    return False
