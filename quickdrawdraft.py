# THIS GAME WAS CODED BY GEMINI 3.1 PRO AND GEMINI 3.8 FLASH, PROMPTED BY RHYS LIANG, ALIASED SP2
# YOU MAY EDIT THE GAME IN ANY WAY YOU LIKE AND REDISTRIBUTE IT
# HAVE FUN!

import os
import sys
import math
import time
import random
import socket
import pygame
import pygame.gfxdraw

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 760
FPS = 60

# Pixel-3D Low-Res Buffer Scale (3x nearest-neighbor for Buckshot aesthetic)
PIXEL_3D_SCALE = 3
BUF_W = SCREEN_WIDTH // PIXEL_3D_SCALE
BUF_H = SCREEN_HEIGHT // PIXEL_3D_SCALE

# LAN Networking Configuration
BROADCAST_PORT = 44555
BROADCAST_IP = "<broadcast>"
MAGIC_HEADER = "QUICKDRAW_V3"

# Target & Opponent Positioning
TARGET_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
TARGET_RADIUS = 128

# Konami Code Sequence: Up, Up, Down, Down, Left, Right, Left, Right
KONAMI_CODE = [
    pygame.K_UP, pygame.K_UP,
    pygame.K_DOWN, pygame.K_DOWN,
    pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_LEFT, pygame.K_RIGHT
]

# Palette - Buckshot Industrial & CRT Arcade Palette
COLOR_BG = (14, 16, 20)
COLOR_BALATRO_BG = (12, 11, 18)
COLOR_CRT_SCANLINE = (0, 0, 0, 42)
COLOR_TABLE_DARK = (20, 23, 29)
COLOR_WOOD_RAIL = (42, 26, 18)
COLOR_RAIL_ACCENT = (215, 162, 50)

COLOR_PANEL_BG = (18, 22, 28, 242)
COLOR_PANEL_BORDER = (58, 68, 82)
COLOR_WHITE = (246, 248, 252)

# Retro Chiseled White Glove Palette
COLOR_GLOVE_BASE = (224, 228, 236)
COLOR_GLOVE_SIDE = (182, 188, 200)
COLOR_GLOVE_DARK = (138, 145, 158)
COLOR_GLOVE_SEAM = (38, 42, 52)
COLOR_CUFF_SUIT = (24, 26, 32)

# Slick Western Gunslinger Palette
COLOR_HAT_DARK = (28, 22, 26)
COLOR_HAT_BRIM = (38, 30, 36)
COLOR_HAT_BAND = (138, 35, 40)
COLOR_BANDANA = (165, 38, 45)
COLOR_BANDANA_SHADOW = (110, 22, 28)
COLOR_COAT_DARK = (36, 28, 26)
COLOR_COAT_MID = (54, 42, 38)
COLOR_COAT_LIGHT = (76, 58, 52)
COLOR_LEATHER_BELT = (95, 54, 30)
COLOR_DENIM = (30, 36, 46)
COLOR_BOOTS = (28, 20, 18)
COLOR_FLESH = (215, 175, 145)

# Buckshot Revolver Metals & Wood
COLOR_GUN_DARK = (36, 40, 48)
COLOR_GUN_MID = (56, 63, 74)
COLOR_GUN_STEEL = (78, 86, 100)
COLOR_GUN_BRIGHT = (118, 128, 144)
COLOR_GUN_RUST = (102, 54, 38)
COLOR_BRASS = (205, 158, 52)
COLOR_PRIMER = (230, 195, 110)
COLOR_GRIP_WOOD = (76, 42, 26)
COLOR_GRIP_DARK = (48, 25, 15)

COLOR_PIXEL_YELLOW = (250, 204, 21)
COLOR_PIXEL_ORANGE = (249, 115, 22)
COLOR_PIXEL_RED = (225, 29, 72)
COLOR_PIXEL_GREEN = (34, 197, 94)
COLOR_PIXEL_BLUE = (59, 130, 246)
COLOR_PIXEL_PURPLE = (168, 85, 247)
COLOR_PIXEL_CYAN = (56, 189, 248)
COLOR_PIXEL_DARK = (10, 12, 16)
COLOR_GOLD = (250, 204, 21)
COLOR_TEXT_DIM = (148, 163, 184)

# ---------------------------------------------------------
# UI & TEXT HELPERS
# ---------------------------------------------------------
def draw_fitted_text(surface, text, font, color, center_x, center_y, max_width, shadow_color=None):
    t_surf = font.render(text, True, color)
    t_sh = font.render(text, True, shadow_color) if shadow_color else None
    if t_surf.get_width() > max_width and max_width > 0:
        scale = max_width / t_surf.get_width()
        nw = max(1, int(t_surf.get_width() * scale))
        nh = max(1, int(t_surf.get_height() * scale))
        t_surf = pygame.transform.smoothscale(t_surf, (nw, nh))
        if t_sh:
            t_sh = pygame.transform.smoothscale(t_sh, (nw, nh))
    if t_sh:
        surface.blit(t_sh, (center_x - t_surf.get_width() // 2 + 2, center_y - t_surf.get_height() // 2 + 2))
    surface.blit(t_surf, (center_x - t_surf.get_width() // 2, center_y - t_surf.get_height() // 2))

def draw_pixel_button(surface, rect, text, font, base_color, text_color=COLOR_WHITE, hover=False, clicked=False, corner=6):
    bx, by, bw, bh = rect.x, rect.y, rect.width, rect.height
    depth = 2 if clicked else (4 if hover else 6)
    offset_y = 4 if clicked else (2 if hover else 0)

    dark_shade = tuple(max(0, int(c * 0.45)) for c in base_color[:3])
    pygame.draw.rect(surface, dark_shade, (bx, by + depth, bw, bh), border_radius=corner)
    pygame.draw.rect(surface, COLOR_PIXEL_DARK, (bx - 2, by + depth - 2, bw + 4, bh + 4), width=2, border_radius=corner)

    face_col = tuple(min(255, int(c * 1.15)) for c in base_color[:3]) if hover else base_color
    face_rect = pygame.Rect(bx, by + offset_y, bw, bh)
    pygame.draw.rect(surface, face_col, face_rect, border_radius=corner)
    pygame.draw.rect(surface, (255, 255, 255, 120), face_rect, width=2, border_radius=corner)

    draw_fitted_text(surface, text, font, text_color, face_rect.centerx, face_rect.centery, bw - 14, shadow_color=COLOR_PIXEL_DARK)

def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# ---------------------------------------------------------
# 3D MATH & LOW-POLY ENGINE
# ---------------------------------------------------------
def rot_x(v, a):
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x, y * ca - z * sa, y * sa + z * ca)

def rot_y(v, a):
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca + z * sa, y, -x * sa + z * ca)

def rot_z(v, a):
    x, y, z = v
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca - y * sa, x * sa + y * ca, z)

def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )

def vec_norm(v):
    m = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if m < 1e-6:
        return (0.0, 1.0, 0.0)
    return (v[0] / m, v[1] / m, v[2] / m)

