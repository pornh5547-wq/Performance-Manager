<div align="center">
  <h1>⚡ PM Performance Manager</h1>
  <p><strong>Windows performance tuning &amp; system management — dark UI, no bloat.</strong></p>
  <p>
    <img alt="Python" src="https://img.shields.io/badge/python-3.12%2B-purple?style=flat-square&logo=python">
    <img alt="Tests" src="https://img.shields.io/badge/tests-206%20passed-brightgreen?style=flat-square">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square">
    <img alt="Platform" src="https://img.shields.io/badge/platform-Windows%2010%2F11-informational?style=flat-square&logo=windows">
  </p>
</div>

---

## ✨ Features

| Category | Tools |
|----------|-------|
| **📊 Dashboard** | Live CPU / RAM / GPU / Disk monitoring, top processes, quick actions |
| **🎮 Gaming Mode** | High-performance power plan, Windows Update toggle, Steam game detection & launch |
| **⚡ Performance Mode** | Restore point, temp/shader/prefetch cleanup, SSD TRIM, standby list clear |
| **🩺 Health Check** | DISM ScanHealth/RestoreHealth, SFC scan, SMART status, TRIM check, CHKDSK |
| **🌐 Network** | DNS flush, Winsock reset, IP stack reset, renew IP, traffic stats, speed test |
| **💾 Drives & Storage** | Per-drive usage, large file finder (recursive by size threshold) |
| **🚀 Startup Manager** | Registry (HKLM/HKCU) & startup folder management |
| **🔒 Privacy Blocker** | Block telemetry services (DiagTrack, Push), registry policies, hosts-based blocking |
| **⚙️ Services** | Enable/disable 100+ Windows services with safety badges |
| **🗑️ Bloatware Uninstaller** | Batch uninstall 50+ pre-installed & provisioned packages |
| **📝 Hosts Editor** | Add / remove / toggle hosts entries |
| **🧠 RAM Optimizer** | Free working sets, kill processes, clear standby list |
| **🔋 Battery** | WMI battery info + powercfg full report |
| **🎨 Visual Effects** | Toggle animations, transparency, startup sound, performance mode |
| **📦 Windows Features** | Toggle 16 optional features via DISM |
| **🔌 Plugin System** | Extensible via JSON manifest plugins |
| **⏰ Scheduled Maintenance** | Auto cleanup, DISM, SFC on configurable interval |
| **🎨 Themes** | Dark/Light/System appearance + 4 color themes |

---

## 🚀 Installation

### Option 1 — Standalone EXE (recommended)

Download the latest `PMPerformanceManager.exe` from the [Releases](https://github.com/pornh5547-wq/Performance-Manager/releases) page.

**Requirements:** Windows 10 or 11. No Python or dependencies needed.

### Option 2 — From source

```bash
git clone https://github.com/pornh5547-wq/Performance-Manager.git
cd Performance-Manager
pip install -r requirements.txt
python main.py
```

Requires Python 3.12+.

---

## 🖥️ Usage

Run `PMPerformanceManager.exe` (or `python main.py`). The app auto-elevates to administrator — most features require admin rights.

**Keyboard shortcuts:**
| Key | Action |
|-----|--------|
| `Ctrl+Tab` | Cycle to next page |
| `Ctrl+W` | Close app |
| `Esc` | Dismiss notification |

---

## 🧪 Tests

```bash
pytest tests/ -v
```

**206 tests** covering all 17 utility modules — no external dependencies, no admin required.

---

## 🔧 Build

```powershell
# PowerShell
pyinstaller --onefile --windowed --name PMPerformanceManager --add-data "app;app" --uac-admin main.py
```

Or run the included build script:

```powershell
.\build_exe.ps1
```

---

## 📁 Configuration

Settings are saved to `%LOCALAPPDATA%\PMPerformanceManager\config.json`.

---

## 📄 License

MIT
