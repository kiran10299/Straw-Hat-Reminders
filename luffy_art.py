"""
luffy_art.py - procedural, cel-shaded anime-style straw-hat pirate (Luffy style).

Everything is drawn with QPainter vector shapes (no image files), so the
character can be animated with a real skeleton: hips, knees, ankles, toes,
shoulders, elbows, head and secondary motion (hat, sash tails, hair).
"""

import math
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPen, QPainterPath, QBrush, QPolygonF

# --------------------------------------------------------------------------
# Palette (anime cel shading: base + shadow + highlight)
# --------------------------------------------------------------------------
OUT = QColor("#1d120c")
SKIN, SKIN_SH, SKIN_HI = QColor("#ffd3a8"), QColor("#e8a675"), QColor("#fff0dc")
VEST, VEST_SH, VEST_IN = QColor("#e3262f"), QColor("#a5141f"), QColor("#5e0b13")
SASH, SASH_SH = QColor("#ffcf3a"), QColor("#d79c12")
SHORTS, SHORTS_SH = QColor("#3274bd"), QColor("#1f4d86")
CUFF, CUFF_SH = QColor("#ffffff"), QColor("#c9d3e2")
HAIR, HAIR_SH, HAIR_HI = QColor("#16181d"), QColor("#050506"), QColor("#4a5d80")
STRAW, STRAW_SH, STRAW_LINE, STRAW_HI = (QColor("#f8d152"), QColor("#d29b20"),
                                         QColor("#b5841a"), QColor("#fff2a8"))
BAND, BAND_SH = QColor("#d3192d"), QColor("#8f0d1c")
SANDAL, SANDAL_SH = QColor("#7d4b25"), QColor("#4f2d14")
MOUTH, TONGUE = QColor("#5e0c16"), QColor("#ff6b7a")

STRAW_COLOR, BAND_COLOR = STRAW, BAND   # used by the tray icon

# --------------------------------------------------------------------------
# Skeleton dimensions (px). Character is ~240 px tall.
# --------------------------------------------------------------------------
L_THIGH, L_SHIN = 40.0, 40.0
L_UPPER, L_FORE = 30.0, 28.0
TORSO_H = 62.0
FOOT_H = 9.0
LIGHT = (-0.8, -0.6)


def P(x, y):
    return QPointF(x, y)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_pt(a, b, t):
    return QPointF(lerp(a.x(), b.x(), t), lerp(a.y(), b.y(), t))


def pen(color, w):
    return QPen(color, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)


def ellipse_path(c, rx, ry):
    path = QPainterPath()
    path.addEllipse(c, rx, ry)
    return path


def fill(p, path, color, ow=2.4):
    p.setPen(pen(OUT, ow) if ow else Qt.NoPen)
    p.setBrush(color)
    p.drawPath(path)


def shade_fill(p, path, base, shadow, s=4.0, ow=2.3, hi=None, hs=2.0):
    """Cel-shaded fill: shadow on the side away from the light, optional rim highlight."""
    p.save()
    p.setClipPath(path, Qt.IntersectClip)
    p.fillPath(path, QBrush(shadow))
    p.fillPath(path.translated(LIGHT[0] * s, LIGHT[1] * s), QBrush(base))
    if hi is not None:
        rim = path.subtracted(path.translated(-LIGHT[0] * hs, -LIGHT[1] * hs))
        p.fillPath(rim, QBrush(hi))
    p.restore()
    if ow:
        p.setBrush(Qt.NoBrush)
        p.setPen(pen(OUT, ow))
        p.drawPath(path)


def tapered_path(pts, widths):
    path = QPainterPath()
    for q, w in zip(pts, widths):
        path = path.united(ellipse_path(q, w / 2, w / 2))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        wa, wb = widths[i] / 2, widths[i + 1] / 2
        dx, dy = b.x() - a.x(), b.y() - a.y()
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        seg = QPainterPath()
        seg.addPolygon(QPolygonF([P(a.x() + nx * wa, a.y() + ny * wa), P(b.x() + nx * wb, b.y() + ny * wb),
                                  P(b.x() - nx * wb, b.y() - ny * wb), P(a.x() - nx * wa, a.y() - ny * wa)]))
        seg.closeSubpath()
        path = path.united(seg)
    return path


def outlined_line(p, a, b, color, w):
    p.setPen(pen(OUT, w + 2.4))
    p.drawLine(a, b)
    p.setPen(pen(color, w))
    p.drawLine(a, b)


# --------------------------------------------------------------------------
# Pose
# --------------------------------------------------------------------------
class Pose:
    def __init__(self):
        self.legs = [(0.0, 0.05), (0.0, 0.05)]          # back, front: (thigh angle, knee bend)
        self.arms = [(0.1, 0.3, 1.0), (0.1, 0.3, 1.0)]  # back, front: (upper angle, elbow bend, stretch)
        self.lift = 0.0
        self.upper_rot = 0.0
        self.lean = 0.0
        self.shake = 0.0
        self.head_rot = 0.0
        self.hat_tilt = 0.0
        self.speed = 0.0
        self.mood = "neutral"
        self.t = 0.0
        self.arms_behind = False


