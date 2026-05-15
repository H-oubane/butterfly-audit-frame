# scorer/fp_reducer.py

KNOWN_LEGIT_CUSTOM = ["OnePlus", "Xiaomi", "Poco", "Redmi"]

def adjust_false_positives(raw_score: int, signals: dict) -> int:
    model = signals.get("device_model", "")
    has_hook = signals.get("frida_running") or signals.get("xposed_found")

    # Règle 1 : ROM custom connue + root sans hook -> probablement légitime
    if any(b in model for b in KNOWN_LEGIT_CUSTOM) and not has_hook:
        raw_score = max(0, raw_score - 25)

    # Règle 2 : debug seul, sans root ni hook -> dev safe probable
    if (signals.get("debug_enabled")
            and not signals.get("su_found")
            and not signals.get("magisk_found")
            and not has_hook):
        raw_score = max(0, raw_score - 15)

    return raw_score