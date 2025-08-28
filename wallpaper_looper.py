#!/usr/bin/env python3
"""
WallpaperLooper — merged, robust, dual-mode, session-saving wallpaper looper

Author: Okeke Wallace Brown + ChatGPT (merged)
Features:
 - Menu-driven: local (pick/copy), online (download), dual
 - Copies selected local images into session_images/ for persistence
 - Downloads online images (picsum.photos) with caching and optional refresh
 - Shuffle / ordered modes, configurable duration
 - Saves session to session.json (resume next run)
 - Saves metadata to metadata.json (downloads + run events) suitable for later training
 - Cross-platform wallpaper setter: Windows, macOS, GNOME, KDE Plasma (best-effort)
Dependency: requests (only for online mode). tkinter optional for GUI picker.
"""

from pathlib import Path
import os
import sys
import time
import json
import random
import platform
import ctypes
import shutil
import subprocess
from itertools import cycle
from datetime import datetime, timezone

# Try optional packages
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

# -------------------- Paths & Config --------------------
ROOT = Path(__file__).parent.resolve()
SESSION_IMAGES_DIR = ROOT / "session_images"
SESSION_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = ROOT / "session.json"
METADATA_FILE = ROOT / "metadata.json"

# Ensure metadata file exists
if not METADATA_FILE.exists():
    METADATA_FILE.write_text("[]", encoding="utf-8")

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# Online reliable image source templates (picsum)
ONLINE_QUERIES = {
    "nature": "https://picsum.photos/1920/1080?random={sig}",
    "graffiti": "https://picsum.photos/1920/1080?random={sig}"
}

# -------------------- Utilities --------------------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def safe_print(*a, **k):
    print(*a, **k)
    sys.stdout.flush()

def append_metadata(entry: dict):
    # append entry to metadata.json (array)
    try:
        text = METADATA_FILE.read_text(encoding="utf-8") or "[]"
        arr = json.loads(text)
    except Exception:
        arr = []
    arr.append(entry)
    try:
        METADATA_FILE.write_text(json.dumps(arr, indent=2), encoding="utf-8")
    except Exception as e:
        safe_print(f"[!] Could not write metadata: {e}")

def write_session(data: dict):
    try:
        SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        safe_print(f"[!] Could not save session: {e}")

def load_session():
    try:
        if SESSION_FILE.exists():
            return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None

# -------------------- File picker & local copy --------------------
def pick_local_images_and_copy():
    """
    Opens file dialog (if available). Copies chosen images into SESSION_IMAGES_DIR.
    Returns list of destination file paths (absolute).
    """
    picked = []
    if not TK_AVAILABLE:
        safe_print("[!] tkinter not available; cannot open file manager picker.")
        safe_print("    Place images into 'session_images/' folder manually or install tkinter.")
        return []

    root = tk.Tk()
    root.withdraw()
    try:
        files = filedialog.askopenfilenames(
            title="Select images to add to session_images/",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
        )
    finally:
        try:
            root.destroy()
        except Exception:
            pass

    for src in files:
        try:
            src_path = Path(src)
            if not src_path.exists() or src_path.suffix.lower() not in IMG_EXTS:
                continue
            dest = SESSION_IMAGES_DIR / f"{int(time.time())}_{src_path.name}"
            shutil.copy2(src_path, dest)
            picked.append(str(dest.resolve()))
        except Exception as e:
            safe_print(f"[!] Could not copy {src}: {e}")
    return picked

def gather_images_from_session_folder():
    imgs = []
    try:
        for p in SESSION_IMAGES_DIR.iterdir():
            if p.is_file() and p.suffix.lower() in IMG_EXTS:
                imgs.append(str(p.resolve()))
    except Exception as e:
        safe_print(f"[!] Error reading session_images/: {e}")
    return sorted(imgs)

# -------------------- Online downloading (picsum) --------------------
def download_online_images(theme: str, count: int = 5, force_refresh: bool = False):
    """
    Downloads `count` images for theme into SESSION_IMAGES_DIR.
    If cached exist and not force_refresh, reuse them.
    Returns list of file paths.
    """
    if not REQUESTS_AVAILABLE:
        safe_print("[!] requests not available. Install `requests` to use online mode.")
        return []

    theme = (theme or "nature").lower()
    if theme not in ONLINE_QUERIES:
        theme = "nature"

    # cached
    cached = sorted([p for p in SESSION_IMAGES_DIR.glob(f"{theme}_*") if p.suffix.lower() in IMG_EXTS], key=lambda p: p.stat().st_mtime, reverse=True)
    if cached and not force_refresh:
        return [str(p.resolve()) for p in cached[:count]]

    downloaded = []
    for i in range(count):
        try:
            sig = random.randint(1, 2**31 - 1)
            url = ONLINE_QUERIES[theme].format(sig=sig)
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            # create unique filename
            fname = f"{theme}_{int(time.time())}_{random.randint(1000,9999)}.jpg"
            fpath = SESSION_IMAGES_DIR / fname
            with open(fpath, "wb") as f:
                f.write(resp.content)
            downloaded.append(str(fpath.resolve()))
            append_metadata({
                "type": "download",
                "theme": theme,
                "filepath": str(fpath.resolve()),
                "source_url": url,
                "downloaded_at": now_iso()
            })
            # small polite pause
            time.sleep(0.2)
        except Exception as e:
            safe_print(f"[!] Download error #{i+1} for {theme}: {e}")
    return downloaded