# --------------------------------------------------------------------------
# Legs
# --------------------------------------------------------------------------
def leg_points(hip, a, k):
    knee = P(hip.x() + L_THIGH * math.sin(a), hip.y() + L_THIGH * math.cos(a))
    sa = a - k
    ankle = P(knee.x() + L_SHIN * math.sin(sa), knee.y() + L_SHIN * math.cos(sa))
    return knee, ankle, sa


def draw_foot(p, ankle, ang, skin, skin_sh):
    p.save()
    p.translate(ankle)
    p.rotate(ang)
    sole = QPainterPath()
    sole.addRoundedRect(QRectF(-8, 3.5, 31, 5.5), 2.7, 2.7)
    shade_fill(p, sole, SANDAL, SANDAL_SH, 2.0, 2.0)
    foot = tapered_path([P(-2, -1), P(9, 0.5), P(19, 1.8)], [12.5, 10.5, 8.0])
    shade_fill(p, foot, skin, skin_sh, 3.0, 2.1)
    p.setPen(pen(skin_sh.darker(115), 1.1))
    for x in (17.5, 20.5):
        p.drawLine(P(x, 0.5), P(x, 4))
    outlined_line(p, P(14, -1.5), P(6, 3.5), SANDAL, 2.4)
    outlined_line(p, P(14, -1.5), P(19, 3.5), SANDAL, 2.4)
    p.restore()


def draw_leg(p, hip, a, k, back):
    knee, ankle, sa = leg_points(hip, a, k)
    skin, skin_sh = (SKIN.darker(108), SKIN_SH.darker(108)) if back else (SKIN, SKIN_SH)
    shorts, shorts_sh = (SHORTS.darker(112), SHORTS_SH.darker(112)) if back else (SHORTS, SHORTS_SH)

    toe_off = (-a - 0.2) * 110 if (a < -0.2 and k < 0.45) else 0.0
    draw_foot(p, ankle, -math.degrees(sa) * 0.45 + toe_off, skin, skin_sh)

    cuff_pt = lerp_pt(hip, knee, 0.66)
    calf = lerp_pt(knee, ankle, 0.30)
    leg = tapered_path([cuff_pt, knee, calf, ankle], [15.5, 12.5, 13.8, 8.5])
    shade_fill(p, leg, skin, skin_sh, 3.5)
    p.setPen(pen(skin_sh.darker(112), 1.2))
    kn = lerp_pt(knee, calf, 0.2)
    p.drawLine(P(kn.x() + 2, kn.y() - 2), P(kn.x() + 4, kn.y() + 1))

    hip_pt = P(hip.x(), hip.y() + 2)
    sp = tapered_path([hip_pt, cuff_pt], [27, 23.5])
    shade_fill(p, sp, shorts, shorts_sh, 4.5)
    p.setPen(pen(shorts_sh.darker(115), 1.3))
    f1, f2 = lerp_pt(hip_pt, cuff_pt, 0.45), lerp_pt(hip_pt, cuff_pt, 0.8)
    p.drawLine(P(f1.x() - 4, f1.y()), P(f2.x() - 2, f2.y()))

    p.save()
    p.translate(cuff_pt)
    p.rotate(-math.degrees(a))
    cuff = QPainterPath()
    cuff.setFillRule(Qt.WindingFill)
    for i in range(5):
        cuff.addEllipse(P(-12 + i * 6, 2.0), 4.8, 4.8)
    cuff.addRoundedRect(QRectF(-14, -2.5, 28, 6), 3, 3)
    cuff = cuff.simplified()
    shade_fill(p, cuff, CUFF.darker(104) if back else CUFF, CUFF_SH, 2.5, 2.1)
    p.setPen(pen(CUFF_SH, 1.0))
    for i in range(4):
        p.drawLine(P(-9 + i * 6, 0), P(-8 + i * 6, 4))
    p.restore()
    return ankle


# --------------------------------------------------------------------------
# Arms
# --------------------------------------------------------------------------
_ARM_U = [0.0, 0.22, 0.5, 0.62, 0.85, 1.0]
_ARM_W = [13.5, 13.0, 9.5, 10.8, 9.0, 8.0]


def _arm_width(u):
    for i in range(len(_ARM_U) - 1):
        if u <= _ARM_U[i + 1]:
            f = (u - _ARM_U[i]) / (_ARM_U[i + 1] - _ARM_U[i])
            return lerp(_ARM_W[i], _ARM_W[i + 1], f)
    return _ARM_W[-1]


def draw_fist(p, wrist, fa, skin, skin_sh):
    p.save()
    p.translate(wrist)
    p.rotate(-math.degrees(fa))
    fist = QPainterPath()
    fist.addRoundedRect(QRectF(-7.5, 0, 15, 13.5), 6, 6)
    shade_fill(p, fist, skin, skin_sh, 3.0, 2.2)
    p.setPen(pen(OUT, 1.2))
    for x in (-3.5, 0.5, 4.0):
        p.drawLine(P(x, 9.5), P(x, 13))
    thumb = tapered_path([P(6.5, 3), P(1.5, 8)], [5.5, 4.8])
    shade_fill(p, thumb, skin, skin_sh, 1.5, 1.6)
    p.restore()


