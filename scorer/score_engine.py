# scorer/score_engine.py

WEIGHTS = {
    "debug_enabled": 15,
    "build_tags_test": 10,
    "su_found": 20,
    "magisk_found": 15,
    "frida_running": 15,
    "xposed_found": 10,
    "selinux_permissive": 5,
    "binary_tampered": 5,  
    "dangerous_permission": 5,
}

def raw_score(signals: dict) -> int:
    score = 0
    if signals.get("debug_enabled"):
        score += WEIGHTS["debug_enabled"]
    if signals.get("build_tags_test"):
        score += WEIGHTS["build_tags_test"]
    if signals.get("su_found"):
        score += WEIGHTS["su_found"]
    if signals.get("magisk_found"):
        score += WEIGHTS["magisk_found"]
    if signals.get("frida_running"):
        score += WEIGHTS["frida_running"]
    if signals.get("xposed_found"):
        score += WEIGHTS["xposed_found"]
    if signals.get("selinux_permissive"):
        score += WEIGHTS["selinux_permissive"]
    
    # Permissions dangereuses : 5 points
    if signals.get("dangerous_permissions"):
        score += WEIGHTS["dangerous_permission"]
    
    return min(score, 100)  # Cap à 100

def get_risk_level(score: int) -> str:
    if score >= 70:
        return "ELEVE"
    elif score >= 40:
        return "MOYEN"
    else:
        return "FAIBLE"

def final_score(signals: dict) -> tuple:
    raw = raw_score(signals)
    capped = min(100, raw)
    level = get_risk_level(capped)
    return capped, level