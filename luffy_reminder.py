import sys
import os
import ctypes
import ctypes.wintypes
import math
import winreg
import random
import winsound
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer, QPoint, QElapsedTimer, QPointF, QRectF, QSettings, QTime, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QCursor, QColor, QPainterPath, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QTimeEdit, QCheckBox, QPushButton

from luffy_art import draw_luffy, walk_pose, celebrate_pose, angry_pose, stretch_pose, fill, OUT, P, STRAW_COLOR, BAND_COLOR, pen
from sanji_zoro_art import draw_sanji, draw_zoro

APP_NAME = "LuffyReminder"
WALK_SPEED = 60.0
WALK_PERIOD = 0.8
STRETCH_HOLD = 3.5

# --------------------------------------------------------------------------
# Bubbles
# --------------------------------------------------------------------------
def draw_bubble(p, rect, text, button, hover, tail_to):
    path = QPainterPath()
    path.addRoundedRect(rect, 18, 18)
    tail = QPainterPath(P(rect.center().x() - 16, rect.bottom() - 2))
    tail.lineTo(tail_to)
    tail.lineTo(P(rect.center().x() + 14, rect.bottom() - 2))
    tail.closeSubpath()
    path = path.united(tail)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawPath(path.translated(3, 4))
    fill(p, path, QColor("#fffdf5"), 3.0)

    font = QFont("Comic Sans MS", 10)
    font.setBold(True)
    p.setFont(font)
    p.setPen(OUT)
    text_rect = QRectF(rect.left() + 14, rect.top() + 8, rect.width() - 28,
                       rect.height() - (56 if button else 16))
    p.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, text)

    if button:
        br = button_rect(rect)
        bp = QPainterPath()
        bp.addRoundedRect(br, 14, 14)
        fill(p, bp, QColor("#3ccf6e") if hover else QColor("#27ae60"), 2.6)
        f2 = QFont("Comic Sans MS", 11)
        f2.setBold(True)
        p.setFont(f2)
        p.setPen(QColor("white"))
        p.drawText(br, Qt.AlignCenter, button)

def button_rect(bubble):
    return QRectF(bubble.center().x() - 85, bubble.bottom() - 48, 170, 36)