def draw_arm(p, sh, ua, eb, mult, back, t, haki=False):
    if haki:
        skin, skin_sh = QColor("#352438"), QColor("#140b17") # Armament Haki
    else:
        skin, skin_sh = (SKIN.darker(110), SKIN_SH.darker(110)) if back else (SKIN, SKIN_SH)
    elbow = P(sh.x() + L_UPPER * mult * math.sin(ua), sh.y() + L_UPPER * mult * math.cos(ua))
    fa = ua + eb
    wrist = P(elbow.x() + L_FORE * mult * math.sin(fa), elbow.y() + L_FORE * mult * math.cos(fa))
    thin = 1.0 / (mult ** 0.6)
    amp = (mult - 1.0) * 5.0
    pts, ws = [], []
    n = 6 if mult > 1.02 else 2
    for seg, (a, b) in enumerate(((sh, elbow), (elbow, wrist))):
        dx, dy = b.x() - a.x(), b.y() - a.y()
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        for i in range(n + (1 if seg == 1 else 0)):
            f = i / n
            u = (seg + f) / 2
            q = lerp_pt(a, b, f)
            off = math.sin(u * math.pi * 3 - t * 14) * amp * math.sin(u * math.pi)
            pts.append(P(q.x() + nx * off, q.y() + ny * off))
            ws.append(_arm_width(u) * (thin if 0.05 < u < 0.95 else max(thin, 0.85)))
    if n == 2:  # add muscle profile points for unstretched arms
        pts = [sh, lerp_pt(sh, elbow, 0.4), elbow, lerp_pt(elbow, wrist, 0.3), wrist]
        ws = [_arm_width(0), _arm_width(0.2), _arm_width(0.5), _arm_width(0.65), _arm_width(1)]
    arm = tapered_path(pts, ws)
    shade_fill(p, arm, skin, skin_sh, 3.5)
    if mult < 1.05:
        p.setPen(pen(skin_sh.darker(112), 1.2))
        d = lerp_pt(sh, elbow, 0.35)
        p.drawLine(P(d.x() + 2, d.y() - 3), P(d.x() + 3, d.y() + 3))
    end = pts[-1]
    if haki:
        p.setBrush(Qt.NoBrush)
        p.setPen(pen(QColor("#a85db0"), 2.0))
        for i in range(1, 4):
            hl = lerp_pt(sh, elbow, i/4.0)
            p.drawArc(QRectF(hl.x()-5, hl.y()-5, 10, 10), 0, 180*16)
    draw_fist(p, end, fa, skin, skin_sh)


# --------------------------------------------------------------------------
# Torso
# --------------------------------------------------------------------------
def draw_torso(p, hip, sh):
    hx, hy, sx, sy = hip.x(), hip.y(), sh.x(), sh.y()
    body = QPainterPath(P(hx - 15, hy))
    body.lineTo(P(hx + 16, hy))
    body.cubicTo(P(hx + 19, hy - 22), P(sx + 25, sy + 28), P(sx + 22, sy + 10))
    body.cubicTo(P(sx + 22, sy + 1), P(sx + 14, sy - 4), P(sx + 6, sy - 5))
    body.lineTo(P(sx - 8, sy - 5))
    body.cubicTo(P(sx - 16, sy - 4), P(sx - 23, sy + 1), P(sx - 23, sy + 10))
    body.cubicTo(P(sx - 25, sy + 28), P(hx - 18, hy - 22), P(hx - 15, hy))
    shade_fill(p, body, SKIN, SKIN_SH, 5.0)

    # muscles
    p.setPen(pen(SKIN_SH, 1.5))
    p.setBrush(Qt.NoBrush)
    pec = QPainterPath(P(sx - 3, sy + 19))
    pec.quadTo(P(sx + 8, sy + 26), P(sx + 19, sy + 17))
    p.drawPath(pec)
    for i, y in enumerate((hy - 30, hy - 20)):
        p.drawLine(P(sx + 1, y), P(sx + 6, y + 1))
        p.drawLine(P(sx + 10, y + 1), P(sx + 15, y))
    p.drawLine(P(sx + 8, sy + 27), P(hx + 8, hy - 15))

    # X scar
    for a, b in ((P(sx - 1, sy + 11), P(sx + 15, sy + 29)), (P(sx + 15, sy + 11), P(sx - 1, sy + 29))):
        p.setPen(pen(SKIN_SH.darker(118), 3.6))
        p.drawLine(a, b)
        p.setPen(pen(QColor("#f3a68a"), 2.0))
        p.drawLine(a, b)

    # vest - back (left) panel
    left = QPainterPath(P(hx - 15, hy))
    left.cubicTo(P(hx - 18, hy - 22), P(sx - 25, sy + 28), P(sx - 23, sy + 10))
    left.cubicTo(P(sx - 23, sy + 1), P(sx - 16, sy - 4), P(sx - 8, sy - 5))
    left.lineTo(P(sx - 2, sy - 4))
    left.cubicTo(P(sx - 4, sy + 14), P(sx - 7, sy + 32), P(hx - 3, hy))
    left.closeSubpath()
    edge_l = QPainterPath(P(sx - 2, sy - 4))
    edge_l.cubicTo(P(sx - 4, sy + 14), P(sx - 7, sy + 32), P(hx - 3, hy))
    shade_fill(p, left, VEST, VEST_SH, 5.0, 0)
    p.save()
    p.setClipPath(left)
    p.strokePath(edge_l, pen(VEST_IN, 6))
    p.setPen(pen(VEST_SH, 1.5))
    fold = QPainterPath(P(sx - 15, sy + 14))
    fold.quadTo(P(sx - 14, sy + 30), P(hx - 11, hy - 6))
    p.drawPath(fold)
    p.restore()
    p.setBrush(Qt.NoBrush)
    p.setPen(pen(OUT, 2.3))
    p.drawPath(left)

    # vest - front (right) panel
    right = QPainterPath(P(sx + 12, sy - 4))
    right.cubicTo(P(sx + 18, sy - 2), P(sx + 22, sy + 2), P(sx + 22, sy + 10))
    right.cubicTo(P(sx + 25, sy + 28), P(hx + 19, hy - 22), P(hx + 16, hy))
    right.lineTo(P(hx + 11, hy))
    right.cubicTo(P(hx + 13, hy - 20), P(sx + 17, sy + 14), P(sx + 12, sy - 4))
    edge_r = QPainterPath(P(hx + 11, hy))
    edge_r.cubicTo(P(hx + 13, hy - 20), P(sx + 17, sy + 14), P(sx + 12, sy - 4))
    shade_fill(p, right, VEST, VEST_SH, 3.0, 0)
    p.save()
    p.setClipPath(right)
    p.strokePath(edge_r, pen(VEST_IN, 4))
    p.restore()
    p.setBrush(Qt.NoBrush)
    p.setPen(pen(OUT, 2.3))
    p.drawPath(right)

    # sash
    sash = QPainterPath(P(hx - 19, hy - 13))
    sash.quadTo(P(hx, hy - 10), P(hx + 19, hy - 13))
    sash.lineTo(P(hx + 19, hy - 1))
    sash.quadTo(P(hx, hy + 2), P(hx - 19, hy - 1))
    sash.closeSubpath()
    shade_fill(p, sash, SASH, SASH_SH, 3.0)
    p.setPen(pen(SASH_SH, 1.2))
    p.drawLine(P(hx - 6, hy - 10), P(hx - 2, hy - 2))
    p.drawLine(P(hx + 6, hy - 10), P(hx + 9, hy - 2))


