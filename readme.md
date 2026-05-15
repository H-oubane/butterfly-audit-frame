# Device Integrity Risk Scorer — Butterfly Audit Frame v1.0

Outil d'audit défensif Android — analyse passive d'un appareil et produit un score de risque (0-100).
Aucune modification du système. Observation uniquement.

---

## C'est quoi cet outil ?

Cet outil examine un appareil Android connecté à ton PC et répond à la question :
"Est-ce que ce téléphone est fiable ou compromis ?"

Il collecte des signaux techniques (root, debug, hooks, SELinux) et les agrège en un score de 0 à 100 avec des explications et des recommandations. Il ne modifie rien sur l'appareil — il observe uniquement.

---

## Ce qu'il faut installer — étape par étape

### Étape 1 — Python

1. Télécharger Python 3.9+ : https://www.python.org/downloads/
2. Lancer l'installateur
3. IMPORTANT : cocher "Add Python to PATH" avant de cliquer sur Install
4. Vérifier l'installation :
```bash
python --version
```
> Tu dois voir `Python 3.x.x`

---

### Étape 2 — ADB (Android Debug Bridge)

ADB est le pont de communication entre ton PC et le téléphone.

1. Télécharger Platform Tools : https://developer.android.com/tools/releases/platform-tools
2. Extraire le zip dans `C:\platform-tools\`
3. Vérifier :
```bash
C:\platform-tools\adb.exe version
```
> Tu dois voir `Android Debug Bridge version X.X.X`

---

### Étape 3 — Activer le mode développeur sur le téléphone

Sans cette étape, ADB ne peut pas communiquer avec le téléphone.

```
Parametres > A propos du telephone > Numero de build > Appuyer 7 fois
```
> Un message "Vous etes maintenant developpeur" apparait

```
Parametres > Options developpeur > Debogage USB > Activer
```

---

### Étape 4 — Connecter le téléphone et vérifier ADB

1. Brancher le téléphone en USB
2. Sur le téléphone : accepter la popup "Autoriser le debogage USB"
3. Vérifier :
```bash
C:\platform-tools\adb.exe devices
```
> Tu dois voir quelque chose comme :
```
List of devices attached
192.168.56.102:5555    device
```
> Si `unauthorized` — accepter la popup sur le téléphone
> Si rien n'apparait — vérifier le câble USB et que le débogage USB est activé

---

### Étape 5 — Frida (détection de hooks)

Frida est un framework d'instrumentation dynamique. L'outil détecte si Frida tourne sur l'appareil.

**Sur le PC — installer le client Frida :**
```bash
pip install frida frida-tools
```

**Sur le téléphone — optionnel, uniquement pour simuler un appareil compromis :**

> Si tu ne fais pas cette étape, l'outil fonctionne normalement.
> Frida sera simplement détecté comme absent (SECURISE).
> Cette étape sert uniquement à tester que la détection de hooks fonctionne.

1. Télécharger `frida-server` pour ARM64 : https://github.com/frida/frida/releases
   > Choisir `frida-server-XX.X.X-android-arm64.xz` — extraire pour obtenir `frida-server`

2. Envoyer sur le téléphone et démarrer :
```bash
C:\platform-tools\adb.exe push frida-server /data/local/tmp/
C:\platform-tools\adb.exe shell chmod +x /data/local/tmp/frida-server
C:\platform-tools\adb.exe shell /data/local/tmp/frida-server &
```

3. Vérifier :
```bash
frida-ps -U
```
> Tu dois voir la liste des processus du téléphone

---

### Étape 6 — Drozer (analyse de surface d'attaque) — OPTIONNEL

**Ce qu'il faut savoir :**
- Drozer n'est nécessaire **QUE** si tu veux analyser les composants exposés (avec `--with-drozer`)
- Sans Drozer, l'outil fonctionne normalement avec les 8 signaux de base
- **Les scans sont automatiques** — pas besoin de taper de commandes manuellement

---

**Sur le PC — installer le client Drozer :**
```bash
pip install drozer
```

**Sur le téléphone — installer l'agent Drozer :**

1. Télécharger `drozer-agent.apk` : https://github.com/WithSecureLabs/drozer/releases

2. Installer l'APK sur le téléphone :
```bash
C:\platform-tools\adb.exe install drozer-agent.apk
```

3. Configurer le port de communication :
```bash
C:\platform-tools\adb.exe forward tcp:31415 tcp:31415
```

4. Sur le téléphone : ouvrir l'application Drozer Agent et appuyer sur le bouton **Start Server** pour activer le serveur

5. **C'est tout !** L'outil détectera automatiquement l'agent au prochain lancement avec `--with-drozer`

---

**Vérifier manuellement (optionnel) :**
```bash
drozer console connect
```
> Tu dois voir le prompt `dz>` — la console Drozer est prête
> drozer console connect --server 127.0.0.1:31415 -c "echo test"
> # Doit afficher "test"
> ```


---

## Choisir son environnement de test

Avant de lancer l'outil, tu dois choisir quel type d'appareil utiliser.
Chaque option produit un score différent et permet de tester des scénarios différents.

### Option 1 — Téléphone physique non rooté 
> Environnement le plus proche de la réalité

- Téléphone Android classique, non modifié
- Debug USB activé uniquement pour le test
- Résultat attendu : FAIBLE — appareil sain

### Option 2 — Émulateur non rooté 
> Bon point de départ pour tester l'outil

Utiliser Genymotion ou Android AVD sans image rootée.

- Créer une machine virtuelle avec une image Android standard
- Connecter via ADB :
```bash
C:\platform-tools\adb.exe connect 192.168.56.102:5555
```


