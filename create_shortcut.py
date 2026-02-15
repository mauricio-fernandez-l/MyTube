from pathlib import Path
from typing import Any
import sys

import win32com.client
from PIL import Image

from mytube.config import load_config


ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]


def _resample_method() -> Any:
    if hasattr(Image, "Resampling"):
        return Image.Resampling.LANCZOS
    return getattr(Image, "LANCZOS", 3)


def _fit_on_square_canvas(img: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    resized = img.copy()
    resized.thumbnail((size, size), _resample_method())
    x = (size - resized.width) // 2
    y = (size - resized.height) // 2
    canvas.paste(resized, (x, y), resized if resized.mode in ("RGBA", "LA") else None)
    return canvas


def create_shortcut():
    """Create desktop shortcut based on config.yaml settings"""
    config = load_config()

    # Get project directory
    project_dir = Path(__file__).parent.absolute()

    # Get shortcut settings from config
    shortcut_config = config.get("shortcut", {})
    shortcut_name = shortcut_config.get("name")
    icon_png_path = shortcut_config.get("icon_png")
    python_args = shortcut_config.get("python_args")
    if isinstance(python_args, list):
        python_args = " ".join(str(part) for part in python_args)
    else:
        python_args = str(python_args)

    # Build absolute paths
    png_path = project_dir / icon_png_path
    ico_path = png_path.with_suffix(".ico")

    # Convert PNG to multiple PNG icon sizes and a single ICO
    if png_path.exists():
        img = Image.open(png_path).convert("RGBA")
        ico_path.parent.mkdir(parents=True, exist_ok=True)

        generated_images = []
        for size in ICON_SIZES:
            icon_img = _fit_on_square_canvas(img, size)
            sized_png_path = png_path.with_name(f"{png_path.stem}_{size}x{size}.png")
            icon_img.save(sized_png_path, format="PNG")
            generated_images.append(icon_img)

        generated_images[-1].save(
            ico_path, format="ICO", sizes=[(size, size) for size in ICON_SIZES]
        )
        print(
            f"Created PNG icon sizes next to source PNG: {', '.join(str(s) for s in ICON_SIZES)}"
        )
        print(f"Created icon: {ico_path}")
    else:
        print(f"Warning: Icon PNG not found: {png_path}")
        ico_path = None

    # Create desktop shortcut
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / f"{shortcut_name}.lnk"

    venv_python = project_dir / ".venv" / "Scripts" / "python.exe"
    python_executable = venv_python if venv_python.exists() else Path(sys.executable)

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(python_executable)
    shortcut.Arguments = python_args
    shortcut.WorkingDirectory = str(project_dir)
    if ico_path and ico_path.exists():
        shortcut.IconLocation = str(ico_path)
    shortcut.save()
    print(f"Created desktop shortcut: {shortcut_path}")
    print(f"Shortcut command: {python_executable} {python_args}")


if __name__ == "__main__":
    create_shortcut()