def draw_sash_tails(p, hip, t, speed):
    knot = P(hip.x() - 16, hip.y() - 6)
    for i, (length, base) in enumerate(((22, 0.35), (17, 0.10))):
        ang = base + 0.35 * speed + 0.13 * math.sin(t * 9 + i * 1.7) * (0.4 + speed)
        mid = P(knot.x() - math.sin(ang) * length * 0.5, knot.y() + math.cos(ang) * length * 0.5)
        tip = P(knot.x() - math.sin(ang + 0.15) * length, knot.y() + math.cos(ang + 0.15) * length)
        tail = tapered_path([knot, mid, tip], [8, 7.5, 6])
        shade_fill(p, tail, SASH, SASH_SH, 2.5, 2.0)
    shade_fill(p, ellipse_path(knot, 5.5, 4.5), SASH, SASH_SH, 2.0, 2.0)


# --------------------------------------------------------------------------
# Head
# --------------------------------------------------------------------------
def draw_eye_open(p, e, sc, look=1.2):
    sclera = ellipse_path(e, 5.2 * sc, 7.2)
    fill(p, sclera, QColor("white"), 1.4)
    p.save()
    p.setClipPath(sclera)
    fill(p, ellipse_path(P(e.x() + look * sc, e.y() + 0.8), 3.9 * sc, 5.8), OUT, 0)
    fill(p, ellipse_path(P(e.x() + look * sc, e.y() + 2.5), 2.6 * sc, 3.2), QColor("#3a2a22"), 0)
    p.restore()
    fill(p, ellipse_path(P(e.x() + (look + 1.2) * sc, e.y() - 2.2), 1.7 * sc, 1.9), QColor("white"), 0)
    fill(p, ellipse_path(P(e.x() + (look - 1.3) * sc, e.y() + 3.0), 0.8 * sc, 0.8), QColor("white"), 0)
    p.setPen(pen(OUT, 2.8))
    p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(e.x() - 5.6 * sc, e.y() - 7.6, 11.2 * sc, 13), 15 * 16, 150 * 16)


