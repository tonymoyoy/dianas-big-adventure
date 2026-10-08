"""8-bit background music, synthesized with numpy (square/triangle waves + noise drums).

A song is a tempo, one chord per bar and a melody written in eighth notes:
    "E5"  start a note      "-"  hold the previous note      "."  rest
Bass, optional arpeggios and drums are generated from the chords, so writing a
new song only needs a melody (8 tokens per bar) and its chords.
Music plays on a reserved mixer channel so it never steals a sound effect's channel.
"""
from dataclasses import dataclass

import numpy as np
import pygame

RATE = 22050
MUSIC_VOLUME = 0.32
STEPS_PER_BAR = 8
NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
CHORD_TONES = {"": (0, 4, 7), "m": (0, 3, 7)}


@dataclass(frozen=True)
class Song:
    bpm: int
    chords: str            # one chord per bar, e.g. "C G Am F"
    melody: str            # 8 tokens per bar
    lead: str = "square"   # square | triangle
    duty: float = 0.25
    arp: bool = False      # quiet arpeggio voice from the chords
    drums: bool = True


SONGS = {
    "title": Song(130, "C F G C C F G C",
                  "C5 - E5 - G5 - C6 - | A5 - - - F5 - A5 - | G5 - - - D5 - G5 - | E5 - - - - - . . | "
                  "C6 - B5 - A5 - G5 - | F5 - A5 - C6 - A5 - | G5 - B5 - D6 - B5 - | C6 - - - - - . ."),
    "victory": Song(165, "C F G C C F G C",
                    "C5 E5 G5 C6 G5 E5 G5 C6 | A5 - C6 - F5 - A5 - | G5 - B5 - D6 - B5 - | C6 - G5 - E5 - C5 - | "
                    "E5 G5 C6 E6 D6 C6 B5 A5 | F5 - A5 - C6 - F6 - | D6 - B5 - G5 - B5 - | C6 - - - . . C6 .",
                    duty=0.5),
    "meadow": Song(140, "C G Am F C G F C",
                   "E5 - G5 - C6 - G5 - | D5 - G5 - B5 - G5 - | C5 - E5 - A5 - G5 E5 | F5 - A5 - C6 - A5 - | "
                   "G5 E5 G5 C6 B5 - G5 - | A5 G5 F5 E5 D5 - G4 - | A4 C5 F5 A5 G5 F5 E5 D5 | C5 - - - . . . ."),
    "lagoon": Song(110, "F Dm A# C F Am A# C",
                   "A5 - - C6 A5 - F5 - | D5 - F5 - A5 - - - | A#5 - A5 - G5 - F5 - | G5 - - - E5 - C5 - | "
                   "F5 - A5 - C6 - A5 - | E5 - A5 - C6 - B5 A5 | D6 - C6 - A#5 - A5 - | G5 - - - - - . .",
                   lead="triangle", arp=True, drums=False),
    "snow": Song(120, "G Em C D G Em C D",
                 "B5 - D6 - B5 - G5 - | E5 - G5 - B5 - - - | C6 - B5 - A5 - G5 - | F#5 - A5 - D6 - - - | "
                 "D6 C6 B5 A5 G5 - B5 - | E6 - D6 - B5 - G5 - | A5 - C6 - B5 - A5 - | F#5 - - - D5 - - -",
                 duty=0.125, arp=True),
    "chocolate": Song(150, "D Bm G A D Bm G A",
                      "F#5 . A5 . D6 . A5 F#5 | D5 . F#5 . B5 . F#5 D5 | G5 . B5 . D6 . B5 G5 | A5 - C#6 - E6 - - - | "
                      "F#6 E6 D6 . A5 . F#5 . | B5 A5 F#5 . D5 . F#5 . | G5 A5 B5 . G5 . E5 . | C#5 - E5 - A5 - . .",
                      duty=0.5),
    "moon": Song(100, "Am F C G Am F G Am",
                 "E5 - - - A5 - - - | C6 - - - A5 - - - | G5 - E5 - G5 - C6 - | B5 - - - - - . . | "
                 "A5 - B5 - C6 - E6 - | D6 - C6 - A5 - - - | B5 - G5 - D6 - B5 - | A5 - - - - - . .",
                 lead="triangle", arp=True, drums=False),
    "woods": Song(125, "Am F C G Am F G E",
                  "A4 - C5 - E5 - A5 - | F5 - E5 - C5 - A4 - | G4 - C5 - E5 - G5 - | D5 - - - B4 - - - | "
                  "A4 - C5 E5 A5 - G5 - | F5 - A5 - C6 - A5 - | G5 - F5 - D5 - B4 - | E5 - - - - - . .",
                  duty=0.125, arp=True),
    "themepark": Song(160, "C Am F G C Am F G",
                      "C5 E5 G5 E5 C6 - G5 - | A5 - E5 - C5 - E5 - | F5 A5 C6 A5 F5 - A5 - | G5 - B5 - D6 - - - | "
                      "E6 D6 C6 - G5 - E5 - | A5 G5 E5 - C5 - A4 - | F5 - A5 - C6 - A5 - | G5 - - - - - . .",
                      duty=0.5),
    "playground": Song(145, "G C D G G C D G",
                       "G5 - B5 - D6 - B5 - | C6 - E6 - C6 - G5 - | A5 - F#5 - D5 - F#5 - | G5 - - - . . D5 - | "
                       "G5 A5 B5 - G5 - B5 - | E5 G5 C6 - E6 - C6 - | D6 C6 A5 - F#5 - A5 - | G5 - - - - - . ."),
    "sky": Song(105, "F C Dm A# F C A# C",
                "C6 - - - A5 - F5 - | G5 - - - E5 - C5 - | D5 - F5 - A5 - D6 - | C6 - A#5 - A5 - G5 - | "
                "A5 - C6 - F6 - - - | E6 - D6 - C6 - G5 - | A#5 - A5 - G5 - F5 - | E5 - - - - - . .",
                lead="triangle", arp=True, drums=False),
    "dream": Song(150, "C Em F G C Am Dm G",
                  "E5 G5 C6 . G5 . E5 G5 | B5 - G5 - E5 - . . | A5 C6 F6 . C6 . A5 C6 | B5 - D6 - G5 - . . | "
                  "C6 - E6 - G6 - E6 - | C6 - A5 - E5 - A5 - | D6 F6 A5 - D6 - F6 - | G5 - - - - - . .",
                  duty=0.5, arp=True),
}