def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def add_box_faces(faces_list, x0, y0, z0, x1, y1, z1, color, tag="body", outline=True):
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    quad_indices = [
        (0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
        (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0),
    ]
    for i0, i1, i2, i3 in quad_indices:
        faces_list.append({
            "verts": [v[i0], v[i1], v[i2], v[i3]],
            "color": color,
            "tag": tag,
            "outline": outline
        })

def add_extruded_limb(faces_list, p_start, p_end, rx, ry, color, seam_color=None, tag="glove"):
    dx, dy, dz = vec_sub(p_end, p_start)
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-4:
        return
    fwd = (dx / length, dy / length, dz / length)
    up_ref = (0.0, 1.0, 0.0) if abs(fwd[1]) < 0.9 else (1.0, 0.0, 0.0)
    right = vec_norm(vec_cross(up_ref, fwd))
    up = vec_norm(vec_cross(fwd, right))

    def corner(p, sx, sy):
        return (
            p[0] + right[0] * sx + up[0] * sy,
            p[1] + right[1] * sx + up[1] * sy,
            p[2] + right[2] * sx + up[2] * sy,
        )

    b0, b1, b2, b3 = corner(p_start, -rx, -ry), corner(p_start, rx, -ry), corner(p_start, rx, ry), corner(p_start, -rx, ry)
    t0, t1, t2, t3 = corner(p_end, -rx * 0.88, -ry * 0.88), corner(p_end, rx * 0.88, -ry * 0.88), corner(p_end, rx * 0.88, ry * 0.88), corner(p_end, -rx * 0.88, ry * 0.88)

    quads = [
        ([b0, b1, b2, b3], color),
        ([t1, t0, t3, t2], color),
        ([t0, b0, b3, t3], COLOR_GLOVE_SIDE if color == COLOR_GLOVE_BASE else color),
        ([b1, t1, t2, b2], COLOR_GLOVE_SIDE if color == COLOR_GLOVE_BASE else color),
        ([b3, b2, t2, t3], color),
        ([t0, t1, b1, b0], COLOR_GLOVE_DARK if color == COLOR_GLOVE_BASE else color),
    ]
    for q_verts, q_col in quads:
        faces_list.append({"verts": q_verts, "color": q_col, "tag": tag, "outline": True})

    if seam_color:
        s0 = corner(p_start, 0, ry * 1.03)
        s1 = corner(p_end, 0, ry * 0.92)
        s2 = corner(p_end, rx * 0.18, ry * 0.92)
        s3 = corner(p_start, rx * 0.18, ry * 1.03)
        faces_list.append({
            "verts": [s0, s1, s2, s3],
            "color": seam_color,
            "tag": tag,
            "outline": False
        })

# ---------------------------------------------------------
# SLICK 3D WESTERN COWBOY GUNSLINGER (OPPONENT MODEL)
# ---------------------------------------------------------
class Opponent3DRig:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = [0.0, -0.65, 20.0]
        self.dead = False
        self.fall_progress = 0.0
        self.projected_polys = []
        self.muzzle_screen_pt = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def kill(self):
        self.dead = True

    def build_mesh(self):
        faces = []
        fp = self.fall_progress

        hy = 1.95 - fp * 1.8
        hz = -fp * 2.8

        # 1. Curved Cattleman Cowboy Hat
        add_box_faces(faces, -0.85, hy + 0.14, hz - 1.25, 0.85, hy + 0.24, hz + 1.25, COLOR_HAT_BRIM, tag="opp_head")
        add_box_faces(faces, -1.45, hy + 0.28, hz - 1.05, -0.85, hy + 0.38, hz + 1.05, COLOR_HAT_BRIM, tag="opp_head")
        add_box_faces(faces,  0.85, hy + 0.28, hz - 1.05,  1.45, hy + 0.38, hz + 1.05, COLOR_HAT_BRIM, tag="opp_head")

        add_box_faces(faces, -0.58, hy + 0.24, hz - 0.72, 0.58, hy + 0.95, hz + 0.72, COLOR_HAT_DARK, tag="opp_head")
        add_box_faces(faces, -0.38, hy + 0.95, hz - 0.55, 0.38, hy + 1.05, hz + 0.55, COLOR_HAT_DARK, tag="opp_head")
        add_box_faces(faces, -0.60, hy + 0.24, hz - 0.74, 0.60, hy + 0.38, hz + 0.74, COLOR_HAT_BAND, tag="opp_head")
        add_box_faces(faces, -0.15, hy + 0.22, hz - 0.76, 0.15, hy + 0.40, hz - 0.73, COLOR_BRASS, tag="opp_head")

        # 2. Face, Bandit Bandana & Duelist Eyes
        add_box_faces(faces, -0.42, hy - 0.52, hz - 0.42, 0.42, hy + 0.22, hz + 0.42, COLOR_FLESH, tag="opp_head")
        add_box_faces(faces, -0.28, hy - 0.12, hz - 0.44, -0.10, hy - 0.04, hz - 0.41, COLOR_PIXEL_YELLOW, tag="opp_head")
        add_box_faces(faces,  0.10, hy - 0.12, hz - 0.44,  0.28, hy - 0.04, hz - 0.41, COLOR_PIXEL_YELLOW, tag="opp_head")

        add_box_faces(faces, -0.46, hy - 0.65, hz - 0.52, 0.46, hy - 0.18, hz + 0.38, COLOR_BANDANA, tag="opp_head")
        add_box_faces(faces, -0.28, hy - 0.92, hz - 0.54, 0.28, hy - 0.65, hz - 0.46, COLOR_BANDANA_SHADOW, tag="opp_head")

        # 3. Shoulder Duster Capelet & Trench Coat
        ty_top = hy - 0.65
        ty_bot = ty_top - 2.15

        add_box_faces(faces, -1.65, ty_top - 0.65, hz - 0.75, 1.65, ty_top + 0.12, hz + 0.75, COLOR_COAT_MID, tag="opp_torso")
        add_box_faces(faces, -0.92, ty_bot, hz - 0.58, 0.92, ty_top, hz + 0.58, COLOR_COAT_DARK, tag="opp_torso")
        add_box_faces(faces, -0.55, ty_bot + 0.35, hz - 0.62, 0.55, ty_top - 0.15, hz - 0.54, COLOR_COAT_LIGHT, tag="opp_torso")

        add_box_faces(faces, -0.75, ty_bot + 0.45, hz - 0.66, 0.75, ty_top - 0.10, hz - 0.60, COLOR_LEATHER_BELT, tag="opp_torso")
        for bi in range(5):
            bx = -0.55 + bi * 0.28
            by = ty_bot + 0.65 + bi * 0.26
            add_box_faces(faces, bx - 0.06, by - 0.09, hz - 0.68, bx + 0.06, by + 0.09, hz - 0.64, COLOR_BRASS, tag="opp_torso")

        add_box_faces(faces, -0.96, ty_bot - 0.28, hz - 0.62, 0.96, ty_bot + 0.05, hz + 0.62, COLOR_LEATHER_BELT, tag="opp_torso")
        add_box_faces(faces, -0.22, ty_bot - 0.24, hz - 0.66, 0.22, ty_bot + 0.02, hz - 0.60, COLOR_BRASS, tag="opp_torso")

        # 4. Drawn Revolver & Duelist Arms
        add_box_faces(faces, 0.95, ty_top - 0.65, hz - 1.85, 1.45, ty_top - 0.18, hz + 0.55, COLOR_COAT_DARK, tag="opp_arm")
        add_box_faces(faces, 1.05, ty_top - 0.60, hz - 2.35, 1.35, ty_top - 0.25, hz - 1.85, COLOR_GLOVE_BASE, tag="opp_arm")

        add_box_faces(faces, 1.10, ty_top - 0.58, hz - 2.85, 1.30, ty_top - 0.28, hz - 2.35, COLOR_GUN_DARK, tag="opp_arm")
        add_box_faces(faces, 1.14, ty_top - 0.52, hz - 3.85, 1.26, ty_top - 0.34, hz - 2.85, COLOR_GUN_STEEL, tag="opp_arm")
        add_box_faces(faces, 1.16, ty_top - 0.34, hz - 3.85, 1.24, ty_top - 0.26, hz - 3.65, COLOR_PIXEL_ORANGE, tag="opp_arm")

        add_box_faces(faces, -1.48, ty_bot + 0.35, hz - 0.35, -0.95, ty_top - 0.20, hz + 0.45, COLOR_COAT_DARK, tag="opp_arm")
        add_box_faces(faces, -1.35, ty_bot - 0.05, hz - 0.65, -0.98, ty_bot + 0.38, hz - 0.25, COLOR_GLOVE_BASE, tag="opp_arm")

        # 5. Split Coat Tails, Pants & Riding Boots
        add_box_faces(faces, -1.05, ty_bot - 1.85, hz - 0.62, -0.15, ty_bot, hz + 0.62, COLOR_COAT_DARK, tag="opp_legs")
        add_box_faces(faces,  0.15, ty_bot - 1.85, hz - 0.62,  1.05, ty_bot, hz + 0.62, COLOR_COAT_DARK, tag="opp_legs")

        add_box_faces(faces, -0.82, ty_bot - 2.45, hz - 0.38, -0.18, ty_bot, hz + 0.38, COLOR_DENIM, tag="opp_legs")
        add_box_faces(faces,  0.18, ty_bot - 2.45, hz - 0.38,  0.82, ty_bot, hz + 0.38, COLOR_DENIM, tag="opp_legs")

        add_box_faces(faces, -0.84, ty_bot - 3.35, hz - 0.42, -0.16, ty_bot - 2.45, hz + 0.42, COLOR_BOOTS, tag="opp_legs")
        add_box_faces(faces,  0.16, ty_bot - 3.35, hz - 0.42,  0.84, ty_bot - 2.45, hz + 0.42, COLOR_BOOTS, tag="opp_legs")
        add_box_faces(faces, -0.88, ty_bot - 3.25, hz + 0.38, -0.72, ty_bot - 3.12, hz + 0.48, COLOR_BRASS, tag="opp_legs")
        add_box_faces(faces,  0.72, ty_bot - 3.25, hz + 0.38,  0.88, ty_bot - 3.12, hz + 0.48, COLOR_BRASS, tag="opp_legs")

        # Rotate onto floor if dead
        if self.dead:
            ground_y = -3.8
            for f in faces:
                laid_verts = []
                for vx, vy, vz in f["verts"]:
                    ry_rel = vy - ground_y
                    rx, ry, rz = rot_z((vx, ry_rel, vz), 1.48)
                    rx, ry, rz = rot_x((rx, ry, rz), 0.35)
                    laid_verts.append((rx - 1.2, ry + ground_y + 0.55, rz + 1.5))
                f["verts"] = laid_verts

        return faces

# ---------------------------------------------------------
# REVOLVER 3D RIG (FIRST PERSON)
# ---------------------------------------------------------
class Revolver3DRig:
    def __init__(self):
        self.low_res_surf = pygame.Surface((BUF_W, BUF_H), pygame.SRCALPHA)
        self.light_dir = vec_norm((-0.38, 0.75, -0.55))
        self.reset()

    def reset(self):
        self.pos_x = 5.2
        self.pos_y = -6.8
        self.pos_z = 9.0

        self.drawn_pos = (2.25, -1.75, 7.6)
        self.aim_pos = (1.05, -1.15, 6.4)

        self.yaw = -0.26
        self.pitch = 0.16
        self.roll = -0.06
        self.spin_pitch = 0.0

        self.hammer_lerp = 0.0
        self.trigger_lerp = 0.0
        self.cylinder_angle = 0.0

        self.fan_active = False
        self.fan_progress = 0.0
        self.muzzle_flash_timer = 0

        self.hammer_screen_pts = []
        self.hammer_center_2d = (0, 0)
        self.muzzle_screen_2d = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def build_current_mesh(self, spinning_mode=False):
        faces = []

        # Heavy Vented Barrel
        add_box_faces(faces, -0.30, 0.02, 1.1, 0.30, 0.50, 6.6, COLOR_GUN_DARK)
        add_box_faces(faces, -0.22, 0.50, 1.1, 0.22, 0.68, 6.6, COLOR_GUN_STEEL)
        for vz in (1.6, 2.7, 3.8, 4.9):
            add_box_faces(faces, -0.24, 0.52, vz, 0.24, 0.65, vz + 0.65, COLOR_PIXEL_DARK, outline=False)
        add_box_faces(faces, -0.22, -0.32, 1.1, 0.22, 0.02, 6.2, COLOR_GUN_MID)
        add_box_faces(faces, -0.08, 0.68, 5.95, 0.08, 0.98, 6.52, COLOR_PIXEL_ORANGE)

        faces.append({
            "verts": [(-0.18, 0.12, 6.62), (0.18, 0.12, 6.62), (0.18, 0.42, 6.62), (-0.18, 0.42, 6.62)],
            "color": (8, 10, 12), "tag": "body", "outline": True
        })

        # Receiver Frame & Rear Sight Notch
        add_box_faces(faces, -0.34, 0.58, -1.45, 0.34, 0.74, 1.20, COLOR_GUN_STEEL)
        add_box_faces(faces, -0.34, 0.74, -1.42, -0.10, 0.92, -1.05, COLOR_GUN_BRIGHT)
        add_box_faces(faces,  0.10, 0.74, -1.42,  0.34, 0.92, -1.05, COLOR_GUN_BRIGHT)
        add_box_faces(faces, -0.36, -0.58, -1.55, 0.36, -0.32, 1.15, COLOR_GUN_DARK)
        add_box_faces(faces, -0.42, -0.58, -1.75, 0.42, 0.60, -1.05, COLOR_GUN_MID)
        add_box_faces(faces, -0.44, -0.25, -1.68, -0.40, 0.38, -1.12, COLOR_GUN_RUST, outline=False)
        add_box_faces(faces,  0.40, -0.25, -1.68,  0.44, 0.38, -1.12, COLOR_GUN_RUST, outline=False)

        # Trigger Guard Loop
        add_box_faces(faces, -0.14, -1.25, -0.85, 0.14, -1.10, 0.55, COLOR_GUN_STEEL)
        add_box_faces(faces, -0.14, -1.20,  0.40, 0.14, -0.55, 0.58, COLOR_GUN_STEEL)
        add_box_faces(faces, -0.14, -1.20, -0.90, 0.14, -0.55, -0.72, COLOR_GUN_STEEL)

        tz = -0.10 - self.trigger_lerp * 0.32
        add_box_faces(faces, -0.07, -1.05, tz - 0.12, 0.07, -0.55, tz + 0.12, COLOR_BRASS)

        # Cylinder
        cyl_sides = 12
        cyl_r = 0.68
        cyl_cy = 0.08
        z_back, z_front = -1.02, 1.05
        ring_back = []
        ring_front = []
        for i in range(cyl_sides):
            a = self.cylinder_angle + i * (2 * math.pi / cyl_sides)
            cx = math.cos(a) * cyl_r
            cy = cyl_cy + math.sin(a) * cyl_r
            ring_back.append((cx, cy, z_back))
            ring_front.append((cx, cy, z_front))

        for i in range(cyl_sides):
            ni = (i + 1) % cyl_sides
            col = COLOR_GUN_STEEL if i % 2 == 0 else COLOR_GUN_DARK
            faces.append({
                "verts": [ring_back[i], ring_front[i], ring_front[ni], ring_back[ni]],
                "color": col, "tag": "body", "outline": True
            })

        faces.append({
            "verts": ring_back[::-1],
            "color": COLOR_GUN_DARK, "tag": "body", "outline": True
        })
        for ch_i in range(6):
            ca = self.cylinder_angle + ch_i * (math.pi / 3.0) + 0.25
            ch_x = math.cos(ca) * 0.42
            ch_y = cyl_cy + math.sin(ca) * 0.42
            pr = 0.14
            brass_quad = [
                (ch_x - pr, ch_y - pr, z_back - 0.02),
                (ch_x + pr, ch_y - pr, z_back - 0.02),
                (ch_x + pr, ch_y + pr, z_back - 0.02),
                (ch_x - pr, ch_y + pr, z_back - 0.02),
            ]
            faces.append({"verts": brass_quad, "color": COLOR_BRASS, "tag": "body", "outline": True})

        # Hammer
        h_piv = (0.0, 0.38, -1.55)
        h_rot = -self.hammer_lerp * 0.78
        temp_hammer_faces = []
        add_box_faces(temp_hammer_faces, -0.14, 0.0, -0.18, 0.14, 0.72, 0.18, COLOR_GUN_BRIGHT, tag="hammer")
        add_box_faces(temp_hammer_faces, -0.34, 0.62, -0.38, 0.34, 0.88, 0.16, COLOR_BRASS, tag="hammer")
        add_box_faces(temp_hammer_faces, -0.28, 0.88, -0.34, 0.28, 0.98, 0.08, COLOR_GUN_BRIGHT, tag="hammer")

        for hf in temp_hammer_faces:
            rot_verts = []
            for vx, vy, vz in hf["verts"]:
                rx, ry, rz = rot_x((vx, vy, vz), h_rot)
                rot_verts.append((rx + h_piv[0], ry + h_piv[1], rz + h_piv[2]))
            hf["verts"] = rot_verts
            faces.append(hf)

        # Grip
        add_extruded_limb(faces, (0.0, -0.45, -1.52), (0.0, -2.55, -2.35), 0.34, 0.40, COLOR_GRIP_WOOD, seam_color=COLOR_GRIP_DARK, tag="grip")
        add_box_faces(faces, -0.32, -2.70, -2.58, 0.32, -2.42, -2.05, COLOR_BRASS)

        # White-Gloved Hands
        if not spinning_mode:
            add_extruded_limb(faces, (0.35, -0.90, -1.65), (0.48, -2.45, -2.55), 0.28, 0.38, COLOR_GLOVE_BASE, seam_color=COLOR_GLOVE_SEAM, tag="glove")
            add_extruded_limb(faces, (-0.16, -0.88, -1.82), (-0.36, -0.86, -1.52), 0.14, 0.14, COLOR_GLOVE_BASE, seam_color=COLOR_GLOVE_SEAM, tag="glove")
            add_extruded_limb(faces, (-0.36, -0.86, -1.52), (-0.38, -0.78, -1.15), 0.12, 0.12, COLOR_GLOVE_SIDE, tag="glove")

            trig_pull_z = -0.15 - self.trigger_lerp * 0.25
            add_extruded_limb(faces, (0.34, -0.92, -1.45), (0.28, -0.96, -0.38), 0.12, 0.12, COLOR_GLOVE_BASE, tag="glove")
            add_extruded_limb(faces, (0.28, -0.96, -0.38), (0.04, -0.96, trig_pull_z), 0.11, 0.11, COLOR_GLOVE_SIDE, tag="glove")

            for fy, fz in [(-1.22, -1.35), (-1.62, -1.60), (-2.02, -1.85)]:
                add_extruded_limb(faces, (0.36, fy, fz - 0.20), (0.06, fy, fz + 0.15), 0.13, 0.13, COLOR_GLOVE_BASE, seam_color=COLOR_GLOVE_SEAM, tag="glove")
                add_extruded_limb(faces, (0.06, fy, fz + 0.15), (-0.28, fy, fz - 0.05), 0.12, 0.12, COLOR_GLOVE_SIDE, tag="glove")

            add_extruded_limb(faces, (0.48, -2.40, -2.50), (1.20, -3.55, -3.25), 0.46, 0.48, COLOR_GLOVE_BASE, seam_color=COLOR_GLOVE_SEAM, tag="glove")
            add_extruded_limb(faces, (1.15, -3.45, -3.20), (2.35, -4.95, -4.10), 0.55, 0.58, COLOR_CUFF_SUIT, tag="glove")
        else:
            add_extruded_limb(faces, (-0.55, -0.85, -0.15), (0.55, -0.85, -0.15), 0.20, 0.20, COLOR_GLOVE_BASE)

        # Fanning Hand
        if self.fan_active:
            t = self.fan_progress
            hx = -1.85 + t * 3.40
            hy = 1.45 - math.sin(t * math.pi) * 0.35 - t * 0.30
            hz = -0.45 - t * 1.65

            add_extruded_limb(faces, (hx - 0.95, hy + 0.55, hz - 0.45), (hx + 0.15, hy + 0.05, hz + 0.15), 0.48, 0.20, COLOR_GLOVE_BASE, seam_color=COLOR_GLOVE_SEAM)
            for lf_i in range(4):
                off = (lf_i - 1.5) * 0.21
                add_extruded_limb(faces, (hx + 0.10, hy + 0.05 + off * 0.3, hz + 0.15 + off), (hx + 0.85, hy - 0.22 + off * 0.3, hz + 0.45 + off), 0.11, 0.11, COLOR_GLOVE_SIDE)
            add_extruded_limb(faces, (hx - 0.90, hy + 0.52, hz - 0.42), (hx - 2.10, hy + 1.25, hz - 1.10), 0.52, 0.32, COLOR_GLOVE_BASE)

        return faces

    def transform_and_project_point(self, v):
        p = (v[0], v[1] + 0.85, v[2] + 0.15)
        p = rot_x(p, self.spin_pitch)
        p = (p[0], p[1] - 0.85, p[2] - 0.15)

        p = rot_z(p, self.roll)
        p = rot_x(p, self.pitch)
        p = rot_y(p, self.yaw)

        wx = p[0] + self.pos_x
        wy = p[1] + self.pos_y
        wz = max(1.2, p[2] + self.pos_z)

        fov_low = 265.0
        bx = BUF_W * 0.5 + (wx * fov_low) / wz
        by = BUF_H * 0.5 - (wy * fov_low) / wz

        sx = bx * PIXEL_3D_SCALE
        sy = by * PIXEL_3D_SCALE
        return (wx, wy, wz), (int(bx), int(by)), (int(sx), int(sy))

    def is_hammer_hovered(self, mouse_pos):
        if not self.hammer_screen_pts:
            return False
        xs = [p[0] for p in self.hammer_screen_pts]
        ys = [p[1] for p in self.hammer_screen_pts]
        bbox = pygame.Rect(min(xs) - 14, min(ys) - 14, (max(xs) - min(xs)) + 28, (max(ys) - min(ys)) + 28)
        return bbox.collidepoint(mouse_pos)

    def render(self, target_surface, sx, sy, highlight_hammer=False, spinning_mode=False):
        self.low_res_surf.fill((0, 0, 0, 0))
        faces = self.build_current_mesh(spinning_mode=spinning_mode)

        rendered_polys = []
        hammer_2d_Full = []

        _, _, self.muzzle_screen_2d = self.transform_and_project_point((0.0, 0.32, 6.7))

        for f in faces:
            world_verts = []
            buf_verts = []
            scr_verts = []
            for v in f["verts"]:
                wv, bv, sv = self.transform_and_project_point(v)
                world_verts.append(wv)
                buf_verts.append(bv)
                scr_verts.append(sv)

            if f["tag"] == "hammer":
                hammer_2d_Full.extend(scr_verts)

            avg_z = sum(wv[2] for wv in world_verts) / len(world_verts)
            if self.fan_active and f["tag"] == "glove" and avg_z < 8.2:
                avg_z -= 0.35

            v0, v1, v2 = world_verts[0], world_verts[1], world_verts[2]
            normal = vec_norm(vec_cross(vec_sub(v1, v0), vec_sub(v2, v0)))
            ndotl = abs(vec_dot(normal, self.light_dir))
            shade = 0.58 + 0.52 * ndotl

            base_c = f["color"]
            if f["tag"] == "hammer" and highlight_hammer:
                lit_col = (255, 238, 130)
            else:
                lit_col = (
                    max(0, min(255, int(base_c[0] * shade))),
                    max(0, min(255, int(base_c[1] * shade))),
                    max(0, min(255, int(base_c[2] * shade))),
                )

            rendered_polys.append((avg_z, buf_verts, lit_col, f["outline"], f["tag"]))

        rendered_polys.sort(key=lambda item: item[0], reverse=True)

        for _, pts, col, has_outline, tag in rendered_polys:
            pygame.draw.polygon(self.low_res_surf, col, pts)
            if has_outline:
                edge_col = (250, 204, 21) if (tag == "hammer" and highlight_hammer) else (16, 18, 24)
                pygame.draw.polygon(self.low_res_surf, edge_col, pts, width=1)

        scaled_3d = pygame.transform.scale(self.low_res_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
        target_surface.blit(scaled_3d, (sx, sy))

        self.hammer_screen_pts = [(p[0] + sx, p[1] + sy) for p in hammer_2d_Full]
        if self.hammer_screen_pts:
            xs = [p[0] for p in self.hammer_screen_pts]
            ys = [p[1] for p in self.hammer_screen_pts]
            cx_h = (min(xs) + max(xs)) // 2
            cy_h = (min(ys) + max(ys)) // 2
            self.hammer_center_2d = (cx_h, cy_h)

            if highlight_hammer:
                pulse_col = COLOR_PIXEL_YELLOW if (pygame.time.get_ticks() // 110) % 2 == 0 else COLOR_WHITE
                box = pygame.Rect(min(xs) - 10, min(ys) - 10, (max(xs) - min(xs)) + 20, (max(ys) - min(ys)) + 20)
                pygame.draw.rect(target_surface, pulse_col, box, width=3, border_radius=4)

# ---------------------------------------------------------
# PARTICLES & FX ENGINE
# ---------------------------------------------------------
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity=0.05):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.base_color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        col = (self.base_color[0], self.base_color[1], self.base_color[2], max(0, min(255, alpha)))
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class FXEngine:
    def __init__(self):
        self.particles = []
        self.shake_time = 0
        self.shake_mag = 0
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)

    def spawn_sparks(self, x, y, count=18, colors=None, speed_range=(2, 9)):
        if colors is None:
            colors = [COLOR_PIXEL_YELLOW, COLOR_PIXEL_ORANGE, COLOR_WHITE]
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(*speed_range)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                random.choice(colors), random.uniform(2, 5), random.randint(15, 38), gravity=0.12
            ))

    def spawn_gunsmoke(self, x, y, count=25):
        for _ in range(count):
            ang = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            spd = random.uniform(1.0, 5.5)
            c = random.choice([(190, 195, 205), (140, 148, 160), (100, 108, 120)])
            self.particles.append(Particle(
                x + random.uniform(-12, 12), y + random.uniform(-12, 12),
                math.cos(ang) * spd, math.sin(ang) * spd,
                c, random.uniform(5, 12), random.randint(30, 65), gravity=-0.04
            ))

    def trigger_shake(self, frames, mag):
        self.shake_time = max(self.shake_time, frames)
        self.shake_mag = max(self.shake_mag, mag)

    def trigger_white_flash(self, alpha=255, color=(255, 255, 255)):
        self.flash_alpha = alpha
        self.flash_color = color

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
        if self.shake_time > 0:
            self.shake_time -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 20)

    def get_offset(self):
        if self.shake_time > 0:
            return int(random.uniform(-self.shake_mag, self.shake_mag)), int(random.uniform(-self.shake_mag, self.shake_mag))
        return 0, 0

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        if self.flash_alpha > 0:
            f_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            f_surf.fill((*self.flash_color, self.flash_alpha))
            surface.blit(f_surf, (0, 0))