def draw_face(p, c, face, mood, t):
    cx, cy = c.x(), c.y()
    ef, en = P(cx - 1, cy + 2), P(cx + 15, cy + 2)    # far eye, near eye
    m = P(cx + 12, cy + 17)

    if mood == "angry":
        p.save()
        p.setClipPath(face)
        p.fillPath(face, QBrush(QColor(255, 40, 30, 45)))
        p.fillRect(QRectF(cx - 30, cy - 9, 64, 15), QColor(70, 0, 0, 55))
        p.restore()

    # scar with stitches under his left eye (near side)
    p.setPen(pen(OUT, 1.5))
    p.drawLine(P(en.x() - 4, en.y() + 10.5), P(en.x() + 4, en.y() + 10))
    p.drawLine(P(en.x() - 2, en.y() + 8.5), P(en.x() - 2.5, en.y() + 12.5))
    p.drawLine(P(en.x() + 2, en.y() + 8.5), P(en.x() + 1.5, en.y() + 12.5))

    # nose
    nose_path = QPainterPath(P(cx + 21, cy + 3))
    nose_path.lineTo(P(cx + 26, cy + 10))
    nose_path.lineTo(P(cx + 22, cy + 11))
    nose_path.closeSubpath()
    shade_fill(p, nose_path, SKIN_SH, SKIN_SH.darker(115), 0, 0)
    p.setPen(pen(OUT, 1.2))
    p.drawLine(P(cx + 23, cy + 10.5), P(cx + 26, cy + 10))

    blink = (t % 3.7) < 0.13
    p.setBrush(Qt.NoBrush)

    if mood == "happy":
        for e, sc in ((ef, 0.8), (en, 1.0)):
            path = QPainterPath(P(e.x() - 5.5 * sc, e.y() + 2))
            path.quadTo(P(e.x(), e.y() - 7), P(e.x() + 5.5 * sc, e.y() + 2))
            p.setPen(pen(OUT, 3.2))
            p.drawPath(path)
        mouth = QPainterPath(P(m.x() - 12, m.y() - 5))
        mouth.quadTo(P(m.x() + 1, m.y() - 3), P(m.x() + 14, m.y() - 7))
        mouth.cubicTo(P(m.x() + 15, m.y() + 12), P(m.x() - 8, m.y() + 15), P(m.x() - 12, m.y() - 5))
        fill(p, mouth, MOUTH, 0)
        p.save()
        p.setClipPath(mouth)
        p.fillRect(QRectF(m.x() - 14, m.y() - 9, 30, 6.5), QColor("white"))
        fill(p, ellipse_path(P(m.x() + 1, m.y() + 10), 8.5, 5.5), TONGUE, 0)
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(pen(OUT, 2.2))
        p.drawPath(mouth)
        p.setPen(pen(QColor("#ff7b7b"), 1.5))
        for bx, by in ((cx - 9, cy + 10), (cx + 21, cy + 12)):
            for i in range(3):
                p.drawLine(P(bx + i * 3, by + 2), P(bx + i * 3 + 2, by - 1))

    elif mood == "stretch":
        for e, sc in ((ef, 0.8), (en, 1.0)):
            path = QPainterPath(P(e.x() - 5 * sc, e.y()))
            path.quadTo(P(e.x(), e.y() + 5), P(e.x() + 5 * sc, e.y()))
            p.setPen(pen(OUT, 2.8))
            p.drawPath(path)
        o = ellipse_path(P(m.x(), m.y() + 1), 5.5, 7)
        fill(p, o, MOUTH, 2.0)
        p.save()
        p.setClipPath(o)
        fill(p, ellipse_path(P(m.x(), m.y() + 6), 4, 3), TONGUE, 0)
        p.restore()

    elif mood == "annoyed":
        for e, sc in ((ef, 0.8), (en, 1.0)):
            draw_eye_open(p, e, sc, 0.5)
            lid = QPainterPath()
            lid.addRect(QRectF(e.x() - 7 * sc, e.y() - 9, 14 * sc, 8.5))
            fill(p, lid, SKIN, 0)
            p.setPen(pen(OUT, 2.8))
            p.drawLine(P(e.x() - 5.5 * sc, e.y() - 0.5), P(e.x() + 5.5 * sc, e.y() - 0.5))
        p.setPen(pen(OUT, 2.4))
        p.drawLine(P(ef.x() - 5, ef.y() - 9), P(ef.x() + 4, ef.y() - 8))
        p.drawLine(P(en.x() + 6, en.y() - 9), P(en.x() - 5, en.y() - 8))
        wave = QPainterPath(P(m.x() - 8, m.y()))
        wave.cubicTo(P(m.x() - 4, m.y() - 4), P(m.x() + 1, m.y() + 4), P(m.x() + 8, m.y() - 1))
        p.setBrush(Qt.NoBrush)
        p.drawPath(wave)
        d = P(cx + 31, cy - 3 + (t * 6) % 6)
        drop = QPainterPath(P(d.x(), d.y() - 7))
        drop.cubicTo(P(d.x() + 5, d.y() - 1), P(d.x() + 5, d.y() + 4), P(d.x(), d.y() + 4))
        drop.cubicTo(P(d.x() - 5, d.y() + 4), P(d.x() - 5, d.y() - 1), P(d.x(), d.y() - 7))
        shade_fill(p, drop, QColor("#9ad8ff"), QColor("#5aa9e0"), 1.5, 1.5)

    elif mood == "angry":
        p.setPen(pen(OUT, 4.5))
        p.drawLine(P(ef.x() - 6, ef.y() - 11), P(ef.x() + 5, ef.y() - 5))
        p.drawLine(P(en.x() + 7, en.y() - 11), P(en.x() - 5, en.y() - 5))
        for e, sc in ((ef, 0.8), (en, 1.0)):
            fill(p, ellipse_path(P(e.x(), e.y() + 1), 5.0 * sc, 4.3), QColor("white"), 1.8)
            fill(p, ellipse_path(P(e.x() + 0.5, e.y() + 1), 1.6, 1.6), OUT, 0)
        # wide shark-teeth shout
        mouth = QPainterPath(P(m.x() - 13, m.y() - 6))
        mouth.lineTo(P(m.x() + 15, m.y() - 8))
        mouth.lineTo(P(m.x() + 12, m.y() + 11))
        mouth.quadTo(P(m.x(), m.y() + 14), P(m.x() - 10, m.y() + 9))
        mouth.closeSubpath()
        fill(p, mouth, MOUTH, 0)
        p.save()
        p.setClipPath(mouth)
        top = QPainterPath(P(m.x() - 16, m.y() - 10))
        bot = QPainterPath(P(m.x() - 16, m.y() + 16))
        for i in range(8):
            x = m.x() - 14 + i * 4
            top.lineTo(P(x, m.y() - 7.5 + i * -0.25))
            top.lineTo(P(x + 2, m.y() - 1.5))
            bot.lineTo(P(x, m.y() + 12))
            bot.lineTo(P(x + 2, m.y() + 6.5))
        top.lineTo(P(m.x() + 18, m.y() - 10))
        bot.lineTo(P(m.x() + 18, m.y() + 16))
        p.fillPath(top, QBrush(QColor("white")))
        p.fillPath(bot, QBrush(QColor("white")))
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(pen(OUT, 2.3))
        p.drawPath(mouth)
        s = 1.0 + 0.2 * math.sin(t * 14)
        v = P(cx + 36, cy - 38)
        for ang in (45, 135, 225, 315):
            r = math.radians(ang)
            a0 = P(v.x() + math.cos(r) * 3 * s, v.y() + math.sin(r) * 3 * s)
            a1 = P(v.x() + math.cos(r) * 10 * s, v.y() + math.sin(r) * 10 * s)
            outlined_line(p, a0, a1, QColor("#ff2a2a"), 3.0 * s)

    else:  # neutral cheerful
        for e, sc in ((ef, 0.8), (en, 1.0)):
            if blink:
                p.setPen(pen(OUT, 2.8))
                p.drawLine(P(e.x() - 4.5 * sc, e.y() + 1), P(e.x() + 4.5 * sc, e.y() + 1))
            else:
                draw_eye_open(p, e, sc)
        p.setPen(pen(OUT, 2.4))
        p.drawLine(P(ef.x() - 4, ef.y() - 11), P(ef.x() + 4, ef.y() - 12))
        p.drawLine(P(en.x() - 4, en.y() - 12), P(en.x() + 5, en.y() - 11))
        grin = QPainterPath(P(m.x() - 10, m.y() - 3))
        grin.cubicTo(P(m.x() - 5, m.y() + 7), P(m.x() + 8, m.y() + 7), P(m.x() + 13, m.y() - 4))
        grin.quadTo(P(m.x() + 2, m.y() + 0.5), P(m.x() - 10, m.y() - 3))
        fill(p, grin, MOUTH, 2.0)
        p.save()
        p.setClipPath(grin)
        p.fillRect(QRectF(m.x() - 10, m.y() - 4, 24, 4), QColor("white"))
        p.restore()
        p.setPen(pen(OUT, 2.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(grin)
        p.drawLine(P(m.x() + 13, m.y() - 4), P(m.x() + 15, m.y() - 6))


def draw_hat(p, bc, tilt):
    p.save()
    p.translate(bc)
    p.rotate(tilt)
    brim = ellipse_path(P(0, 0), 51, 12.5)
    shade_fill(p, brim, STRAW, STRAW_SH, 3.0, 2.6, STRAW_HI, 1.6)
    p.save()
    p.setClipPath(brim)
    p.setPen(pen(STRAW_LINE, 1.0))
    p.setBrush(Qt.NoBrush)
    for r in (43, 35):
        p.drawEllipse(P(0, 0), r, r * 0.245)
    for deg in range(0, 360, 10):
        r = math.radians(deg)
        p.drawLine(P(math.cos(r) * 37, math.sin(r) * 9), P(math.cos(r) * 49, math.sin(r) * 12))
    p.restore()

    dome = QPainterPath(P(-25, -1))
    dome.cubicTo(P(-27, -37), P(31, -37), P(29, -1))
    dome.quadTo(P(2, 6), P(-25, -1))
    shade_fill(p, dome, STRAW, STRAW_SH, 5.0, 0, STRAW_HI, 2.0)
    p.save()
    p.setClipPath(dome)
    p.setPen(pen(STRAW_LINE, 1.0))
    for y in (-18, -24, -29):
        w = QPainterPath(P(-30, y + 4))
        w.quadTo(P(2, y - 2), P(34, y + 4))
        p.drawPath(w)
    for x in range(-22, 30, 7):
        p.drawLine(P(x, -12), P(x + 1, -31))
    band = QPainterPath(P(-30, -11))
    band.quadTo(P(2, -5), P(34, -11))
    band.lineTo(P(34, 8))
    band.lineTo(P(-30, 8))
    band.closeSubpath()
    p.fillPath(band, QBrush(BAND_SH))
    p.fillPath(band.translated(-2.5, -1.5), QBrush(BAND))
    fill(p, ellipse_path(P(-7, -24), 9, 3.5), QColor(255, 250, 210, 110), 0)
    p.setPen(pen(OUT, 1.6))
    p.setBrush(Qt.NoBrush)
    p.drawPath(QPainterPath(band))
    p.restore()
    p.setPen(pen(OUT, 2.6))
    p.setBrush(Qt.NoBrush)
    p.drawPath(dome)
    p.restore()


def draw_head(p, c, mood, t, hat_tilt, speed):
    cx, cy = c.x(), c.y()

    # back hair - spiky, swaying slightly
    sway = math.sin(t * 7) * 1.2 * (0.3 + speed)
    hair = QPainterPath(P(cx + 8, cy - 22))
    n = 17
    for i in range(n + 1):
        ang = math.radians(92 + i * (196 / n))
        r = 30 if i % 2 == 0 else 39 + (2 if i % 4 == 1 else 0)
        dx = sway if i % 2 else 0
        hair.lineTo(P(cx - 2 + math.cos(ang) * r + dx, cy - 3 - math.sin(ang) * r * 0.95))
    hair.lineTo(P(cx + 4, cy + 10))
    hair.closeSubpath()
    shade_fill(p, hair, HAIR, HAIR_SH, 4.0, 2.0)
    p.save()
    p.setClipPath(hair)
    p.setPen(pen(HAIR_HI, 2.0))
    p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(cx - 32, cy - 26, 30, 30), 100 * 16, 70 * 16)
    p.drawArc(QRectF(cx - 30, cy - 6, 20, 22), 160 * 16, 50 * 16)
    p.restore()

    # face (3/4 view facing right)
    face = QPainterPath(P(cx - 21, cy - 12))
    face.cubicTo(P(cx - 25, cy + 8), P(cx - 16, cy + 24), P(cx - 2, cy + 27))
    face.cubicTo(P(cx + 4, cy + 29), P(cx + 10, cy + 30), P(cx + 14, cy + 29))
    face.cubicTo(P(cx + 22, cy + 26), P(cx + 27, cy + 14), P(cx + 27, cy + 2))
    face.cubicTo(P(cx + 27, cy - 24), P(cx - 17, cy - 30), P(cx - 21, cy - 12))
    shade_fill(p, face, SKIN, SKIN_SH, 3.5, 2.4)
    p.save()
    p.setClipPath(face)
    p.fillPath(ellipse_path(P(cx + 3, cy - 19), 36, 11), QBrush(QColor(214, 140, 95, 150)))  # hat shadow
    p.restore()

    # ear
    ear = ellipse_path(P(cx - 19, cy + 5), 6.2, 8.2)
    shade_fill(p, ear, SKIN, SKIN_SH, 2.5, 2.2)
    p.setPen(pen(SKIN_SH.darker(125), 1.4))
    p.drawArc(QRectF(cx - 22, cy + 1, 6, 8), 90 * 16, 200 * 16)

    draw_face(p, c, face, mood, t)

    # sideburn and fringe spikes
    side = QPainterPath(P(cx - 25, cy - 14))
    side.lineTo(P(cx - 14, cy - 12))
    side.lineTo(P(cx - 13, cy + 3))
    side.lineTo(P(cx - 19, cy - 3))
    side.closeSubpath()
    shade_fill(p, side, HAIR, HAIR_SH, 2.0, 1.6)
    fringe = QPainterPath(P(cx - 24, cy - 22))
    spikes = [(-17, -6), (-10, -17), (-4, -3), (3, -16), (9, -5), (15, -17), (21, -4), (26, -16), (31, -8)]
    for dx, dy in spikes:
        fringe.lineTo(P(cx + dx, cy + dy))
    fringe.lineTo(P(cx + 32, cy - 26))
    fringe.closeSubpath()
    shade_fill(p, fringe, HAIR, HAIR_SH, 2.5, 1.6)

    draw_hat(p, P(cx + 3, cy - 21), hat_tilt)


# --------------------------------------------------------------------------
# Whole character
# --------------------------------------------------------------------------
def draw_luffy(p, pose):
    """Draw the character with feet on y=0, centred on x=0, facing right."""
    lows = [leg_points(P(0, 0), a, k)[1].y() for a, k in pose.legs]
    hip_y = -(max(lows) + FOOT_H) - pose.lift
    hip = P(pose.shake, hip_y)
    sh = P(hip.x() + pose.lean, hip_y - TORSO_H)

    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 55))
    p.drawEllipse(P(5, 2), max(18.0, 42 - pose.lift * 0.5), 6)

    def upper_begin():
        p.save()
        p.translate(hip)
        p.rotate(pose.upper_rot)
        p.translate(-hip)

    back_sh = P(sh.x() - 10, sh.y() + 5)
    front_sh = P(sh.x() + 11, sh.y() + 5)

    upper_begin()
    draw_arm(p, back_sh, *pose.arms[0], back=True, t=pose.t, haki=(pose.mood=='angry'))
    p.restore()

    draw_sash_tails(p, hip, pose.t, pose.speed)
    draw_leg(p, hip, *pose.legs[0], back=True)
    draw_leg(p, hip, *pose.legs[1], back=False)

    shorts = QPainterPath()
    shorts.addRoundedRect(QRectF(hip.x() - 20, hip_y - 7, 40, 24), 8, 8)
    shade_fill(p, shorts, SHORTS, SHORTS_SH, 4.0)

    upper_begin()
    neck_top = P(sh.x() + 4, sh.y() - 13)
    neck = tapered_path([P(sh.x() + 3, sh.y() + 2), neck_top], [13, 12])
    shade_fill(p, neck, SKIN_SH, SKIN_SH.darker(112), 2.0)
    draw_torso(p, hip, sh)
    if pose.arms_behind:
        draw_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t, haki=(pose.mood=='angry'))
    p.save()
    p.translate(neck_top)
    p.rotate(pose.head_rot)
    p.translate(-neck_top)
    draw_head(p, P(sh.x() + 5, sh.y() - 37), pose.mood, pose.t, pose.hat_tilt, pose.speed)
    p.restore()
    if not pose.arms_behind:
        draw_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t, haki=(pose.mood=='angry'))
    p.restore()