# -------------------- Wallpaper setter: Windows, macOS, GNOME, KDE --------------------
def set_wallpaper(path: str) -> bool:
    """
    Attempt to set wallpaper cross-platform.
    Returns True if operation likely succeeded, False otherwise.
    """
    system = platform.system()
    p = Path(path)
    if not p.exists():
        safe_print(f"[!] Image not found: {path}")
        return False
    try:
        if system == "Windows":
            # SPI_SETDESKWALLPAPER = 20
            return bool(ctypes.windll.user32.SystemParametersInfoW(20, 0, str(p), 3))
        elif system == "Darwin":
            cmd = f"osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"{p}\"'"
            res = os.system(cmd)
            return res == 0
        elif system == "Linux":
            # Try GNOME (gsettings)
            try:
                res = subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{p}"])
                if res == 0:
                    return True
            except Exception:
                pass
            # Try KDE Plasma (plasma-apply-wallpaperimage may not exist)
            try:
                # Use DBus to tell plasmashell to set wallpaper
                script = f"var Desktops = desktops(); for (i=0;i<Desktops.length;i++) {{ d = Desktops[i]; d.wallpaperPlugin = 'org.kde.image'; d.currentConfigGroup = Array('Wallpaper','org.kde.image','General'); d.writeConfig('Image', 'file://{p}'); }}"
                res = subprocess.call(["qdbus-qt5", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script])
                if res == 0:
                    return True
            except Exception:
                pass
            # Last fallback: try feh (common in lightweight WMs)
            try:
                res = subprocess.call(["feh", "--bg-scale", str(p)])
                return res == 0
            except Exception:
                pass
            safe_print("[!] Could not set wallpaper on this Linux desktop environment.")
            return False
        else:
            safe_print(f"[!] Unsupported OS: {system}")
            return False
    except Exception as e:
        safe_print(f"[!] Error setting wallpaper: {e}")
        return False

# -------------------- Menu & interactive flow --------------------
def prompt_menu():
    safe_print("\n=== WallpaperLooper — Menu ===")
    safe_print("1) Local images (open file manager and copy to session_images/)")
    safe_print("2) Online images (download picsum images)")
    safe_print("3) Dual mode (local pick + online download)")
    safe_print("4) Resume last session (if exists)")
    safe_print("0) Exit")
    choice = input("Choose an option [0-4]: ").strip()
    return choice

def input_int(prompt, default):
    val = input(f"{prompt} [{default}]: ").strip()
    if val == "":
        return default
    try:
        return int(val)
    except Exception:
        return default

