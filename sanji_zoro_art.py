import math
import random
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPen, QPainterPath, QBrush, QPolygonF
from luffy_art import *

# --------------------------------------------------------------------------
# Palette for Sanji & Zoro
# --------------------------------------------------------------------------
SUIT_BK, SUIT_BK_SH = QColor("#222224"), QColor("#111112")
SHIRT_BL, SHIRT_BL_SH = QColor("#305680"), QColor("#1c3654")
TIE_YL = QColor("#e8c138")
HAIR_S, HAIR_S_SH, HAIR_S_HI = QColor("#fce274"), QColor("#d6b22b"), QColor("#fff3b3")
SHOE_BK, SHOE_BK_SH = QColor("#1a1a1a"), QColor("#000000")

HAIR_Z, HAIR_Z_SH, HAIR_Z_HI = QColor("#49c464"), QColor("#2a8740"), QColor("#85e89b")
BAND_Z, BAND_Z_SH = QColor("#19804b"), QColor("#0d4d2b")
PANT_Z, PANT_Z_SH = QColor("#284732"), QColor("#15291c")
SHIRT_W, SHIRT_W_SH = QColor("#f4f5f0"), QColor("#c2c4bb")

# --------------------------------------------------------------------------
# Sanji
# --------------------------------------------------------------------------
def draw_sanji_head(p, c, mood, t):
    cx, cy = c.x(), c.y()
    
    # Face base
    face = QPainterPath(P(cx - 21, cy - 12))
    face.cubicTo(P(cx - 25, cy + 8), P(cx - 16, cy + 24), P(cx - 2, cy + 27))
    face.cubicTo(P(cx + 4, cy + 29), P(cx + 10, cy + 30), P(cx + 14, cy + 29))
    face.cubicTo(P(cx + 22, cy + 26), P(cx + 27, cy + 14), P(cx + 27, cy + 2))
    face.cubicTo(P(cx + 27, cy - 24), P(cx - 17, cy - 30), P(cx - 21, cy - 12))
    shade_fill(p, face, SKIN, SKIN_SH, 3.5, 2.4)
    
    # Draw standard face but we will cover left eye
    draw_face(p, c, face, mood, t)
    
    # Sanji specific: right eye curly eyebrow
    p.setPen(pen(OUT, 2.2))
    p.setBrush(Qt.NoBrush)
    eb = QPainterPath(P(cx + 6, cy - 4))
    eb.quadTo(P(cx + 14, cy - 8), P(cx + 18, cy - 6))
    eb.quadTo(P(cx + 24, cy - 2), P(cx + 22, cy + 1))
    eb.quadTo(P(cx + 18, cy - 1), P(cx + 19, cy - 4))
    eb.quadTo(P(cx + 21, cy - 6), P(cx + 23, cy - 4))
    p.drawPath(eb)
    
    # Cigarette in mouth
    p.save()
    p.translate(cx + 9, cy + 18)
    p.rotate(-20)
    cig = QPainterPath(P(0, 0))
    cig.lineTo(P(16, 0))
    p.setPen(pen(OUT, 3.5))
    p.drawPath(cig)
    p.setPen(pen(QColor("white"), 2.2))
    p.drawPath(cig)
    p.setPen(pen(QColor("#ff5500"), 2.2))
    p.drawLine(P(14, 0), P(16, 0))
    
    # Smoke
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(200, 200, 200, 150))
    smoke_y = - (t * 20 % 15)
    smoke_x = math.sin(t * 3) * 4
    p.drawEllipse(P(17 + smoke_x, smoke_y), 3, 3)
    p.drawEllipse(P(18 - smoke_x, smoke_y - 6), 4, 4)
    p.restore()
    
    # Hair: blonde fringe sweeping over left side of face
    fringe = QPainterPath(P(cx - 22, cy - 26))
    fringe.cubicTo(P(cx - 35, cy - 10), P(cx - 25, cy + 20), P(cx + 4, cy + 25))
    fringe.cubicTo(P(cx - 5, cy + 5), P(cx - 5, cy - 15), P(cx + 2, cy - 24))
    fringe.lineTo(P(cx - 22, cy - 26))
    shade_fill(p, fringe, HAIR_S, HAIR_S_SH, 3.5, 2.0, HAIR_S_HI)
    
    # Hair: top and back
    hair = QPainterPath(P(cx - 22, cy - 26))
    hair.cubicTo(P(cx - 10, cy - 45), P(cx + 20, cy - 40), P(cx + 28, cy - 20))
    hair.cubicTo(P(cx + 35, cy - 10), P(cx + 30, cy + 5), P(cx + 25, cy + 10))
    hair.cubicTo(P(cx + 28, cy), P(cx + 25, cy - 20), P(cx + 2, cy - 24))
    hair.closeSubpath()
    shade_fill(p, hair, HAIR_S, HAIR_S_SH, 3.5, 2.0, HAIR_S_HI)
    
    # Hair spikes in front
    spike = QPainterPath(P(cx + 5, cy - 25))
    spike.quadTo(P(cx + 15, cy - 15), P(cx + 12, cy - 20))
    spike.quadTo(P(cx + 20, cy - 15), P(cx + 18, cy - 22))
    shade_fill(p, spike, HAIR_S, HAIR_S_SH, 0, 1.5)