# --------------------------------------------------------------------------
# Main Overlay
# --------------------------------------------------------------------------
class LuffyOverlay(QWidget):
    W, H = 470, 450

    def __init__(self, on_done, play_sound_cb):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
                         Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.resize(self.W, self.H)
        self.on_done = on_done
        self.play_sound = play_sound_cb
        self.busy = False
        self.hover = False
        self.dragging = False
        self.drag_offset = QPoint(0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self.clock = QElapsedTimer()
        self.anchor = P(self.W / 2, self.H - 6)
        self.bubble = QRectF(self.W / 2 - 165, 6, 330, 124)

    def start(self, kind):
        scr = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        g = scr.availableGeometry()
        self.geo = g
        self.kind = kind
        self.answered = False
        self.state = "walk"
        self.state_t = 0.0
        self.t = 0.0
        self.phase = 0.0
        
        self.char_type = "luffy"
        if kind == "lunch":
            self.char_type = "sanji"
        elif kind == "zoro":
            self.char_type = "zoro"

        # Zoro walks the wrong way (right to left)
        if self.char_type == "zoro":
            self.x0 = g.right() + 90
            self.x = self.x0
            self.target = g.left() - 200
        else:
            self.x0 = g.left() - 90
            self.x = self.x0
            self.target = (g.right() - 180) if kind == "water" else g.center().x()
            
        self.busy = True
        
        mood = "neutral"
        if kind == "lunch": mood = "lunch"
        elif kind == "zoro": mood = "confused"
        
        self.pose = walk_pose(0, 0, mood)
        if self.char_type == "zoro":
            self.pose.head_rot = -0.5 # Looking confused backwards
            
        self.place()
        self.show()
        self.raise_()
        self.clock.start()
        self.timer.start(16)
        self.play_sound("chime")

    def finish(self):
        self.timer.stop()
        self.hide()
        self.busy = False
        self.on_done(self.kind, self.answered)

    def place(self):
        # Calculate screen position based on logical x
        # self.x is the center horizontal coordinate
        sx = int(self.x - self.anchor.x())
        sy = int(self.geo.bottom() + 1 - self.anchor.y())
        self.move(sx, sy)

    def set_state(self, s):
        self.state = s
        self.state_t = 0.0

    def answer(self):
        if self.answered:
            return
        self.answered = True
        self.set_state("celebrate")
        self.play_sound("boing")
        self.update()

    def step(self):
        if self.dragging:
            self.clock.restart()
            return
            
        dt = min(self.clock.restart() / 1000.0, 0.05)
        self.t += dt
        self.state_t += dt
        omega = 2 * math.pi / WALK_PERIOD
        st = self.state
        
        is_zoro = self.char_type == "zoro"
        dir_sign = -1.0 if is_zoro else 1.0

        if st == "walk":
            self.x += WALK_SPEED * dir_sign * dt
            self.phase += omega * dt
            
            if is_zoro:
                prog = (self.x0 - self.x) / max(1.0, self.x0 - self.target)
            else:
                prog = (self.x - self.x0) / max(1.0, self.target - self.x0)
                
            mood = "lunch" if self.char_type == "sanji" else "neutral"
            if self.kind == "water" and prog > 0.55:
                mood = "annoyed"
            elif is_zoro:
                mood = "confused"
                
            self.pose = walk_pose(self.phase, self.t, mood)
            if self.char_type == "sanji" and mood != "lunch":
                self.pose.arms[0] = (-0.3, 1.0, 1.0) # Hands in pockets
                self.pose.arms[1] = (-0.3, 1.0, 1.0)
            elif self.char_type == "zoro":
                self.pose.arms[1] = (0.3, 1.5, 1.0) # Hand resting on swords
                self.pose.head_rot = math.sin(self.t * 2) * 0.4
            
            # Reached target?
            if (not is_zoro and self.x >= self.target) or (is_zoro and self.x <= self.target):
                if self.char_type == "sanji":
                    self.set_state("exit") # Sanji just keeps walking after stopping briefly? Actually let's let him exit.
                elif self.char_type == "zoro":
                    self.finish()
                    return
                else:
                    self.set_state("angry" if self.kind == "water" else "stretch")
                    if self.kind == "water": self.play_sound("angry")
        elif st == "celebrate":
            self.pose = celebrate_pose(self.state_t)
            if self.state_t > 2.0:
                self.set_state("exit")
        elif st == "angry":
            self.pose = angry_pose(self.state_t)
            if self.state_t > 6.0:
                self.set_state("exit")
        elif st == "stretch":
            self.pose = stretch_pose(self.state_t)
            if self.state_t > STRETCH_HOLD:
                self.set_state("exit")
        elif st == "exit":
            speed = 1.35
            self.x += WALK_SPEED * dir_sign * speed * dt
            self.phase += omega * speed * dt
            
            if self.char_type == "sanji": mood = "lunch"
            elif self.char_type == "zoro": mood = "confused"
            elif self.answered: mood = "happy"
            else: mood = "angry" if self.kind == "water" else "annoyed"
            
            self.pose = walk_pose(self.phase, self.t, mood)
            if self.char_type == "sanji" and mood != "lunch":
                self.pose.arms[0] = (-0.3, 1.0, 1.0)
                self.pose.arms[1] = (-0.3, 1.0, 1.0)
            elif self.char_type == "zoro":
                self.pose.arms[1] = (0.3, 1.5, 1.0)
                self.pose.head_rot = math.sin(self.t * 2) * 0.4
            
            if (not is_zoro and self.x > self.geo.right() + 140) or (is_zoro and self.x < self.geo.left() - 140):
                self.finish()
                return
        self.place()
        self.update()

    def bubble_content(self):
        st, water, stretch = self.state, self.kind == "water", self.kind == "stretch"
        eye = self.kind == "eye"
        lunch = self.kind == "lunch"
        zoro = self.kind == "zoro"

        if zoro:
            return "Where is everyone...? Did they get lost again?", None

        if self.answered:
            if water: return "Shishishi! Great job, nakama!\nStay strong!", None
            if eye: return "Good! Keep your eyes healthy!", None
            return "Shishishi! Feels great, right?\nBack to work, nakama!", None
            
        if lunch:
            if st == "walk" or st == "exit":
                return "Lunch time, everyone!\nI made something special!", None

        if water:
            btn = "YES, I DRANK!"
            if st == "walk":
                prog = (self.x - self.x0) / max(1.0, self.target - self.x0)
                if prog > 0.55: return "Oi... did you drink water yet?!\nI'm waiting!", btn
                return "Oi, nakama! Time to drink water!\nDrink up!", btn
            if st == "angry":
                return "OIIII!! WHY DIDN'T YOU DRINK WATER?!\nDrink it NOW!!", btn
            return "Hmph! I'll be back. Drink your water!", None
            
        if stretch:
            btn = "I STRETCHED!"
            if st == "walk": return "Hey nakama! You've been on the\nscreen for an hour. Stretch time!", btn
            if st == "stretch": return "Gomu Gomu no... STRETCH!\nStand up and stretch with me!", btn
            return "Don't forget to stretch later, okay?", None
            
        if eye:
            btn = "I RESTED MY EYES!"
            if st == "walk": return "Time for the 20-20-20 rule!\nLook 20ft away for 20s!", btn
            if st == "stretch": return "Keep looking away...\nBlink a few times!", btn
            return "Take care of your eyes!", None
            
        return "", None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        
        # Draw bubble
        text, btn = self.bubble_content()
        self.current_button = btn
        if text:
            draw_bubble(p, self.bubble, text, btn, self.hover, P(self.anchor.x() + 6, self.anchor.y() - 245))
            
        p.translate(self.anchor)
        
        # Scale for Zoro walking left
        if self.char_type == "zoro":
            p.scale(-1, 1)
            
        if self.char_type == "sanji":
            draw_sanji(p, self.pose)
        elif self.char_type == "zoro":
            draw_zoro(p, self.pose)
        else:
            draw_luffy(p, self.pose)
            
        p.end()

    def mouseMoveEvent(self, e):
        if self.dragging:
            new_pos = e.globalPos() - self.drag_offset
            self.move(new_pos)
            # Update logical x so he resumes from dropped location
            self.x = new_pos.x() + self.anchor.x()
            return

        h = bool(getattr(self, "current_button", None)) and button_rect(self.bubble).contains(e.pos())
        if h != self.hover:
            self.hover = h
            self.setCursor(Qt.PointingHandCursor if h else Qt.ArrowCursor)
            self.update()

    def mousePressEvent(self, e):
        if getattr(self, "current_button", None) and button_rect(self.bubble).contains(e.pos()):
            self.answer()
        else:
            self.dragging = True
            self.drag_offset = e.globalPos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)
            
    def mouseReleaseEvent(self, e):
        self.dragging = False
        self.setCursor(Qt.ArrowCursor if not self.hover else Qt.PointingHandCursor)
        # Snap back to bottom of screen
        self.place()

