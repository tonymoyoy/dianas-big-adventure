# Diana's Big Adventure

A gentle side-scrolling platformer made for a toddler named Diana. She runs and jumps through ten themed worlds in her favourite dress, with her border collie trotting behind her, collecting treasures on the way to the pink heart flag.

There are no enemies, no lives and no timer. Falling into a hole just bounces her back out on a trampoline. Everything is drawn and every sound and song is synthesized in code, so there are no image or audio files.

## Getting started

Requires Python 3.11+ (developed and tested on 3.12).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

On Windows, use `.venv\Scripts\python` in place of `.venv/bin/python`.

| Option | What it does |
|---|---|
| `main.py --level 7` | Start straight in a world (1-10) |
| `main.py --smoke` | Headless self-test: an autopilot plays every level |

## Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | Left / Right or A / D | D-pad or left stick |
| Jump | Space, Up or W | A / B / X / Y |
| Confirm | Space or Enter | A, Start |
| Pause / back | Esc | Back |
| Music on/off | M | |
| Fullscreen | F11 | |

The menus also work with the mouse.

## How a game goes

1. **Pick a dress:** 10 outfits, from Pink Princess and Snow Queen to Little Mermaid, Rainbow and Starry Night.
2. **Pick a dog:** Azulita (black and white border collie) or Vainilla (all-white border collie).
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
main.py            entry point and command-line options
game/
  app.py           window, main loop, scene switching, smoke test
  scenes.py        title, dress/dog/world pickers, gameplay, results, ending
  levels.py        the ten level maps as ASCII art (legend at the top)
  tiles.py         turns a map into collision data, items, springs, trampolines
  player.py        Diana's movement and collision physics
  characters.py    drawing Diana, her outfits and the dogs
  worlds.py        each world's colours, physics, background and collectible
  music.py         8-bit songs synthesized with numpy
  sound.py         sound effects
  input.py         keyboard/gamepad input and the test autopilot
  save.py          progress saving
tests/             level, physics, music, outfit and dog tests
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