def draw_sanji_leg(p, hip, a, k, back):
    knee, ankle, sa = leg_points(hip, a, k)
    suit, suit_sh = (SUIT_BK.darker(110), SUIT_BK_SH.darker(110)) if back else (SUIT_BK, SUIT_BK_SH)
    
    # Dress Shoe
    p.save()
    p.translate(ankle)
    p.rotate(-math.degrees(sa) * 0.45)
    shoe = QPainterPath()
    shoe.addRoundedRect(QRectF(-6, -2, 28, 10), 4, 4)
    tip = tapered_path([P(20, 3), P(28, 7)], [10, 2])
    shoe = shoe.united(tip)
    shade_fill(p, shoe, SHOE_BK, SHOE_BK_SH, 3.0, 2.0, QColor("#555"))
    # Heel
    p.setBrush(SHOE_BK_SH)
    p.drawRect(QRectF(-5, 8, 8, 4))
    p.restore()
    
    # Suit Pant
    leg = tapered_path([hip, knee, ankle], [22, 16, 15])
    shade_fill(p, leg, suit, suit_sh, 3.5)
    # Crease
    p.setPen(pen(OUT, 1.0))
    p.drawLine(lerp_pt(hip, knee, 0.2), lerp_pt(knee, ankle, 0.8))
    return ankle