# --------------------------------------------------------------------------
# Animation poses
# --------------------------------------------------------------------------
STRIDE_A = 0.44
WALK_PERIOD = 1.0
WALK_SPEED = 2 * (L_THIGH + L_SHIN) * math.sin(STRIDE_A) / (WALK_PERIOD / 2)


def walk_pose(phase, t, mood, speed=1.0):
    pose = Pose()
    legs = []
    for off in (math.pi, 0.0):                      # back, front
        ph = phase + off
        a = STRIDE_A * math.sin(ph)
        k = 0.12 + 1.0 * max(0.0, math.cos(ph)) ** 1.5 + 0.12 * max(0.0, -math.cos(ph)) * max(0.0, math.sin(ph))
        legs.append((a, k))
    pose.legs = legs
    arms = []
    for off in (0.0, math.pi):                      # arms swing opposite to the same-side leg
        ph = phase + off - 0.25                     # slight lag = natural follow-through
        ua = -0.55 * math.sin(ph + math.pi)
        eb = 0.30 + 0.6 * max(0.0, ua / 0.55)
        arms.append((ua, eb, 1.0))
    pose.arms = arms
    pose.lean = 3.5
    pose.upper_rot = 2.5 + 1.5 * math.sin(phase * 2)
    pose.head_rot = -1.8 * math.sin(phase * 2 + 0.6)
    pose.hat_tilt = 1.5 * math.sin(phase * 2 + 1.2)
    pose.speed = speed
    pose.mood = mood
    pose.t = t
    return pose


