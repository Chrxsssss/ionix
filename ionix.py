import os
import re
import subprocess
import sys

ascii_art = r"""
██╗ ██████╗ ███╗   ██╗██╗██╗  ██╗
██║██╔═══██╗████╗  ██║██║╚██╗██╔╝
██║██║   ██║██╔██╗ ██║██║ ╚███╔╝
██║██║   ██║██║╚██╗██║██║ ██╔██╗
██║╚██████╔╝██║ ╚████║██║██╔╝ ██╗
╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝ (HBH) (DS) (Ghosty)

                 by : Chrxs
"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[!] La commande a échoué (code {e.returncode}) : {' '.join(cmd)}")
    except FileNotFoundError:
        print(f"\n[!] Commande introuvable : {cmd[0]}")
    except Exception as e:
        print(f"\n[!] Erreur : {e}")
    return False


def sanitize_package_name(name):
    return re.sub(r"[^0-9a-zA-Z_.]", "", name.strip())


def sanitize_app_name(name):
    return re.sub(r"[^0-9a-zA-Z_\- ]", "", name.strip())


# FIX 1 : validation du fichier .py (extension + existence + pas un dossier)
def validate_py_file(py_file):
    # FIX 10 : retire guillemets simples/doubles collés par copier-coller
    py_file = py_file.strip().strip('"').strip("'")

    if not py_file:
        print("\n[!] Aucun fichier saisi.")
        return None

    if os.path.isdir(py_file):
        print(f"\n[!] '{py_file}' est un dossier, pas un fichier .py.")
        return None

    if not py_file.lower().endswith(".py"):
        print(f"\n[!] Le fichier doit avoir l'extension .py (reçu : '{py_file}').")
        return None

    if not os.path.isfile(py_file):
        print(f"\n[!] Fichier introuvable : '{py_file}'")
        return None

    return os.path.abspath(py_file)  # FIX 2 : toujours utiliser le chemin absolu


def build_exe(py_file):
    py_file = validate_py_file(py_file)
    if not py_file:
        return

    print("\n[+] Génération du fichier EXE...\n")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        # FIX 3 : --noconsole retiré par défaut pour voir les erreurs éventuelles.
        # Décommentez la ligne suivante si vous voulez cacher la console :
        # "--noconsole",
        py_file,
    ]

    if run_command(cmd):
        print("\n[✓] EXE généré avec succès.")
        print("[✓] Regarde dans le dossier : dist/")


def is_buildozer_available():
    """
    Détecte buildozer via 3 méthodes pour couvrir tous les cas d'installation
    (pip standard, --break-system-packages, pipx, chemin alternatif...).
    """
    # Méthode 1 : commande 'buildozer' directe dans le PATH
    try:
        r = subprocess.run(["buildozer", "--version"], capture_output=True)
        if r.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Méthode 2 : python -m buildozer (cas pip --break-system-packages)
    try:
        r = subprocess.run(
            [sys.executable, "-m", "buildozer", "--version"],
            capture_output=True
        )
        if r.returncode == 0:
            return True
    except Exception:
        pass

    # Méthode 3 : importlib (dernier recours)
    import importlib.util
    return importlib.util.find_spec("buildozer") is not None


def validate_package_name(package_name):
    """
    Valide le format du nom de package Android.
    Règles : au moins 2 segments séparés par '.', chaque segment
    commence par une lettre minuscule, contient uniquement [a-z0-9_].
    Ex valide   : com.chrxs.rsw
    Ex invalides: Ch4.test.app  /  com  /  com.1test.app
    """
    segments = package_name.split(".")
    if len(segments) < 2:
        return False
    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    return all(pattern.match(s) for s in segments)


def is_java_available():
    """Vérifie que javac (Java JDK) est installé et accessible."""
    try:
        r = subprocess.run(["javac", "-version"], capture_output=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def build_apk(py_file):
    if os.name == "nt":
        print("\n[!] Buildozer n'est pas pris en charge sous Windows.")
        print("    Utilisez Linux, WSL ou une VM.")
        return

    # FIX 11 : vérifier que Buildozer est installé AVANT de demander les infos
    if not is_buildozer_available():
        print("\n[!] Buildozer n'est pas installé.")
        print("    → Allez dans [3] Installer les dépendances → [2] Installer Buildozer + Cython")
        return

    # FIX 13 : vérifier que Java JDK est installé (requis par Buildozer)
    if not is_java_available():
        print("\n[!] Java JDK (javac) est introuvable.")
        print("    Installez-le avec :")
        print("    sudo apt install default-jdk -y")
        print("    Puis vérifiez : javac -version")
        return

    py_file = validate_py_file(py_file)
    if not py_file:
        return

    app_name = sanitize_app_name(input("\nNom de l'application : "))
    if not app_name:
        print("\n[!] Nom d'application invalide.")
        return

    # FIX 12 : validation stricte du package + message d'aide clair
    while True:
        package_name = sanitize_package_name(input("Nom du package (ex: com.chrxs.monapp) : "))
        if validate_package_name(package_name):
            break
        print("\n[!] Format invalide. Règles :")
        print("    - Au moins 2 segments séparés par '.'")
        print("    - Chaque segment commence par une lettre MINUSCULE")
        print("    - Uniquement lettres minuscules, chiffres, underscores")
        print("    - Exemple correct : com.chrxs.rsw\n")

    wrapper_created = False

    try:
        if os.path.basename(py_file).lower() != "main.py":

            if os.path.exists("main.py"):
                print("\n[!] main.py existe déjà dans ce dossier, renommez-le d'abord.")
                return

            with open("main.py", "w", encoding="utf-8") as wrapper:
                wrapper.write("import runpy\n")
                wrapper.write(f"runpy.run_path(r'{py_file}', run_name='__main__')\n")

            wrapper_created = True

        if not os.path.exists("buildozer.spec"):
            print("\n[+] Initialisation Buildozer...\n")
            if not run_command([sys.executable, "-m", "buildozer", "init"]):
                return
        else:
            print("\n[i] buildozer.spec déjà présent, réutilisation.")

        if not os.path.exists("buildozer.spec"):
            print("\n[!] buildozer.spec introuvable après init.")
            return

        with open("buildozer.spec", "r", encoding="utf-8") as f:
            data = f.read()

        data = re.sub(r"(?m)^title\s*=.*$", f"title = {app_name}", data)
        data = re.sub(
            r"(?m)^package\.name\s*=.*$",
            f"package.name = {app_name.lower().replace(' ', '_')}",
            data,
        )
        data = re.sub(
            r"(?m)^package\.domain\s*=.*$",
            f"package.domain = {package_name}",
            data,
        )

        with open("buildozer.spec", "w", encoding="utf-8") as f:
            f.write(data)

        print("\n[+] Génération du fichier APK...\n")

        if run_command([sys.executable, "-m", "buildozer", "android", "debug"]):
            print("\n[✓] APK généré avec succès.")
            print("[✓] Regarde dans le dossier : bin/")
        else:
            print("\n[!] Échec de génération APK.")

    finally:
        if wrapper_created and os.path.exists("main.py"):
            os.remove("main.py")


# FIX 5 : détecte si pip est bloqué par le système (Kali, Ubuntu 23+, Debian 12+)
# et ajoute automatiquement --break-system-packages si nécessaire.
def pip_install(*packages):
    base_cmd = [sys.executable, "-m", "pip", "install"] + list(packages)

    # Teste d'abord sans le flag
    result = subprocess.run(
        base_cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return True

    # FIX 6 : si l'erreur est "externally-managed-environment", réessaye avec le flag
    if "externally-managed-environment" in result.stderr or "externally managed" in result.stderr:
        print("\n[i] Environnement géré par le système détecté, ajout de --break-system-packages...")
        return run_command(base_cmd + ["--break-system-packages"])

    # Autre erreur : affiche le message et retourne False
    print(f"\n[!] Erreur pip :\n{result.stderr.strip()}")
    return False


def install_requirements():
    while True:
        print("""
