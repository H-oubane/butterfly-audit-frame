# audit.py

import argparse
import sys
from collect.drozer_collect import collect_signals
from scorer.score_engine import final_score
from report.json_report import export_json


def main(use_drozer: bool = False):

    # Parser les arguments si appelé comme entry point (risk-scorer)
    if any(arg in sys.argv for arg in ["--audit", "--with-drozer"]):
        parser = argparse.ArgumentParser(prog="risk-scorer")
        parser.add_argument("--audit", action="store_true")
        parser.add_argument("--with-drozer", action="store_true")
        args = parser.parse_args()
        if not args.audit:
            print("Usage : risk-scorer --audit [--with-drozer]")
            return
        use_drozer = args.with_drozer

    # Couleurs thème HACK / AUDIT
    RED_DARK  = "\033[38;5;88m"
    RED_NEON  = "\033[38;5;196m"
    GOLD      = "\033[38;5;214m"
    CYAN      = "\033[36m"
    WHITE     = "\033[97m"
    DARK_GRAY = "\033[90m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    RESET     = "\033[0m"

    print(RED_DARK + r'''
              .==-.              .==-.  
             \()8`-._  `.   .'  _.-'8()/     
             (88"   ::.  \./  .::   "88)     
              \_.'`-::::.(#).::::-'`_/      
                `._... .q(_)p. ..._.'         
                  ""-..-'|=|`-..-""           
                  .""' .'|=|`. "".          
                ,':8(o)./|=|\.(o)8:`.        
               (O :8 ::/ \_/ \:: 8: O)       
                \O `::/       \::' O/        
                 ""--'         `--""         
''' + RESET)

    print(GOLD + r'''
        ✧･ﾟ: *✧･ﾟ:*  BAGUETTE MAGIQUE ACTIVE  *:･ﾟ✧*:･ﾟ✧
''' + RESET)

    print(RED_NEON + r'''
            /|_/|
           ( o.o )   
            > ^ <
''' + RESET)

    print(GOLD + r'''
            ✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧
               BUTTERFLY AUDIT FRAME
                      v1.0
            ✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧⋄⋆⋅⋆⋄✧
''' + RESET)

    print(CYAN + "=== DEVICE INTEGRITY AUDIT ===" + RESET)
    print(DARK_GRAY + "Analyse passive de l'environnement Android - Mode observation uniquement" + RESET)
    print("")

    signals = collect_signals(use_drozer=use_drozer)
    score, level = final_score(signals)

    # ========== INFORMATIONS APPAREIL ==========
    print(RED_NEON + "\n" + "="*60 + RESET)
    print(GOLD + "INFORMATIONS APPAREIL" + RESET)
    print(RED_NEON + "-"*60 + RESET)
    print(WHITE + f"  Appareil        : {signals['device_model']}" + RESET)
    print(WHITE + f"  Android         : {signals['android_version']}" + RESET)
    print(WHITE + f"  Date du scan    : {signals['timestamp'][:10]}" + RESET)

    # ========== SIGNAUX DE SECURITE ==========
    print(RED_NEON + "\n" + "="*60 + RESET)
    print(GOLD + "SIGNAUX DE SECURITE ANALYSES" + RESET)
    print(RED_NEON + "-"*60 + RESET)

    # Signal 1 : Debug enabled
    print(CYAN + "\n[1] Mode Debug Android" + RESET)
    if signals['debug_enabled']:
        print(RED_NEON + "    DANGER : ro.debuggable = 1" + RESET)
        print(DARK_GRAY + "    -> Explication : L'appareil est en mode debug. N'importe quelle application" + RESET)
        print(DARK_GRAY + "       peut deboguer votre app et acceder aux donnees sensibles." + RESET)
        print(DARK_GRAY + "    -> Risque : Elevation de privileges, vol de donnees" + RESET)
    else:
        print(GREEN + "    SECURISE : ro.debuggable = 0" + RESET)
        print(DARK_GRAY + "    -> Explication : Le mode debug est desactive." + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 2 : Build tags
    print(CYAN + "\n[2] Signature du firmware" + RESET)
    if signals['build_tags_test']:
        print(RED_NEON + "    DANGER : build tags = test-keys" + RESET)
        print(DARK_GRAY + "    -> Explication : Le firmware n'est pas officiel (test-keys)." + RESET)
        print(DARK_GRAY + "       Il peut avoir ete modifie par un tiers." + RESET)
        print(DARK_GRAY + "    -> Risque : Firmware non fiable, backdoor possible" + RESET)
    else:
        print(GREEN + "    SECURISE : build tags = release-keys" + RESET)
        print(DARK_GRAY + "    -> Explication : Firmware officiel signe par le constructeur." + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 3 : Root (su)
    print(CYAN + "\n[3] Binaire su (root)" + RESET)
    if signals['su_found']:
        print(RED_NEON + "    DANGER : su trouve" + RESET)
        print(DARK_GRAY + "    -> Explication : Le binaire 'su' permet l'execution de commandes" + RESET)
        print(DARK_GRAY + "       avec les privileges root (administrateur)." + RESET)
        print(DARK_GRAY + "    -> Risque : Acces total a l'appareil, bypass du sandboxing" + RESET)
    else:
        print(GREEN + "    SECURISE : su non trouve" + RESET)
        print(DARK_GRAY + "    -> Explication : Aucun binaire d'elevation de privileges detecte." + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 4 : Magisk
    print(CYAN + "\n[4] Framework Magisk (root moderne)" + RESET)
    if signals['magisk_found']:
        print(RED_NEON + "    DANGER : Magisk detecte" + RESET)
        print(DARK_GRAY + "    -> Explication : Magisk est un framework de root moderne qui" + RESET)
        print(DARK_GRAY + "       tente de se cacher des detections classiques." + RESET)
        print(DARK_GRAY + "    -> Risque : Root invisible, modifications systeme" + RESET)
    else:
        print(GREEN + "    SECURISE : Magisk non detecte" + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 5 : Frida
    print(CYAN + "\n[5] Frida (hook framework)" + RESET)
    if signals['frida_running']:
        print(RED_NEON + "    DANGER : Frida actif" + RESET)
        print(DARK_GRAY + "    -> Explication : Frida permet d'intercepter et modifier les" + RESET)
        print(DARK_GRAY + "       appels de methodes Java/Python a l'execution." + RESET)
        print(DARK_GRAY + "    -> Risque : Espionnage des methodes, contournement de securites" + RESET)
    else:
        print(GREEN + "    SECURISE : Frida non detecte" + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 6 : Xposed
    print(CYAN + "\n[6] XPosed / LSPosed (hook permanent)" + RESET)
    if signals['xposed_found']:
        print(RED_NEON + "    DANGER : XPosed detecte" + RESET)
        print(DARK_GRAY + "    -> Explication : XPosed modifie le runtime Android de facon" + RESET)
        print(DARK_GRAY + "       permanente pour intercepter les appels systeme." + RESET)
        print(DARK_GRAY + "    -> Risque : Modification permanente, contournement generalise" + RESET)
    else:
        print(GREEN + "    SECURISE : XPosed non detecte" + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 7 : SELinux
    print(CYAN + "\n[7] SELinux (protection MAC)" + RESET)
    if signals['selinux_permissive']:
        print(YELLOW + "    WARNING : SELinux en mode Permissive" + RESET)
        print(DARK_GRAY + "    -> Explication : SELinux en mode Permissive n'applique aucune" + RESET)
        print(DARK_GRAY + "       politique de securite. Toutes les actions sont autorisees." + RESET)
        print(DARK_GRAY + "    -> Risque : Protection desactivee, aucun controle d'acces" + RESET)
    else:
        print(GREEN + "    SECURISE : SELinux en mode Enforcing" + RESET)
        print(DARK_GRAY + "    -> Explication : Les politiques de securite sont appliquees." + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 8 : Binaire altere
    print(CYAN + "\n[8] Integrite des binaires systeme" + RESET)
    if signals['binary_tampered']:
        print(RED_NEON + "    DANGER : Binaires systeme modifies" + RESET)
        print(DARK_GRAY + "    -> Explication : Les checksums des binaires ne correspondent" + RESET)
        print(DARK_GRAY + "       pas aux valeurs de reference." + RESET)
        print(DARK_GRAY + "    -> Risque : Tampering confirme du systeme" + RESET)
    else:
        print(GREEN + "    SECURISE : Binaires integres" + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # Signal 9 : Permissions dangereuses
    print(CYAN + "\n[9] Permissions dangereuses" + RESET)
    dangerous_perms = signals.get('dangerous_permissions', [])
    if dangerous_perms:
        print(RED_NEON + f"    DANGER : {len(dangerous_perms)} permission(s) dangereuse(s) detectee(s)" + RESET)
        print(DARK_GRAY + "    -> Explication : Des applications peuvent acceder a vos donnees sensibles" + RESET)
        print(DARK_GRAY + "    -> Permissions : " + ", ".join(dangerous_perms) + RESET)
        print(DARK_GRAY + "    -> Risque : Exposition des donnees personnelles, vie privee" + RESET)
    else:
        print(GREEN + "    SECURISE : Aucune permission dangereuse detectee" + RESET)
        print(DARK_GRAY + "    -> Statut : CONFORME" + RESET)

    # ========== DROZER - SURFACE D'ATTAQUE ==========
    if use_drozer:
        print(RED_NEON + "\n" + "="*60 + RESET)
        print(GOLD + "DROZER - SURFACE D'ATTAQUE ANDROID" + RESET)
        print(RED_NEON + "-"*60 + RESET)

        if signals.get('drozer_available'):
            if signals.get('drozer_connected'):
                print(GREEN + "✓ CONNEXION ETABLIE" + RESET)
                print(DARK_GRAY + f"  Timestamp : {signals.get('drozer_timestamp', 'N/A')}" + RESET)
                print(CYAN + "\n  Resultats des scans automatiques :" + RESET)

                # Packages
                pkg_count = signals.get('drozer_package_count', 0)
                print(WHITE + f"  Packages installes       : {pkg_count}" + RESET)

                # Providers
                prov = signals.get('drozer_exposed_providers', [])
                if prov:
                    print(RED_NEON + f"  Providers exposes        : {len(prov)}" + RESET)
                    for p in prov[:5]:
                        print(DARK_GRAY + f"    - {p}" + RESET)
                    if len(prov) > 5:
                        print(DARK_GRAY + f"    ... et {len(prov)-5} autres" + RESET)
                else:
                    print(GREEN + "  Providers exposes        : 0 (aucun)" + RESET)

                # Activities
                acts = signals.get('drozer_exposed_activities', [])
                if acts:
                    print(RED_NEON + f"  Activities exposees      : {len(acts)}" + RESET)
                    for a in acts[:5]:
                        print(DARK_GRAY + f"    - {a}" + RESET)
                    if len(acts) > 5:
                        print(DARK_GRAY + f"    ... et {len(acts)-5} autres" + RESET)
                else:
                    print(GREEN + "  Activities exposees      : 0 (aucune)" + RESET)

                # Services
                svcs = signals.get('drozer_exposed_services', [])
                if svcs:
                    print(RED_NEON + f"  Services exposes         : {len(svcs)}" + RESET)
                    for s in svcs[:5]:
                        print(DARK_GRAY + f"    - {s}" + RESET)
                    if len(svcs) > 5:
                        print(DARK_GRAY + f"    ... et {len(svcs)-5} autres" + RESET)
                else:
                    print(GREEN + "  Services exposes         : 0 (aucun)" + RESET)

                # Receivers
                rcvs = signals.get('drozer_exposed_receivers', [])
                if rcvs:
                    print(RED_NEON + f"  Broadcast receivers      : {len(rcvs)}" + RESET)
                    for r in rcvs[:5]:
                        print(DARK_GRAY + f"    - {r}" + RESET)
                    if len(rcvs) > 5:
                        print(DARK_GRAY + f"    ... et {len(rcvs)-5} autres" + RESET)
                else:
                    print(GREEN + "  Broadcast receivers      : 0 (aucun)" + RESET)

                raw = signals.get('drozer_output', '').strip()
                if raw:
                    print(DARK_GRAY + f"\n  Recap : {raw}" + RESET)

            else:
                print(RED_NEON + "✗ CONNEXION ECHOUEE" + RESET)
                print(DARK_GRAY + "  L'agent Drozer n'est pas joignable sur 127.0.0.1:31415" + RESET)
                print(YELLOW + "\n  DIAGNOSTIC:" + RESET)
                print(DARK_GRAY + "  • Verifier que l'app 'Drozer Agent' est installee et lancee" + RESET)
                print(DARK_GRAY + "  • Verifier le forward de port :" + RESET)
                print(YELLOW + "    adb forward tcp:31415 tcp:31415" + RESET)
        else:
            print(RED_NEON + "✗ CLIENT NON DETECTE" + RESET)
            print(DARK_GRAY + "  Drozer n'est pas present dans le PATH du systeme" + RESET)
            print(YELLOW + "\n  INSTALLATION:" + RESET)
            print(YELLOW + "  pip install drozer" + RESET)

    # ========== SCORE ==========
    print(RED_NEON + "\n" + "="*60 + RESET)
    print(GOLD + "SCORE DE RISQUE" + RESET)
    print(RED_NEON + "-"*60 + RESET)

    if score >= 70:
        stars = "★★★"
        level_color = RED_NEON
    elif score >= 40:
        stars = "★★☆"
        level_color = GOLD
    else:
        stars = "★☆☆"
        level_color = CYAN

    print(level_color + f"\n  SCORE FINAL : {score}/100 [{level}] {stars}" + RESET)

    bar_length = 30
    filled = int(bar_length * score / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(level_color + f"  [{bar}]" + RESET)

    # ========== RECOMMANDATIONS ==========
    print(RED_NEON + "\n" + "="*60 + RESET)
    print(GOLD + "RECOMMANDATIONS" + RESET)
    print(RED_NEON + "-"*60 + RESET)

    rec_list = []

    if signals['debug_enabled']:
        rec_list.append("Mode debug actif : Desactiver ro.debuggable en production (modifier build.prop)")
    if signals['build_tags_test']:
        rec_list.append("Firmware test-keys : Reinstaller un firmware officiel release-keys")
    if signals['su_found']:
        rec_list.append("Root present (su) : Ne pas faire confiance au client - Verifier cote serveur")
    if signals['magisk_found']:
        rec_list.append("Magisk detecte : Ajouter Play Integrity API / SafetyNet attestation")
    if signals['frida_running']:
        rec_list.append("Frida actif : Ajouter anti-debug (ptrace, /proc/self/status) et obfuscation .so")
    if signals['xposed_found']:
        rec_list.append("Xposed/LSPosed detecte : Verifier l'integrite du code a l'execution")
    if signals['selinux_permissive']:
        rec_list.append("SELinux permissif : Activer Enforcing via setenforce 1")
    if signals['binary_tampered']:
        rec_list.append("Binaires systeme modifies : Reinstaller le firmware d'origine")
    if dangerous_perms:
        rec_list.append(f"Permissions dangereuses ({len(dangerous_perms)}) : Verifier les applications ayant acces aux donnees sensibles")
    if use_drozer and signals.get('drozer_connected'):
        if signals.get('drozer_provider_count'):
            rec_list.append("Providers exposes detectes : Verifier android:exported dans le manifest")
        if signals.get('drozer_activity_count'):
            rec_list.append("Activities exposees detectees : Verifier android:exported dans le manifest")
        if signals.get('drozer_service_count'):
            rec_list.append("Services exposes detectes : Verifier android:exported dans le manifest")
        if signals.get('drozer_receiver_count'):
            rec_list.append("Receivers exposes detectes : Verifier android:exported dans le manifest")

    if rec_list:
        print(RED_NEON + "\n  Actions correctives :\n" + RESET)
        for i, rec in enumerate(rec_list, 1):
            print(WHITE + f"  {i}. {rec}" + RESET)

        print(RED_NEON + "\n" + "-"*60 + RESET)
        print(GOLD + "Commandes rapides :" + RESET)
        print(RED_NEON + "-"*60 + RESET)

        if signals['debug_enabled']:
            print(DARK_GRAY + "  adb shell \"su -c 'setprop ro.debuggable 0'\"" + RESET)
        if signals['selinux_permissive']:
            print(DARK_GRAY + "  adb shell setenforce 1" + RESET)
        if signals['frida_running']:
            print(DARK_GRAY + "  adb shell pkill frida" + RESET)
        if signals['su_found'] or signals['magisk_found']:
            print(DARK_GRAY + "  Implementer Play Integrity API (cote serveur)" + RESET)
        if dangerous_perms:
            print(DARK_GRAY + "  adb shell dumpsys package permissions | grep -E 'READ_CONTACTS|ACCESS_FINE_LOCATION|RECORD_AUDIO|CAMERA'" + RESET)
    else:
        print(CYAN + "\n  Aucune action corrective requise\n" + RESET)

    print(RED_NEON + "\n" + "="*60 + RESET)
    print("\n" + GOLD + "  ✧･ﾟ: *✧･ﾟ:*  AUDIT TERMINE  *:･ﾟ✧*:･ﾟ✧" + RESET + "\n")

    export_json(signals, score, level)


if __name__ == "__main__":
    main()