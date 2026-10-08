"""Diana's Big Adventure — an easy side-scroller with 5 worlds.

    python main.py            play
    python main.py --level 3  jump straight into level 3 (1-5)
    python main.py --smoke    headless self-test: an autopilot plays every level
"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--level", type=int, help="start directly in this level (1-5)")
    parser.add_argument("--smoke", action="store_true", help="run the headless autopilot test")
    args = parser.parse_args()

    if args.smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        from game.app import smoke_test
        ok = True
        for i, finished, got, total, secs in smoke_test():
            print(f"level {i + 1}: {'finished' if finished else 'NOT FINISHED'} in {secs:.1f}s, items {got}/{total}")
            ok &= finished
        sys.exit(0 if ok else 1)

    from game.app import App
    from game.levels import LEVELS
    from game.scenes import PlayScene, TitleScene

    app = App()
    if args.level:
        first = PlayScene(app, max(1, min(len(LEVELS), args.level)) - 1)
    else:
        first = TitleScene(app)
    app.run(first)


if __name__ == "__main__":
    main()
