# collect/drozer_collect.py

import subprocess
import json
import datetime
import shutil
import time
import socket
from pathlib import Path


def run_adb(cmd: str) -> str:
    ADB = r"C:\platform-tools\adb.exe"
    try:
        result = subprocess.run(f'"{ADB}" shell {cmd}', shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception:
        return ""


def find_drozer_path() -> str:
    # Chemin direct connu
    direct = r"C:\Users\houda\AppData\Local\Programs\Python\Python311\Scripts\drozer.EXE"
    if Path(direct).exists():
        return direct

    # Recherche dans le PATH
    path = shutil.which("drozer")
    if path:
        return path

    # Candidats supplementaires
    candidates = [
        r"C:\platform-tools\drozer.exe",
        r"C:\platform-tools\drozer",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    return ""


def drozer_available() -> bool:
    try:
        return bool(find_drozer_path())
    except Exception:
        return False


def _check_drozer_connection(host: str = "127.0.0.1", port: int = 31415) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def _run_drozer_command(drozer_path: str, command: str, timeout: int = 180) -> tuple[bool, str]:
    """Execute une commande Drozer - version qui marche sur TOUS les devices."""
    try:
        # La clé : --server 127.0.0.1:31415 (ce qui a marché sur ton OPPO)
        result = subprocess.run(
            [drozer_path, "console", "connect", "--server", "127.0.0.1:31415", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0 and not output:
            return False, result.stderr.strip()
        return True, output if output else ""
    except subprocess.TimeoutExpired:
        return False, f"Timeout apres {timeout}s"
    except Exception as e:
        return False, str(e)


def _parse_component_lines(output: str) -> list:
    """Extrait les lignes utiles en ignorant les messages de Drozer."""
    if not output:
        return []
    
    lines = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Ignorer les lignes de statut de Drozer
        if stripped.startswith(('dz>', 'Selecting', 'Attempting', 'Please wait', 'Could not find')):
            continue
        if 'Genymobile' in stripped or 'emoji' in stripped.lower():
            continue
        lines.append(stripped)
    return lines


def drozer_agent_check() -> dict:
    result = {
        "available": False,
        "connected": False,
        "package_count": 0,
        "provider_count": 0,
        "activity_count": 0,
        "service_count": 0,
        "receiver_count": 0,
        "exposed_providers": [],
        "exposed_activities": [],
        "exposed_services": [],
        "exposed_receivers": [],
        "output": "",
        "timestamp": datetime.datetime.now().isoformat(),
    }

    drozer_path = find_drozer_path()
    if not drozer_path:
        return result

    result["available"] = True
    run_adb("forward tcp:31415 tcp:31415")
    time.sleep(1)

    # Test de connexion simple
    ok, _ = _run_drozer_command(drozer_path, "echo test", timeout=10)
    result["connected"] = ok

    if not result["connected"]:
        result["output"] = "Agent Drozer non connecte"
        return result

    output_lines = []

    # --- Packages ---
    ok, out = _run_drozer_command(drozer_path, "run app.package.list", timeout=180)
    all_packages = []
    if ok and out:
        for line in out.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Ignorer les en-têtes Drozer
            if line.lower().startswith(('selecting', 'attempting', 'dz>')):
                continue
            # Extraire le nom du package (avant le premier espace ou parenthèse)
            if '(' in line:
                pkg = line.split('(')[0].strip()
            elif ' ' in line:
                pkg = line.split()[0]
            else:
                pkg = line
            if '.' in pkg and len(pkg) > 4:
                all_packages.append(pkg)
        
        result["package_count"] = len(all_packages)
        output_lines.append(f"Packages : {len(all_packages)} detectes")
    else:
        output_lines.append(f"Packages : {out[:100] if out else 'aucune donnee'}")

    # --- Providers ---
    ok, out = _run_drozer_command(drozer_path, "run scanner.provider.finduris -a", timeout=90)
    if ok and out:
        providers = [l.strip() for l in out.split('\n') if 'content://' in l]
        result["exposed_providers"] = providers[:30]
        result["provider_count"] = len(providers)
        output_lines.append(f"Providers exposes : {len(providers)}")
    else:
        output_lines.append("Providers exposes : 0")

    # --- Packages tiers (TOUS les packages non-système) ---
    third_party = []
    
    # Liste des préfixes système à EXCLURE (avec points pour éviter les faux positifs)
    system_prefixes = (
        'android.', 'com.android.', 'com.google.', 'com.qualcomm.', 
        'com.mediatek.', 'com.oppo.', 'com.coloros.', 'com.heytap.',
        'com.genymotion.', 'com.example.', 'com.oneplus.', 'com.xiaomi.',
        'com.samsung.', 'com.huawei.', 'com.nokia.', 'com.lge.',
        'com.microsoft.', 'com.amazon.', 'com.facebook.', 'com.whatsapp'
    )
    
    for pkg in all_packages:
        # Vérifier si c'est un package système
        is_system = False
        for prefix in system_prefixes:
            if pkg.startswith(prefix):
                is_system = True
                break
        
        # Garder tous les packages NON système
        if not is_system:
            third_party.append(pkg)
    
    # Supprimer les doublons et trier
    third_party = sorted(set(third_party))
    
    output_lines.append(f"Packages tiers : {len(third_party)}")
    if third_party:
        output_lines.append(f"Exemples : {', '.join(third_party[:10])}")

    # --- Activités exposées (limité aux 20 premiers) ---
    all_activities = []
    for pkg in third_party[:100]:
        ok, out = _run_drozer_command(drozer_path, f"run app.activity.info -a {pkg}", timeout=30)
        if ok and out:
            for line in out.split('\n'):
                if 'activity' in line.lower() and 'Permission:' not in line and 'Package:' not in line:
                    all_activities.append(f"{pkg}: {line.strip()}")
    result["exposed_activities"] = all_activities[:30]
    result["activity_count"] = len(all_activities)
    output_lines.append(f"Activities exposees : {len(all_activities)}")

    # --- Services exposés ---
    all_services = []
    for pkg in third_party[:100]:
        ok, out = _run_drozer_command(drozer_path, f"run app.service.info -a {pkg}", timeout=30)
        if ok and out:
            for line in out.split('\n'):
                if 'service' in line.lower() and 'Permission:' not in line and 'Package:' not in line:                    all_services.append(f"{pkg}: {line.strip()}")
    result["exposed_services"] = all_services[:30]
    result["service_count"] = len(all_services)
    output_lines.append(f"Services exposes : {len(all_services)}")

    # --- Receivers exposés ---
    all_receivers = []
    for pkg in third_party[:100]:
        ok, out = _run_drozer_command(drozer_path, f"run app.broadcast.info -a {pkg}", timeout=30)
        if ok and out:
            for line in out.split('\n'):
                if 'receiver' in line.lower() and 'Permission:' not in line and 'Package:' not in line:                    all_receivers.append(f"{pkg}: {line.strip()}")
    result["exposed_receivers"] = all_receivers[:30]
    result["receiver_count"] = len(all_receivers)
    output_lines.append(f"Receivers exposes : {len(all_receivers)}")

    result["output"] = "\n".join(output_lines)
    return result

def adb_available() -> bool:
    try:
        ADB = r"C:\platform-tools\adb.exe"
        result = subprocess.run(f'"{ADB}" devices', shell=True, capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().splitlines()
        return any("device" in line and not line.startswith("List") for line in lines)
    except Exception:
        return False


def get_dangerous_permissions() -> list:
    dangerous_perms = []
    permissions_to_check = {
        "READ_CONTACTS": "android.permission.READ_CONTACTS",
        "ACCESS_FINE_LOCATION": "android.permission.ACCESS_FINE_LOCATION",
        "RECORD_AUDIO": "android.permission.RECORD_AUDIO",
        "CAMERA": "android.permission.CAMERA",
        "READ_SMS": "android.permission.READ_SMS",
        "SEND_SMS": "android.permission.SEND_SMS",
        "READ_CALL_LOG": "android.permission.READ_CALL_LOG",
        "ACCESS_BACKGROUND_LOCATION": "android.permission.ACCESS_BACKGROUND_LOCATION",
    }
    output = run_adb("dumpsys package packages")
    for perm_name, perm_string in permissions_to_check.items():
        if perm_string in output:
            dangerous_perms.append(perm_name)
    return dangerous_perms


def collect_signals(output_path: str = "scorer/signals.json", use_drozer: bool = False) -> dict:
    if not adb_available():
        pass

    drozer_result = drozer_agent_check() if use_drozer else {
        "available": False,
        "connected": False,
        "package_count": 0,
        "provider_count": 0,
        "activity_count": 0,
        "service_count": 0,
        "receiver_count": 0,
        "exposed_providers": [],
        "exposed_activities": [],
        "exposed_services": [],
        "exposed_receivers": [],
        "output": "",
        "timestamp": "",
    }

    signals = {
        "timestamp":          datetime.datetime.now().isoformat(),
        "device_model":       run_adb("getprop ro.product.model"),
        "android_version":    run_adb("getprop ro.build.version.release"),
        "debug_enabled":      run_adb("getprop ro.debuggable") == "1",
        "build_tags_test":    "test-keys" in run_adb("getprop ro.build.tags"),
        "su_found":           bool(run_adb("which su")),
        "magisk_found":       bool(run_adb("ls /data/adb/magisk/ 2>/dev/null")) or "magisk" in run_adb("pm list packages").lower() or "com.topjohnwu.magisk" in run_adb("pm list packages"),
        "frida_running":      "frida" in run_adb("ps -A"),
        "xposed_found":       "xposed" in run_adb("pm list packages").lower() or "lsposed" in run_adb("pm list packages").lower(),
        "selinux_permissive": run_adb("getenforce") == "Permissive",
        "drozer_available":   drozer_result["available"],
        "drozer_connected":   drozer_result["connected"],
        "drozer_package_count": drozer_result["package_count"],
        "drozer_provider_count": drozer_result["provider_count"],
        "drozer_activity_count": drozer_result["activity_count"],
        "drozer_service_count": drozer_result["service_count"],
        "drozer_receiver_count": drozer_result["receiver_count"],
        "drozer_exposed_providers": drozer_result.get("exposed_providers", []),
        "drozer_exposed_activities": drozer_result.get("exposed_activities", []),
        "drozer_exposed_services": drozer_result.get("exposed_services", []),
        "drozer_exposed_receivers": drozer_result.get("exposed_receivers", []),
        "drozer_output":      drozer_result["output"],
        "drozer_timestamp":   drozer_result.get("timestamp", ""),
        "binary_tampered":    False,
        "dangerous_permissions": get_dangerous_permissions(),
    }

    with open(output_path, "w") as f:
        json.dump(signals, f, indent=2)

    return signals


if __name__ == "__main__":
    collect_signals()