=====================================
INSTALLATION DES DEPENDANCES
=====================================

[1] Installer PyInstaller
[2] Installer Buildozer + Cython
[3] Retour

=====================================
""")
        choice = input("Choix : ").strip()

        if choice == "1":
            # FIX 7 : mise à jour de pip avant installation pour éviter les erreurs de résolution
            print("\n[+] Mise à jour de pip...\n")
            pip_install("--upgrade", "pip")

            print("\n[+] Installation de PyInstaller...\n")
            if pip_install("pyinstaller"):
                print("\n[✓] PyInstaller installé.")
            else:
                print("\n[!] Échec de l'installation de PyInstaller.")

        elif choice == "2":
            if os.name == "nt":
                print("\n[!] Buildozer n'est pas pris en charge sous Windows.")
                print("    Utilisez Linux, WSL ou une VM.")
                continue

            # FIX 8 : mise à jour de pip + installation groupée pour éviter les conflits de dépendances
            print("\n[+] Mise à jour de pip...\n")
            pip_install("--upgrade", "pip")

            print("\n[+] Installation de Buildozer et Cython...\n")
            # FIX 9 : installation groupée (un seul appel) = résolution de dépendances cohérente
            if pip_install("buildozer", "cython"):
                print("\n[✓] Buildozer et Cython installés.")
            else:
                print("\n[!] Une ou plusieurs installations ont échoué.")

        elif choice == "3":
            return

        else:
            print("\n[!] Choix invalide.")


def main():
    while True:
        clear()
        print(ascii_art)
        print("""
=====================================
           IONIX MENU
=====================================

[1] Transformer en EXE
[2] Transformer en APK
[3] Installer les dépendances
[4] Quitter

=====================================
""")
        choice = input("Choix : ").strip()

        if choice == "1":
            py_file = input("\nEntrez votre fichier .py : ").strip()
            build_exe(py_file)
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "2":
            py_file = input("\nEntrez votre fichier .py : ").strip()
            build_apk(py_file)
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "3":
            install_requirements()

        elif choice == "4":
            print("\n[✓] Fermeture du programme.")
            break

        else:
            print("\n[!] Choix invalide.")
            input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