def celebrate_pose(t):
    pose = Pose()
    h = abs(math.sin(t * math.pi * 2.0)) * 28
    f = h / 28
    pose.lift = h
    pose.legs = [(-0.15 + 0.35 * f, 0.15 + 0.9 * f), (0.10 + 0.55 * f, 0.15 + 1.1 * f)]
    wave = math.sin(t * 14) * 0.15
    pose.arms = [(2.75 + wave, 0.2, 1.0), (2.2 - wave, 0.35, 1.0)]
    pose.head_rot = -6 * f
    pose.hat_tilt = -5 * f
    pose.speed = 0.6
    pose.mood = "happy"
    pose.t = t
    return pose


def angry_pose(t):
    pose = Pose()
    s = max(0.0, math.sin(t * 9))
    pose.legs = [(-0.16, 0.08), (0.16 + 0.35 * s, 0.08 + 0.8 * s)]
    shake = math.sin(t * 28) * 0.18
    pose.arms = [(1.75 + shake, 1.05, 1.0), (1.95 - shake, 1.0, 1.0)]
    pose.shake = math.sin(t * 45) * 1.3
    pose.upper_rot = 5
    pose.head_rot = 3 + math.sin(t * 30) * 1.5
    pose.hat_tilt = math.sin(t * 30) * 2
    pose.speed = 0.3
    pose.mood = "angry"
    pose.t = t
    return pose


def stretch_pose(t):
    pose = Pose()
    T = 3.4
    s = 0.5 - 0.5 * math.cos(2 * math.pi * t / T)        # 0..1..0
    up = min(1.0, s * 1.7)
    ua = lerp(0.15, -2.72, up)                            # swing back & up behind the head
    mult = 1.0 + 1.2 * max(0.0, (s - 0.45) / 0.55)       # gomu gomu rubber stretch!
    eb = lerp(0.45, 0.0, up)
    pose.arms = [(ua - 0.12, eb, mult), (ua + 0.05, eb, mult)]
    pose.arms_behind = True
    pose.legs = [(-0.13, 0.05), (0.13, 0.05)]
    pose.upper_rot = 9 * math.sin(2 * math.pi * t / (2 * T)) * s
    pose.head_rot = -4 * s
    pose.lift = 3 * s
    pose.mood = "stretch" if s > 0.35 else "happy"
    pose.t = t
    return pose
