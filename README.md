# Diana's Big Adventure

A gentle side-scrolling platformer made for a toddler named Diana. She runs and jumps through ten themed worlds in her favourite dress, with her border collie trotting behind her, collecting treasures on the way to the pink heart flag.

**Play it in your browser (works on phones too):** https://tonymoyoy.github.io/dianas-big-adventure/

There are no enemies, no lives and no timer. Falling into a hole just bounces her back out on a trampoline. Everything is drawn and every sound and song is synthesized in code, so there are no image or audio files.

## Getting started

Requires Python 3.11+ (developed and tested on 3.12).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

On Windows, use `.venv\Scripts\python` in place of `.venv/bin/python`.

The game uses [pygame-ce](https://pyga.me) (the community edition of pygame) for its smooth, anti-aliased circles. pygame-ce and regular pygame can't be installed side by side, so if you have an older environment, run `pip uninstall pygame` before installing the requirements.

| Option | What it does |
|---|---|
| `main.py --level 7` | Start straight in a world (1-10) |
| `main.py --touch` | Show the phone touch buttons; the mouse acts as a finger (for testing) |
| `main.py --smoke` | Headless self-test: an autopilot plays every level |

## Playing in a web browser (phones and tablets too)

The game also runs in a web browser, built with [pygbag](https://pygame-web.github.io). The browser version shows touch buttons as soon as the screen is touched. Turn the phone sideways (landscape).

```bash
.venv/bin/pip install pygbag==0.9.3
.venv/bin/python build_web.py --serve     # then open http://127.0.0.1:8000
```

Use `127.0.0.1`, not `localhost`: pygbag treats `http://localhost:8...` as its own development server and won't find numpy. The first load downloads Python and numpy (about 15 MB), then the browser caches them. Progress is saved in the browser.

**Publishing it online:** the workflow in `.github/workflows/pages.yml` builds the web version and publishes it on GitHub Pages every time `main` is pushed. Turn it on once in the repository's **Settings → Pages → Source: GitHub Actions**. The game is then at `https://<your-user>.github.io/<repo-name>/`. Open it on the phone and use "Add to Home screen" for an app-like icon.

## Controls

| Action | Keyboard | Gamepad | Touch screen |
|---|---|---|---|
| Move | Left / Right or A / D | D-pad or left stick | Hold the ◀ ▶ buttons (bottom left) |
| Jump | Space, Up or W | A / B / X / Y | Tap the big ▲ button (bottom right) |
| Confirm | Space or Enter | A, Start | Tap |
| Pause / back | Esc | Back | ⏸ button (top right), Android back button |
| Music on/off | M | | |
| Fullscreen | F11 | | |

The menus also work with the mouse or by tapping. The touch buttons appear by themselves the first time the screen is touched (and always on Android). You can hold ◀ ▶ and tap jump at the same time.

## How a game goes

1. **Pick a dress:** 10 outfits, from Pink Princess and Snow Queen to Little Mermaid, Rainbow and Starry Night.
2. **Pick a dog:** Azulita (black and white border collie) or Vainilla (light brown border collie).
3. **Choose a world:** finishing a world unlocks the next.
4. **Play:** reach the pink heart flag. Collecting every item is optional.

Choices, unlocked worlds and best scores are saved in `save.json` in the project folder. Delete it to start fresh.

## The worlds

| # | World | Collect |
|---|---|---|
| 1 | Sunny Meadow | flowers |
| 2 | Mermaid Lagoon | pearls |
| 3 | Snowy Hills | snowflakes |
| 4 | Chocolate Land | chocolates |
| 5 | Moon Base (floaty jumps) | stars |
| 6 | Blocky Woods | diamonds |
| 7 | Magic Theme Park | balloons |
| 8 | Playground Park | ice creams |
| 9 | Cloud Kingdom (a bit floaty) | rainbows |
| 10 | Pink Dream House | purses |

## Made to be easy

- Generous jumps with "coyote time" (you can still jump just after running off a ledge) and jump buffering.
- Every hole has a trampoline at the bottom that bounces you back up.
- Checkpoint flags, plus a respawn point that follows wherever you last stood safely.
- Automated tests check every level against the physics: gaps must be clearly jumpable, steps climbable and every item reachable.

## Project layout

```
main.py            entry point and command-line options (async main loop, also used in the browser)
build_web.py       builds the browser version with pygbag into build/web
game/
  app.py           window, main loop, scene switching, smoke test
  scenes.py        title, dress/dog/world pickers, gameplay, results, ending
  levels.py        the ten level maps as ASCII art (legend at the top)
  tiles.py         turns a map into collision data, items, springs, trampolines
  player.py        Diana's movement and collision physics
  characters.py    drawing Diana, her outfits and the dogs
  draw.py          smooth (anti-aliased) circle helper used by all the art
  worlds.py        each world's colours, physics, background and collectible
  music.py         8-bit songs synthesized with numpy
  sound.py         sound effects
  input.py         keyboard/gamepad/touch input and the test autopilot
  touch.py         on-screen touch buttons for phones and tablets
  save.py          progress saving (save.json, or browser localStorage on the web)
tests/             level, physics, music, outfit, dog, drawing and touch tests
```

## Adding or editing a level

Levels are 12 rows of text in `game/levels.py`:

```
#  ground block          =  floating platform (jump up through it)
*  collectible item      ^  bouncy spring
C  checkpoint flag       P  player start
F  finish flag           .  empty air
```

After changing a map, run the tests. They will point out gaps that are too wide, walls that are too tall and items that can't be reached.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python main.py --smoke
```

A new world also needs an entry in `WORLDS` (`game/worlds.py`) and a song in `SONGS` (`game/music.py`) with the same key.
