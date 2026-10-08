# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Diana's Big Adventure": a pygame side-scroller made for a young girl named Diana (she likes dresses, princesses, mermaids, little dogs and chocolate). The player is Diana in a pink dress and crown, with a puppy following her. 5 levels, one per themed world (meadow, mermaid lagoon, snowy hills with a castle, chocolate land, moon). No enemies, no lives, no timer: reach the pink heart finish flag and collect items along the way. **Keeping it easy is a hard requirement.** Any change to physics or level layout must keep it forgiving.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # setup
.venv/bin/python main.py              # play (F11 fullscreen, Esc pause/back, M music)
.venv/bin/python main.py --level 4    # jump straight into a level (1-5)
.venv/bin/python main.py --smoke      # headless: autopilot plays all levels, exit 1 if any unfinished
.venv/bin/python -m pytest -q         # all tests
.venv/bin/python -m pytest tests/test_levels.py -k chocolate   # one level's static checks
```

Tests and `--smoke` run headless via `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` (set automatically). The "no fast renderer available" warning under the dummy driver is harmless.

## Architecture

- `main.py` → `game/app.py` `App`: owns the window (960x540, `SCALED`), `Controls`, `SaveData`, `Sound`, fonts and the current scene. The loop runs `controls.begin_frame()` → events → `controls.update()` → `scene.update(dt)` → `scene.draw(screen)`. Scenes switch with `app.switch(NewScene(app, ...))`.
- `game/scenes.py`: Title → DogSelect → LevelSelect → Play → LevelComplete → (after level 5) End. Scenes only read the abstract input signals on `app.controls` (`move_x`, `jump_pressed`, `confirm`, `back`, `nav_x`), never raw keys. That's why `input.AutoPilot` can stand in for `Controls` in `app.smoke_test()`.
- `PlayScene` states: `play | respawn | finish | paused`. A fall respawns at `respawn_point`, which tracks the **last spot stood on with both feet on solid ground** (checkpoints also set it). So a fall costs only a few seconds.
- `game/levels.py`: levels are 12-row ASCII maps (legend in the module docstring). `game/tiles.py` `Level` parses them into grid dicts (`solids`, `platforms` keyed by `(col,row)`) plus `Item`/`Spring`/`Checkpoint` objects. `=` platforms are one-way (jump up through them). Springs are trigger zones that bounce on any downward/resting contact, including walking into them. `Level` also auto-places a `PitPad` trampoline under every run of columns with no ground in the bottom row, so falling into a pit bounces Diana back out at `spring_speed` (no map character needed). The fall-respawn remains only as a safety net.
- `game/player.py`: physics with coyote time + jump buffer, X-then-Y collision against the grid. Ground detection uses a 1px probe below the feet. Character drawing lives in `game/characters.py` (`draw_diana`, `draw_puppy`, and `PuppyFollower`, which replays Diana's recent path). The dog is one of two border collies in `DOGS`: Azulita (black with white markings) or Vainilla (all white), picked in `DogSelectScene` and read everywhere via `app.dog` and is reused by the menus.
- `game/worlds.py`: each `World` bundles palette, physics overrides (`gravity`, `jump_speed`, `spring_speed`; the moon is floatier), a background function, and an item drawing function. Everything is drawn with pygame primitives; there are no asset files. Surfaces are built lazily by `World.build()`, which needs the display initialised.
- Audio: `App` calls `pygame.mixer.pre_init()` **before** `pygame.init()` (otherwise the mixer starts at 44.1kHz and must be matched). `game/sound.py` synthesizes short effects; `game/music.py` renders 8-bit loops with numpy from a compact notation (tempo, one chord per bar, 8 eighth-note tokens per bar: note / `-` hold / `.` rest; bass, arpeggios and drums are generated from the chords). Each scene names its song in a `music` attribute and `App.switch()` starts it on a reserved mixer channel; `M` toggles music. `tests/test_music.py` checks every song renders as a clean loop.
- `game/save.py`: `save.json` in the project root (gitignored): `unlocked` count, best items per level, and the chosen `dog`.

## Level design constraints (enforced by tests)

`tests/test_levels.py` derives limits from each world's physics. Gaps must be within ~65% of jump reach, ground steps no taller than jump height (unless a spring `^` is within 6 columns before), and every `*` near a standable cell. `tests/test_player.py::test_autopilot_finishes_every_level` actually plays each level. A common failure: a gap placed right where a jump off a high platform lands. After editing a map, run both test files.
