
<div align="center">  

# 🖼️ Wallpaper Looper Pro

**Minimal • Smart • Beautiful**

Loop, scrape, and manage wallpapers effortlessly.
Made for **creators, researchers, and everyday dreamers.**

![GitHub release](https://img.shields.io/badge/release-v1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-yellow)

</div>  

---

## 🌟 Why Wallpaper Looper Pro?

Because your desktop deserves more than one face.
This isn’t just a wallpaper changer — it’s a **wallpaper workflow tool**.

* 🎨 Collect images from **Unsplash** by category & resolution
* 🔀 Shuffle, randomize, or preview wallpapers
* 📁 Store images neatly in `images/` with **metadata.json** logs
* ⚡ Minimal, lightweight, and **cross-platform**
* 🧹 Smart cleanup so storage never gets messy

---

## ✨ Features

| Feature                | Description                                         |
| ---------------------- | --------------------------------------------------- |
| 🌄 **Online Scraping** | Pull high-quality wallpapers directly from Unsplash |
| 🖼️ **Local Looping**  | Reuse your own folders of images                    |
| 🔀 **Randomization**   | Shuffle images & intervals for fresh vibes          |
| 📊 **Metadata Logs**   | JSON + optional logs for research or datasets       |
| 💻 **Cross-Platform**  | Windows, macOS, GNOME Linux wallpaper setting       |
| 🧹 **Auto-Clean**      | Remove stale images to save space                   |

---

## 🚀 Quick Start

```bash
# Create environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Install deps
pip install -r requirements.txt

# Run with online wallpapers
python wallpaper_looper.py --count 6 --interval 20 --category nature

# Run with local wallpapers
python wallpaper_looper.py --local ./my_images --count 10 --shuffle
```

---

## 🎥 Live Demo

*(Recommended: Add a looping GIF or MP4 here — e.g. wallpapers changing every 3s)*

![Demo Preview](assets/demo.gif)

---

## 📂 Outputs

```
📂 images/            → Downloaded wallpapers  
📝 metadata.json      → Metadata log (great for AI training datasets)  
📜 wallpaper_looper.log → Optional runtime log (--log flag)  
```

---

## 🛠️ Use Cases

* 🔬 **Researchers** – Build image datasets for ML/AI experiments
* 🎨 **Creators** – Moodboards, references, and inspiration loops
* 🖥️ **Users** – Keep your desktop dynamic & alive
* 💻 **Developers** – Lightweight wallpaper testing tool

---

## 🌍 Vision

> *“A wallpaper isn’t just a background. It’s a daily reminder of mood, creativity, and perspective.”*

Wallpaper Looper Pro is built to give you **control + automation** in one minimal tool.

---

## 👤 Author

**Wallace Brown**
Founder @ **LeadDevCorps** 🚀
Automating creativity for **Africa and beyond 🌍**

[![LinkedIn](https://img.shields.io/badge/LinkedIn--blue?logo=linkedin\&logoColor=white)](https://linkedin.com/in/okekewallace)
[![GitHub](https://img.shields.io/badge/GitHub--black?logo=github\&logoColor=white)](https://github.com/wallaceokeke)

---

## 📜 License

Licensed under the **MIT License** — see [LICENSE](LICENSE).

---

