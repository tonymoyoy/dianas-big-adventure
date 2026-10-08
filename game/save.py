"""Progress saving: which levels are unlocked, the most items found per level, and the chosen dog and outfit.

On a computer it is save.json in the project folder. In a web browser (pygbag) files
vanish on reload, so it is kept in the browser's localStorage instead.
"""
import json
import sys
from pathlib import Path

SAVE_PATH = Path(__file__).resolve().parent.parent / "save.json"
WEB_KEY = "dianas-big-adventure-save"


def _local_storage():
    """The browser's localStorage when running under pygbag, else None."""
    if sys.platform != "emscripten":
        return None
    return __import__("platform").window.localStorage


class SaveData:
    def __init__(self, num_levels, path=SAVE_PATH, persist=True):
        self.num_levels = num_levels
        self.path = path
        self.persist = persist
        self.unlocked = 1
        self.best = {}
        self.dog = None        # chosen dog key, see characters.DOGS
        self.outfit = None     # chosen outfit key, see characters.OUTFITS
        if persist:
            self._load()

    def _read(self):
        storage = _local_storage()
        if storage is not None:
            return storage.getItem(WEB_KEY) or ""
        return self.path.read_text()

    def _write(self, text):
        storage = _local_storage()
        if storage is not None:
            storage.setItem(WEB_KEY, text)
        else:
            self.path.write_text(text)

    def _load(self):
        try:
            data = json.loads(self._read())
            self.unlocked = max(1, min(self.num_levels, int(data.get("unlocked", 1))))
            self.best = {int(k): int(v) for k, v in data.get("best", {}).items()}
            if self.best:   # levels added later unlock for anyone who already beat the one before
                self.unlocked = max(self.unlocked, min(self.num_levels, max(self.best) + 2))
            self.dog = data.get("dog") if isinstance(data.get("dog"), str) else None
            self.outfit = data.get("outfit") if isinstance(data.get("outfit"), str) else None
        except Exception:   # missing or damaged save: start fresh
            pass

    def record(self, level_index, items):
        self.best[level_index] = max(items, self.best.get(level_index, 0))
        self.unlocked = max(self.unlocked, min(self.num_levels, level_index + 2))
        self.save()

    def save(self):
        if not self.persist:
            return
        try:
            self._write(json.dumps({"unlocked": self.unlocked, "best": self.best, "dog": self.dog, "outfit": self.outfit}, indent=2))
        except Exception:   # never let a failed save interrupt play
            pass
