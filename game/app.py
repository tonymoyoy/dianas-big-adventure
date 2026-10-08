"""Window, main loop and scene switching."""
import asyncio
import sys

import pygame

from .input import AutoPilot, Controls
from .levels import LEVELS
from .music import Music
from .save import SaveData
from .settings import FPS, HEIGHT, TITLE, WIDTH
from .sound import RATE, Sound

# Running in a web browser (built with pygbag)
WEB = sys.platform == "emscripten"

FONT_NAMES = ["comicneue", "comicsansms", "arialroundedmtbold", "ubuntu", "dejavusans"]


class App:
    def __init__(self, persist_save=True, touch=False):
        pygame.mixer.pre_init(RATE, -16, 2, 512)   # must come before pygame.init()
        pygame.init()
        pygame.display.set_caption(TITLE)
        try:
            # In the browser, the web page scales the game to fit instead
            flags = 0 if WEB else pygame.SCALED | pygame.RESIZABLE
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except pygame.error:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.controls = Controls(touch=touch)
        self.save = SaveData(len(LEVELS), persist=persist_save)
        self.sound = Sound()
        self.music = Music()
        self.font_big = pygame.font.SysFont(FONT_NAMES, 64, bold=True)
        self.font_mid = pygame.font.SysFont(FONT_NAMES, 36, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAMES, 24, bold=True)
        self.running = True
        self.scene = None

    @property
    def dog(self):
        """Key of the dog that comes along with Diana (see characters.DOGS)."""
        from .characters import DEFAULT_DOG, DOGS
        return self.save.dog if self.save.dog in DOGS else DEFAULT_DOG

    @property
    def outfit(self):
        """Key of the dress Diana is wearing (see characters.OUTFITS)."""
        from .characters import DEFAULT_OUTFIT, OUTFITS
        return self.save.outfit if self.save.outfit in OUTFITS else DEFAULT_OUTFIT

    def switch(self, scene):
        self.scene = scene
        if scene.music:
            self.music.play(scene.music)

    async def run(self, first_scene):
        self.switch(first_scene)
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 1 / 30)
            self.controls.begin_frame()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11 and not WEB:
                    pygame.display.toggle_fullscreen()
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_m:
                    self.music.toggle()
                self.controls.handle_event(e)
                self.scene.handle_event(e)
            self.controls.update()
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)   # hands the frame to the browser (pygbag); no cost on desktop
        pygame.quit()


def smoke_test(max_seconds=150):
    """Let the autopilot play every level headless. Returns list of (level, finished, items, total)."""
    from .scenes import PlayScene

    app = App(persist_save=False)
    app.save.unlocked = len(LEVELS)
    results = []
    dt = 1 / FPS
    for i in range(len(LEVELS)):
        app.controls = AutoPilot()
        scene = PlayScene(app, i)
        app.switch(scene)
        frames = 0
        while not scene.finished and frames < max_seconds * FPS:
            app.controls.begin_frame()
            app.controls.steer(scene, dt)
            scene.update(dt)
            if frames % 10 == 0:
                scene.draw(app.screen)
            frames += 1
        results.append((i, scene.finished, scene.collected, scene.total, frames / FPS))
    pygame.quit()
    return results
