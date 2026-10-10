# Straw Hat Desktop Reminders ☠️👒

<p align="left">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.7+" /></a>
  <a href="https://riverbankcomputing.com/software/pyqt/"><img src="https://img.shields.io/badge/GUI-PyQt5%20QPainter-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5" /></a>
  <a href="https://github.com/kiran10299/Straw-Hat-Reminders"><img src="https://img.shields.io/badge/Graphics-100%25%20Procedural%20Vector-ff4655?style=for-the-badge" alt="Procedural Vector" /></a>
  <a href="https://microsoft.com/windows"><img src="https://img.shields.io/badge/Platform-Windows%20API%20%7C%20Ctypes-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge" alt="MIT License" /></a>
</p>

A fully animated, interactive desktop companion and ergonomic health reminder application for Windows, featuring **Monkey D. Luffy, Roronoa Zoro, and Sanji** from One Piece. Built entirely in Python!

Instead of using static images or pre-rendered GIFs, all characters and animations in this project are generated **procedurally in real-time using mathematical vector graphics (QPainter)** and a custom skeletal animation system. This allows for fluid multi-layer animations, secondary cloth & hair physics, Busoshoku Haki transitions, and live drag-and-drop interactivity.

## ✨ Features

- **🧠 Smart Activity Tracking:** The app monitors your idle time and lock screen status using the Windows API. Timers only run when you are actively using your computer.
- **🎨 Procedural Cel-Shaded Art:** All graphics are rendered mathematically in real-time. No external image assets are used!
- **⚡ Dynamic States & Haki:** Characters react dynamically. If you ignore a water reminder, Luffy will activate Armament Haki (Busoshoku) and Gear Second steam!
- **🖱️ Interactivity:** You can drag and drop the characters around your screen using your mouse.
- **⚙️ System Tray & Settings:** Runs quietly in your system tray. Right-click the Straw Hat icon to open the Settings Menu and configure your timers.
- **🚀 Auto-Start:** Automatically registers itself to launch quietly in the background when Windows boots up.

## 👥 Meet the Crew

<div align="center">
  <img src="luffy_preview.png" width="200" alt="Luffy">
  <img src="zoro_preview.png" width="200" alt="Zoro">
  <img src="sanji_preview.png" width="200" alt="Sanji">
</div>

1. **Monkey D. Luffy:**
   - **Water Reminder:** Reminds you to drink water every 30 minutes of active screen time.
   - **Stretch Reminder:** Reminds you to stand up and stretch every 60 minutes.
   - **Eye Rest (20-20-20 Rule):** Reminds you to look away from the screen for 20 seconds every 20 minutes.
2. **Sanji:**
   - **Lunch Break:** Walks across your screen carrying a silver cloche platter every day at exactly 1:15 PM (customizable) to remind you to eat. Features a glowing cigarette and smoke particles.
3. **Roronoa Zoro:**
   - **Getting Lost:** True to his character, Zoro randomly wanders across your screen in the *wrong direction* every 1 to 3 hours, looking confused. 

## 🛠️ Requirements

- **OS:** Windows (Uses `ctypes` for Windows API idle tracking and WinReg for autostart)
- **Python:** Python 3.7 or higher
- **Dependencies:** `PyQt5`

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kiran10299/Straw-Hat-Reminders.git
   cd Straw-Hat-Reminders
   ```

2. **Install the required dependencies:**
   ```bash
   pip install PyQt5
   ```

3. **Start the application:**
   Double-click the `Start Luffy Reminder.bat` file, or run it directly via Python without a console window:
   ```bash
   pythonw luffy_reminder.py
   ```

## 🎮 Testing the Animations

If you want to immediately see the characters without waiting for the timers, you can use the provided batch scripts, or use the command line arguments:

- `pythonw luffy_reminder.py --water`
- `pythonw luffy_reminder.py --stretch`
- `pythonw luffy_reminder.py --eye`
- `pythonw luffy_reminder.py --lunch`
- `pythonw luffy_reminder.py --zoro`

Because the app uses Local Sockets (IPC), running these commands will instantly trigger the animations on your currently running background process rather than opening a duplicate app.

## 📂 File Structure
- `luffy_reminder.py`: The main application, IPC server, System Tray, Settings UI, and timer logic.
- `luffy_art.py`: Procedural drawing engine, skeletal animation system, and Luffy's rendering logic.
- `sanji_zoro_art.py`: Vector math and drawing logic for Sanji and Zoro.
- `sounds/`: Synthesized `.wav` sound effects.

## 🤝 Contributing
Feel free to fork the repository, add new characters, or create your own custom reminders! 