### Option 3 — Émulateur rooté 
> Pour simuler un appareil compromis et tester toutes les détections

**Avec Genymotion :**
- Genymotion propose des images avec root activé nativement
- Lors de la création de la VM : choisir une image avec "Root access" activé
- Ou activer le root depuis les paramètres Genymotion de la VM

**Avec Android AVD :**
- Choisir une image `Google APIs` (sans Play Store) — ces images autorisent le root
- Lancer l'émulateur avec le flag `-writable-system` :
```bash
emulator -avd NomDeLaVM -writable-system
```
- Puis activer root :
```bash
C:\platform-tools\adb.exe root
```

- Résultat attendu : ELEVE — root détecté, SELinux permissive, test-keys

> Pour aller plus loin et atteindre un score critique (90-100), lancer aussi frida-server
> sur l'émulateur rooté (voir Étape 5).

---

## Installation du projet

Une fois tous les prérequis installés :

```bash
cd "C:\chemin\vers\le\dossier\du\projet"
pip install .     
```

---

##  Utilisation rapide

### 1️ Audit sécurité standard

Vérifie les signaux de sécurité (debug, root, hooks, SELinux, permissions) :

```bash
python audit.py --audit
```

**Sortie :**
- Score de risque (0-100)
- Rapport détaillé dans le terminal
- Rapport JSON : `report/audit_report.json`

### 2️ Audit complet avec Drozer

Inclut la détection automatique de l'agent Drozer + analyse complète de la surface d'attaque :

```bash
python audit.py --audit --with-drozer
```

**Ce mode détecte automatiquement :**
✅ Agent Drozer opérationnel (connexion TCP 127.0.0.1:31415)
✅ Providers exposés (Content Providers non sécurisés)
✅ Activities exposées (écrans accessibles)
✅ Services exposés (tâches background accessibles)
✅ Broadcast receivers exposés (récepteurs de messages)
✅ Packages installés sur l'appareil

> **Note Windows :** Les scans détaillés sont automatiques. Pour une analyse interactive avancée, vous pouvez aussi lancer `drozer console connect` manuellement.

---


## Signaux analysés

| # | Signal | Ce qui est vérifié | Détails |
|---|---|---|---|
| 1 | Mode debug | ro.debuggable = 1 | Permet le débogage d'applications |
| 2 | Signature firmware | build tags = test-keys | Firmware non officiel |
| 3 | Binaire su (root) | /system/bin/su existe | Accès root potentiel |
| 4 | Magisk | Package/dossier Magisk | Framework root moderne |
| 5 | Frida | Processus frida-server actif | Hook dynamique détecté |
| 6 | Xposed / LSPosed | Package xposed/lsposed | Hook permanent détecté |
| 7 | SELinux | Mode Permissive | Contrôle d'accès désactivé |
| 8 | Intégrité binaires | Modification système détectée | Tampering potentiel |
| 9 | Permissions dangereuses | Contacts, Localisation, SMS, Caméra, etc. | Données sensibles accessibles |
| 10 | Drozer Agent (optionnel) | Connexion TCP 127.0.0.1:31415 | - Détection agent Drozer |

###  Autres fonctionnalités

**Drozer Detection (--with-drozer) :**
- Vérification automatique de la connexion TCP à l'agent Drozer
- Rapport détaillé sur la surface d'attaque Android
- Instructions interactives pour les scans manuels
- Identification des composants exposés (providers, activities, services, receivers)

**Permissions Dangereuses :**
- Collecte automatique des permissions sensibles
- Recommandations spécifiques par permission

---

| Score | Niveau | Signification |
|---|---|---|
| 0 - 39 | FAIBLE | Appareil sain, aucune anomalie critique |
| 40 - 69 | MOYEN | Signaux suspects, verifier la configuration |
| 70 - 100 | ELEVE | Appareil compromis, actions immediates requises |

---

## Recommandations automatiques

L'outil affiche des recommandations adaptées au score détecté :

- ELEVE : Play Integrity API, certificate pinning, anti-hooking, ne pas faire confiance au client
- MOYEN : audit des composants exportes, renforcement de la detection, surveillance continue
- FAIBLE : maintenir les bonnes pratiques, audits periodiques

---

## Dépannage

| Problème | Solution |
|---|---|
| `python audit.py` ne marche pas | Relancer le terminal ou vérifier que tu es dans le bon dossier |
| `python` introuvable | Reinstaller Python en cochant "Add to PATH" |
| Aucun device détecté | Vérifier câble USB + débogage USB actif |
| `unauthorized` sur `adb devices` | Accepter la popup d'autorisation sur le téléphone |
| `frida-ps -U` ne répond pas | Vérifier que frida-server tourne sur le téléphone |
| `pip install -r requirements.txt` échoue | Vérifier que tu es bien dans le dossier du projet |
| **Drozer : connexion échouée** | Vérifier que l'app Drozer Agent est active (Start Server) et que `adb forward tcp:31415 tcp:31415` a été lancée |
| **Drozer : aucun composant détecté** | Vérifier les permissions de l'agent Drozer (Android 11+: "Accès à toutes les applications") |
| **Drozer : analyse très lente** | Normal sur téléphone avec beaucoup d'applis (30-60 min possible) |
| Score très élevé sur émulateur | Normal sur émulateur rooté — c'est un environnement de test |

---

## Avertissement

Utiliser uniquement sur des appareils dont vous avez l'autorisation explicite.
Cet outil est strictement pedagogique et oriente securite defensive.
L'analyse d'appareils sans consentement est illegale.