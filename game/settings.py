"""Global constants: screen, tiles, physics, colors."""

TITLE = "Diana's Big Adventure"
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

# Player
PLAYER_W, PLAYER_H = 34, 44
RUN_SPEED = 300          # px/s
GROUND_ACCEL = 2400      # px/s^2
AIR_ACCEL = 1800
FRICTION = 2600
MAX_FALL = 1100
COYOTE_TIME = 0.12       # can still jump this long after walking off a ledge
JUMP_BUFFER = 0.15       # jump pressed slightly before landing still counts

# Defaults; worlds may override gravity / jump / spring speed
GRAVITY = 2000
JUMP_SPEED = 900
SPRING_SPEED = 1350

# Falling this far below the level bottom triggers a respawn
FALL_LIMIT = 80

WHITE = (255, 255, 255)
OUTLINE = (45, 35, 60)
GOLD = (255, 205, 60)