# --------------------------------------------------------------------------
# Screen activity (idle time + lock screen detection)
# --------------------------------------------------------------------------
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_time():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0
    return 0.0

def is_screen_locked():
    desk = ctypes.windll.user32.OpenInputDesktop(0, False, 0x0100)
    if not desk:
        return True
    ctypes.windll.user32.CloseDesktop(desk)
    return False

class ActivityMonitor:
    def __init__(self):
        self.active_time = 0.0
        self.last_check = datetime.now()

    def tick(self):
        now = datetime.now()
        dt = (now - self.last_check).total_seconds()
        self.last_check = now
        if not is_screen_locked() and get_idle_time() < 120.0:
            self.active_time += dt

    def pop_minutes(self):
        mins = self.active_time / 60.0
        self.active_time = 0.0
        return mins

# --------------------------------------------------------------------------
# Settings Dialog
# --------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("Luffy Reminder Settings")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.settings = settings
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        def add_spin(label, key, min_v, max_v):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            spin = QSpinBox()
            spin.setRange(min_v, max_v)
            spin.setSuffix(" mins")
            row.addWidget(spin)
            layout.addLayout(row)
            return spin

        self.water_spin = add_spin("Water Reminder:", "water_interval", 1, 120)
        self.stretch_spin = add_spin("Stretch Reminder:", "stretch_interval", 1, 240)
        self.eye_spin = add_spin("Eye Rest Reminder:", "eye_interval", 1, 120)

        row = QHBoxLayout()
        row.addWidget(QLabel("Sanji Lunch Time:"))
        self.lunch_time = QTimeEdit()
        row.addWidget(self.lunch_time)
        layout.addLayout(row)

        self.zoro_check = QCheckBox("Enable Zoro Getting Lost")
        layout.addWidget(self.zoro_check)

        self.sound_check = QCheckBox("Enable Sound Effects")
        layout.addWidget(self.sound_check)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_close)
        btn_box.addStretch()
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def load_settings(self):
        self.water_spin.setValue(int(self.settings.value("water_interval", 30)))
        self.stretch_spin.setValue(int(self.settings.value("stretch_interval", 60)))
        self.eye_spin.setValue(int(self.settings.value("eye_interval", 20)))
        t = self.settings.value("lunch_time", "13:15")
        self.lunch_time.setTime(QTime.fromString(t, "HH:mm"))
        self.zoro_check.setChecked(self.settings.value("zoro_enabled", True, type=bool))
        self.sound_check.setChecked(self.settings.value("sound_enabled", True, type=bool))

    def save_and_close(self):
        self.settings.setValue("water_interval", self.water_spin.value())
        self.settings.setValue("stretch_interval", self.stretch_spin.value())
        self.settings.setValue("eye_interval", self.eye_spin.value())
        self.settings.setValue("lunch_time", self.lunch_time.time().toString("HH:mm"))
        self.settings.setValue("zoro_enabled", self.zoro_check.isChecked())
        self.settings.setValue("sound_enabled", self.sound_check.isChecked())
        self.accept()


