# Arch Linux Package Manager GUI (Pacman + Flatpak)

A Python-based graphical package manager for Arch Linux that lets you **search, install, and uninstall** applications from both **Pacman** and **Flatpak** in one place.  
Built with [Flet](https://flet.dev), it provides a simple tabbed interface for managing your system and Flatpak apps.

---

## ✨ Features
- **Tabbed interface**:  
  - **Uninstall tab**: browse installed Pacman and Flatpak packages, select, and remove.  
  - **Install tab**: search Pacman repositories and Flatpak remotes, then install selected apps.
- **Integrated search**:
  - Uninstall search updates results as you type.
  - Install search updates results **only after pressing Enter** in the search box.
- **Sudo support**: enter your password once to perform system-level operations.
- **Flatpak support**

---

## 🚀 Requirements
- Arch Linux (or Arch-based distro like Manjaro, EndeavourOS, etc.)
- Python 3.9+
- [Flet](https://flet.dev) (`pip install flet`)
- Pacman (preinstalled on Arch)
- Flatpak (`sudo pacman -S flatpak`)

---

## 📷 Screenshots
<img width="1278" height="745" alt="PackageManager-Uninstall Screen" src="https://github.com/user-attachments/assets/13b34560-51c8-4f3f-852a-a88b535f1999" />
<img width="1276" height="733" alt="PackageManager-Install Screen" src="https://github.com/user-attachments/assets/ec43eb6a-7543-48be-985d-fb416ac0f49c" />

---

## 📦 Installation
Clone this repository and install dependencies:

```bash
git clone https://github.com/Dan23022/arch-package-manager-gui.git
cd arch-package-manager-gui
pip install flet'''