def note_freq(name):
    """'A4' -> 440.0, 'F#5', 'A#5' ..."""
    letter, rest = name[0], name[1:]
    semi = NOTE_INDEX[letter]
    if rest[0] == "#":
        semi += 1
        rest = rest[1:]
    midi = 12 * (int(rest) + 1) + semi
    return 440.0 * 2 ** ((midi - 69) / 12)


def parse_chord(chord):
    """'F#m' -> (root semitone 0-11, tones)."""
    root = NOTE_INDEX[chord[0]]
    quality = chord[1:]
    if quality.startswith("#"):
        root += 1
        quality = quality[1:]
    return root % 12, CHORD_TONES[quality]


def melody_events(melody):
    """Tokens -> list of (start_step, length_steps, freq)."""
    tokens = melody.replace("|", " ").split()
    events = []
    for i, tok in enumerate(tokens):
        if tok == "-":
            if events and events[-1][0] + events[-1][1] == i:
                start, length, f = events[-1]
                events[-1] = (start, length + 1, f)
        elif tok != ".":
            events.append((i, 1, note_freq(tok)))
    return events, len(tokens)


def _wave(kind, freq, n, duty=0.25):
    phase = (np.arange(n) * freq / RATE) % 1.0
    if kind == "square":
        return np.where(phase < duty, 1.0, -1.0)
    if kind == "triangle":
        return 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
    raise ValueError(kind)


def _envelope(n, staccato=False):
    env = np.ones(n)
    a = min(n, int(RATE * 0.004))
    env[:a] = np.linspace(0, 1, a)
    d = min(n - a, int(RATE * 0.08))
    env[a:a + d] = np.linspace(1, 0.6, d)
    env[a + d:] = 0.6
    r = min(n, int(RATE * (0.04 if staccato else 0.02)))
    env[n - r:] *= np.linspace(1, 0, r)
    return env


