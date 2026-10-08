import numpy as np
import pytest

from game.levels import LEVELS
from game.music import RATE, SONGS, STEPS_PER_BAR, melody_events, note_freq, render


def test_note_tuning():
    assert note_freq("A4") == pytest.approx(440.0)
    assert note_freq("A5") == pytest.approx(880.0)
    assert note_freq("C4") == pytest.approx(261.63, abs=0.01)
    assert note_freq("F#5") == pytest.approx(739.99, abs=0.01)


def test_every_world_has_a_song():
    for ldef in LEVELS:
        assert ldef.world in SONGS
    assert "title" in SONGS and "victory" in SONGS


@pytest.mark.parametrize("name", list(SONGS))
def test_song_renders_a_clean_loop(name):
    song = SONGS[name]
    _, steps = melody_events(song.melody)
    assert steps == len(song.chords.split()) * STEPS_PER_BAR
    data = render(song)
    expected = steps * (60 / song.bpm / 2) * RATE
    assert abs(len(data) - expected) <= 1
    assert np.all(np.isfinite(data))
    assert np.max(np.abs(data)) == pytest.approx(1.0)
    # loop should start and end quietly so it repeats without a click
    edge = int(RATE * 0.002)
    assert np.max(np.abs(data[-edge:])) < 0.3
