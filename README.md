# Straw Hat Desktop Reminders ☠️👒

A fully animated, interactive desktop companion and health reminder application for Windows, featuring your favorite characters from One Piece. Built entirely in Python!

Instead of using static images or GIFs, all characters and animations in this project are generated **procedurally using vector graphics (QPainter)** and a custom skeletal animation system. This allows for smooth, dynamic animations, secondary motion (like clothes and hair blowing in the wind), and interactive features.

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
