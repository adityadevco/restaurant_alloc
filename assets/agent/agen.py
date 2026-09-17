import pygame
import sys

pygame.init()

# --------------------------------------------------
# WINDOW
# --------------------------------------------------
WIDTH, HEIGHT = 500, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Metrius Eats - Agent Animation")

clock = pygame.time.Clock()

# --------------------------------------------------
# LOAD AGENT SPRITES
# --------------------------------------------------
agent_open = pygame.image.load(
    "agent_1.png"
).convert_alpha()

agent_middle = pygame.image.load(
    "agent_3.png"
).convert_alpha()

agent_thinking = pygame.image.load(
    "agent_2.png"
).convert_alpha()

# --------------------------------------------------
# SPRITE SIZE
# --------------------------------------------------
SPRITE_SIZE = (180, 270)

agent_open = pygame.transform.scale(
    agent_open,
    SPRITE_SIZE
)

agent_middle = pygame.transform.scale(
    agent_middle,
    SPRITE_SIZE
)

agent_thinking = pygame.transform.scale(
    agent_thinking,
    SPRITE_SIZE
)

# --------------------------------------------------
# POSITION
# --------------------------------------------------
x = WIDTH // 2 - SPRITE_SIZE[0] // 2
y = HEIGHT // 2 - SPRITE_SIZE[1] // 2

# --------------------------------------------------
# ANIMATION STATES
# --------------------------------------------------
state = "OPEN"

timer = 0

# How long each frame stays on screen
OPEN_TIME = 900          # Agent 1
MIDDLE_TIME = 180        # Agent 3
THINKING_TIME = 500      # Agent 2

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------
running = True

while running:

    dt = clock.tick(60)
    timer += dt

    # ----------------------------------------------
    # EVENTS
    # ----------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ----------------------------------------------
    # STATE MACHINE
    # ----------------------------------------------

    # ==============================================
    # AGENT 1
    # Eyes open / normal position
    # ==============================================
    if state == "OPEN":

        sprite = agent_open

        if timer >= OPEN_TIME:

            state = "MIDDLE"
            timer = 0

    # ==============================================
    # AGENT 3
    # Intermediate transition
    # ==============================================
    elif state == "MIDDLE":

        sprite = agent_middle

        if timer >= MIDDLE_TIME:

            state = "THINKING"
            timer = 0

    # ==============================================
    # AGENT 2
    # Eyes closed / head down
    # ==============================================
    elif state == "THINKING":

        sprite = agent_thinking

        if timer >= THINKING_TIME:

            state = "MIDDLE_RETURN"
            timer = 0

    # ==============================================
    # AGENT 3 AGAIN
    # Transition back upward
    # ==============================================
    elif state == "MIDDLE_RETURN":

        sprite = agent_middle

        if timer >= MIDDLE_TIME:

            state = "OPEN"
            timer = 0

    # ----------------------------------------------
    # DRAW
    # ----------------------------------------------

    screen.fill((30, 35, 45))

    screen.blit(
        sprite,
        (x, y)
    )

    pygame.display.flip()

# --------------------------------------------------
# QUIT
# --------------------------------------------------
pygame.quit()
sys.exit()