def render(song):
    """Render one seamless loop of a song to float samples in [-1, 1]."""
    step = 60.0 / song.bpm / 2
    events, total_steps = melody_events(song.melody)
    chords = song.chords.split()
    assert total_steps == len(chords) * STEPS_PER_BAR, "melody needs 8 tokens per chord"
    n_total = int(round(total_steps * step * RATE))
    out = np.zeros(n_total)

    def add(start_step, length_steps, freq, kind, vol, duty=0.25, gap=0.9):
        s = int(start_step * step * RATE)
        n = max(1, int(length_steps * step * RATE * gap))
        n = min(n, n_total - s)
        out[s:s + n] += _wave(kind, freq, n, duty) * _envelope(n) * vol

    for start, length, f in events:
        add(start, length, f, song.lead, 0.30 if song.lead == "square" else 0.45, song.duty)

    for bar, chord in enumerate(chords):
        root, tones = parse_chord(chord)
        base = bar * STEPS_PER_BAR
        bass_root = 440.0 * 2 ** ((root + 36 - 69 + 12) / 12)   # octave 2-3
        # Bass: root, root, fifth, octave (quarter notes)
        for k, mult in enumerate((1, 1, 1.5, 2)):
            add(base + k * 2, 2, bass_root * mult, "triangle", 0.5, gap=0.85)
        if song.arp:
            for k in range(STEPS_PER_BAR):
                tone = tones[k % 3] + (12 if k >= 4 else 0)
                f = 440.0 * 2 ** ((root + tone + 60 - 69) / 12)
                add(base + k, 1, f, "square", 0.07, duty=0.5, gap=0.6)

    if song.drums:
        rng = np.random.default_rng(7)
        for s_i in range(total_steps):
            pos = s_i % STEPS_PER_BAR
            s = int(s_i * step * RATE)
            if pos in (0, 4):     # kick: quick downward pitch sweep
                n = min(int(RATE * 0.09), n_total - s)
                f = np.linspace(150, 45, n)
                out[s:s + n] += np.sin(np.cumsum(2 * np.pi * f / RATE)) * np.linspace(1, 0, n) * 0.55
            elif pos in (2, 6):   # snare: noise burst
                n = min(int(RATE * 0.07), n_total - s)
                out[s:s + n] += rng.uniform(-1, 1, n) * np.linspace(1, 0, n) ** 2 * 0.22
            else:                 # hi-hat: tiny tick
                n = min(int(RATE * 0.02), n_total - s)
                out[s:s + n] += rng.uniform(-1, 1, n) * np.linspace(1, 0, n) * 0.06

    peak = np.max(np.abs(out)) or 1.0
    return out / peak


class Music:
    """Loops one song at a time on a reserved channel, fading each new song in; M toggles."""

    def __init__(self):
        self.enabled = True
        self.current = None
        self.cache = {}
        self.channel = None
        try:
            if pygame.mixer.get_init():
                pygame.mixer.set_reserved(1)
                self.channel = pygame.mixer.Channel(0)
        except pygame.error:
            self.channel = None

    def _sound(self, name):
        if name not in self.cache:
            freq, size, channels = pygame.mixer.get_init()
            data = render(SONGS[name])
            if freq != RATE:
                idx = np.linspace(0, len(data) - 1, int(len(data) * freq / RATE))
                data = np.interp(idx, np.arange(len(data)), data)
            pcm = (data * MUSIC_VOLUME * 32767).astype(np.int16)
            if channels > 1:
                pcm = np.repeat(pcm[:, None], channels, axis=1)
            self.cache[name] = pygame.mixer.Sound(buffer=pcm.tobytes())
        return self.cache[name]

    def play(self, name):
        if self.channel is None or name == self.current:
            return
        self.current = name
        if not self.enabled:
            return
        try:
            self.channel.play(self._sound(name), loops=-1, fade_ms=400)
        except pygame.error:
            pass

    def toggle(self):
        self.enabled = not self.enabled
        if self.channel is None:
            return
        if self.enabled and self.current:
            self.channel.play(self._sound(self.current), loops=-1, fade_ms=400)
        else:
            self.channel.stop()
