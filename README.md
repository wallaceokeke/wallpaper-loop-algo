# Wallpaper Looper Pro

Minimal, production-like CLI tool to scrape or loop local wallpapers with features useful for users and researchers.

## Features
- Scrape random wallpapers from Unsplash (by category and resolution).
- Loop user-provided local images from a folder.
- Save downloaded images into `images/` and log metadata in `metadata.json` (suitable for later use in training).
- Options to shuffle, preview, randomize order and intervals, auto-cleanup old images.
- Cross-platform attempts to set desktop wallpaper (Windows, macOS, GNOME Linux).
- Minimal dependency: `requests`.

## Quick start

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate   # or `venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
```

2. Run:
```bash
python wallpaper_looper.py --count 6 --interval 20 --category nature
```

3. Use local images:
```bash
python wallpaper_looper.py --local /path/to/images --count 10 --shuffle
```

4. Preview mode (no wallpaper changes):
```bash
python wallpaper_looper.py --local ./my_photos --preview --count 5
```

5. Randomization examples:
```bash
# Randomize order every cycle and use random intervals between 10 and 60 seconds
python wallpaper_looper.py --local ./photos --randomize-order --randomize-intervals --min-interval 10 --max-interval 60
```

## Outputs
- `images/` — downloaded images stored here
- `metadata.json` — JSON array of metadata entries (download info + runtime logs). Useful for training imaging models.
- `wallpaper_looper.log` — optional runtime log when `--log` flag is used.

## License
MIT
