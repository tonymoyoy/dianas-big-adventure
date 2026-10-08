"""Tiny synthesized sound effects (no audio files). Silently does nothing if audio is unavailable."""
import math
from array import array

import pygame

RATE = 22050
VOLUME = 0.22

# name -> list of (start_hz, end_hz, seconds)
SOUNDS = {
    "jump": [(330, 620, 0.12)],
    "collect": [(880, 880, 0.06), (1320, 1320, 0.12)],
    "bounce": [(200, 700, 0.22)],
    "checkpoint": [(523, 523, 0.08), (659, 659, 0.08), (784, 784, 0.16)],
    "respawn": [(500, 250, 0.25)],
    "finish": [(523, 523, 0.12), (659, 659, 0.12), (784, 784, 0.12), (1047, 1047, 0.35)],
    "select": [(660, 660, 0.05)],
    "locked": [(200, 180, 0.15)],
}


def _synth(notes, channels, rate=RATE):
    buf = array("h")
    for f0, f1, dur in notes:
        n = int(rate * dur)
        phase = 0.0
        for i in range(n):
            k = i / n
            freq = f0 + (f1 - f0) * k
            phase += math.tau * freq / rate
            env = min(1.0, i / (rate * 0.005)) * (1 - k) ** 1.5
            v = math.sin(phase) + 0.25 * math.sin(phase * 2)
            sample = int(v * env * VOLUME * 32767 / 1.25)
            for _ in range(channels):
                buf.append(sample)
    return buf


class Sound:
    def __init__(self):
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=RATE, size=-16, channels=2, buffer=512)
            freq, size, channels = pygame.mixer.get_init()
            if size != -16:
                return
            for name, notes in SOUNDS.items():
                self.sounds[name] = pygame.mixer.Sound(buffer=_synth(notes, channels, freq).tobytes())
        except (pygame.error, TypeError):
            self.sounds = {}

    def play(self, name):
        s = self.sounds.get(name)
        if s:
            s.play()