def draw_sanji_torso(p, hip, sh):
    # Blue shirt and yellow tie underneath
    body = QPainterPath(P(hip.x() - 15, hip.y()))
    body.lineTo(P(hip.x() + 16, hip.y()))
    body.cubicTo(P(hip.x() + 19, hip.y() - 22), P(sh.x() + 25, sh.y() + 28), P(sh.x() + 22, sh.y() + 10))
    body.cubicTo(P(sh.x() + 22, sh.y() + 1), P(sh.x() + 14, sh.y() - 4), P(sh.x() + 6, sh.y() - 5))
    body.lineTo(P(sh.x() - 8, sh.y() - 5))
    body.cubicTo(P(sh.x() - 16, sh.y() - 4), P(sh.x() - 23, sh.y() + 1), P(sh.x() - 23, sh.y() + 10))
    body.cubicTo(P(sh.x() - 25, sh.y() + 28), P(hip.x() - 18, hip.y() - 22), P(hip.x() - 15, hip.y()))
    
    # Shirt base
    shade_fill(p, body, SHIRT_BL, SHIRT_BL_SH, 5.0)
    
    # Tie
    tie = QPainterPath(P(sh.x() + 7, sh.y() + 2))
    tie.lineTo(P(sh.x() + 4, sh.y() + 20))
    tie.lineTo(P(sh.x() + 8, sh.y() + 25))
    tie.lineTo(P(sh.x() + 12, sh.y() + 20))
    tie.closeSubpath()
    shade_fill(p, tie, TIE_YL, TIE_YL.darker(120), 2.0)
    
    # Suit Jacket Left
    left = QPainterPath(P(hip.x() - 15, hip.y()))
    left.cubicTo(P(hip.x() - 18, hip.y() - 22), P(sh.x() - 25, sh.y() + 28), P(sh.x() - 23, sh.y() + 10))
    left.cubicTo(P(sh.x() - 23, sh.y() + 1), P(sh.x() - 16, sh.y() - 4), P(sh.x() - 8, sh.y() - 5))
    left.lineTo(P(sh.x() + 2, sh.y() - 4))
    left.lineTo(P(sh.x() - 2, sh.y() + 28))
    left.lineTo(P(hip.x() - 2, hip.y()))
    left.closeSubpath()
    shade_fill(p, left, SUIT_BK, SUIT_BK_SH, 5.0, 0)
    p.setBrush(Qt.NoBrush)
    p.setPen(pen(OUT, 2.3))
    p.drawPath(left)
    
    # Suit Jacket Right
    right = QPainterPath(P(sh.x() + 12, sh.y() - 4))
    right.cubicTo(P(sh.x() + 18, sh.y() - 2), P(sh.x() + 22, sh.y() + 2), P(sh.x() + 22, sh.y() + 10))
    right.cubicTo(P(sh.x() + 25, sh.y() + 28), P(hip.x() + 19, hip.y() - 22), P(hip.x() + 16, hip.y()))
    right.lineTo(P(hip.x() + 8, hip.y()))
    right.lineTo(P(sh.x() + 14, sh.y() + 28))
    right.closeSubpath()
    shade_fill(p, right, SUIT_BK, SUIT_BK_SH, 3.0, 0)
    p.setBrush(Qt.NoBrush)
    p.setPen(pen(OUT, 2.3))
    p.drawPath(right)
    
def draw_sanji_arm(p, sh, ua, eb, mult, back, t):
    suit, suit_sh = (SUIT_BK.darker(110), SUIT_BK_SH.darker(110)) if back else (SUIT_BK, SUIT_BK_SH)
    elbow = P(sh.x() + L_UPPER * mult * math.sin(ua), sh.y() + L_UPPER * mult * math.cos(ua))
    fa = ua + eb
    wrist = P(elbow.x() + L_FORE * mult * math.sin(fa), elbow.y() + L_FORE * mult * math.cos(fa))
    
    pts = [sh, lerp_pt(sh, elbow, 0.4), elbow, lerp_pt(elbow, wrist, 0.3), wrist]
    ws = [15, 14, 12, 11, 10]
    arm = tapered_path(pts, ws)
    shade_fill(p, arm, suit, suit_sh, 3.5)
    
    # Cuff
    p.save()
    p.translate(wrist)
    p.rotate(-math.degrees(fa))
    p.setBrush(QColor("white"))
    p.setPen(pen(OUT, 1.5))
    p.drawRect(QRectF(-6, -1, 12, 4))
    p.restore()
    
    skin, skin_sh = (SKIN.darker(110), SKIN_SH.darker(110)) if back else (SKIN, SKIN_SH)
    draw_fist(p, wrist, fa, skin, skin_sh)
    return wrist

