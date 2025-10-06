from PIL import Image
import win32com.client
from pathlib import Path

# Configuration
PNG_PATH = "images/my_image.png"  # Change this to your PNG file path
SHORTCUT_NAME = "MyTube"  # Change this to your desired shortcut name

# Convert PNG to ICO
project_dir = Path(__file__).parent.absolute()
png_path = project_dir / PNG_PATH
ico_path = project_dir / f"images/{SHORTCUT_NAME}.ico"

img = Image.open(png_path)
img.save(ico_path, format="ICO", sizes=[(32, 32)])

# Create launcher batch file
batch_content = f"""@echo off
cd /d "{project_dir}"
.venv\\Scripts\\python.exe launch.py
"""
batch_path = project_dir / "launch.bat"
with open(batch_path, "w") as f:
    f.write(batch_content)

# Create desktop shortcut
desktop_path = Path.home() / "Desktop"
shortcut_path = desktop_path / f"{SHORTCUT_NAME}.lnk"

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(str(shortcut_path))
shortcut.Targetpath = str(batch_path)
shortcut.WorkingDirectory = str(project_dir)
shortcut.IconLocation = str(ico_path)
shortcut.save()
