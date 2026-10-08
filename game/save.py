"""Progress saving: which levels are unlocked, the most items found per level, and the chosen dog and outfit."""
import json
from pathlib import Path

SAVE_PATH = Path(__file__).resolve().parent.parent / "save.json"


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

    def _load(self):
        try:
            data = json.loads(self.path.read_text())
            self.unlocked = max(1, min(self.num_levels, int(data.get("unlocked", 1))))
            self.best = {int(k): int(v) for k, v in data.get("best", {}).items()}
            if self.best:   # levels added later unlock for anyone who already beat the one before
                self.unlocked = max(self.unlocked, min(self.num_levels, max(self.best) + 2))
            self.dog = data.get("dog") if isinstance(data.get("dog"), str) else None
            self.outfit = data.get("outfit") if isinstance(data.get("outfit"), str) else None
        except (OSError, ValueError, TypeError, AttributeError):
            pass

    def record(self, level_index, items):
        self.best[level_index] = max(items, self.best.get(level_index, 0))
        self.unlocked = max(self.unlocked, min(self.num_levels, level_index + 2))
        self.save()

    def save(self):
        if not self.persist:
            return
        try:
            self.path.write_text(json.dumps({"unlocked": self.unlocked, "best": self.best, "dog": self.dog, "outfit": self.outfit}, indent=2))
        except OSError:
            pass