def draw_sanji(p, pose, look_x=None):
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
    draw_sanji_arm(p, back_sh, *pose.arms[0], back=True, t=pose.t)
    p.restore()

    draw_sanji_leg(p, hip, *pose.legs[0], back=True)
    draw_sanji_leg(p, hip, *pose.legs[1], back=False)

    upper_begin()
    neck_top = P(sh.x() + 4, sh.y() - 13)
    neck = tapered_path([P(sh.x() + 3, sh.y() + 2), neck_top], [13, 12])
    shade_fill(p, neck, SKIN_SH, SKIN_SH.darker(112), 2.0)
    
    draw_sanji_torso(p, hip, sh)
    
    if pose.arms_behind:
        draw_sanji_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t)
        
    p.save()
    p.translate(neck_top)
    p.rotate(pose.head_rot)
    p.translate(-neck_top)
    draw_sanji_head(p, P(sh.x() + 5, sh.y() - 37), pose.mood, pose.t)
    p.restore()
    
    if not pose.arms_behind:
        wrist = draw_sanji_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t)
        if pose.mood == 'lunch':
            # Detailed food tray
            tray = QPainterPath()
            tray.addRoundedRect(QRectF(wrist.x() - 25, wrist.y() - 12, 45, 6), 3, 3)
            shade_fill(p, tray, QColor("#e0e0e0"), QColor("#888888"), 1.0)
            
            # Silver Cloche
            cloche = QPainterPath()
            cloche.moveTo(wrist.x() - 18 + 36, wrist.y() - 32 + 20)
            cloche.arcTo(QRectF(wrist.x() - 18, wrist.y() - 32, 36, 40), 0, 180)
            shade_fill(p, cloche, QColor("#f4f4f4"), QColor("#a0a0a0"), 1.0)
            # Cloche handle
            p.setBrush(QColor("gold"))
            p.drawEllipse(P(wrist.x() - 3, wrist.y() - 34), 4, 3)
            
    p.restore()


# --------------------------------------------------------------------------
# Zoro
# --------------------------------------------------------------------------
def draw_zoro_head(p, c, mood, t):
    cx, cy = c.x(), c.y()
    
    face = QPainterPath(P(cx - 21, cy - 12))
    face.cubicTo(P(cx - 25, cy + 8), P(cx - 16, cy + 24), P(cx - 2, cy + 27))
    face.cubicTo(P(cx + 4, cy + 29), P(cx + 10, cy + 30), P(cx + 14, cy + 29))
    face.cubicTo(P(cx + 22, cy + 26), P(cx + 27, cy + 14), P(cx + 27, cy + 2))
    face.cubicTo(P(cx + 27, cy - 24), P(cx - 17, cy - 30), P(cx - 21, cy - 12))
    shade_fill(p, face, SKIN, SKIN_SH, 3.5, 2.4)
    
    # Eye scar (left eye, far side)
    p.setPen(pen(OUT, 1.5))
    p.drawLine(P(cx - 4, cy - 3), P(cx + 2, cy + 8))
    
    draw_face(p, c, face, mood, t)
    
    # 3 Earrings on right ear (near side)
    p.setBrush(QColor("gold"))
    p.setPen(pen(OUT, 1.0))
    for i in range(3):
        p.drawEllipse(P(cx - 18, cy + 12 + i * 4), 2.5, 4)
        
    # Green Hair - Spiky Marimo style
    hair = QPainterPath(P(cx - 22, cy - 12))
    spikes = [
        (-25, -20), (-15, -35), (-5, -42), (5, -40), (15, -35), 
        (25, -25), (30, -10), (28, 5)
    ]
    for sx, sy in spikes:
        hair.quadTo(P(cx + sx - 5, cy + sy + 10), P(cx + sx, cy + sy))
    hair.lineTo(P(cx + 10, cy - 10))
    hair.lineTo(P(cx - 22, cy - 12))
    shade_fill(p, hair, HAIR_Z, HAIR_Z_SH, 4.0, 2.0, HAIR_Z_HI)

