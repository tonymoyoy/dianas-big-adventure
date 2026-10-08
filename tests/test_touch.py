"""Touch controls: simulated fingers drive Diana through the real scenes (headless)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from game.app import App  # noqa: E402
from game.scenes import LevelSelectScene, PlayScene  # noqa: E402
from game.settings import HEIGHT, WIDTH  # noqa: E402
from game.touch import JUMP_CENTER, LEFT_CENTER, PAUSE_CENTER, RIGHT_CENTER  # noqa: E402


@pytest.fixture
def app():
    return App(persist_save=False)


def finger(kind, pos, fid=0):
    """A finger event at a point given in game coordinates."""
    return pygame.event.Event(kind, touch_id=1, finger_id=fid, x=pos[0] / WIDTH, y=pos[1] / HEIGHT,
                              dx=0.0, dy=0.0, pressure=1.0)


def frame(app, scene, *events, n=1):
    """Run n game frames the way App.run does; events arrive on the first."""
    for i in range(n):
        app.controls.begin_frame()
        for e in events if i == 0 else ():
            app.controls.handle_event(e)
            scene.handle_event(e)
        app.controls.update()
        scene.update(1 / 60)


def settled_play_scene(app):
    scene = PlayScene(app, 0)
    frame(app, scene, n=30)   # land on the ground
    return scene


def test_touch_mode_turns_on_at_first_touch(app):
    scene = settled_play_scene(app)
    assert not app.controls.touch_mode
    frame(app, scene, finger(pygame.FINGERDOWN, (WIDTH / 2, HEIGHT / 2)))
    assert app.controls.touch_mode


def test_hold_right_moves_and_lifting_stops(app):
    scene = settled_play_scene(app)
    x0 = scene.player.x
    frame(app, scene, finger(pygame.FINGERDOWN, RIGHT_CENTER), n=30)
    assert scene.player.x > x0 + 50
    frame(app, scene, finger(pygame.FINGERUP, RIGHT_CENTER), n=30)
    assert app.controls.move_x == 0 and scene.player.vx == 0


def test_hold_left_moves_left(app):
    scene = settled_play_scene(app)
    frame(app, scene, finger(pygame.FINGERDOWN, RIGHT_CENTER), n=40)
    frame(app, scene, finger(pygame.FINGERUP, RIGHT_CENTER))
    x0 = scene.player.x
    frame(app, scene, finger(pygame.FINGERDOWN, LEFT_CENTER), n=20)
    assert scene.player.x < x0 - 30


def test_tap_jump_jumps(app):
    scene = settled_play_scene(app)
    assert scene.player.on_ground
    frame(app, scene, finger(pygame.FINGERDOWN, JUMP_CENTER))
    assert scene.player.vy < 0


def test_run_and_jump_with_two_fingers(app):
    scene = settled_play_scene(app)
    frame(app, scene, finger(pygame.FINGERDOWN, RIGHT_CENTER, fid=0), n=10)
    frame(app, scene, finger(pygame.FINGERDOWN, JUMP_CENTER, fid=1))
    assert scene.player.vy < 0 and scene.player.vx > 0


def test_sliding_finger_from_right_to_left(app):
    scene = settled_play_scene(app)
    frame(app, scene, finger(pygame.FINGERDOWN, RIGHT_CENTER))
    assert app.controls.move_x == 1
    frame(app, scene, finger(pygame.FINGERMOTION, LEFT_CENTER))
    assert app.controls.move_x == -1


def test_pause_button_and_tap_to_resume(app):
    scene = settled_play_scene(app)
    frame(app, scene, finger(pygame.FINGERDOWN, PAUSE_CENTER))
    assert scene.state == "paused"
    tap = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=scene.PAUSE_BUTTONS["resume"].center, button=1, touch=True)
    frame(app, scene, tap)
    assert scene.state == "play"


def test_android_back_button_pauses(app):
    scene = settled_play_scene(app)
    frame(app, scene, pygame.event.Event(pygame.KEYDOWN, key=pygame.K_AC_BACK, mod=0, unicode="", scancode=0))
    assert scene.state == "paused"


def test_mouse_only_acts_as_finger_when_asked():
    plain = App(persist_save=False)
    scene = settled_play_scene(plain)
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=JUMP_CENTER, button=1)
    frame(plain, scene, click)
    assert scene.player.on_ground

    forced = App(persist_save=False, touch=True)
    scene = settled_play_scene(forced)
    frame(forced, scene, click)
    assert scene.player.vy < 0


def test_touch_buttons_do_nothing_in_menus(app):
    scene = LevelSelectScene(app, 0)
    frame(app, scene, finger(pygame.FINGERDOWN, JUMP_CENTER))
    assert not isinstance(app.scene, PlayScene)
    assert not app.controls.jump_pressed
