import os
import shutil
import tempfile
import glob
from app.utils._pwsh import run
from app.config import log

TEMP_CLEANUP_PATHS = [
    os.environ.get('TEMP', ''),
    os.environ.get('TMP', ''),
    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
]

SHADER_CACHE_PATHS = [
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'AMD', 'ShaderCache'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NVIDIA', 'ShaderCache'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Intel', 'ShaderCache'),
    os.path.join(os.environ.get('APPDATA', ''), 'NVIDIA', 'ShaderCache'),
]

BROWSER_CACHE_PATHS = [
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Cache'),
]

PREFETCH_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Prefetch')

def get_size(path):
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            total += os.path.getsize(fp)
                    except:
                        pass
    except:
        pass
    return total

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

def clean_temp_files():
    cleaned = 0
    freed_bytes = 0
    errors = []
    for path in TEMP_CLEANUP_PATHS:
        if os.path.exists(path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            try:
                                freed_bytes += os.path.getsize(item_path)
                                os.unlink(item_path)
                                cleaned += 1
                            except:
                                pass
                        elif os.path.isdir(item_path):
                            freed_bytes += get_size(item_path)
                            shutil.rmtree(item_path, ignore_errors=True)
                            cleaned += 1
                    except:
                        errors.append(item_path)
            except:
                errors.append(path)
    log(f"Temp cleanup: {cleaned} items removed, {format_size(freed_bytes)} freed")
    return {"cleaned": cleaned, "freed_bytes": freed_bytes, "errors": errors}

def clean_shader_cache():
    cleaned = 0
    freed_bytes = 0
    for path in SHADER_CACHE_PATHS:
        if os.path.exists(path):
            try:
                freed_bytes += get_size(path)
                shutil.rmtree(path, ignore_errors=True)
                cleaned += 1
            except:
                pass
    log(f"Shader cache cleanup: {cleaned} caches cleared, {format_size(freed_bytes)} freed")
    return {"cleaned": cleaned, "freed_bytes": freed_bytes}

def clean_prefetch():
    freed_bytes = 0
    cleaned = 0
    if os.path.exists(PREFETCH_PATH):
        try:
            for f in glob.glob(os.path.join(PREFETCH_PATH, '*')):
                try:
                    freed_bytes += os.path.getsize(f)
                    os.remove(f)
                    cleaned += 1
                except:
                    pass
        except:
            pass
    log(f"Prefetch cleanup: {cleaned} files removed, {format_size(freed_bytes)} freed")
    return {"cleaned": cleaned, "freed_bytes": freed_bytes}

def clean_browser_cache():
    cleaned = 0
    freed_bytes = 0
    for path in BROWSER_CACHE_PATHS:
        if os.path.exists(path):
            try:
                freed_bytes += get_size(path)
                shutil.rmtree(path, ignore_errors=True)
                cleaned += 1
            except:
                pass
    log(f"Browser cache cleanup: {cleaned} caches cleared, {format_size(freed_bytes)} freed")
    return {"cleaned": cleaned, "freed_bytes": freed_bytes}

def clean_recycle_bin():
    result = run('rd /s /q %systemdrive%\\$Recycle.Bin', shell=True)
    if result:
        log("Recycle bin cleaned")
        return {"success": True}
    return {"success": False}

def get_total_cleanable_size():
    total = 0
    for path in TEMP_CLEANUP_PATHS + SHADER_CACHE_PATHS + BROWSER_CACHE_PATHS:
        if os.path.exists(path):
            total += get_size(path)
    if os.path.exists(PREFETCH_PATH):
        total += get_size(PREFETCH_PATH)
    return total

def run_full_cleanup():
    results = {
        "temp": clean_temp_files(),
        "shader": clean_shader_cache(),
        "browser": clean_browser_cache(),
        "prefetch": clean_prefetch(),
    }
    total_freed = sum(r.get('freed_bytes', 0) for r in results.values())
    log(f"Full cleanup completed: {format_size(total_freed)} total freed")
    return results, total_freed