def draw_zoro_torso(p, hip, sh):
    # Chest
    body = QPainterPath(P(hip.x() - 15, hip.y()))
    body.lineTo(P(hip.x() + 16, hip.y()))
    body.cubicTo(P(hip.x() + 19, hip.y() - 22), P(sh.x() + 25, sh.y() + 28), P(sh.x() + 22, sh.y() + 10))
    body.cubicTo(P(sh.x() + 22, sh.y() + 1), P(sh.x() + 14, sh.y() - 4), P(sh.x() + 6, sh.y() - 5))
    body.lineTo(P(sh.x() - 8, sh.y() - 5))
    body.cubicTo(P(sh.x() - 16, sh.y() - 4), P(sh.x() - 23, sh.y() + 1), P(sh.x() - 23, sh.y() + 10))
    body.cubicTo(P(sh.x() - 25, sh.y() + 28), P(hip.x() - 18, hip.y() - 22), P(hip.x() - 15, hip.y()))
    
    shade_fill(p, body, SKIN, SKIN_SH, 5.0)
    
    # Chest Scar
    p.setPen(pen(SKIN_SH.darker(130), 2.5))
    p.drawLine(P(sh.x() + 20, sh.y() + 10), P(sh.x() - 10, sh.y() + 35))
    
    # White Shirt (open)
    shirt_l = QPainterPath(P(hip.x() - 15, hip.y()))
    shirt_l.cubicTo(P(hip.x() - 18, hip.y() - 22), P(sh.x() - 25, sh.y() + 28), P(sh.x() - 23, sh.y() + 10))
    shirt_l.cubicTo(P(sh.x() - 23, sh.y() + 1), P(sh.x() - 16, sh.y() - 4), P(sh.x() - 8, sh.y() - 5))
    shirt_l.lineTo(P(sh.x() - 12, sh.y() + 15))
    shirt_l.lineTo(P(hip.x() - 10, hip.y()))
    shirt_l.closeSubpath()
    shade_fill(p, shirt_l, SHIRT_W, SHIRT_W_SH, 4.0, 0)
    
    shirt_r = QPainterPath(P(sh.x() + 12, sh.y() - 4))
    shirt_r.cubicTo(P(sh.x() + 18, sh.y() - 2), P(sh.x() + 22, sh.y() + 2), P(sh.x() + 22, sh.y() + 10))
    shirt_r.cubicTo(P(sh.x() + 25, sh.y() + 28), P(hip.x() + 19, hip.y() - 22), P(hip.x() + 16, hip.y()))
    shirt_r.lineTo(P(hip.x() + 8, hip.y()))
    shirt_r.lineTo(P(sh.x() + 20, sh.y() + 20))
    shirt_r.closeSubpath()
    shade_fill(p, shirt_r, SHIRT_W, SHIRT_W_SH, 4.0, 0)
    
    # Haramaki (Belly band)
    band = QPainterPath(P(hip.x() - 18, hip.y() - 15))
    band.quadTo(P(hip.x(), hip.y() - 20), P(hip.x() + 19, hip.y() - 15))
    band.lineTo(P(hip.x() + 18, hip.y() + 5))
    band.quadTo(P(hip.x(), hip.y() + 10), P(hip.x() - 17, hip.y() + 5))
    band.closeSubpath()
    shade_fill(p, band, BAND_Z, BAND_Z_SH, 3.0)
    # Vertical lines
    p.setPen(pen(BAND_Z_SH.darker(115), 1.5))
    for i in range(-12, 15, 4):
        p.drawLine(P(hip.x() + i, hip.y() - 15), P(hip.x() + i, hip.y() + 5))

def draw_zoro_leg(p, hip, a, k, back):
    knee, ankle, sa = leg_points(hip, a, k)
    pant, pant_sh = (PANT_Z.darker(110), PANT_Z_SH.darker(110)) if back else (PANT_Z, PANT_Z_SH)
    
    # Boot
    p.save()
    p.translate(ankle)
    p.rotate(-math.degrees(sa) * 0.45)
    shoe = tapered_path([P(-2, -1), P(9, 0.5), P(19, 1.8)], [16.5, 14.5, 10.0])
    shade_fill(p, shoe, QColor("#222"), QColor("#000"), 3.0, 2.1)
    # Boot Cuff
    p.setBrush(QColor("#111"))
    p.drawEllipse(P(1, -2), 9, 4)
    p.restore()
    
    # Pant
    leg = tapered_path([hip, knee, ankle], [28, 20, 16])
    shade_fill(p, leg, pant, pant_sh, 3.5)
    return ankle

