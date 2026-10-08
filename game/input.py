"""Keyboard + gamepad input, reduced to a few simple signals.

Scenes read:
    move_x        -1, 0 or 1 (held)
    jump_pressed  True on the frame jump was pressed
    confirm       True on the frame Space/Enter/A was pressed
    back          True on the frame Esc/Back was pressed
    nav_x         -1/1 on the frame left/right was pressed (menus)

For touch screens, Controls also tracks "pointers" (fingers, and the mouse when
touch mode is forced for desktop testing) in game coordinates. game/touch.py turns
them into move_x / jump_pressed during gameplay.
"""
import os
import sys

import pygame

from .settings import HEIGHT, WIDTH

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
CONFIRM_KEYS = (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
AXIS_DEADZONE = 0.5


def on_android():
    """True when running as an Android app (python-for-android or CPython on Android)."""
    return hasattr(sys, "getandroidapilevel") or "ANDROID_ARGUMENT" in os.environ   # python-for-android sets this


class Controls:
    def __init__(self, touch=False):
        self.joysticks = {}
        self.move_x = 0
        self._axis_dir = 0
        # Touch mode shows the on-screen buttons. It turns on by itself at the first
        # finger touch; `touch=True` forces it and lets the mouse act as a finger.
        self.touch_mode = touch or on_android()
        self.mouse_is_finger = touch
        self.pointers = {}       # pointer id -> (x, y) in game coordinates, while held
        self.begin_frame()

    def begin_frame(self):
        self.jump_pressed = False
        self.confirm = False
        self.back = False
        self.nav_x = 0
        self.pointer_downs = []  # (x, y) of pointers pressed this frame

    def _press(self, pid, pos):
        self.pointers[pid] = pos
        self.pointer_downs.append(pos)

    def handle_event(self, e):
        if self._handle_pointer(e):
            return
        if e.type == pygame.KEYDOWN:
            if e.key in JUMP_KEYS:
                self.jump_pressed = True
            if e.key in CONFIRM_KEYS:
                self.confirm = True
            if e.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):   # AC_BACK: Android back button
                self.back = True
            if e.key in LEFT_KEYS:
                self.nav_x = -1
            elif e.key in RIGHT_KEYS:
                self.nav_x = 1
        elif e.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(e.device_index)
            self.joysticks[joy.get_instance_id()] = joy
        elif e.type == pygame.JOYDEVICEREMOVED:
            self.joysticks.pop(e.instance_id, None)
        elif e.type == pygame.JOYBUTTONDOWN:
            if e.button in (0, 1, 2, 3):
                self.jump_pressed = True
                self.confirm = True
            elif e.button == 6:
                self.back = True
            elif e.button == 7:
                self.confirm = True
        elif e.type == pygame.JOYHATMOTION and e.value[0]:
            self.nav_x = e.value[0]
        elif e.type == pygame.JOYAXISMOTION and e.axis == 0:
            d = 1 if e.value > AXIS_DEADZONE else -1 if e.value < -AXIS_DEADZONE else 0
            if d and d != self._axis_dir:
                self.nav_x = d
            self._axis_dir = d

    def _handle_pointer(self, e):
        """Track fingers (and the mouse in forced touch mode). Returns True if consumed."""
        if e.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            # SDL reports fingers as 0..1 across the game area (SCALED handles letterboxing)
            pid = ("finger", e.touch_id, e.finger_id)
            pos = (e.x * WIDTH, e.y * HEIGHT)
            if e.type == pygame.FINGERDOWN:
                self.touch_mode = True
                self._press(pid, pos)
            elif e.type == pygame.FINGERMOTION and pid in self.pointers:
                self.pointers[pid] = pos
            elif e.type == pygame.FINGERUP:
                self.pointers.pop(pid, None)
            return True
        if self.mouse_is_finger and not getattr(e, "touch", False):
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._press("mouse", e.pos)
            elif e.type == pygame.MOUSEMOTION and "mouse" in self.pointers:
                self.pointers["mouse"] = e.pos
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.pointers.pop("mouse", None)
        if e.type in (pygame.WINDOWFOCUSLOST, pygame.APP_WILLENTERBACKGROUND):
            self.pointers.clear()   # a finger lifted while away would otherwise stay "held"
        return False

    def update(self):
        keys = pygame.key.get_pressed()
        x = 0
        if any(keys[k] for k in LEFT_KEYS):
            x -= 1
        if any(keys[k] for k in RIGHT_KEYS):
            x += 1
        for joy in self.joysticks.values():
            if joy.get_numhats():
                x += joy.get_hat(0)[0]
            if joy.get_numaxes():
                v = joy.get_axis(0)
                if abs(v) > AXIS_DEADZONE:
                    x += 1 if v > 0 else -1
        self.move_x = max(-1, min(1, x))


class AutoPilot:
    """Plays a level by holding right and jumping at walls and gaps (smoke tests)."""

    def __init__(self):
        self.move_x = 1
        self.begin_frame()
        self._last_x = None
        self._stuck = 0.0

    def begin_frame(self):
        self.jump_pressed = False
        self.confirm = False
        self.back = False
        self.nav_x = 0

    def handle_event(self, e):
        pass

    def update(self):
        pass

    def steer(self, scene, dt):
        from .settings import TILE
        p, lvl = scene.player, scene.level
        r = p.rect
        self.move_x = 1
        if self._last_x is not None and abs(p.x - self._last_x) < 0.5:
            self._stuck += dt
        else:
            self._stuck = 0.0
        self._last_x = p.x
        if not p.on_ground:
            return
        col = (r.right + 6) // TILE
        body_rows = range(r.top // TILE, (r.bottom - 1) // TILE + 1)
        wall = any((col, row) in lvl.solids for row in body_rows)
        foot_row = r.bottom // TILE
        def has_floor(row):
            return (col, row) in lvl.solids or (col, row) in lvl.platforms
        floor = has_floor(foot_row)
        # Just walk off a ledge when there is ground a little way below
        drop_ok = any(has_floor(row) for row in range(foot_row + 1, foot_row + 5))
        if wall or (not floor and not drop_ok) or self._stuck > 0.3:
            self.jump_pressed = True
