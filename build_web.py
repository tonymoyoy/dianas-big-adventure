"""Build the web-browser version of the game with pygbag.

    .venv/bin/pip install pygbag
    .venv/bin/python build_web.py            # build into build/web
    .venv/bin/python build_web.py --serve    # build, then play at http://127.0.0.1:8000

pygbag packs everything in the folder it is given, so the game is first copied
into a clean folder (only main.py and game/) to keep .venv, tests and save.json out.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "build" / "stage" / "dianas-big-adventure"
OUT = ROOT / "build" / "web"


def make_icon(path):
    """A 64x64 pink heart for the browser tab / home-screen icon."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.display.init()
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    for color, grow in (((45, 35, 60), 3), ((255, 110, 170), 0)):
        r = 15 + grow
        pygame.draw.circle(surf, color, (21, 24), r)
        pygame.draw.circle(surf, color, (43, 24), r)
        pygame.draw.polygon(surf, color, [(5 - grow, 30), (59 + grow, 30), (32, 58 + grow)])
    pygame.draw.circle(surf, (255, 255, 255), (16, 19), 4)
    pygame.image.save(surf, str(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true", help="after building, serve build/web on localhost:8000")
    args = parser.parse_args()

    shutil.rmtree(STAGE.parent, ignore_errors=True)
    STAGE.mkdir(parents=True)
    shutil.copy2(ROOT / "main.py", STAGE / "main.py")
    shutil.copytree(ROOT / "game", STAGE / "game", ignore=shutil.ignore_patterns("__pycache__"))
    make_icon(STAGE / "favicon.png")

    subprocess.run([sys.executable, "-m", "pygbag", "--build", "--no_opt",
                    "--title", "Diana's Big Adventure", str(STAGE)], check=True)

    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STAGE / "build" / "web", OUT)
    print(f"\nWeb build ready in {OUT.relative_to(ROOT)}/")

    if args.serve:
        # Not "localhost": pygbag treats http://localhost:8... as its own dev server and
        # would look for packages (numpy) there instead of on its CDN.
        print("Play at http://127.0.0.1:8000  (Ctrl+C to stop)")
        subprocess.run([sys.executable, "-m", "http.server", "8000", "--directory", str(OUT)])


if __name__ == "__main__":
    main()
