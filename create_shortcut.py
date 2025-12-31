from pathlib import Path

import win32com.client
from PIL import Image

from mytube.config import load_config


def create_shortcut():
    """Create desktop shortcut based on config.yaml settings"""
    config = load_config()

    # Get project directory
    project_dir = Path(__file__).parent.absolute()

    # Get shortcut settings from config
    shortcut_config = config.get("shortcut", {})
    shortcut_name = shortcut_config.get("name", "MyTube")
    icon_png_path = shortcut_config.get("icon_png", "images/my_image.png")
    icon_ico_path = shortcut_config.get("icon_ico", f"images/{shortcut_name}.ico")

    # Build absolute paths
    png_path = project_dir / icon_png_path
    ico_path = project_dir / icon_ico_path

    # Convert PNG to ICO
    if png_path.exists():
        img = Image.open(png_path)
        ico_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(ico_path, format="ICO", sizes=[(32, 32)])
        print(f"Created icon: {ico_path}")
    else:
        print(f"Warning: Icon PNG not found: {png_path}")
        ico_path = None

    # Create launcher batch file
    batch_content = f"""@echo off
cd /d "{project_dir}"
.venv\\Scripts\\python.exe launch.py
"""
    batch_path = project_dir / "launch.bat"
    with open(batch_path, "w") as f:
        f.write(batch_content)
    print(f"Created launcher: {batch_path}")

    # Create desktop shortcut
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / f"{shortcut_name}.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(batch_path)
    shortcut.WorkingDirectory = str(project_dir)
    if ico_path and ico_path.exists():
        shortcut.IconLocation = str(ico_path)
    shortcut.save()
    print(f"Created desktop shortcut: {shortcut_path}")


if __name__ == "__main__":
    create_shortcut()