def draw_swords(p, hip):
    # Draw 3 swords on right hip (back side visually)
    p.save()
    p.translate(hip.x() - 10, hip.y() - 5)
    p.rotate(-35)
    
    for i, (scab_c, hilt_c) in enumerate([
        (QColor("#f4f5f0"), QColor("#284732")), # Wado Ichimonji
        (QColor("#8b0000"), QColor("#5c0000")), # Sandai Kitetsu
        (QColor("#222222"), QColor("#aa00aa"))  # Shusui / Enma
    ]):
        y = i * 7
        # Scabbard
        sword = QPainterPath()
        sword.addRoundedRect(QRectF(-45, y, 55, 5), 2, 2)
        shade_fill(p, sword, scab_c, scab_c.darker(120), 1.5)
        
        # Crossguard (Tsuba)
        tsuba = QPainterPath()
        tsuba.addEllipse(P(12, y + 2.5), 3, 5)
        shade_fill(p, tsuba, QColor("gold"), QColor("darkgoldenrod"), 1.0)
        
        # Hilt (Tsuka)
        hilt = QPainterPath()
        hilt.addRoundedRect(QRectF(14, y + 0.5, 16, 4), 1, 1)
        shade_fill(p, hilt, hilt_c, hilt_c.darker(150), 1.0)
        # Hilt wrap pattern (diamonds)
        p.setPen(pen(QColor("gold"), 0.5))
        for j in range(15, 28, 3):
            p.drawLine(P(j, y + 0.5), P(j+2, y + 4.5))
            p.drawLine(P(j+2, y + 0.5), P(j, y + 4.5))
            
    p.restore()

def draw_zoro(p, pose, look_x=None):
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
    
    # Swords should be behind the body and left arm
    draw_swords(p, hip)
    
    draw_arm(p, back_sh, *pose.arms[0], back=True, t=pose.t)
    p.restore()

    draw_zoro_leg(p, hip, *pose.legs[0], back=True)
    draw_zoro_leg(p, hip, *pose.legs[1], back=False)

    upper_begin()
    neck_top = P(sh.x() + 4, sh.y() - 13)
    neck = tapered_path([P(sh.x() + 3, sh.y() + 2), neck_top], [13, 12])
    shade_fill(p, neck, SKIN_SH, SKIN_SH.darker(112), 2.0)
    
    draw_zoro_torso(p, hip, sh)
    
    # Zoro bandana on left arm (front arm)
    if not pose.arms_behind:
        draw_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t)
        # Draw bandana tied on bicep
        elbow = P(front_sh.x() + L_UPPER * math.sin(pose.arms[1][0]), front_sh.y() + L_UPPER * math.cos(pose.arms[1][0]))
        bicep = lerp_pt(front_sh, elbow, 0.4)
        p.save()
        p.translate(bicep)
        p.rotate(-math.degrees(pose.arms[1][0]))
        p.setBrush(BAND_Z)
        p.setPen(pen(OUT, 1.5))
        p.drawRect(QRectF(-8, -4, 16, 6))
        # Knot
        p.drawEllipse(P(-9, -1), 3, 3)
        p.drawLine(P(-10, -1), P(-16, -5))
        p.drawLine(P(-10, -1), P(-14, 4))
        p.restore()
        
    p.save()
    p.translate(neck_top)
    p.rotate(pose.head_rot)
    p.translate(-neck_top)
    draw_zoro_head(p, P(sh.x() + 5, sh.y() - 37), pose.mood, pose.t)
    p.restore()
    
    if pose.arms_behind:
        draw_arm(p, front_sh, *pose.arms[1], back=False, t=pose.t)
    p.restore()