def main():
    # Load last session if exists
    last = load_session()
    choice = prompt_menu()
    cfg = {
        "mode": None,
        "local_added": [],     # paths copied into session_images/
        "theme": None,
        "online_count": 5,
        "online_refresh": False,
        "duration": 30,
        "shuffle": True,
        "images": []
    }

    if choice == "0":
        safe_print("Exiting.")
        return

    if choice == "4":
        if not last:
            safe_print("[!] No saved session found.")
            choice = prompt_menu()
        else:
            safe_print("[*] Resuming saved session.")
            cfg = last
            images = cfg.get("images", [])
            if not images:
                # try to rebuild images from saved preferences
                safe_print("[*] No cached image list in session — rebuilding from prefs.")
                # try local
                local_imgs = gather_images_from_session_folder()
                images = local_imgs
                if cfg.get("mode") in ("online", "dual"):
                    if REQUESTS_AVAILABLE:
                        online_imgs = download_online_images(cfg.get("theme", "nature"), count=cfg.get("online_count",5), force_refresh=cfg.get("online_refresh", False))
                        images.extend(online_imgs)
                images = [p for p in images if Path(p).exists()]
            if not images:
                safe_print("[!] Could not find any images for the saved session. Starting fresh menu.")
                choice = prompt_menu()
            else:
                safe_print(f"Found {len(images)} images from session. Starting loop.")
                run_loop(images, cfg.get("duration",30), cfg.get("shuffle", True))
                return

    # If we reach here, either fresh choice or resumed failed
    if choice == "1":
        cfg["mode"] = "local"
        safe_print("[*] Opening file manager to pick images...")
        picked = pick_local_images_and_copy()
        if not picked:
            safe_print("[!] No files picked/copied. You can add files into session_images/ manually and rerun.")
            # still offer to use existing session folder images
            existing = gather_images_from_session_folder()
            if not existing:
                safe_print("[!] session_images/ is empty. Exiting.")
                return
            else:
                safe_print(f"Found {len(existing)} existing images in session_images/. Using them.")
                images = existing
                cfg["images"] = images
        else:
            cfg["local_added"] = picked
            images = gather_images_from_session_folder()
            cfg["images"] = images

    elif choice == "2":
        cfg["mode"] = "online"
        if not REQUESTS_AVAILABLE:
            safe_print("[!] requests library missing. Install it with `pip install requests` to enable online mode.")
            return
        theme = input("Choose theme (nature/graffiti) [nature]: ").strip().lower() or "nature"
        if theme not in ("nature", "graffiti"):
            theme = "nature"
        cfg["theme"] = theme
        cnt = input_int("How many online images to download", 5)
        cfg["online_count"] = max(1, cnt)
        fr = input("Force refresh (download new images even if cache exists)? (y/n) [n]: ").strip().lower()
        cfg["online_refresh"] = (fr == "y")
        safe_print(f"[*] Downloading {cfg['online_count']} {cfg['theme']} images...")
        online_imgs = download_online_images(cfg["theme"], count=cfg["online_count"], force_refresh=cfg["online_refresh"])
        if not online_imgs:
            safe_print("[!] Could not download online images. Exiting.")
            return
        cfg["images"] = online_imgs
    elif choice == "3":
        cfg["mode"] = "dual"
        # local pick optional
        use_local = input("Include local images? (y/n) [y]: ").strip().lower() != "n"
        if use_local:
            safe_print("[*] Open file manager to pick local images (they will be copied to session_images/).")
            picked = pick_local_images_and_copy()
            cfg["local_added"] = picked
        # online part
        if not REQUESTS_AVAILABLE:
            safe_print("[!] requests not available; online portion skipped.")
            online_imgs = []
        else:
            theme = input("Choose online theme (nature/graffiti) [nature]: ").strip().lower() or "nature"
            if theme not in ("nature", "graffiti"):
                theme = "nature"
            cfg["theme"] = theme
            cnt = input_int("How many online images to download", 4)
            cfg["online_count"] = max(1, cnt)
            fr = input("Force refresh online images? (y/n) [n]: ").strip().lower()
            cfg["online_refresh"] = (fr == "y")
            safe_print(f"[*] Downloading {cfg['online_count']} {cfg['theme']} images...")
            online_imgs = download_online_images(cfg["theme"], count=cfg["online_count"], force_refresh=cfg["online_refresh"])
        # gather final images list
        images = gather_images_from_session_folder()
        images.extend(online_imgs if 'online_imgs' in locals() else [])
        # dedupe while preserving order
        seen = set()
        final = []
        for p in images:
            if p not in seen and Path(p).exists():
                final.append(p)
                seen.add(p)
        cfg["images"] = final
        safe_print(f"[*] Prepared {len(final)} images (local+online).")
    else:
        safe_print("[!] Invalid choice. Exiting.")
        return

    # ensure we have images now
    images = cfg.get("images", []) or []
    if not images:
        # attempt fallback: look in session_images or download default online
        images = gather_images_from_session_folder()
        if not images and REQUESTS_AVAILABLE:
            safe_print("[*] No local images found — attempting fallback online download (nature, 5 images).")
            images = download_online_images("nature", count=5, force_refresh=True)
    # Validate existence
    images = [p for p in images if Path(p).exists()]
    if not images:
        safe_print("[!] Could not prepare any images. Exiting.")
        return

    # duration & shuffle
    duration = input_int("Seconds per wallpaper", 30)
    shuffle = input("Shuffle images? (y/n) [y]: ").strip().lower() != "n"

    cfg["duration"] = duration
    cfg["shuffle"] = shuffle

    # Save session (store paths and options)
    cfg["timestamp"] = now_iso()
    # store a copy of images list
    cfg["images"] = images
    write_session(cfg)

    # run loop
    run_loop(images, duration, shuffle)

# -------------------- Runner loop --------------------
def run_loop(images, duration, shuffle):
    safe_print(f"\n[*] Starting wallpaper loop with {len(images)} images — {duration}s per image. Press Ctrl+C to stop.")
    run_count = 0
    pool = list(images)
    try:
        if shuffle:
            random.shuffle(pool)
        for img in cycle(pool):
            run_count += 1
            entry = {
                "type": "run",
                "timestamp": now_iso(),
                "image": img,
                "duration": duration,
                "shuffle": shuffle,
                "count": run_count
            }
            append_metadata(entry)
            ok = set_wallpaper(img)
            safe_print(f"→ [{run_count}] Set: {img} (success={bool(ok)}) — next in {duration}s")
            time.sleep(duration)
    except KeyboardInterrupt:
        safe_print("\n[*] Stopped by user. Saving session and exiting.")
        # update session with current image list, etc.
        sess = load_session() or {}
        sess["images"] = images
        sess["duration"] = duration
        sess["shuffle"] = shuffle
        sess["timestamp"] = now_iso()
        write_session(sess)
    except Exception as e:
        safe_print(f"[!] Runtime error: {e}")

if __name__ == "__main__":
    main()
