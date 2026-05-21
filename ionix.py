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
    # BUG FIX 1 : on retire aussi les caractères qui casseraient le fichier .spec
    return re.sub(r"[^0-9a-zA-Z_\- ]", "", name.strip())


def build_exe(py_file):
    if not os.path.exists(py_file):
        print("\n[!] Fichier introuvable.")
        return

    print("\n[+] Génération du fichier EXE...\n")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        py_file,
    ]

    if run_command(cmd):
        print("\n[✓] EXE généré avec succès.")
        print("[✓] Regarde dans le dossier : dist/")


def build_apk(py_file):
    if os.name == "nt":
        print("\n[!] Buildozer n'est pas pris en charge sous Windows.")
        print("    Utilisez Linux, WSL ou une VM.")
        return

    if not os.path.exists(py_file):
        print("\n[!] Fichier introuvable.")
        return

    app_name = sanitize_app_name(input("\nNom de l'application : "))
    package_name = sanitize_package_name(input("Nom du package (ex: com.test.app) : "))

    if not app_name:
        print("\n[!] Nom invalide.")
        return

    if not package_name or "." not in package_name:
        print("\n[!] Package invalide.")
        return

    wrapper_created = False

    try:
        if os.path.basename(py_file).lower() != "main.py":

            if os.path.exists("main.py"):
                print("\n[!] main.py existe déjà dans ce dossier, renommez-le d'abord.")
                return

            # BUG FIX 2 : utiliser os.path.abspath pour un chemin fiable dans runpy
            abs_py_file = os.path.abspath(py_file).replace("\\", "/")

            with open("main.py", "w", encoding="utf-8") as wrapper:
                wrapper.write("import runpy\n")
                wrapper.write(f"runpy.run_path(r'{abs_py_file}', run_name='__main__')\n")

            wrapper_created = True

        # BUG FIX 3 : ne pas relancer buildozer init si le spec existe déjà
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

        # BUG FIX 4 : utiliser re.sub pour remplacer même si le spec a déjà
        # été modifié (évite un remplacement silencieusement raté)
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
        # BUG FIX 5 : garantir la suppression de main.py même en cas d'erreur
        if wrapper_created and os.path.exists("main.py"):
            os.remove("main.py")


def install_requirements():
    while True:
        print("""
=====================================
INSTALLATION DES DEPENDANCES
=====================================

[1] Installer PyInstaller
[2] Installer Buildozer
[3] Retour

=====================================
""")
        choice = input("Choix : ").strip()

        if choice == "1":
            # BUG FIX 6 : afficher le résultat de run_command
            if run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
                print("\n[✓] PyInstaller installé.")
            else:
                print("\n[!] Échec de l'installation de PyInstaller.")

        elif choice == "2":
            ok1 = run_command([sys.executable, "-m", "pip", "install", "buildozer"])
            ok2 = run_command([sys.executable, "-m", "pip", "install", "cython"])
            if ok1 and ok2:
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