# ---------------------------------------------------------
# LAN NETWORKING (SUB-5MS BROADCAST P2P)
# ---------------------------------------------------------
class LANNetworkManager:
    def __init__(self, nickname="Gunslinger"):
        self.instance_id = hex(random.getrandbits(32))[2:]
        self.nickname = nickname

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass

        try:
            self.sock.bind(("", BROADCAST_PORT))
        except OSError:
            self.sock.bind(("0.0.0.0", BROADCAST_PORT))
        self.sock.setblocking(False)

        self.last_broadcast_time = 0
        self.peers = {}  # {id: (name, last_seen, ip, state)}

        self.outgoing_challenge = None  # (target_id, timestamp)
        self.challenge_cooldowns = {}   # {target_id: timestamp}

        self.pending_challenge = None   # (challenger_id, challenger_name, timestamp)
        self.opponent_id = None
        self.opponent_name = None
        self.is_host = False

    def broadcast_presence(self, app_state):
        now = time.time()
        if now - self.last_broadcast_time >= 0.8:
            self.last_broadcast_time = now
            msg = f"{MAGIC_HEADER}|LOBBY_PING|{self.instance_id}|{self.nickname}|{app_state}"
            try:
                self.sock.sendto(msg.encode(), (BROADCAST_IP, BROADCAST_PORT))
            except OSError:
                pass

    def send_broadcast_cmd(self, target_id, cmd, payload=""):
        msg = f"{MAGIC_HEADER}|{cmd}|{target_id}|{self.instance_id}|{payload}"
        try:
            self.sock.sendto(msg.encode(), (BROADCAST_IP, BROADCAST_PORT))
        except OSError:
            pass

    def prune_peers(self):
        now = time.time()
        for i_id in list(self.peers.keys()):
            if now - self.peers[i_id][1] > 3.0:
                del self.peers[i_id]
        
        # Cleanup expired outgoing challenges and cooldowns
        if self.outgoing_challenge and now - self.outgoing_challenge[1] > 15.0:
            self.outgoing_challenge = None
        if self.pending_challenge and now - self.pending_challenge[2] > 15.0:
            self.pending_challenge = None
        for i_id in list(self.challenge_cooldowns.keys()):
            if now > self.challenge_cooldowns[i_id]:
                del self.challenge_cooldowns[i_id]

    def poll(self):
        now = time.time()
        self.prune_peers()
        events = []

        while True:
            try:
                data, addr = self.sock.recvfrom(2048)
            except (BlockingIOError, socket.error):
                break

            text = data.decode(errors="ignore")
            parts = text.split("|")
            if len(parts) < 3 or parts[0] != MAGIC_HEADER:
                continue

            cmd = parts[1]

            if cmd == "LOBBY_PING":
                sender_id = parts[2]
                sender_name = parts[3]
                state = parts[4] if len(parts) > 4 else "MENU"
                if sender_id != self.instance_id:
                    self.peers[sender_id] = (sender_name, now, addr[0], state)

            elif cmd in ("CHALLENGE", "ACCEPT", "DECLINE", "SYNC_START", "SYNC_GO", "HIT_CONFIRMED", "LOBBY_RETURN"):
                target_id = parts[2]
                sender_id = parts[3]
                payload = parts[4] if len(parts) > 4 else ""

                if target_id == self.instance_id:
                    if cmd == "CHALLENGE":
                        events.append(("CHALLENGE_RECEIVED", sender_id, payload))
                    elif cmd == "ACCEPT":
                        events.append(("CHALLENGE_ACCEPTED", sender_id, payload))
                    elif cmd == "DECLINE":
                        events.append(("CHALLENGE_DECLINED", sender_id))
                    elif cmd == "SYNC_START":
                        events.append(("SYNC_START", sender_id))
                    elif cmd == "SYNC_GO":
                        events.append(("SYNC_GO", sender_id))
                    elif cmd == "HIT_CONFIRMED":
                        events.append(("HIT_CONFIRMED", sender_id, payload))
                    elif cmd == "LOBBY_RETURN":
                        events.append(("LOBBY_RETURN", sender_id))

        return events

