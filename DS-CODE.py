```python
import os
import subprocess

ascii_art = r"""
██████╗ ███████╗      ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║  ██║███████╗     ██║     ██║   ██║██║  ██║█████╗
██║  ██║╚════██║     ██║     ██║   ██║██║  ██║██╔══╝
██████╔╝███████║     ╚██████╗╚██████╔╝██████╔╝███████╗
╚═════╝ ╚══════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝

                    by : Chrxs
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def build_exe(py_file):

    if not os.path.exists(py_file):
        print("\n[!] Fichier introuvable.")
        return

    print("\n[+] Génération du fichier EXE...\n")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        py_file
    ]

    try:
        subprocess.run(cmd, check=True)

        print("\n[✓] EXE généré avec succès.")
        print("[✓] Regarde dans le dossier : dist/")

    except Exception as e:
        print(f"\n[!] Erreur : {e}")


def build_apk(py_file):

    if not os.path.exists(py_file):
        print("\n[!] Fichier introuvable.")
        return

    app_name = input("\nNom de l'application : ")
    package_name = input("Nom du package (ex: com.test.app) : ")

    print("\n[+] Initialisation Buildozer...\n")

    try:
        os.system("buildozer init")

        if os.path.exists("buildozer.spec"):

            with open("buildozer.spec", "r", encoding="utf-8") as f:
                data = f.read()

            data = data.replace(
                "title = My Application",
                f"title = {app_name}"
            )

            data = data.replace(
                "package.name = myapp",
                f"package.name = {app_name.lower()}"
            )

            data = data.replace(
                "package.domain = org.test",
                f"package.domain = {package_name}"
            )

            with open("buildozer.spec", "w", encoding="utf-8") as f:
                f.write(data)

        print("\n[+] Génération du fichier APK...\n")

        subprocess.run(
            ["buildozer", "android", "debug"],
            check=True
        )

        print("\n[✓] APK généré avec succès.")
        print("[✓] Regarde dans le dossier : bin/")

    except Exception as e:
        print(f"\n[!] Erreur : {e}")


def install_requirements():

    print("""
=====================================
INSTALLATION DES DEPENDANCES
=====================================

[1] Installer PyInstaller
[2] Installer Buildozer
[3] Retour

=====================================
""")

    choice = input("Choix : ")

    if choice == "1":

        subprocess.run([
            "pip",
            "install",
            "pyinstaller"
        ])

    elif choice == "2":

        subprocess.run([
            "pip",
            "install",
            "buildozer"
        ])

        subprocess.run([
            "pip",
            "install",
            "cython"
        ])

    elif choice == "3":
        return

    else:
        print("\n[!] Choix invalide.")


def main():

    clear()

    print(ascii_art)

    print("""
=====================================
        DS-CODE BUILDER
=====================================

[1] Transformer en EXE
[2] Transformer en APK
[3] Installer les dépendances
[4] Quitter

=====================================
""")

    choice = input("Choix : ")

    if choice == "1":

        py_file = input("\nEntrez votre fichier .py : ")
        build_exe(py_file)

    elif choice == "2":

        py_file = input("\nEntrez votre fichier .py : ")
        build_apk(py_file)

    elif choice == "3":

        install_requirements()

    elif choice == "4":

        print("\n[✓] Fermeture du programme.")

    else:

        print("\n[!] Choix invalide.")


if __name__ == "__main__":
    main()
```
