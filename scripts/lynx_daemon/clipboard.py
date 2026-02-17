"""Clipboard copy and text-insertion helpers (Wayland + X11)."""
from __future__ import annotations

import os
import shutil
import subprocess

from .config import cfg


def _is_wayland() -> bool:
    return (
        os.getenv("XDG_SESSION_TYPE", "").lower() == "wayland"
        or bool(os.getenv("WAYLAND_DISPLAY"))
    )


def copy_to_clipboard(text: str) -> bool:
    """Copy *text* to the system clipboard. Returns ``True`` on success."""
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode(), check=False)
        return True
    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"], input=text.encode(), check=False
        )
        return True
    return False


def paste_into_active_window(text: str) -> bool:
    """Simulate a paste (or type) into the currently focused window."""
    if not cfg.auto_paste:
        return False

    if _is_wayland():
        if cfg.insert_mode == "type" and shutil.which("wtype"):
            return subprocess.run(["wtype", text], check=False).returncode == 0
        if shutil.which("wtype"):
            return (
                subprocess.run(
                    ["wtype", "-M", "ctrl", "v", "-m", "ctrl"], check=False
                ).returncode
                == 0
            )
        return False

    if shutil.which("xdotool"):
        if (
            subprocess.run(
                ["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=False
            ).returncode
            == 0
        ):
            return True
    if cfg.insert_mode == "type" and shutil.which("xdotool"):
        return (
            subprocess.run(
                ["xdotool", "type", "--clearmodifiers", text], check=False
            ).returncode
            == 0
        )

    return False
