import pygame
import sys

# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()

# ============================================================
# WINDOW
# ============================================================

WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Metrius Eats - Customer 3 Animation")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BACKGROUND = (30, 30, 35)

PANEL_LEFT = (38, 38, 44)
PANEL_RIGHT = (45, 45, 52)

DIVIDER = (100, 100, 110)

TEXT_COLOR = (230, 230, 230)

# ============================================================
# PANEL DIMENSIONS
# ============================================================

HALF_WIDTH = WIDTH // 2

LEFT_PANEL = pygame.Rect(
    0,
    0,
    HALF_WIDTH,
    HEIGHT
)

RIGHT_PANEL = pygame.Rect(
    HALF_WIDTH,
    0,
    HALF_WIDTH,
    HEIGHT
)

# ============================================================
# LOAD BLINKING SPRITES
# ============================================================

still = pygame.image.load(
    "still.png"
).convert_alpha()

intermediate = pygame.image.load(
    "intermediate.png"
).convert_alpha()

closed = pygame.image.load(
    "closed.png"
).convert_alpha()

# ============================================================
# LOAD WALKING SPRITES
# ============================================================

walk1 = pygame.image.load(
    "walk_1.png"
).convert_alpha()

walk2 = pygame.image.load(
    "walk_2.png"
).convert_alpha()

# ============================================================
# SPRITE DISPLAY LIMIT
# ============================================================
#
# These are MAXIMUM dimensions.
#
# The images are NOT forced to these dimensions.
# They are proportionally reduced so that they fit
# inside this area without distortion.
#
# ============================================================

MAX_WIDTH = 180
MAX_HEIGHT = 270


def fit_sprite(image, size_multiplier=1.0):
    """
    Resize an image proportionally so that it fits inside
    MAX_WIDTH x MAX_HEIGHT.

    The original aspect ratio is preserved.
    """

    original_width = image.get_width()
    original_height = image.get_height()

    # Calculate scale for width
    width_scale = MAX_WIDTH / original_width

    # Calculate scale for height
    height_scale = MAX_HEIGHT / original_height

    # Use the smaller scale so the complete image fits
    scale = min(
        width_scale,
        height_scale
    )

    # Optional size adjustment
    scale *= size_multiplier

    new_width = int(
        original_width * scale
    )

    new_height = int(
        original_height * scale
    )

    return pygame.transform.smoothscale(
        image,
        (
            new_width,
            new_height
        )
    )


# ============================================================
# SCALE BLINK SPRITES
# ============================================================

still = fit_sprite(still)

intermediate = fit_sprite(intermediate)

closed = fit_sprite(closed)

# ============================================================
# SCALE WALKING SPRITES
# ============================================================

walk1 = fit_sprite(walk1)

walk2 = fit_sprite(walk2)

# ============================================================
# SPRITE LISTS
# ============================================================

# ------------------------------------------------------------
# BLINK LOOP
#
# still
#   ↓
# intermediate
#   ↓
# closed
#   ↓
# intermediate
#   ↓
# still
# ------------------------------------------------------------

BLINK_FRAMES = [
    still,
    intermediate,
    closed,
    intermediate
]

# ------------------------------------------------------------
# WALK LOOP
#
# walk_1
#   ↓
# walk_2
#   ↓
# walk_1
#   ↻
# ------------------------------------------------------------

WALK_FRAMES = [
    walk1,
    walk2
]

# ============================================================
# BLINK TIMING
# ============================================================

BLINK_TIMES = [
    1800,   # STILL
    120,    # INTERMEDIATE
    500,    # CLOSED
    120     # INTERMEDIATE
]

blink_frame = 0

blink_timer = 0

# ============================================================
# WALK TIMING
# ============================================================

# 300 ms per walking frame

WALK_FRAME_TIME = 300

walk_frame = 0

walk_timer = 0

# ============================================================
# FONT
# ============================================================

font = pygame.font.SysFont(
    "Arial",
    22,
    bold=True
)

small_font = pygame.font.SysFont(
    "Arial",
    16
)

# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # ========================================================
    # DELTA TIME
    # ========================================================

    dt = clock.tick(60)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ========================================================
    # BLINK ANIMATION
    # ========================================================

    blink_timer += dt

    if blink_timer >= BLINK_TIMES[blink_frame]:

        blink_timer = 0

        blink_frame += 1

        # Loop back to STILL
        if blink_frame >= len(BLINK_FRAMES):

            blink_frame = 0

    current_blink_sprite = BLINK_FRAMES[
        blink_frame
    ]

    # ========================================================
    # WALK ANIMATION
    # ========================================================

    walk_timer += dt

    if walk_timer >= WALK_FRAME_TIME:

        walk_timer = 0

        walk_frame += 1

        # Loop:
        #
        # walk_1 → walk_2 → walk_1
        #

        if walk_frame >= len(WALK_FRAMES):

            walk_frame = 0

    current_walk_sprite = WALK_FRAMES[
        walk_frame
    ]

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.fill(
        BACKGROUND
    )

    # ========================================================
    # LEFT PANEL
    # ========================================================

    pygame.draw.rect(
        screen,
        PANEL_LEFT,
        LEFT_PANEL
    )

    # ========================================================
    # RIGHT PANEL
    # ========================================================

    pygame.draw.rect(
        screen,
        PANEL_RIGHT,
        RIGHT_PANEL
    )

    # ========================================================
    # DIVIDER
    # ========================================================

    pygame.draw.line(
        screen,
        DIVIDER,
        (
            HALF_WIDTH,
            0
        ),
        (
            HALF_WIDTH,
            HEIGHT
        ),
        3
    )

    # ========================================================
    # TITLES
    # ========================================================

    left_title = font.render(
        "CUSTOMER BLINK",
        True,
        TEXT_COLOR
    )

    right_title = font.render(
        "CUSTOMER WALK",
        True,
        TEXT_COLOR
    )

    # --------------------------------------------------------
    # LEFT TITLE
    # --------------------------------------------------------

    screen.blit(
        left_title,
        (
            HALF_WIDTH // 2
            - left_title.get_width() // 2,
            25
        )
    )

    # --------------------------------------------------------
    # RIGHT TITLE
    # --------------------------------------------------------

    screen.blit(
        right_title,
        (
            HALF_WIDTH
            + HALF_WIDTH // 2
            - right_title.get_width() // 2,
            25
        )
    )

    # ========================================================
    # DRAW BLINKING CUSTOMER
    # ========================================================

    blink_x = (
        HALF_WIDTH // 2
        - current_blink_sprite.get_width() // 2
    )

    blink_y = (
        HEIGHT // 2
        - current_blink_sprite.get_height() // 2
        + 25
    )

    screen.blit(
        current_blink_sprite,
        (
            blink_x,
            blink_y
        )
    )

    # ========================================================
    # DRAW WALKING CUSTOMER
    # ========================================================

    walk_x = (
        HALF_WIDTH
        + HALF_WIDTH // 2
        - current_walk_sprite.get_width() // 2
    )

    walk_y = (
        HEIGHT // 2
        - current_walk_sprite.get_height() // 2
        + 25
    )

    screen.blit(
        current_walk_sprite,
        (
            walk_x,
            walk_y
        )
    )

    # ========================================================
    # STATUS TEXT
    # ========================================================

    blink_status = small_font.render(
        f"Frame: {blink_frame + 1}/4",
        True,
        TEXT_COLOR
    )

    walk_status = small_font.render(
        f"Frame: {walk_frame + 1}/2",
        True,
        TEXT_COLOR
    )

    # --------------------------------------------------------
    # BLINK STATUS
    # --------------------------------------------------------

    screen.blit(
        blink_status,
        (
            20,
            HEIGHT - 35
        )
    )

    # --------------------------------------------------------
    # WALK STATUS
    # --------------------------------------------------------

    screen.blit(
        walk_status,
        (
            HALF_WIDTH + 20,
            HEIGHT - 35
        )
    )

    # ========================================================
    # UPDATE DISPLAY
    # ========================================================

    pygame.display.flip()

# ============================================================
# EXIT
# ============================================================

pygame.quit()

sys.exit()