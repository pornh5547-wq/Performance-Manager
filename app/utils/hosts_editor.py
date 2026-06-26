import os

def get_hosts_path():
    return os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'drivers', 'etc', 'hosts')

def read_hosts():
    path = get_hosts_path()
    entries = []
    if not os.path.exists(path):
        return entries
    try:
        with open(path, 'r') as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    entries.append({"line": i, "content": line.rstrip('\n\r'), "enabled": True, "comment": True, "raw": line})
                else:
                    parts = stripped.split()
                    if len(parts) >= 2:
                        entries.append({
                            "line": i, "content": line.rstrip('\n\r'), "enabled": True, "comment": False,
                            "ip": parts[0], "domain": parts[1], "raw": line,
                            "redirected": parts[0] in ("127.0.0.1", "0.0.0.1", "::1"),
                        })
                    else:
                        entries.append({"line": i, "content": line.rstrip('\n\r'), "enabled": True, "comment": True, "raw": line})
    except:
        pass
    return entries

def write_hosts(entries):
    path = get_hosts_path()
    try:
        with open(path, 'w') as f:
            for e in entries:
                f.write(e.get("raw", "") + "\n")
        return True
    except:
        return False

def add_entry(ip, domain):
    path = get_hosts_path()
    try:
        with open(path, 'a') as f:
            f.write(f"\n{ip} {domain}")
        return True
    except:
        return False

def remove_entry(domain):
    path = get_hosts_path()
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        with open(path, 'w') as f:
            for line in lines:
                if domain not in line:
                    f.write(line)
        return True
    except:
        return False

def toggle_entry(entry):
    if entry.get("comment"):
        return False
    path = get_hosts_path()
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        idx = entry["line"] - 1
        if 0 <= idx < len(lines):
            line = lines[idx]
            stripped = line.lstrip()
            if stripped.startswith('#'):
                rest = stripped[1:].lstrip()
                indent = line[:len(line) - len(stripped)]
                lines[idx] = indent + rest + ('\n' if not rest.endswith('\n') else '')
            else:
                lines[idx] = '#' + line
        with open(path, 'w') as f:
            f.writelines(lines)
        return True
    except:
        return False

def restore_defaults():
    path = get_hosts_path()
    default = "# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names.\n#\n127.0.0.1       localhost\n::1             localhost\n"
    try:
        with open(path, 'w') as f:
            f.write(default)
        return True
    except:
        return False
