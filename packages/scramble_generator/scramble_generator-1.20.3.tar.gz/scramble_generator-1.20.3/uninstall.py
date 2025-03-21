import os
import sys
import shutil


def print_green(skk):
    print("\033[92m {}\033[00m".format(skk))


def get_venv_path():
    home_dir = os.path.expanduser("~")
    venv_dir = os.path.join(home_dir, ".venvs")
    return os.path.join(venv_dir, "scramble_generator_venv")


def get_desktop_file_path():
    return os.path.expanduser("~/.local/share/applications/scramble_generator.desktop")


def uninstall():
    venv_path = get_venv_path()
    desktop_file_path = get_desktop_file_path()

    if os.path.exists(venv_path):
        print("Removing the virtual environment...", end="")
        sys.stdout.flush()
        shutil.rmtree(venv_path)
        print_green("󰄬")

    if os.path.exists(desktop_file_path):
        print("Removing the .desktop entry...", end="")
        sys.stdout.flush()
        os.remove(desktop_file_path)
        print_green("󰄬")


def main():
    uninstall()


if __name__ == "__main__":
    main()