# ---------------------------------------------------------
# MAIN QUICKDRAW APPLICATION
# ---------------------------------------------------------
class QuickdrawApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quickdraw - 3D Buckshot Multiplayer")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        font_name = pygame.font.match_font("couriernew") or pygame.font.match_font("consolas") or "arial"
        self.font_title_mega = pygame.font.Font(font_name, 54)
        self.font_title = pygame.font.Font(font_name, 28)
        self.font_main = pygame.font.Font(font_name, 18)
        self.font_small = pygame.font.Font(font_name, 14)
        self.font_tiny = pygame.font.Font(font_name, 12)

        self.app_state = "MENU"
        self.game_mode = "SINGLE"
        self.scanline_surface = self._build_scanline_overlay()
        self.title_phase = 0.0

        self.revolver = Revolver3DRig()
        self.opponent = Opponent3DRig()
        self.fx = FXEngine()
        self.net = LANNetworkManager(nickname=f"Gunslinger_{random.randint(100, 999)}")

        # Action Rectangles
        self.holster_rect = pygame.Rect(SCREEN_WIDTH - 245, SCREEN_HEIGHT - 128, 215, 98)
        self.brace_rect = pygame.Rect(30, SCREEN_HEIGHT - 128, 215, 98)
        self.sp_retry_rect = pygame.Rect(580 + 550 // 2 - 155, 565, 310, 56)
        self.mp_retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 155, 490, 310, 56)

        self.nickname_input_active = False
        self.lobby_notice = ""
        self.lobby_notice_timer = 0

        # Duel State Variables
        self.duel_stage = "COUNTDOWN"
        self.stage_timer = 0
        self.go_flash_timer = 0
        self.go_timestamp = 0
        self.elapsed_ms = 0
        self.stopwatch_running = False

        # Singleplayer Scoring & Stats
        self.shot_pos = None
        self.shot_offset = (0, 0)
        self.shot_distance = 0.0
        self.accuracy_score = 0
        self.speed_multiplier = 1.0
        self.total_score = 0
        self.rank_title = ""
        self.rank_color = COLOR_GOLD
        self.high_score = 0
        self.best_time_ms = None
        self.zoom_lerp = 0.0

        # Konami Code Easter Egg
        self.konami_idx = 0
        self.cheat_armed = False
        self.macro_active = False

        # Multiplayer Results
        self.duel_winner = None
        self.opponent_time_ms = 0

    def _build_scanline_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(overlay, COLOR_CRT_SCANLINE, (0, y), (SCREEN_WIDTH, y), 1)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 95), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=35)
        pygame.draw.rect(vignette, (0, 0, 0, 175), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=12)
        overlay.blit(vignette, (0, 0))
        return overlay

    def start_singleplayer_duel(self):
        self.game_mode = "SINGLE"
        self.revolver.reset()
        self.duel_stage = "COUNTDOWN"
        self.stage_timer = pygame.time.get_ticks()
        self.go_flash_timer = 0
        self.elapsed_ms = 0
        self.stopwatch_running = False
        self.shot_pos = None
        self.zoom_lerp = 0.0

        if self.cheat_armed:
            self.macro_active = True
            self.cheat_armed = False
        else:
            self.macro_active = False

        self.app_state = "GAME"

    def start_multiplayer_duel(self, is_host):
        self.game_mode = "LAN_MULTIPLAYER"
        self.net.is_host = is_host
        self.revolver.reset()
        self.opponent.reset()
        self.duel_stage = "COUNTDOWN"
        self.stage_timer = pygame.time.get_ticks()
        self.go_flash_timer = 0
        self.elapsed_ms = 0
        self.stopwatch_running = False
        self.shot_pos = None
        self.duel_winner = None
        self.macro_active = False
        self.app_state = "GAME"

        if is_host:
            self.net.send_broadcast_cmd(self.net.opponent_id, "SYNC_START")

    def calculate_score(self):
        dx = self.shot_pos[0] - TARGET_CENTER[0]
        dy = self.shot_pos[1] - TARGET_CENTER[1]
        self.shot_offset = (dx, dy)
        self.shot_distance = math.hypot(dx, dy)

        if self.shot_distance <= TARGET_RADIUS:
            norm_dist = self.shot_distance / TARGET_RADIUS
            bullseye_bonus = 1000 if self.shot_distance <= 16 else (400 if self.shot_distance <= 36 else 0)
            self.accuracy_score = int(4000 * ((1.0 - norm_dist) ** 1.35)) + bullseye_bonus
        else:
            over = self.shot_distance - TARGET_RADIUS
            self.accuracy_score = max(100, int(600 - over * 6))

        sec = max(0.001, self.elapsed_ms / 1000.0)
        self.speed_multiplier = round(max(0.5, min(4.5, 3.6 / (sec ** 0.85))), 2)

        self.total_score = int(self.accuracy_score * self.speed_multiplier)
        if self.total_score > self.high_score:
            self.high_score = self.total_score
        if self.shot_distance <= TARGET_RADIUS:
            if self.best_time_ms is None or self.elapsed_ms < self.best_time_ms:
                self.best_time_ms = self.elapsed_ms

        if self.total_score >= 9500:
            self.rank_title = "S+ // DEADEYE LEGEND"
            self.rank_color = COLOR_PIXEL_YELLOW
        elif self.total_score >= 7000:
            self.rank_title = "A // PHANTOM GUNSLINGER"
            self.rank_color = COLOR_PIXEL_CYAN
        elif self.total_score >= 4800:
            self.rank_title = "B // BOUNTY HUNTER"
            self.rank_color = COLOR_PIXEL_GREEN
        elif self.total_score >= 2500:
            self.rank_title = "C // SALOON DEPUTY"
            self.rank_color = COLOR_PIXEL_ORANGE
        else:
            self.rank_title = "D // RUSTY TRIGGER"
            self.rank_color = COLOR_PIXEL_RED

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.title_phase += 0.04
            self.handle_network()
            self.handle_events()
            self.update(dt)
            self.render()
            pygame.display.flip()

    def handle_network(self):
        self.net.broadcast_presence(self.app_state)
        events = self.net.poll()

        for ev in events:
            etype = ev[0]
            if etype == "CHALLENGE_RECEIVED":
                sender_id, challenger_name = ev[1], ev[2]
                if self.app_state in ("LAN_LOBBY", "MENU"):
                    self.net.pending_challenge = (sender_id, challenger_name, time.time())

            elif etype == "CHALLENGE_ACCEPTED":
                sender_id, opponent_name = ev[1], ev[2]
                self.net.outgoing_challenge = None
                self.net.opponent_id = sender_id
                self.net.opponent_name = opponent_name
                self.start_multiplayer_duel(is_host=True)

            elif etype == "CHALLENGE_DECLINED":
                sender_id = ev[1]
                if self.net.outgoing_challenge and self.net.outgoing_challenge[0] == sender_id:
                    self.net.outgoing_challenge = None
                self.net.challenge_cooldowns[sender_id] = time.time() + 15.0

            elif etype == "SYNC_START":
                sender_id = ev[1]
                self.start_multiplayer_duel(is_host=False)

            elif etype == "SYNC_GO":
                now = pygame.time.get_ticks()
                self.duel_stage = "WAIT_HOLSTER"
                self.go_timestamp = now
                self.stopwatch_running = True
                self.go_flash_timer = 35
                self.fx.trigger_shake(8, 4)

            elif etype == "HIT_CONFIRMED":
                # Opponent shot you first! Realistic gunshot crack -> 1s pitch-black screen -> Defeat!
                sender_id, opp_time = ev[1], int(ev[2])
                if self.duel_winner is None:
                    self.duel_winner = "OPPONENT"
                    self.opponent_time_ms = opp_time
                    self.stopwatch_running = False
                    self.duel_stage = "OPPONENT_FLASH"
                    self.stage_timer = pygame.time.get_ticks()
                    self.fx.trigger_shake(26, 15)
                    self.fx.trigger_white_flash(245, color=(255, 235, 235))

            elif etype == "LOBBY_RETURN":
                if self.duel_stage != "DUEL_RESULT":
                    self.app_state = "LAN_LOBBY"
                    self.lobby_notice = "Other player left, returning to lobby"
                    self.lobby_notice_timer = pygame.time.get_ticks() + 4500
                    self.net.opponent_id = None
                    self.net.opponent_name = None
                    self.duel_winner = None
                    self.duel_stage = "COUNTDOWN"

    def check_opponent_body_hit(self, mouse_pos):
        mx, my = mouse_pos
        for poly in self.opponent.projected_polys:
            if point_in_polygon(mx, my, poly):
                return True
        dist = math.hypot(mx - TARGET_CENTER[0], my - TARGET_CENTER[1])
        return dist <= 95

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.game_mode == "LAN_MULTIPLAYER" and self.net.opponent_id:
                    self.net.send_broadcast_cmd(self.net.opponent_id, "LOBBY_RETURN")
                pygame.quit()
                sys.exit()

            # Text input for nickname in Lobby
            if self.app_state == "LAN_LOBBY" and self.nickname_input_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.nickname_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.net.nickname = self.net.nickname[:-1]
                    else:
                        if len(self.net.nickname) < 16 and event.unicode.isprintable():
                            self.net.nickname += event.unicode
                    return

            # Konami Code & Spacebar Restart Handling
            if event.type == pygame.KEYDOWN:
                can_enter_konami = (self.app_state == "MENU") or (
                    self.app_state == "GAME" and self.game_mode == "SINGLE" and self.duel_stage == "ZOOM_SCORE"
                )
                if can_enter_konami:
                    if event.key == KONAMI_CODE[self.konami_idx]:
                        self.konami_idx += 1
                        if self.konami_idx == len(KONAMI_CODE):
                            self.cheat_armed = True
                            self.konami_idx = 0
                    else:
                        self.konami_idx = 1 if event.key == KONAMI_CODE[0] else 0

                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                    if self.app_state == "GAME":
                        if self.game_mode == "SINGLE" and self.duel_stage in ("SHOOTING", "SPINNING", "ZOOM_SCORE"):
                            self.start_singleplayer_duel()
                            return
                        elif self.game_mode == "LAN_MULTIPLAYER" and self.duel_stage == "DUEL_RESULT":
                            self._exit_to_lobby_and_notify()
                            return

            if self.app_state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    sp_btn = pygame.Rect(SCREEN_WIDTH // 2 - 210, 480, 420, 58)
                    mp_btn = pygame.Rect(SCREEN_WIDTH // 2 - 210, 555, 420, 58)
                    if sp_btn.collidepoint(mouse_pos):
                        self.start_singleplayer_duel()
                    elif mp_btn.collidepoint(mouse_pos):
                        self.app_state = "LAN_LOBBY"

            elif self.app_state == "LAN_LOBBY":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    back_btn = pygame.Rect(24, 18, 110, 34)
                    if back_btn.collidepoint(mouse_pos):
                        self.app_state = "MENU"
                        return

                    nick_box = pygame.Rect(SCREEN_WIDTH // 2 - 140, 155, 280, 42)
                    if nick_box.collidepoint(mouse_pos):
                        self.nickname_input_active = True
                        return
                    else:
                        self.nickname_input_active = False

                    # Modal Incoming Challenge dialog
                    if self.net.pending_challenge:
                        acc_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, 430, 120, 44)
                        dec_btn = pygame.Rect(SCREEN_WIDTH // 2 + 10, 430, 120, 44)
                        c_id, c_name, _ = self.net.pending_challenge
                        if acc_btn.collidepoint(mouse_pos):
                            self.net.opponent_id = c_id
                            self.net.opponent_name = c_name
                            self.net.send_broadcast_cmd(c_id, "ACCEPT", self.net.nickname)
                            self.net.pending_challenge = None
                            self.start_multiplayer_duel(is_host=False)
                            return
                        elif dec_btn.collidepoint(mouse_pos):
                            self.net.send_broadcast_cmd(c_id, "DECLINE")
                            self.net.pending_challenge = None
                            return

                    # Challenge button clicks in the live peer list
                    lobby_peers = list(self.net.peers.items())
                    list_rect = pygame.Rect(SCREEN_WIDTH // 2 - 340, 240, 680, 420)
                    for idx, (p_id, (p_name, _, _, p_state)) in enumerate(lobby_peers):
                        row_y = list_rect.y + 72 + idx * 58
                        chal_btn = pygame.Rect(SCREEN_WIDTH // 2 + 170, row_y - 17, 120, 36)
                        if chal_btn.collidepoint(mouse_pos):
                            if p_state == "GAME":
                                pass
                            elif p_id in self.net.challenge_cooldowns and time.time() < self.net.challenge_cooldowns[p_id]:
                                pass
                            elif self.net.outgoing_challenge and time.time() - self.net.outgoing_challenge[1] < 15.0:
                                pass
                            else:
                                self.net.send_broadcast_cmd(p_id, "CHALLENGE", self.net.nickname)
                                self.net.outgoing_challenge = (p_id, time.time())
                            return

            elif self.app_state == "GAME":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.duel_stage != "BLACKOUT":
                        menu_btn = pygame.Rect(24, 18, 110, 34)
                        if menu_btn.collidepoint(mouse_pos):
                            if self.game_mode == "LAN_MULTIPLAYER":
                                if self.duel_stage != "DUEL_RESULT":
                                    self._exit_to_lobby_and_notify()
                                else:
                                    self.app_state = "LAN_LOBBY"
                            else:
                                self.app_state = "MENU"
                            return

                    if not self.macro_active:
                        # STEP 1: Click Holster
                        if self.duel_stage == "WAIT_HOLSTER":
                            if self.holster_rect.collidepoint(mouse_pos):
                                self.duel_stage = "DRAWING"
                                self.stage_timer = pygame.time.get_ticks()
                                self.fx.spawn_sparks(self.holster_rect.centerx, self.holster_rect.centery, count=14, colors=[COLOR_PIXEL_GREEN, COLOR_WHITE])
                                return

                        # STEP 2: Click Hammer
                        elif self.duel_stage in ("DRAWING", "WAIT_HAMMER"):
                            if self.revolver.is_hammer_hovered(mouse_pos):
                                self.duel_stage = "FANNING"
                                self.stage_timer = pygame.time.get_ticks()
                                self.revolver.fan_active = True
                                self.revolver.fan_progress = 0.0
                                hx, hy = self.revolver.hammer_center_2d
                                self.fx.spawn_sparks(hx, hy, count=20, colors=[COLOR_PIXEL_YELLOW, COLOR_PIXEL_ORANGE, COLOR_WHITE])
                                self.fx.trigger_shake(6, 3)
                                return

                        # STEP 3: Click Lock Sights
                        elif self.duel_stage == "WAIT_BRACE":
                            if self.brace_rect.collidepoint(mouse_pos):
                                self.duel_stage = "WAIT_SHOOT"
                                self.stage_timer = pygame.time.get_ticks()
                                self.fx.spawn_sparks(self.brace_rect.centerx, self.brace_rect.centery, count=14, colors=[COLOR_PIXEL_CYAN, COLOR_WHITE])
                                return

                        # STEP 4: Fire!
                        elif self.duel_stage == "WAIT_SHOOT":
                            if self.game_mode == "SINGLE":
                                dist = math.hypot(mouse_pos[0] - TARGET_CENTER[0], mouse_pos[1] - TARGET_CENTER[1])
                                if dist <= TARGET_RADIUS + 85:
                                    self._execute_singleplayer_shot(mouse_pos)
                                    return
                            else:
                                if self.check_opponent_body_hit(mouse_pos):
                                    self._execute_multiplayer_hit(mouse_pos)
                                    return

                    # Post-Shot Buttons
                    if self.game_mode == "SINGLE":
                        if self.duel_stage in ("SHOOTING", "SPINNING", "ZOOM_SCORE"):
                            if self.sp_retry_rect.collidepoint(mouse_pos):
                                self.start_singleplayer_duel()
                                return
                            elif self.duel_stage in ("SHOOTING", "SPINNING"):
                                self.duel_stage = "ZOOM_SCORE"
                                self.zoom_lerp = 1.0
                                self.revolver.spin_pitch = 0.0
                                return
                    else:
                        if self.duel_stage == "DUEL_RESULT":
                            if self.mp_retry_rect.collidepoint(mouse_pos):
                                # Just leave locally if the game is already completely over
                                self.app_state = "LAN_LOBBY"
                                self.net.opponent_id = None
                                self.duel_winner = None
                                return

    def _exit_to_lobby_and_notify(self):
        """Notifies the opponent to return to the lobby and exits."""
        if self.net.opponent_id:
            self.net.send_broadcast_cmd(self.net.opponent_id, "LOBBY_RETURN")
            self.net.opponent_id = None
            self.net.opponent_name = None
        self.duel_winner = None
        self.app_state = "LAN_LOBBY"

    def _execute_singleplayer_shot(self, mouse_pos):
        now = pygame.time.get_ticks()
        self.stopwatch_running = False
        self.elapsed_ms = now - self.go_timestamp
        self.shot_pos = mouse_pos
        self.calculate_score()

        self.duel_stage = "SHOOTING"
        self.stage_timer = now
        self.revolver.trigger_lerp = 1.0
        self.revolver.hammer_lerp = 0.0
        self.revolver.muzzle_flash_timer = 6

        mx, my = self.revolver.muzzle_screen_2d
        self.fx.trigger_white_flash(180)
        self.fx.trigger_shake(22, 12)
        self.fx.spawn_gunsmoke(mx, my, count=30)
        self.fx.spawn_sparks(mx, my, count=28, speed_range=(4, 14))
        self.fx.spawn_sparks(mouse_pos[0], mouse_pos[1], count=24, colors=[COLOR_PIXEL_RED, COLOR_WHITE, COLOR_PIXEL_YELLOW])

    def _execute_multiplayer_hit(self, mouse_pos):
        now = pygame.time.get_ticks()
        self.stopwatch_running = False
        self.elapsed_ms = now - self.go_timestamp
        self.shot_pos = mouse_pos

        if self.duel_winner is None:
            self.duel_winner = "PLAYER"
            self.net.send_broadcast_cmd(self.net.opponent_id, "HIT_CONFIRMED", str(self.elapsed_ms))

        # Knock opponent flat onto the ground and trigger full-screen white flash!
        self.opponent.kill()
        self.duel_stage = "SHOOTING"
        self.stage_timer = now
        self.revolver.trigger_lerp = 1.0
        self.revolver.hammer_lerp = 0.0
        self.revolver.muzzle_flash_timer = 6

        mx, my = self.revolver.muzzle_screen_2d
        self.fx.trigger_white_flash(255)
        self.fx.trigger_shake(26, 14)
        self.fx.spawn_gunsmoke(mx, my, count=35)
        self.fx.spawn_sparks(mouse_pos[0], mouse_pos[1], count=35, colors=[COLOR_PIXEL_RED, COLOR_PIXEL_YELLOW, COLOR_WHITE])

    def update(self, dt):
        self.fx.update()
        if self.app_state != "GAME":
            return

        now = pygame.time.get_ticks()
        if self.stopwatch_running:
            self.elapsed_ms = now - self.go_timestamp

        if self.go_flash_timer > 0:
            self.go_flash_timer -= 1
        if self.revolver.muzzle_flash_timer > 0:
            self.revolver.muzzle_flash_timer -= 1

        # -----------------------------------------------------
        # SINGLEPLAYER KONAMI 1MS MACRO EXECUTION
        # -----------------------------------------------------
        if self.game_mode == "SINGLE" and self.macro_active and self.duel_stage == "WAIT_HOLSTER":
            self.fx.spawn_sparks(self.holster_rect.centerx, self.holster_rect.centery, count=14, colors=[COLOR_PIXEL_GREEN, COLOR_WHITE])
            dx, dy, dz = self.revolver.drawn_pos
            self.revolver.pos_x, self.revolver.pos_y, self.revolver.pos_z = dx, dy, dz

            self.revolver.hammer_lerp = 1.0
            self.revolver.cylinder_angle += math.pi / 3.0
            hx, hy = self.revolver.hammer_center_2d
            self.fx.spawn_sparks(hx, hy, count=20, colors=[COLOR_PIXEL_YELLOW, COLOR_PIXEL_ORANGE, COLOR_WHITE])

            self.fx.spawn_sparks(self.brace_rect.centerx, self.brace_rect.centery, count=14, colors=[COLOR_PIXEL_CYAN, COLOR_WHITE])
            ax, ay, az = self.revolver.aim_pos
            self.revolver.pos_x, self.revolver.pos_y, self.revolver.pos_z = ax, ay, az

            self.shot_pos = TARGET_CENTER
            self.stopwatch_running = False
            self.elapsed_ms = 1
            self.calculate_score()

            self.revolver.roll = -0.06
            Z_target = 22.0
            FOV_3D = 795.0
            T_x = (TARGET_CENTER[0] - SCREEN_WIDTH * 0.5) * Z_target / FOV_3D
            T_y = -(TARGET_CENTER[1] - SCREEN_HEIGHT * 0.5) * Z_target / FOV_3D
            T_z = Z_target
            S_x = self.revolver.pos_x - 0.83 * math.sin(self.revolver.roll)
            S_y = self.revolver.pos_y + 0.83 * math.cos(self.revolver.roll)
            S_z = self.revolver.pos_z
            V_x, V_y, V_z = T_x - S_x, T_y - S_y, T_z - S_z
            self.revolver.yaw = math.atan2(V_x, V_z)
            self.revolver.pitch = -math.atan2(V_y, math.hypot(V_x, V_z))

            self.duel_stage = "SHOOTING"
            self.stage_timer = now
            self.revolver.trigger_lerp = 1.0
            self.revolver.hammer_lerp = 0.0
            self.revolver.muzzle_flash_timer = 6

            mx, my = self.revolver.muzzle_screen_2d
            self.fx.trigger_white_flash(180)
            self.fx.trigger_shake(22, 12)
            self.fx.spawn_gunsmoke(mx, my, count=30)
            self.fx.spawn_sparks(mx, my, count=28, speed_range=(4, 14))
            self.fx.spawn_sparks(TARGET_CENTER[0], TARGET_CENTER[1], count=24, colors=[COLOR_PIXEL_RED, COLOR_WHITE, COLOR_PIXEL_YELLOW])
            self.macro_active = False
            return

        # 1. Countdown
        if self.duel_stage == "COUNTDOWN":
            if self.game_mode == "SINGLE" or self.net.is_host:
                if now - self.stage_timer >= 2100:
                    self.duel_stage = "WAIT_HOLSTER"
                    self.go_timestamp = now
                    self.stopwatch_running = True
                    self.go_flash_timer = 35
                    self.fx.trigger_shake(8, 4)
                    if self.game_mode == "LAN_MULTIPLAYER" and self.net.is_host:
                        self.net.send_broadcast_cmd(self.net.opponent_id, "SYNC_GO")

        # 2. Drawing 3D Revolver
        elif self.duel_stage == "DRAWING":
            t = min(1.0, (now - self.stage_timer) / 180.0)
            ease = 1.0 - (1.0 - t) ** 3
            dx, dy, dz = self.revolver.drawn_pos
            self.revolver.pos_x = 5.2 + (dx - 5.2) * ease
            self.revolver.pos_y = -6.8 + (dy - (-6.8)) * ease
            self.revolver.pos_z = 9.2 + (dz - 9.2) * ease
            self.revolver.pitch = -0.55 * (1.0 - ease) + 0.14 * ease
            if t >= 1.0:
                self.duel_stage = "WAIT_HAMMER"

        # 3. Fanning Hammer
        elif self.duel_stage == "FANNING":
            t = min(1.0, (now - self.stage_timer) / 145.0)
            self.revolver.fan_progress = t
            self.revolver.hammer_lerp = min(1.0, t * 1.35)
            self.revolver.cylinder_angle = t * (math.pi / 3.0)
            self.revolver.pos_y = self.revolver.drawn_pos[1] - math.sin(t * math.pi) * 0.28
            self.revolver.pitch = 0.14 - math.sin(t * math.pi) * 0.10
            if t >= 1.0:
                self.revolver.fan_active = False
                self.revolver.hammer_lerp = 1.0
                self.duel_stage = "WAIT_BRACE"

        # 4. Aiming (Exact 3D Sight Alignment)
        elif self.duel_stage == "WAIT_SHOOT":
            t_lock = min(1.0, (now - self.stage_timer) / 120.0)
            dx, dy, dz = self.revolver.drawn_pos
            ax, ay, az = self.revolver.aim_pos
            self.revolver.pos_x = dx + (ax - dx) * t_lock
            self.revolver.pos_y = dy + (ay - dy) * t_lock
            self.revolver.pos_z = dz + (az - dz) * t_lock

            mx, my = pygame.mouse.get_pos()
            Z_target = 20.0 if self.game_mode == "LAN_MULTIPLAYER" else 22.0
            FOV_3D = 795.0
            T_x = (mx - SCREEN_WIDTH * 0.5) * Z_target / FOV_3D
            T_y = -(my - SCREEN_HEIGHT * 0.5) * Z_target / FOV_3D
            T_z = Z_target

            self.revolver.roll = -0.06
            S_x = self.revolver.pos_x - 0.83 * math.sin(self.revolver.roll)
            S_y = self.revolver.pos_y + 0.83 * math.cos(self.revolver.roll)
            S_z = self.revolver.pos_z
            V_x, V_y, V_z = T_x - S_x, T_y - S_y, T_z - S_z
            self.revolver.yaw = math.atan2(V_x, V_z)
            self.revolver.pitch = -math.atan2(V_y, math.hypot(V_x, V_z))

        # 5. Recoil Kick
        elif self.duel_stage == "SHOOTING":
            t = min(1.0, (now - self.stage_timer) / 340.0)
            kick = math.sin(t * math.pi)
            ax, ay, az = self.revolver.aim_pos
            self.revolver.pos_z = az - kick * 1.35
            self.revolver.pos_y = ay + kick * 0.45
            self.revolver.spin_pitch = -kick * 0.72

            if t >= 1.0:
                self.revolver.spin_pitch = 0.0
                if self.game_mode == "LAN_MULTIPLAYER":
                    # Show the opponent lying dead on the floor for 0.5s before spinning gun!
                    self.duel_stage = "CORPSE_HOLD"
                    self.stage_timer = now
                else:
                    self.duel_stage = "SPINNING"
                    self.stage_timer = now

        # 6A. Victor Corpse Hold (0.5s showing opponent lying on the floor)
        elif self.duel_stage == "CORPSE_HOLD":
            if now - self.stage_timer >= 500:
                self.duel_stage = "SPINNING"
                self.stage_timer = now

        # 6B. 360-Degree Revolver Spin & Holster
        elif self.duel_stage == "SPINNING":
            t = min(1.0, (now - self.stage_timer) / 720.0)
            ease = 1.0 - (1.0 - t) ** 2
            self.revolver.spin_pitch = -ease * (4.0 * math.pi)
            self.revolver.yaw = -0.45
            self.revolver.roll = -0.25
            if t > 0.65:
                drop_t = (t - 0.65) / 0.35
                self.revolver.pos_y = self.revolver.aim_pos[1] - (drop_t ** 2) * 5.5
            if t >= 1.0:
                self.duel_stage = "DUEL_RESULT" if self.game_mode == "LAN_MULTIPLAYER" else "ZOOM_SCORE"
                self.stage_timer = now

        # 7A. Singleplayer Target Zoom
        elif self.duel_stage == "ZOOM_SCORE":
            self.zoom_lerp = min(1.0, self.zoom_lerp + 0.06)

        # 7B. Loser Sequence Step 1: Realistic sharp gunshot flash (65ms)
        elif self.duel_stage == "OPPONENT_FLASH":
            if now - self.stage_timer >= 65:
                self.duel_stage = "BLACKOUT"
                self.stage_timer = now

        # 7C. Loser Sequence Step 2: Buckshot Roulette 1-Second Pitch Blackout
        elif self.duel_stage == "BLACKOUT":
            if now - self.stage_timer >= 1000:
                self.duel_stage = "DUEL_RESULT"
                self.stage_timer = now

    # -----------------------------------------------------
    # RENDERING METHODS
    # -----------------------------------------------------
    def render(self):
        # Pure pitch-black screen during the 1-second Buckshot Roulette death blackout
        if self.app_state == "GAME" and self.duel_stage == "BLACKOUT":
            self.screen.fill((0, 0, 0))
            return

        if self.app_state == "MENU":
            self.render_menu()
        elif self.app_state == "LAN_LOBBY":
            self.render_lobby()
        else:
            self.render_game()

        self.screen.blit(self.scanline_surface, (0, 0))

    def render_target_board(self, cx, cy, radius, bullet_offset=None, show_measurement=False):
        pygame.gfxdraw.filled_circle(self.screen, int(cx + 5), int(cy + 7), int(radius + 8), (8, 10, 14, 190))
        pygame.gfxdraw.filled_circle(self.screen, int(cx), int(cy), int(radius + 6), COLOR_GUN_STEEL)
        pygame.gfxdraw.aacircle(self.screen, int(cx), int(cy), int(radius + 6), COLOR_RAIL_ACCENT)

        num_rings = 5
        for i in range(num_rings, 0, -1):
            r = int(radius * (i / num_rings))
            col = COLOR_PIXEL_RED if i % 2 == 1 else COLOR_WHITE
            pygame.gfxdraw.filled_circle(self.screen, int(cx), int(cy), r, col)
            pygame.gfxdraw.aacircle(self.screen, int(cx), int(cy), r, (30, 35, 45))

        pygame.draw.line(self.screen, (40, 10, 15), (int(cx - 10), int(cy)), (int(cx + 10), int(cy)), 2)
        pygame.draw.line(self.screen, (40, 10, 15), (int(cx), int(cy - 10)), (int(cx), int(cy + 10)), 2)

        if bullet_offset is not None:
            scale_factor = radius / float(TARGET_RADIUS)
            bh_x = int(cx + bullet_offset[0] * scale_factor)
            bh_y = int(cy + bullet_offset[1] * scale_factor)

            if show_measurement:
                # Dashed measurement line from Bullseye to Bullet Hole
                pygame.draw.line(self.screen, COLOR_PIXEL_YELLOW, (int(cx), int(cy)), (bh_x, bh_y), 3)
                pygame.gfxdraw.filled_circle(self.screen, int(cx), int(cy), 5, COLOR_PIXEL_YELLOW)

            scorch_r = max(9, int(13 * scale_factor))
            hole_r = max(5, int(7 * scale_factor))
            pygame.gfxdraw.filled_circle(self.screen, bh_x, bh_y, scorch_r, (45, 48, 55))
            for c_i in range(6):
                ca = c_i * (math.pi / 3.0) + 0.4
                c_len = scorch_r + 7 * scale_factor
                pygame.draw.line(
                    self.screen, (20, 22, 28),
                    (bh_x, bh_y),
                    (int(bh_x + math.cos(ca) * c_len), int(bh_y + math.sin(ca) * c_len)), 2
                )
            pygame.gfxdraw.filled_circle(self.screen, bh_x, bh_y, hole_r, (10, 12, 16))
            pygame.draw.circle(self.screen, COLOR_PIXEL_YELLOW if show_measurement else (180, 185, 195), (bh_x, bh_y), hole_r + 2, width=2)

    def render_menu(self):
        self.screen.fill(COLOR_BALATRO_BG)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (24, 23, 37), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (24, 23, 37), (0, y), (SCREEN_WIDTH, y))

        bob = math.sin(self.title_phase) * 7
        title_y = int(95 + bob)
        title_text = "BUCKSHOT QUICKDRAW"

        for ox, oy, col in [(6, 6, (12, 10, 18)), (4, 4, (160, 45, 20)), (2, 2, (235, 162, 50))]:
            sh = self.font_title_mega.render(title_text, True, col)
            self.screen.blit(sh, (SCREEN_WIDTH // 2 - sh.get_width() // 2 + ox, title_y + oy))

        title_surf = self.font_title_mega.render(title_text, True, (254, 240, 138))
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, title_y))

        ribbon_txt = self.font_main.render("[ SINGLEPLAYER TARGET RANGE  |  SUB-5MS LAN MULTIPLAYER DEATHMATCH ]", True, COLOR_PIXEL_ORANGE)
        self.screen.blit(ribbon_txt, (SCREEN_WIDTH // 2 - ribbon_txt.get_width() // 2, title_y + 70))

        self.render_target_board(240, 365, 92)

        self.revolver.pos_x = 2.65
        self.revolver.pos_y = -1.35
        self.revolver.pos_z = 7.2
        self.revolver.yaw = -0.35 + math.sin(self.title_phase * 0.6) * 0.18
        self.revolver.pitch = 0.15 + math.cos(self.title_phase * 0.5) * 0.06
        self.revolver.roll = -0.06
        self.revolver.spin_pitch = 0.0
        self.revolver.hammer_lerp = 0.0
        self.revolver.render(self.screen, 0, 0, highlight_hammer=True)

        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 225, 500, 205)
        s = pygame.Surface((box_rect.w, box_rect.h), pygame.SRCALPHA)
        s.fill((18, 22, 30, 235))
        self.screen.blit(s, box_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_RAIL_ACCENT, box_rect, width=2, border_radius=12)

        steps = [
            "HOW TO PLAY (WHEN 'GO!' FLASHES):",
            "1. CLICK [BOTTOM-RIGHT] HOLSTER TO DRAW 3D REVOLVER",
            "2. CLICK THE [3D HAMMER] (GLOWS ON HOVER) TO FAN IT",
            "3. CLICK [BOTTOM-LEFT] SIGHTS ICON TO LOCK AIM",
            "4. SHOOT THE TARGET OR OPPONENT AS FAST AS POSSIBLE!",
        ]
        for i, line in enumerate(steps):
            col = COLOR_GOLD if i == 0 else COLOR_WHITE
            draw_fitted_text(self.screen, line, self.font_small, col, box_rect.centerx, box_rect.y + 28 + i * 36, 470)

        best_t_str = f"{self.best_time_ms / 1000.0:.3f}s" if self.best_time_ms is not None else "--.---s"
        rec_str = f"SINGLEPLAYER HIGH SCORE: {self.high_score:,} PTS   |   FASTEST HIT: {best_t_str}"
        draw_fitted_text(self.screen, rec_str, self.font_main, COLOR_PIXEL_CYAN, SCREEN_WIDTH // 2, 452, 620)

        mouse_pos = pygame.mouse.get_pos()
        sp_btn = pygame.Rect(SCREEN_WIDTH // 2 - 210, 480, 420, 58)
        mp_btn = pygame.Rect(SCREEN_WIDTH // 2 - 210, 555, 420, 58)
        draw_pixel_button(self.screen, sp_btn, "SINGLEPLAYER PRACTICE >>", self.font_title, COLOR_PIXEL_GREEN, hover=sp_btn.collidepoint(mouse_pos))
        draw_pixel_button(self.screen, mp_btn, "2-PLAYER LAN DUEL LOBBY >>", self.font_title, COLOR_PIXEL_CYAN, hover=mp_btn.collidepoint(mouse_pos))

    def render_lobby(self):
        """Multiplayer lobby without IP addresses or text collisions."""
        self.screen.fill(COLOR_BALATRO_BG)
        mouse_pos = pygame.mouse.get_pos()

        back_btn = pygame.Rect(24, 18, 110, 34)
        draw_pixel_button(self.screen, back_btn, "<< MENU", self.font_small, COLOR_PIXEL_DARK, hover=back_btn.collidepoint(mouse_pos))

        draw_fitted_text(self.screen, "SAME WI-FI MULTIPLAYER LOBBY", self.font_title_mega, COLOR_GOLD, SCREEN_WIDTH // 2, 75, 750)
        draw_fitted_text(self.screen, "SUB-5MS BROADCAST DISCOVERY — NO SERVERS NEEDED", self.font_main, COLOR_PIXEL_ORANGE, SCREEN_WIDTH // 2, 120, 600)

        if self.lobby_notice and pygame.time.get_ticks() < self.lobby_notice_timer:
            n_box = pygame.Rect(SCREEN_WIDTH // 2 - 270, 140, 540, 40)
            pygame.draw.rect(self.screen, (38, 14, 18), n_box, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_PIXEL_RED, n_box, width=2, border_radius=8)
            draw_fitted_text(self.screen, self.lobby_notice, self.font_main, COLOR_PIXEL_YELLOW, n_box.centerx, n_box.centery, 520)

        # Nickname Editor Box
        nick_box = pygame.Rect(SCREEN_WIDTH // 2 - 140, 188, 280, 42)
        pygame.draw.rect(self.screen, (22, 28, 38), nick_box, border_radius=8)
        b_col = COLOR_PIXEL_YELLOW if self.nickname_input_active else COLOR_PANEL_BORDER
        pygame.draw.rect(self.screen, b_col, nick_box, width=2, border_radius=8)
        draw_fitted_text(self.screen, f"NICKNAME: {self.net.nickname}", self.font_main, COLOR_WHITE, nick_box.centerx, nick_box.centery, 260)

        # Main Peer Card Container
        list_rect = pygame.Rect(SCREEN_WIDTH // 2 - 340, 240, 680, 420)
        pygame.draw.rect(self.screen, (16, 20, 28), list_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_RAIL_ACCENT, list_rect, width=2, border_radius=12)

        hdr_str = "ACTIVE GUNSLINGERS ON YOUR WI-FI NETWORK:"
        draw_fitted_text(self.screen, hdr_str, self.font_main, COLOR_GOLD, list_rect.centerx, list_rect.y + 24, 620)
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (list_rect.x + 20, list_rect.y + 48), (list_rect.right - 20, list_rect.y + 48), 1)

        peers_list = list(self.net.peers.items())
        if not peers_list:
            draw_fitted_text(self.screen, "NO OTHER GUNSLINGERS DETECTED YET...", self.font_main, COLOR_TEXT_DIM, list_rect.centerx, list_rect.centery, 580)
        else:
            for idx, (p_id, (p_name, _, _, p_state)) in enumerate(peers_list):
                row_y = list_rect.y + 72 + idx * 58
                row_box = pygame.Rect(list_rect.x + 24, row_y - 20, list_rect.w - 48, 46)
                pygame.draw.rect(self.screen, (24, 30, 40), row_box, border_radius=8)
                
                # Display Nickname only
                draw_fitted_text(self.screen, f"• {p_name}", self.font_main, COLOR_WHITE, row_box.x + 140, row_box.centery, 240)

                chal_btn = pygame.Rect(SCREEN_WIDTH // 2 + 170, row_y - 17, 120, 36)
                
                # Determine state of the challenge button
                is_playing = (p_state == "GAME")
                in_cooldown = p_id in self.net.challenge_cooldowns and time.time() < self.net.challenge_cooldowns[p_id]
                has_outgoing = self.net.outgoing_challenge and time.time() - self.net.outgoing_challenge[1] < 15.0
                is_this_outgoing = has_outgoing and self.net.outgoing_challenge[0] == p_id

                if is_playing:
                    draw_pixel_button(self.screen, chal_btn, "PLAYING...", self.font_small, (50, 55, 65), text_color=COLOR_TEXT_DIM)
                elif is_this_outgoing:
                    draw_pixel_button(self.screen, chal_btn, "SENT...", self.font_small, COLOR_PIXEL_CYAN)
                elif in_cooldown or has_outgoing:
                    draw_pixel_button(self.screen, chal_btn, "CHALLENGE", self.font_small, (50, 55, 65), text_color=COLOR_TEXT_DIM)
                else:
                    draw_pixel_button(self.screen, chal_btn, "CHALLENGE", self.font_small, COLOR_PIXEL_GREEN, hover=chal_btn.collidepoint(mouse_pos))

        # Modal Challenge Acceptance Popup
        if self.net.pending_challenge:
            modal = pygame.Rect(SCREEN_WIDTH // 2 - 220, 310, 440, 190)
            pygame.draw.rect(self.screen, (10, 12, 16), modal, border_radius=12)
            pygame.draw.rect(self.screen, COLOR_PIXEL_YELLOW, modal, width=3, border_radius=12)
            c_id, c_name, c_timestamp = self.net.pending_challenge
            
            rem_time = max(0, 15 - int(time.time() - c_timestamp))
            draw_fitted_text(self.screen, "DUEL CHALLENGE RECEIVED!", self.font_title, COLOR_GOLD, modal.centerx, modal.y + 35, 400)
            draw_fitted_text(self.screen, f"{c_name} wants to verse you! ({rem_time}s)", self.font_main, COLOR_WHITE, modal.centerx, modal.y + 80, 400)

            acc_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, 430, 120, 44)
            dec_btn = pygame.Rect(SCREEN_WIDTH // 2 + 10, 430, 120, 44)
            draw_pixel_button(self.screen, acc_btn, "ACCEPT", self.font_small, COLOR_PIXEL_GREEN, hover=acc_btn.collidepoint(mouse_pos))
            draw_pixel_button(self.screen, dec_btn, "DECLINE", self.font_small, COLOR_PIXEL_RED, hover=dec_btn.collidepoint(mouse_pos))

    def render_3d_opponent_gunslinger(self, sx, sy, show_muzzle_flash=False):
        """Projects and renders the 3D opponent gunslinger facing the camera."""
        faces = self.opponent.build_mesh()
        self.opponent.projected_polys.clear()

        # Project opponent muzzle tip for realistic flash rendering
        mx_w = 1.20 + self.opponent.pos[0]
        my_w = 1.95 - 0.65 - 0.42 + self.opponent.pos[1]
        mz_w = max(1.5, -3.95 + self.opponent.pos[2])
        mbx = BUF_W * 0.5 + (mx_w * 265.0) / mz_w
        mby = BUF_H * 0.5 - (my_w * 265.0) / mz_w
        self.opponent.muzzle_screen_pt = (int(mbx * PIXEL_3D_SCALE + sx), int(mby * PIXEL_3D_SCALE + sy))

        rendered = []
        for f in faces:
            scr_verts = []
            z_sum = 0.0
            for vx, vy, vz in f["verts"]:
                wx = vx + self.opponent.pos[0]
                wy = vy + self.opponent.pos[1]
                wz = max(1.5, vz + self.opponent.pos[2])
                z_sum += wz

                bx = BUF_W * 0.5 + (wx * 265.0) / wz
                by = BUF_H * 0.5 - (wy * 265.0) / wz
                scr_verts.append((int(bx * PIXEL_3D_SCALE + sx), int(by * PIXEL_3D_SCALE + sy)))

            avg_z = z_sum / len(f["verts"])
            self.opponent.projected_polys.append(scr_verts)

            v0, v1, v2 = f["verts"][0], f["verts"][1], f["verts"][2]
            normal = vec_norm(vec_cross(vec_sub(v1, v0), vec_sub(v2, v0)))
            ndotl = abs(vec_dot(normal, (-0.38, 0.75, -0.55)))
            shade = 0.58 + 0.48 * ndotl

            base_c = f["color"]
            lit_c = (
                max(0, min(255, int(base_c[0] * shade))),
                max(0, min(255, int(base_c[1] * shade))),
                max(0, min(255, int(base_c[2] * shade))),
            )
            rendered.append((avg_z, scr_verts, lit_c))

        rendered.sort(key=lambda item: item[0], reverse=True)
        for _, pts, col in rendered:
            pygame.draw.polygon(self.screen, col, pts)
            pygame.draw.polygon(self.screen, COLOR_PIXEL_DARK, pts, width=1)

        # Realistic sharp gunshot flash (No cartoon star/yellow circles!)
        if show_muzzle_flash:
            fx, fy = self.opponent.muzzle_screen_pt
            # Sharp directional needle spikes directly toward the player's screen
            spike_h = [
                (fx - 48, fy), (fx - 4, fy - 6), (fx, fy - 38), (fx + 4, fy - 6),
                (fx + 48, fy), (fx + 4, fy + 6), (fx, fy + 38), (fx - 4, fy + 6)
            ]
            spike_d = [
                (fx - 28, fy - 28), (fx - 4, fy - 3), (fx + 28, fy - 28), (fx + 3, fy - 4),
                (fx + 28, fy + 28), (fx + 4, fy + 3), (fx - 28, fy + 28), (fx - 3, fy + 4)
            ]
            # Outer hot gas envelope (subtle crimson / deep orange)
            pygame.draw.polygon(self.screen, (220, 45, 35), spike_h)
            pygame.draw.polygon(self.screen, (240, 95, 40), spike_d)
            # Incandescent blinding white core
            pygame.draw.circle(self.screen, (255, 250, 245), (fx, fy), 18)
            pygame.draw.circle(self.screen, (255, 255, 255), (fx, fy), 10)

    def render_game(self):
        self.screen.fill(COLOR_BG)
        sx, sy = self.fx.get_offset()

        range_rect = pygame.Rect(24 + sx, 64 + sy, SCREEN_WIDTH - 48, SCREEN_HEIGHT - 88)
        pygame.draw.rect(self.screen, COLOR_WOOD_RAIL, range_rect, border_radius=22)
        pygame.draw.rect(self.screen, COLOR_RAIL_ACCENT, range_rect, width=3, border_radius=22)

        inner_range = range_rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, COLOR_TABLE_DARK, inner_range, border_radius=16)

        tcx, tcy = TARGET_CENTER[0] + sx, TARGET_CENTER[1] + sy
        for corner_pt in [(44, 84), (SCREEN_WIDTH - 44, 84), (44, SCREEN_HEIGHT - 44), (SCREEN_WIDTH - 44, SCREEN_HEIGHT - 44)]:
            pygame.draw.line(self.screen, (28, 33, 42), (tcx, tcy), (corner_pt[0] + sx, corner_pt[1] + sy), 2)
        for ring_w in (360, 620, 920):
            r_box = pygame.Rect(tcx - ring_w // 2, tcy - int(ring_w * 0.32), ring_w, int(ring_w * 0.64))
            pygame.draw.rect(self.screen, (28, 33, 42), r_box, width=1, border_radius=8)

        menu_btn = pygame.Rect(24, 18, 110, 34)
        draw_pixel_button(self.screen, menu_btn, "<< LOBBY" if self.game_mode == "LAN_MULTIPLAYER" else "<< MENU", self.font_small, COLOR_PIXEL_DARK, hover=menu_btn.collidepoint(pygame.mouse.get_pos()))

        if self.game_mode == "SINGLE":
            mode_lbl = "SINGLEPLAYER PRACTICE"
        else:
            mode_lbl = f"DUEL VS: {self.net.opponent_name} (HOST)" if not self.net.is_host else f"DUEL VS: {self.net.opponent_name}"
        draw_fitted_text(self.screen, mode_lbl, self.font_main, COLOR_PIXEL_CYAN, SCREEN_WIDTH // 2, 34, 450)

        self.render_stopwatch()

        if self.game_mode == "SINGLE" and self.duel_stage == "ZOOM_SCORE":
            z = self.zoom_lerp
            ease_z = 1.0 - (1.0 - z) ** 3
            cur_cx = TARGET_CENTER[0] + (330 - TARGET_CENTER[0]) * ease_z
            cur_cy = TARGET_CENTER[1] + (395 - TARGET_CENTER[1]) * ease_z
            cur_rad = TARGET_RADIUS + (215 - TARGET_RADIUS) * ease_z

            self.render_target_board(
                cur_cx, cur_cy, cur_rad,
                bullet_offset=self.shot_offset,
                show_measurement=(z > 0.6)
            )
            if z > 0.4:
                self.render_score_panel()
        else:
            # Render Downrange Target (Singleplayer Bullseye OR Multiplayer 3D Gunslinger)
            if self.game_mode == "SINGLE":
                self.render_target_board(
                    tcx, tcy, TARGET_RADIUS,
                    bullet_offset=self.shot_offset if self.shot_pos else None,
                    show_measurement=False
                )
            else:
                self.render_3d_opponent_gunslinger(sx, sy, show_muzzle_flash=(self.duel_stage == "OPPONENT_FLASH"))

            # Render Detailed Corner Widgets
            self.render_corner_widgets(sx, sy)

            # Render 3D Revolver & Gloved Hands
            if self.duel_stage not in ("COUNTDOWN", "WAIT_HOLSTER", "DUEL_RESULT"):
                mouse_pos = pygame.mouse.get_pos()
                hammer_hover = (self.duel_stage in ("DRAWING", "WAIT_HAMMER") and self.revolver.is_hammer_hovered(mouse_pos))
                is_spinning = (self.duel_stage == "SPINNING")
                self.revolver.render(self.screen, sx, sy, highlight_hammer=hammer_hover, spinning_mode=is_spinning)

                if self.duel_stage == "WAIT_HAMMER":
                    hx, hy = self.revolver.hammer_center_2d
                    lbl_col = COLOR_PIXEL_YELLOW if hammer_hover else COLOR_WHITE
                    draw_fitted_text(self.screen, "[ CLICK HAMMER ]", self.font_tiny, lbl_col, hx, hy - 48, 150, shadow_color=(0, 0, 0))

            self.render_center_callouts()

            if self.duel_stage == "DUEL_RESULT" and self.game_mode == "LAN_MULTIPLAYER":
                self.render_multiplayer_result_panel()

        self.fx.draw(self.screen)

    def render_stopwatch(self):
        sw_rect = pygame.Rect(SCREEN_WIDTH - 235, 12, 210, 44)
        pygame.draw.rect(self.screen, (12, 16, 22), sw_rect, border_radius=8)
        border_c = COLOR_PIXEL_GREEN if self.stopwatch_running else (COLOR_PIXEL_YELLOW if self.shot_pos else COLOR_PANEL_BORDER)
        pygame.draw.rect(self.screen, border_c, sw_rect, width=2, border_radius=8)

        sec = self.elapsed_ms // 1000
        ms = self.elapsed_ms % 1000
        time_str = f"TIME: {sec:02d}.{ms:03d}s"
        t_col = COLOR_PIXEL_YELLOW if self.stopwatch_running else (COLOR_PIXEL_GREEN if self.shot_pos else COLOR_TEXT_DIM)
        draw_fitted_text(self.screen, time_str, self.font_main, t_col, sw_rect.centerx, sw_rect.centery, 190)

    def render_corner_widgets(self, sx, sy):
        """Renders the exact holster and iron-sight corner widgets shown in the screenshot."""
        mouse_pos = pygame.mouse.get_pos()
        pulse = (pygame.time.get_ticks() // 150) % 2 == 0

        # --- BOTTOM-RIGHT: HOLSTER / DRAW WIDGET ---
        hr = self.holster_rect.move(sx, sy)
        holster_active = (self.duel_stage == "WAIT_HOLSTER")
        holster_done = (self.duel_stage not in ("COUNTDOWN", "WAIT_HOLSTER"))

        if holster_active:
            bg_col = (22, 85, 45) if not hr.collidepoint(mouse_pos) else (30, 115, 60)
            b_col = COLOR_PIXEL_YELLOW if pulse else COLOR_PIXEL_GREEN
        elif holster_done:
            bg_col = (18, 32, 24)
            b_col = (45, 85, 60)
        else:
            bg_col = (20, 24, 32)
            b_col = COLOR_PANEL_BORDER

        pygame.draw.rect(self.screen, bg_col, hr, border_radius=12)
        pygame.draw.rect(self.screen, b_col, hr, width=3 if holster_active else 2, border_radius=12)

        icx, icy = hr.x + 42, hr.centery
        pygame.draw.polygon(self.screen, COLOR_GOLD if holster_active else COLOR_TEXT_DIM, [
            (icx - 18, icy - 14), (icx + 14, icy - 14), (icx + 6, icy + 20), (icx - 10, icy + 12)
        ], width=2)
        pygame.draw.rect(self.screen, COLOR_WHITE if holster_active else COLOR_TEXT_DIM, (icx - 12, icy - 22, 20, 10), border_radius=2)

        h_lbl1 = "1. DRAW GUN" if not holster_done else "DRAWN [OK]"
        h_lbl2 = "CLICK HERE FAST!" if holster_active else ("DONE" if holster_done else "WAIT FOR GO...")
        draw_fitted_text(self.screen, h_lbl1, self.font_main, COLOR_WHITE if holster_active else COLOR_TEXT_DIM, hr.x + 132, hr.y + 34, 135)
        draw_fitted_text(self.screen, h_lbl2, self.font_tiny, COLOR_PIXEL_YELLOW if holster_active else COLOR_TEXT_DIM, hr.x + 132, hr.y + 66, 135)

        # --- BOTTOM-LEFT: STEADY AIM / LOCK SIGHTS WIDGET ---
        br = self.brace_rect.move(sx, sy)
        brace_active = (self.duel_stage == "WAIT_BRACE")
        brace_done = (self.duel_stage in ("WAIT_SHOOT", "SHOOTING", "CORPSE_HOLD", "SPINNING", "ZOOM_SCORE", "DUEL_RESULT", "OPPONENT_FLASH", "BLACKOUT"))

        if brace_active:
            bg_col = (18, 68, 95) if not br.collidepoint(mouse_pos) else (25, 95, 130)
            b_col = COLOR_PIXEL_YELLOW if pulse else COLOR_PIXEL_CYAN
        elif brace_done:
            bg_col = (18, 30, 38)
            b_col = (45, 80, 95)
        else:
            bg_col = (20, 24, 32)
            b_col = COLOR_PANEL_BORDER

        pygame.draw.rect(self.screen, bg_col, br, border_radius=12)
        pygame.draw.rect(self.screen, b_col, br, width=3 if brace_active else 2, border_radius=12)

        bcx, bcy = br.x + 42, br.centery
        r_col = COLOR_PIXEL_CYAN if brace_active else COLOR_TEXT_DIM
        pygame.draw.circle(self.screen, r_col, (bcx, bcy), 18, width=2)
        pygame.draw.circle(self.screen, r_col, (bcx, bcy), 4)
        pygame.draw.line(self.screen, r_col, (bcx - 24, bcy), (bcx + 24, bcy), 2)
        pygame.draw.line(self.screen, r_col, (bcx, bcy - 24), (bcx, bcy + 24), 2)

        b_lbl1 = "3. LOCK AIM" if not brace_done else "LOCKED [OK]"
        b_lbl2 = "CLICK HERE!" if brace_active else ("READY TO FIRE" if brace_done else "COCK HAMMER FIRST")
        draw_fitted_text(self.screen, b_lbl1, self.font_main, COLOR_WHITE if brace_active else COLOR_TEXT_DIM, br.x + 132, br.y + 34, 135)
        draw_fitted_text(self.screen, b_lbl2, self.font_tiny, COLOR_PIXEL_YELLOW if brace_active else COLOR_TEXT_DIM, br.x + 132, br.y + 66, 135)

        if self.duel_stage == "WAIT_SHOOT":
            mx, my = mouse_pos
            pygame.draw.circle(self.screen, COLOR_PIXEL_YELLOW, (mx, my), 16, width=2)
            pygame.draw.line(self.screen, COLOR_PIXEL_RED, (mx - 22, my), (mx + 22, my), 2)
            pygame.draw.line(self.screen, COLOR_PIXEL_RED, (mx, my - 22), (mx, my + 22), 2)

    def render_center_callouts(self):
        cx, cy = TARGET_CENTER
        now = pygame.time.get_ticks()

        if self.duel_stage == "COUNTDOWN":
            elapsed = now - self.stage_timer
            num = 3 - int(elapsed // 700)
            if num >= 1:
                banner = pygame.Rect(cx - 80, cy - 55, 160, 110)
                s = pygame.Surface((160, 110), pygame.SRCALPHA)
                s.fill((12, 15, 22, 225))
                self.screen.blit(s, banner.topleft)
                pygame.draw.rect(self.screen, COLOR_GOLD, banner, width=3, border_radius=12)
                draw_fitted_text(self.screen, str(num), self.font_title_mega, COLOR_WHITE, cx, cy, 130, shadow_color=(0, 0, 0))

        elif self.go_flash_timer > 0:
            banner = pygame.Rect(cx - 140, cy - 60, 280, 120)
            s = pygame.Surface((280, 120), pygame.SRCALPHA)
            s.fill((18, 65, 32, 235))
            self.screen.blit(s, banner.topleft)
            pygame.draw.rect(self.screen, COLOR_PIXEL_YELLOW, banner, width=4, border_radius=14)
            draw_fitted_text(self.screen, "GO!", self.font_title_mega, COLOR_PIXEL_YELLOW, cx, cy, 240, shadow_color=(0, 0, 0))

    def render_score_panel(self):
        """Full Singleplayer Score Report Panel."""
        panel_rect = pygame.Rect(580, 130, 550, 515)
        s = pygame.Surface((panel_rect.w, panel_rect.h), pygame.SRCALPHA)
        s.fill((16, 20, 28, 242))
        self.screen.blit(s, panel_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_RAIL_ACCENT, panel_rect, width=3, border_radius=16)

        cx = panel_rect.centerx
        draw_fitted_text(self.screen, "QUICKDRAW SCORE REPORT", self.font_title, COLOR_GOLD, cx, panel_rect.y + 42, 500, shadow_color=(0, 0, 0))
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (panel_rect.x + 30, panel_rect.y + 76), (panel_rect.right - 30, panel_rect.y + 76), 2)

        sec = self.elapsed_ms / 1000.0
        hit_status = "BULLSEYE!" if self.shot_distance <= 16 else ("TARGET HIT" if self.shot_distance <= TARGET_RADIUS else "OUTSIDE RING (GRAZE)")

        rows = [
            ("SHOT ACCURACY:", f"{self.shot_distance:.1f} PX FROM CENTER ({hit_status})", COLOR_WHITE),
            ("ACCURACY BASE:", f"{self.accuracy_score:,} PTS", COLOR_PIXEL_GREEN),
            ("DRAW & FIRE TIME:", f"{sec:.3f} SECONDS", COLOR_PIXEL_CYAN),
            ("SPEED MULTIPLIER:", f"x{self.speed_multiplier:.2f}", COLOR_PIXEL_YELLOW),
        ]

        for i, (label, val, col) in enumerate(rows):
            ry = panel_rect.y + 115 + i * 54
            r_box = pygame.Rect(panel_rect.x + 28, ry - 20, panel_rect.w - 56, 42)
            pygame.draw.rect(self.screen, (24, 30, 40), r_box, border_radius=8)
            l_surf = self.font_small.render(label, True, COLOR_TEXT_DIM)
            self.screen.blit(l_surf, (r_box.x + 14, r_box.centery - l_surf.get_height() // 2))
            draw_fitted_text(self.screen, val, self.font_main, col, r_box.right - 145, r_box.centery, 270)

        tot_box = pygame.Rect(panel_rect.x + 28, panel_rect.y + 335, panel_rect.w - 56, 86)
        pygame.draw.rect(self.screen, (12, 15, 20), tot_box, border_radius=10)
        pygame.draw.rect(self.screen, self.rank_color, tot_box, width=2, border_radius=10)

        draw_fitted_text(self.screen, f"FINAL SCORE: {self.total_score:,}", self.font_title, COLOR_WHITE, cx, tot_box.y + 28, 460)
        draw_fitted_text(self.screen, f"RANK: {self.rank_title}", self.font_main, self.rank_color, cx, tot_box.y + 62, 460)

        mouse_pos = pygame.mouse.get_pos()
        draw_pixel_button(
            self.screen, self.sp_retry_rect, "DRAW AGAIN >> (SPACE)",
            self.font_title, COLOR_PIXEL_GREEN, hover=self.sp_retry_rect.collidepoint(mouse_pos)
        )

    def render_multiplayer_result_panel(self):
        """Multiplayer Result Screen: Strictly displays the Victor's draw time."""
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 280, 200, 560, 380)
        s = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
        s.fill((16, 20, 28, 245))
        self.screen.blit(s, panel.topleft)

        won = (self.duel_winner == "PLAYER")
        b_col = COLOR_PIXEL_GREEN if won else COLOR_PIXEL_RED
        pygame.draw.rect(self.screen, b_col, panel, width=3, border_radius=16)

        headline = "YOU DREW FIRST — VICTORY!" if won else "YOU WERE GUNNED DOWN — DEFEAT"
        draw_fitted_text(self.screen, headline, self.font_title, b_col, panel.centerx, panel.y + 55, 510, shadow_color=(0, 0, 0))
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (panel.x + 30, panel.y + 92), (panel.right - 30, panel.y + 92), 2)

        if won:
            victor_time_s = self.elapsed_ms / 1000.0
            victor_label = f"VICTOR'S TIME ({self.net.nickname}): {victor_time_s:.3f}s"
            sub_msg = f"You eliminated {self.net.opponent_name} before they could fire!"
        else:
            victor_time_s = self.opponent_time_ms / 1000.0
            victor_label = f"VICTOR'S TIME ({self.net.opponent_name}): {victor_time_s:.3f}s"
            sub_msg = f"{self.net.opponent_name} beat you to the draw."

        time_box = pygame.Rect(panel.x + 35, panel.y + 125, panel.w - 70, 68)
        pygame.draw.rect(self.screen, (12, 16, 22), time_box, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_GOLD, time_box, width=2, border_radius=10)
        draw_fitted_text(self.screen, victor_label, self.font_title, COLOR_PIXEL_YELLOW, time_box.centerx, time_box.centery, time_box.w - 24)

        draw_fitted_text(self.screen, sub_msg, self.font_main, COLOR_WHITE, panel.centerx, panel.y + 235, 490)

        mouse_pos = pygame.mouse.get_pos()
        draw_pixel_button(
            self.screen, self.mp_retry_rect, "RETURN TO LOBBY >>",
            self.font_title, COLOR_PIXEL_GREEN, hover=self.mp_retry_rect.collidepoint(mouse_pos)
        )

# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QuickdrawApp()
    app.run()