# --------------------------------------------------------------------------
# Autostart (HKCU Run key)
# --------------------------------------------------------------------------
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def autostart_command():
    exe = sys.executable
    if exe.endswith("python.exe"):
        exe = exe.replace("python.exe", "pythonw.exe")
    return f'"{exe}" "{os.path.abspath(__file__)}"'

def set_autostart(enabled):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if enabled:
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, autostart_command())
            else:
                try: winreg.DeleteValue(k, APP_NAME)
                except OSError: pass
    except Exception as e:
        print("Autostart error:", e)

def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, APP_NAME)
            return val == autostart_command()
    except OSError:
        return False

# --------------------------------------------------------------------------
# Main App Manager
# --------------------------------------------------------------------------
class Manager(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "LuffyReminder")
        self.monitor = ActivityMonitor()
        
        self.w_acc = 0.0
        self.s_acc = 0.0
        self.e_acc = 0.0
        self.last_lunch = None
        self.zoro_timer = random.randint(60, 180) # Next Zoro in X minutes of real time
        
        self.overlay = LuffyOverlay(self.overlay_done, self.play_sound)

        # Timers
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.tick)
        self.clock.start(5000)

        self.setup_tray()

    def setup_tray(self):
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(32, 54)
        path = QPainterPath(P(-18, -2))
        path.lineTo(P(18, -2))
        path.quadTo(P(0, -25), P(-18, -2))
        fill(p, path, STRAW_COLOR, 3.5)
        fill(p, QPainterPath(P(-12, -2)).united(QPainterPath(P(12, -2))), BAND_COLOR, 0)
        p.setPen(pen(BAND_COLOR, 6))
        p.drawLine(P(-11, -5), P(11, -5))
        p.end()

        self.tray = QSystemTrayIcon(QIcon(pix), self)
        menu = QMenu()
        
        settings_act = menu.addAction("Settings...")
        settings_act.triggered.connect(self.show_settings)
        
        menu.addSeparator()

        self.auto_act = QAction("Start with Windows", menu, checkable=True)
        self.auto_act.setChecked(autostart_enabled())
        self.auto_act.toggled.connect(set_autostart)
        menu.addAction(self.auto_act)

        menu.addSeparator()
        menu.addAction("Quit").triggered.connect(QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def play_sound(self, name):
        if not self.settings.value("sound_enabled", True, type=bool):
            return
        snd = os.path.join(os.path.dirname(__file__), "sounds", f"{name}.wav")
        if os.path.exists(snd):
            winsound.PlaySound(snd, winsound.SND_ASYNC)

    def show_settings(self):
        dlg = SettingsDialog(self.settings)
        dlg.exec_()

    def tick(self):
        if self.overlay.busy:
            self.monitor.tick()
            self.monitor.pop_minutes()
            return

        self.monitor.tick()
        active_mins = self.monitor.pop_minutes()
        
        self.w_acc += active_mins
        self.s_acc += active_mins
        self.e_acc += active_mins
        
        # Real-time checks (Lunch & Zoro)
        now = datetime.now()
        lunch_time_str = self.settings.value("lunch_time", "13:15")
        lunch_qtime = QTime.fromString(lunch_time_str, "HH:mm")
        
        # Check if lunch time just passed
        if self.last_lunch != now.date():
            if now.hour == lunch_qtime.hour() and now.minute >= lunch_qtime.minute():
                self.last_lunch = now.date()
                self.trigger("lunch")
                return
                
        if self.settings.value("zoro_enabled", True, type=bool):
            self.zoro_timer -= 5.0 / 60.0 # subtract elapsed real minutes
            if self.zoro_timer <= 0:
                self.zoro_timer = random.randint(60, 180)
                self.trigger("zoro")
                return

        # Active time checks
        w_int = int(self.settings.value("water_interval", 30))
        s_int = int(self.settings.value("stretch_interval", 60))
        e_int = int(self.settings.value("eye_interval", 20))

        if self.w_acc >= w_int:
            self.trigger("water")
        elif self.s_acc >= s_int:
            self.trigger("stretch")
        elif self.e_acc >= e_int:
            self.trigger("eye")

    def trigger(self, kind):
        if self.overlay.busy: return
        self.overlay.start(kind)

    def overlay_done(self, kind, answered):
        if answered:
            if kind == "water": self.w_acc = 0.0
            if kind == "stretch": self.s_acc = 0.0
            if kind == "eye": self.e_acc = 0.0
        # If not answered, keep accumulating so it fires again soon.

# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
if __name__ == "__main__":
    from PyQt5.QtNetwork import QLocalServer, QLocalSocket
    
    app = QApplication(sys.argv)
    
    # IPC logic to prevent multiple instances and handle direct triggers
    socket = QLocalSocket()
    socket.connectToServer(APP_NAME)
    if socket.waitForConnected(500):
        if len(sys.argv) > 1:
            cmd = sys.argv[1].replace("--", "")
            socket.write(cmd.encode("utf-8"))
            socket.waitForBytesWritten(1000)
        sys.exit(0)
        
    server = QLocalServer()
    server.removeServer(APP_NAME)
    server.listen(APP_NAME)
    
    manager = Manager()
    
    def on_new_connection():
        conn = server.nextPendingConnection()
        if conn.waitForReadyRead(1000):
            cmd = conn.readAll().data().decode("utf-8")
            if cmd in ("water", "stretch", "eye", "lunch", "zoro"):
                manager.trigger(cmd)
        conn.disconnectFromServer()
        
    server.newConnection.connect(on_new_connection)
    
    # Enable autostart on first run
    settings = manager.settings
    if not settings.value("autostart_configured", False, type=bool):
        set_autostart(True)
        settings.setValue("autostart_configured", True)

    sys.exit(app.exec_())
