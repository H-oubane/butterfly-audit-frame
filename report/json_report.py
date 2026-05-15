# report/json_report.py

import json
from pathlib import Path

def export_json(signals: dict, score: int, risk_level: str, output_path: str = "report/audit_report.json"):
    report = {
        "timestamp":      signals.get("timestamp"),
        "device_model":   signals.get("device_model"),
        "android_version":signals.get("android_version"),
        "score":          score,
        "risk_level":     risk_level,
        "signals": {
            "debug_enabled":      signals.get("debug_enabled"),
            "build_tags_test":    signals.get("build_tags_test"),
            "su_found":           signals.get("su_found"),
            "magisk_found":       signals.get("magisk_found"),
            "frida_running":      signals.get("frida_running"),
            "xposed_found":       signals.get("xposed_found"),
            "selinux_permissive": signals.get("selinux_permissive"),
            "drozer_available":   signals.get("drozer_available"),
            "drozer_connected":   signals.get("drozer_connected"),
            "drozer_package_count": signals.get("drozer_package_count"),
            "drozer_provider_count": signals.get("drozer_provider_count"),
            "drozer_activity_count": signals.get("drozer_activity_count"),
            "drozer_service_count": signals.get("drozer_service_count"),
            "drozer_receiver_count": signals.get("drozer_receiver_count"),
            "drozer_exposed_providers": signals.get("drozer_exposed_providers", []),
            "drozer_exposed_activities": signals.get("drozer_exposed_activities", []),
            "drozer_exposed_services": signals.get("drozer_exposed_services", []),
            "drozer_exposed_receivers": signals.get("drozer_exposed_receivers", []),
            "drozer_timestamp": signals.get("drozer_timestamp"),
            "binary_tampered":    signals.get("binary_tampered"),
        },
        "recommendations": _get_recommendations(score, signals)
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


def _get_recommendations(score: int, signals: dict) -> list:
    recs = []
    if signals.get("debug_enabled"):
        recs.append("Désactiver le mode debug (ro.debuggable=0)")
    if signals.get("su_found") or signals.get("magisk_found"):
        recs.append("Appareil rooté détecté — implémenter Play Integrity API")
    if signals.get("frida_running") or signals.get("xposed_found"):
        recs.append("Hook actif détecté — ajouter certificate pinning")
    if signals.get("selinux_permissive"):
        recs.append("Activer SELinux en mode Enforcing")
    if signals.get("drozer_available") and not signals.get("drozer_connected"):
        recs.append("Drozer disponible mais agent non connecté — vérifier le forward de port 31415")
    if signals.get("drozer_connected"):
        if signals.get("drozer_provider_count"):
            recs.append("Providers exposés détectés via Drozer — vérifier les composants publiquement accessibles")
        if signals.get("drozer_activity_count"):
            recs.append("Activities exposées détectées via Drozer — vérifier les composants exportés")
        if signals.get("drozer_service_count"):
            recs.append("Services exposés détectés via Drozer — vérifier les composants exportés")
        if signals.get("drozer_receiver_count"):
            recs.append("Broadcast receivers exposés détectés via Drozer — vérifier les composants exportés")
    if signals.get("binary_tampered"):
        recs.append("Tampering système détecté — ne pas faire confiance à ce device")
    if score < 40:
        recs.append("Environnement sain — continuer les audits réguliers")
    return recs