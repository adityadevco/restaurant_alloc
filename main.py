import pygame
import sys
import os
import math


from kitchen import Kitchen

from header import Header

from sidebar import Sidebar

from customer_queue import CustomerQueue

from input import WaitingPeopleInput

from tables import TableManager

from agent import (
    RestaurantAgent,
    ALGORITHM_DEFAULT,
    ALGORITHM_EXPECTED_SARSA,
    ALGORITHM_ACTOR_CRITIC,
    ALGORITHM_DQN,
    ALGORITHM_N_STEP_TREE_BACKUP
)

import messages

from result_tracker import ResultTracker


pygame.init()

# ============================================================
# WINDOW CONFIGURATION
# ============================================================

# Original project design resolution.
# All existing UI components continue using these coordinates.
DESIGN_WIDTH = 1450
DESIGN_HEIGHT = 875

GAME_WIDTH = 1200
SIDEBAR_WIDTH = 250

HEADER_HEIGHT = 125
GAME_HEIGHT = 750

WIDTH = DESIGN_WIDTH
HEIGHT = DESIGN_HEIGHT


# ============================================================
# DISPLAY / SCREEN SCALING
# ============================================================

# Get the actual monitor resolution.
display_info = pygame.display.Info()

SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h


# Leave some space for the Windows title bar / taskbar.
MAX_WIDTH = SCREEN_WIDTH - 40
MAX_HEIGHT = SCREEN_HEIGHT - 100


# Calculate proportional scale.
scale_x = MAX_WIDTH / DESIGN_WIDTH
scale_y = MAX_HEIGHT / DESIGN_HEIGHT

DISPLAY_SCALE = min(
    scale_x,
    scale_y,
    1.0
)


WINDOW_WIDTH = int(
    DESIGN_WIDTH * DISPLAY_SCALE
)

WINDOW_HEIGHT = int(
    DESIGN_HEIGHT * DISPLAY_SCALE
)


# ============================================================
# CREATE WINDOW
# ============================================================

screen = pygame.display.set_mode(
    (
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    ),
    pygame.RESIZABLE
)

pygame.display.set_caption(
    "Metrius Eats - Restaurant Simulation"
)


# ============================================================
# INTERNAL DESIGN SURFACE
# ============================================================

# All existing project components continue drawing at
# the original 1450 x 875 resolution.
game_surface = pygame.Surface(
    (
        DESIGN_WIDTH,
        DESIGN_HEIGHT
    )
)


clock = pygame.time.Clock()


pygame.display.set_caption(
    "Metrius Eats - Restaurant Simulation"
)


clock = pygame.time.Clock()


BACKGROUND = (
    20,
    20,
    25
)


# ============================================================
# ASSET PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


ENVIRONMENT_DIR = os.path.join(
    ASSETS_DIR,
    "environment"
)


TABLES_DIR = os.path.join(
    ASSETS_DIR,
    "tables"
)


AGENT_DIR = os.path.join(
    ASSETS_DIR,
    "agent"
)


CUSTOMERS_DIR = os.path.join(
    ASSETS_DIR,
    "customers"
)


FLOOR_PATH = os.path.join(
    ASSETS_DIR,
    "environment",
    "floor.png"
)


# ============================================================
# LOAD FLOOR
# ============================================================

try:

    floor = pygame.image.load(
        FLOOR_PATH
    ).convert_alpha()


except FileNotFoundError:

    print()
    print(
        "========================================"
    )
    print(
        "ERROR: FLOOR IMAGE NOT FOUND"
    )
    print(
        "========================================"
    )
    print(
        FLOOR_PATH
    )
    print()

    pygame.quit()

    sys.exit()


except pygame.error as e:

    print()
    print(
        "========================================"
    )
    print(
        "ERROR LOADING FLOOR"
    )
    print(
        "========================================"
    )
    print(
        e
    )
    print()

    pygame.quit()

    sys.exit()


print()
print(
    "========================================"
)
print(
    "FLOOR LOADED SUCCESSFULLY"
)
print(
    "========================================"
)

print(
    f"Original floor size: "
    f"{floor.get_width()} x "
    f"{floor.get_height()}"
)

print(
    f"Floor path: {FLOOR_PATH}"
)

print()


# ============================================================
# SCALE FLOOR
# ============================================================

floor_width = floor.get_width()

floor_height = floor.get_height()


scale_x = (
    GAME_WIDTH
    /
    floor_width
)


scale_y = (
    GAME_HEIGHT
    /
    floor_height
)


floor_scale = min(
    scale_x,
    scale_y
)


floor_new_width = int(
    floor_width
    *
    floor_scale
)


floor_new_height = int(
    floor_height
    *
    floor_scale
)


floor = pygame.transform.smoothscale(
    floor,
    (
        floor_new_width,
        floor_new_height
    )
)


floor_x = (
    GAME_WIDTH
    -
    floor_new_width
) // 2


floor_y = (
    HEADER_HEIGHT
    +
    (
        GAME_HEIGHT
        -
        floor_new_height
    ) // 2
)


# ============================================================
# TABLE MANAGER
# ============================================================

table_manager = TableManager(
    ASSETS_DIR
)


print()
print(
    "========================================"
)
print(
    "TABLE MANAGER INITIALIZED"
)
print(
    "========================================"
)

print(
    f"Total tables: "
    f"{len(table_manager.tables)}"
)

print()


for table in table_manager.tables:

    print(
        f"{table.table_id}: "
        f"{table.capacity} seats | FREE"
    )


print()


# ============================================================
# RESTAURANT AGENT
# ============================================================

agent = RestaurantAgent(
    table_manager=table_manager,
    algorithm=ALGORITHM_DEFAULT
)


result_tracker = ResultTracker()

result_tracker.start_algorithm(
    "Default"
)


print()
print(
    "========================================"
)
print(
    "RESTAURANT AGENT"
)
print(
    "========================================"
)

print(
    f"Algorithm: "
    f"{agent.get_algorithm_name()}"
)

print(
    "Post-free cleaning delay: 5 seconds"
)

print()


# ============================================================
# AGENT SPRITES
# ============================================================

AGENT_1_PATH = os.path.join(
    AGENT_DIR,
    "agent_1.png"
)


AGENT_2_PATH = os.path.join(
    AGENT_DIR,
    "agent_2.png"
)


AGENT_3_PATH = os.path.join(
    AGENT_DIR,
    "agent_3.png"
)


try:

    agent_open = pygame.image.load(
        AGENT_1_PATH
    ).convert_alpha()


    agent_thinking = pygame.image.load(
        AGENT_2_PATH
    ).convert_alpha()


    agent_middle = pygame.image.load(
        AGENT_3_PATH
    ).convert_alpha()


except FileNotFoundError as e:

    print()
    print(
        "========================================"
    )
    print(
        "ERROR: AGENT IMAGE NOT FOUND"
    )
    print(
        "========================================"
    )
    print(
        e
    )
    print()

    pygame.quit()

    sys.exit()


except pygame.error as e:

    print()
    print(
        "========================================"
    )
    print(
        "ERROR LOADING AGENT IMAGE"
    )
    print(
        "========================================"
    )
    print(
        e
    )
    print()

    pygame.quit()

    sys.exit()


AGENT_MAX_WIDTH = 110

AGENT_MAX_HEIGHT = 165


def fit_agent(
    image
):

    original_width = (
        image.get_width()
    )

    original_height = (
        image.get_height()
    )


    width_scale = (
        AGENT_MAX_WIDTH
        /
        original_width
    )


    height_scale = (
        AGENT_MAX_HEIGHT
        /
        original_height
    )


    scale = min(
        width_scale,
        height_scale
    )


    new_width = max(
        1,
        int(
            original_width
            *
            scale
        )
    )


    new_height = max(
        1,
        int(
            original_height
            *
            scale
        )
    )


    return pygame.transform.smoothscale(
        image,
        (
            new_width,
            new_height
        )
    )


agent_open = fit_agent(
    agent_open
)


agent_middle = fit_agent(
    agent_middle
)


agent_thinking = fit_agent(
    agent_thinking
)


AGENT_FRAMES = [

    agent_open,

    agent_middle,

    agent_thinking,

    agent_middle

]


AGENT_FRAME_TIMES = [

    1800,

    150,

    500,

    150

]


agent_frame = 0

agent_timer = 0


AGENT_X = 555

AGENT_Y = 350


# ============================================================
# CLEANING ANIMATION
# ============================================================

cleaning_animation_time = 0.0


CLEANING_RING_RADIUS = 52

CLEANING_RING_WIDTH = 4

CLEANING_DOT_COUNT = 8


cleaning_font = pygame.font.SysFont(
    "arial",
    17,
    bold=True
)


cleaning_timer_font = pygame.font.SysFont(
    "arial",
    15,
    bold=True
)


def draw_cleaning_animation():

    for table_index in list(
        agent.free_timers.keys()
    ):

        if (
            table_index < 0
            or
            table_index >= len(
                table_manager.tables
            )
        ):

            continue


        try:

            remaining = agent.get_table_wait_time(
                table_index
            )

        except Exception:

            continue


        if remaining <= 0:

            continue


        table = table_manager.tables[
            table_index
        ]


        try:

            table_x, table_y = (
                table.position
            )

        except (
            AttributeError,
            TypeError,
            ValueError
        ):

            continue


        screen_x = int(
            table_x
        )


        screen_y = int(
            table_y
            +
            HEADER_HEIGHT
        )


        phase = (
            cleaning_animation_time
            *
            0.006
        )


        pulse = (
            math.sin(
                phase
            )
            +
            1
        ) / 2


        radius = int(
            CLEANING_RING_RADIUS
            +
            (
                pulse
                *
                7
            )
        )


        overlay_size = (
            radius * 2
            +
            30
        )


        overlay = pygame.Surface(
            (
                overlay_size,
                overlay_size
            ),
            pygame.SRCALPHA
        )


        overlay_center = (
            overlay_size // 2,
            overlay_size // 2
        )


        glow_alpha = int(
            25
            +
            pulse * 25
        )


        pygame.draw.circle(
            overlay,
            (
                255,
                180,
                40,
                glow_alpha
            ),
            overlay_center,
            radius + 8,
            7
        )


        pygame.draw.circle(
            overlay,
            (
                255,
                190,
                60,
                210
            ),
            overlay_center,
            radius,
            CLEANING_RING_WIDTH
        )


        for dot_index in range(
            CLEANING_DOT_COUNT
        ):

            angle = (
                phase
                +
                (
                    2
                    *
                    math.pi
                    *
                    dot_index
                    /
                    CLEANING_DOT_COUNT
                )
            )


            dot_radius = (
                radius
                -
                4
            )


            dot_x = (
                overlay_center[0]
                +
                int(
                    math.cos(angle)
                    *
                    dot_radius
                )
            )


            dot_y = (
                overlay_center[1]
                +
                int(
                    math.sin(angle)
                    *
                    dot_radius
                )
            )


            dot_alpha = int(
                80
                +
                175
                *
                (
                    dot_index
                    /
                    CLEANING_DOT_COUNT
                )
            )


            pygame.draw.circle(
                overlay,
                (
                    255,
                    220,
                    120,
                    dot_alpha
                ),
                (
                    dot_x,
                    dot_y
                ),
                3
            )


        sparkle_size = int(
            5
            +
            pulse * 3
        )


        pygame.draw.circle(
            overlay,
            (
                255,
                245,
                190,
                220
            ),
            overlay_center,
            sparkle_size
        )


        screen.blit(
            overlay,
            (
                screen_x
                -
                overlay_size // 2,
                screen_y
                -
                overlay_size // 2
            )
        )


        cleaning_text = cleaning_font.render(
            "CLEANING",
            True,
            (
                255,
                225,
                150
            )
        )


        cleaning_text_x = (
            screen_x
            -
            cleaning_text.get_width() // 2
        )


        cleaning_text_y = (
            screen_y
            -
            10
        )


        text_background = pygame.Rect(
            cleaning_text_x - 7,
            cleaning_text_y - 3,
            cleaning_text.get_width() + 14,
            cleaning_text.get_height() + 6
        )


        pygame.draw.rect(
            screen,
            (
                20,
                20,
                25,
                215
            ),
            text_background,
            border_radius=6
        )


        screen.blit(
            cleaning_text,
            (
                cleaning_text_x,
                cleaning_text_y
            )
        )


        remaining_seconds = max(
            1,
            math.ceil(
                remaining
            )
        )


        timer_text = cleaning_timer_font.render(
            f"{remaining_seconds}s",
            True,
            (
                255,
                255,
                255
            )
        )


        timer_x = (
            screen_x
            -
            timer_text.get_width() // 2
        )


        timer_y = (
            screen_y
            +
            28
        )


        screen.blit(
            timer_text,
            (
                timer_x,
                timer_y
            )
        )


# ============================================================
# VISUAL CUSTOMER QUEUE
# ============================================================

QUEUE_X = 120

QUEUE_FRONT_Y = 110

QUEUE_SPACING = 58


queue = CustomerQueue(
    assets_root=ASSETS_DIR,
    queue_x=QUEUE_X,
    front_y=QUEUE_FRONT_Y,
    spacing_y=QUEUE_SPACING,
    customer_scale=1.0,
    max_customers=6
)


for customer_type in range(
    1,
    7
):

    queue.add_customer(
        customer_type
    )


print()
print(
    "========================================"
)
print(
    "CUSTOMER SHOWCASE QUEUE"
)
print(
    "========================================"
)

print(
    f"Customers displayed: "
    f"{len(queue)}"
)

print(
    "This queue is visual-only."
)

print(
    "It does not control table allocation."
)

print(
    "It remains fixed during the simulation."
)

print()


# ============================================================
# WAITING PEOPLE INPUT
# ============================================================

WAITING_INPUT_WIDTH = GAME_WIDTH

WAITING_INPUT_HEIGHT = 116

WAITING_INPUT_X = 0

WAITING_INPUT_Y = (
    HEIGHT
    -
    WAITING_INPUT_HEIGHT
)


def handle_new_group(
    group_size
):

    print()
    print(
        "========================================"
    )
    print(
        "[MAIN] NEW REAL CUSTOMER GROUP"
    )
    print(
        "========================================"
    )

    print(
        f"[MAIN] Group size: "
        f"{group_size}"
    )

    print(
        "[MAIN] Group added to waiting queue."
    )

    print(
        "[MAIN] Agent will keep checking for "
        "a suitable READY table."
    )

    print()


waiting_input = WaitingPeopleInput(
    x=WAITING_INPUT_X,
    y=WAITING_INPUT_Y,
    width=WAITING_INPUT_WIDTH,
    height=WAITING_INPUT_HEIGHT,
    on_group_added=handle_new_group
)


print()
print(
    "========================================"
)
print(
    "WAITING PEOPLE INPUT"
)
print(
    "========================================"
)

print(
    f"Input X: "
    f"{WAITING_INPUT_X}"
)

print(
    f"Input Y: "
    f"{WAITING_INPUT_Y}"
)

print(
    f"Input Width: "
    f"{WAITING_INPUT_WIDTH}"
)

print(
    f"Input Height: "
    f"{WAITING_INPUT_HEIGHT}"
)

print()

print(
    "Enter a group size."
)

print(
    "Example: 6 ENTER"
)

print()

print(
    "Flow:"
)

print(
    "    Input -> Waiting Queue -> Agent -> Table"
)

print()


# ============================================================
# KITCHEN
# ============================================================

kitchen = Kitchen(
    screen
)


KITCHEN_X = 1040


KITCHEN_CHEF_Y = (
    160
    +
    HEADER_HEIGHT
)


KITCHEN_TABLE_Y = (
    240
    +
    HEADER_HEIGHT
)


kitchen.chef_position = (
    KITCHEN_X,
    KITCHEN_CHEF_Y
)


kitchen.work_table_position = (
    KITCHEN_X,
    KITCHEN_TABLE_Y
)


# ============================================================
# HEADER
# ============================================================

header = Header(
    screen
)


# ============================================================
# TRACKER
# ============================================================

def get_tracker_algorithm_name():

    algorithm = agent.get_algorithm_name()


    if algorithm == ALGORITHM_EXPECTED_SARSA:

        return "Expected SARSA"


    if algorithm == ALGORITHM_ACTOR_CRITIC:

        return "Actor-Critic"


    if algorithm == ALGORITHM_DQN:

        return "DQN"


    if algorithm == ALGORITHM_N_STEP_TREE_BACKUP:

        return "N-step Tree Backup"


    return "Default"


def snapshot_current_algorithm():

    algorithm_name = (
        get_tracker_algorithm_name()
    )


    merged_statistics = {}


    try:

        general_statistics = agent.get_statistics()


        if isinstance(
            general_statistics,
            dict
        ):

            merged_statistics.update(
                general_statistics
            )


    except Exception:

        pass


    try:

        rl_statistics = agent.get_rl_statistics()


        if isinstance(
            rl_statistics,
            dict
        ):

            merged_statistics.update(
                rl_statistics
            )


    except Exception:

        pass


    merged_statistics[
        "customers_served"
    ] = getattr(
        agent,
        "total_customers_served",
        merged_statistics.get(
            "customers_served",
            0
        )
    )


    merged_statistics[
        "successful_allocations"
    ] = getattr(
        agent,
        "successful_allocations",
        merged_statistics.get(
            "successful_allocations",
            0
        )
    )


    merged_statistics[
        "total_decisions"
    ] = getattr(
        agent,
        "total_decisions",
        merged_statistics.get(
            "total_decisions",
            0
        )
    )


    merged_statistics[
        "failed_allocations"
    ] = getattr(
        agent,
        "failed_allocations",
        merged_statistics.get(
            "failed_allocations",
            0
        )
    )


    try:

        merged_statistics[
            "average_wait_time"
        ] = agent.get_average_wait_time()


    except Exception:

        pass


    result_tracker.update_from_statistics(
        merged_statistics,
        algorithm_name
    )


# ============================================================
# PDF EXPORT
# ============================================================

def handle_pdf_export():

    print()
    print(
        "========================================"
    )
    print(
        "[MAIN] PDF EXPORT STARTED"
    )
    print(
        "========================================"
    )


    try:

        snapshot_current_algorithm()


        from pdf_report import generate_pdf_report


        report_data = (
            result_tracker.get_report_data()
        )


        pdf_path = generate_pdf_report(
            report_data
        )


        print(
            f"[MAIN] PDF created: {pdf_path}"
        )


        print(
            "[MAIN] PDF EXPORT COMPLETE"
        )


        try:

            waiting_input.set_agent_message(
                "Algorithm results exported to PDF."
            )


        except Exception:

            pass


    except ImportError as exc:

        print(
            "[MAIN] PDF EXPORT ERROR: "
            "pdf_report.py is not available yet."
        )


        print(
            f"[MAIN] Details: {exc}"
        )


        try:

            waiting_input.set_agent_message(
                "PDF exporter is not ready yet."
            )


        except Exception:

            pass


    except Exception as exc:

        print(
            "[MAIN] PDF EXPORT ERROR:"
        )


        print(
            repr(exc)
        )


        try:

            waiting_input.set_agent_message(
                "PDF export failed. Check the console."
            )


        except Exception:

            pass


    print(
        "========================================"
    )

    print()


# ============================================================
# ALGORITHM SWITCHING
# ============================================================

def handle_algorithm_change(
    algorithm_name
):

    print()
    print(
        "========================================"
    )
    print(
        "[MAIN] ALGORITHM CHANGE REQUEST"
    )
    print(
        f"[MAIN] Requested: {algorithm_name}"
    )
    print(
        "========================================"
    )


    snapshot_current_algorithm()


    changed = agent.set_algorithm(
        algorithm_name,
        waiting_input
    )


    if changed:

        new_tracker_algorithm = (
            get_tracker_algorithm_name()
        )


        result_tracker.start_algorithm(
            new_tracker_algorithm
        )


        print(
            "[MAIN] Algorithm changed successfully."
        )


        print(
            f"[MAIN] Result tracking: "
            f"{new_tracker_algorithm}"
        )


    else:

        print(
            "[MAIN] Algorithm was already selected."
        )


    print()


# ============================================================
# SIDEBAR
# ============================================================
#
# IMPORTANT:
#
# The sidebar is a FULL-HEIGHT RIGHT COLUMN.
#
# Window:
#
#     WIDTH  = 1450
#     HEIGHT = 875
#
# Restaurant/game area:
#
#     X = 0
#     Y = 0
#     W = 1200
#
# Sidebar:
#
#     X = 1200
#     Y = 0
#     W = 250
#     H = 875
#
# Therefore the sidebar occupies the complete right side,
# including the 125px area beside the header.
#
# This is intentionally NOT:
#
#     y = HEADER_HEIGHT
#
# because that would create the unwanted top gap.
# ============================================================

sidebar = Sidebar(
    screen,
    x=GAME_WIDTH,
    y=0,
    width=SIDEBAR_WIDTH,
    height=HEIGHT,
    on_algorithm_changed=handle_algorithm_change,
    on_export_requested=handle_pdf_export
)


# ============================================================
# INITIAL SIDEBAR ALGORITHM
# ============================================================

if agent.get_algorithm_name() == ALGORITHM_EXPECTED_SARSA:

    sidebar.set_algorithm(
        "Expected SARSA"
    )


elif agent.get_algorithm_name() == ALGORITHM_ACTOR_CRITIC:

    sidebar.set_algorithm(
        "Actor-Critic"
    )


elif agent.get_algorithm_name() == ALGORITHM_DQN:

    sidebar.set_algorithm(
        "DQN"
    )


elif agent.get_algorithm_name() == ALGORITHM_N_STEP_TREE_BACKUP:

    sidebar.set_algorithm(
        "N-step Tree Backup"
    )


else:

    sidebar.set_algorithm(
        "Default"
    )


result_tracker.start_algorithm(
    get_tracker_algorithm_name()
)


# ============================================================
# TABLE STATUS HELPERS
# ============================================================

def get_table_status_counts():

    occupied = 0

    cleaning = 0

    ready = 0


    for index, table in enumerate(
        table_manager.tables
    ):

        is_occupied = bool(
            getattr(
                table,
                "occupied",
                False
            )
        )


        if is_occupied:

            occupied += 1

            continue


        if index in agent.free_timers:

            remaining = (
                agent.get_table_wait_time(
                    index
                )
            )


            if remaining > 0:

                cleaning += 1

                continue


        ready += 1


    return (
        occupied,
        ready,
        cleaning
    )


def get_occupied_table_indices():

    occupied = set()


    for index, table in enumerate(
        table_manager.tables
    ):

        if getattr(
            table,
            "occupied",
            False
        ):

            occupied.add(
                index
            )


    return occupied


# ============================================================
# MAIN LOOP
# ============================================================

running = True


while running:


    # --------------------------------------------------------
    # FRAME TIME
    # --------------------------------------------------------

    dt = clock.tick(
        60
    )


    dt_seconds = (
        dt
        /
        1000.0
    )


    cleaning_animation_time += dt


    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():


        if event.type == pygame.QUIT:

            running = False


        sidebar.handle_event(
            event
        )


        waiting_input.handle_event(
            event
        )


    # --------------------------------------------------------
    # AGENT ANIMATION
    # --------------------------------------------------------

    agent_timer += dt


    if (
        agent_timer
        >=
        AGENT_FRAME_TIMES[
            agent_frame
        ]
    ):

        agent_timer = 0

        agent_frame += 1


        if (
            agent_frame
            >=
            len(
                AGENT_FRAMES
            )
        ):

            agent_frame = 0


    current_agent = (
        AGENT_FRAMES[
            agent_frame
        ]
    )


    # --------------------------------------------------------
    # UPDATE SYSTEMS
    # --------------------------------------------------------

    waiting_input.update(
        dt
    )


    queue.update(
        dt_seconds
    )


    table_manager.update(
        dt
    )


    agent.update(
        dt,
        waiting_input
    )


    # --------------------------------------------------------
    # OCCUPANCY BEFORE ALLOCATION
    # --------------------------------------------------------

    occupied_before = (
        get_occupied_table_indices()
    )


    # --------------------------------------------------------
    # PROCESS ONE GROUP PER FRAME
    # --------------------------------------------------------

    allocated_table = (
        agent.process_waiting_queue(
            waiting_input,
            0
        )
    )


    # --------------------------------------------------------
    # OCCUPANCY AFTER ALLOCATION
    # --------------------------------------------------------

    occupied_after = (
        get_occupied_table_indices()
    )


    newly_occupied = (
        occupied_after
        -
        occupied_before
    )


    # --------------------------------------------------------
    # RECORD NEW ALLOCATION
    # --------------------------------------------------------

    if newly_occupied:


        allocated_index = (
            next(
                iter(
                    newly_occupied
                )
            )
        )


        if (
            0 <= allocated_index
            <
            len(
                table_manager.tables
            )
        ):


            allocated_table_object = (
                table_manager.tables[
                    allocated_index
                ]
            )


            group_size = getattr(
                allocated_table_object,
                "group_size",
                0
            )


            table_id = getattr(
                allocated_table_object,
                "table_id",
                "--"
            )


            capacity = getattr(
                allocated_table_object,
                "capacity",
                None
            )


            tracker_algorithm = (
                get_tracker_algorithm_name()
            )


            decision_reward = getattr(
                agent,
                "current_reward",
                0.0
            )


            unused_seats = None


            if capacity is not None:

                try:

                    unused_seats = max(
                        0,
                        int(capacity)
                        -
                        int(group_size)
                    )


                except (
                    TypeError,
                    ValueError
                ):

                    unused_seats = None


            # ------------------------------------------------
            # RESULT TRACKER
            # ------------------------------------------------

            result_tracker.record_decision(
                algorithm_name=tracker_algorithm,
                group_size=group_size,
                table_name=table_id,
                reward=decision_reward,
                penalty=(
                    1
                    if float(decision_reward) < 0
                    else 0
                ),
                result="SUCCESS",
                unused_seats=unused_seats
            )


            if float(decision_reward) < 0:

                result_tracker.record_penalty(
                    penalty=1,
                    algorithm_name=tracker_algorithm,
                    waste=(
                        unused_seats is not None
                        and
                        unused_seats >= 3
                    )
                )


            # ------------------------------------------------
            # LATEST DECISION
            # ------------------------------------------------

            sidebar.set_latest_decision(
                group_size=group_size,
                table_id=table_id,
                table_capacity=capacity,
                result="SUCCESS",
                reward=agent.current_reward,
                algorithm=(
                    "Expected SARSA"
                    if agent.get_algorithm_name()
                    == ALGORITHM_EXPECTED_SARSA

                    else (
                        "Actor-Critic"
                        if agent.get_algorithm_name()
                        == ALGORITHM_ACTOR_CRITIC

                        else (
                            "DQN"
                            if agent.get_algorithm_name()
                            == ALGORITHM_DQN

                            else (
                                "N-step Tree Backup"
                                if agent.get_algorithm_name()
                                == ALGORITHM_N_STEP_TREE_BACKUP

                                else "Default"
                            )
                        )
                    )
                )
            )


    # ========================================================
    # HEADER UPDATE
    # ========================================================

    header.update(
        dt_seconds,
        customers_served=(
            agent.total_customers_served
        ),
        average_wait_time=(
            agent.get_average_wait_time()
        ),
        satisfaction=(
            agent.get_satisfaction()
        )
    )


    # ========================================================
    # WAITING QUEUE
    # ========================================================

    waiting_people = (
        waiting_input.get_waiting_people()
    )


    sidebar.set_waiting_queue(
        len(
            waiting_people
        )
    )


    # ========================================================
    # TABLE STATUS
    # ========================================================

    (
        occupied_count,
        ready_count,
        cleaning_count
    ) = (
        get_table_status_counts()
    )


    sidebar.set_tables_occupied(
        occupied_count,
        len(
            table_manager.tables
        )
    )


    sidebar.set_tables_ready(
        ready_count
    )


    sidebar.set_tables_cleaning(
        cleaning_count
    )


    # ========================================================
    # CURRENT CUSTOMERS
    # ========================================================

    current_customers = sum(

        (
            getattr(
                table,
                "group_size",
                0
            )
            or 0
        )

        for table
        in table_manager.tables

        if getattr(
            table,
            "occupied",
            False
        )

    )


    sidebar.set_current_customers(
        current_customers
    )


    # ========================================================
    # CURRENT ALGORITHM
    # ========================================================

    current_algorithm_name = (
        agent.get_algorithm_name()
    )


    if current_algorithm_name == ALGORITHM_EXPECTED_SARSA:

        display_algorithm_name = "Expected SARSA"


    elif current_algorithm_name == ALGORITHM_ACTOR_CRITIC:

        display_algorithm_name = "Actor-Critic"


    elif current_algorithm_name == ALGORITHM_DQN:

        display_algorithm_name = "DQN"


    elif current_algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:

        display_algorithm_name = "N-step Tree Backup"


    else:

        display_algorithm_name = "Default"


    if getattr(
        sidebar,
        "selected_algorithm",
        None
    ) != display_algorithm_name:

        sidebar.set_algorithm(
            display_algorithm_name
        )


    # ========================================================
    # GENERAL SIDEBAR INFORMATION
    # ========================================================

    sidebar.set_average_wait_time(
        agent.get_average_wait_time()
    )


    if hasattr(
        sidebar,
        "sync_waiting_time"
    ):

        sidebar.sync_waiting_time(
            agent.get_waiting_time_seconds()
        )


    sidebar.set_satisfaction(
        agent.get_satisfaction()
    )


    # ========================================================
    # RL STATISTICS
    # ========================================================

    rl_statistics = agent.get_rl_statistics()


    if not isinstance(
        rl_statistics,
        dict
    ):

        rl_statistics = {}


    # ========================================================
    # ACTOR-CRITIC STATISTICS
    # ========================================================

    if (
        current_algorithm_name
        ==
        ALGORITHM_ACTOR_CRITIC
        and
        hasattr(
            agent,
            "get_actor_critic_statistics"
        )
    ):

        try:

            actor_critic_statistics = (
                agent.get_actor_critic_statistics()
            )


            if isinstance(
                actor_critic_statistics,
                dict
            ):

                rl_statistics.update(
                    actor_critic_statistics
                )


        except Exception as exc:

            print(
                f"[MAIN] Actor-Critic statistics warning: {exc}"
            )


    # ========================================================
    # RESULT TRACKER STATISTICS
    # ========================================================

    tracker_statistics = {}


    try:

        tracker_statistics.update(
            agent.get_statistics()
        )


    except Exception:

        pass


    if isinstance(
        rl_statistics,
        dict
    ):

        tracker_statistics.update(
            rl_statistics
        )


    tracker_statistics[
        "customers_served"
    ] = getattr(
        agent,
        "total_customers_served",
        tracker_statistics.get(
            "customers_served",
            0
        )
    )


    tracker_statistics[
        "successful_allocations"
    ] = getattr(
        agent,
        "successful_allocations",
        tracker_statistics.get(
            "successful_allocations",
            0
        )
    )


    tracker_statistics[
        "total_decisions"
    ] = getattr(
        agent,
        "total_decisions",
        tracker_statistics.get(
            "total_decisions",
            0
        )
    )


    tracker_statistics[
        "failed_allocations"
    ] = getattr(
        agent,
        "failed_allocations",
        tracker_statistics.get(
            "failed_allocations",
            0
        )
    )


    try:

        tracker_statistics[
            "average_wait_time"
        ] = agent.get_average_wait_time()


    except Exception:

        pass


    result_tracker.update_from_statistics(
        tracker_statistics,
        get_tracker_algorithm_name()
    )


    # ========================================================
    # COMMON RL SIDEBAR VALUES
    # ========================================================

    sidebar.set_episode(
        rl_statistics.get(
            "episode",
            0
        )
    )


    sidebar.set_current_reward(
        rl_statistics.get(
            "current_reward",
            getattr(
                agent,
                "current_reward",
                0.0
            )
        )
    )


    sidebar.set_best_reward(
        rl_statistics.get(
            "best_reward",
            0.0
        )
    )


    sidebar.set_q_updates(
        rl_statistics.get(
            "q_updates",
            0
        )
    )


    sidebar.set_allocation_accuracy(
        rl_statistics.get(
            "allocation_accuracy",
            0.0
        )
    )


    # ========================================================
    # TOTAL REWARD
    # ========================================================

    if (
        hasattr(
            sidebar,
            "set_total_reward"
        )
        and
        "total_reward"
        in
        rl_statistics
    ):

        sidebar.set_total_reward(
            rl_statistics[
                "total_reward"
            ]
        )


    # ========================================================
    # TOTAL PENALTIES
    # ========================================================

    if (
        hasattr(
            sidebar,
            "set_total_penalties"
        )
        and
        "total_penalties"
        in
        rl_statistics
    ):

        sidebar.set_total_penalties(
            rl_statistics[
                "total_penalties"
            ]
        )


    # ========================================================
    # WASTE PENALTIES
    # ========================================================

    if (
        hasattr(
            sidebar,
            "set_waste_penalties"
        )
        and
        "waste_penalties"
        in
        rl_statistics
    ):

        sidebar.set_waste_penalties(
            rl_statistics[
                "waste_penalties"
            ]
        )


    # ========================================================
    # ACTOR-CRITIC VALUES
    # ========================================================

    if (
        hasattr(
            sidebar,
            "set_actor_updates"
        )
        and
        "actor_updates"
        in
        rl_statistics
    ):

        sidebar.set_actor_updates(
            rl_statistics[
                "actor_updates"
            ]
        )


    if (
        hasattr(
            sidebar,
            "set_critic_updates"
        )
        and
        "critic_updates"
        in
        rl_statistics
    ):

        sidebar.set_critic_updates(
            rl_statistics[
                "critic_updates"
            ]
        )


    if (
        hasattr(
            sidebar,
            "set_actor_loss"
        )
        and
        "actor_loss"
        in
        rl_statistics
    ):

        sidebar.set_actor_loss(
            rl_statistics[
                "actor_loss"
            ]
        )


    if (
        hasattr(
            sidebar,
            "set_critic_loss"
        )
        and
        "critic_loss"
        in
        rl_statistics
    ):

        sidebar.set_critic_loss(
            rl_statistics[
                "critic_loss"
            ]
        )


    if (
        hasattr(
            sidebar,
            "set_entropy"
        )
        and
        "entropy"
        in
        rl_statistics
    ):

        sidebar.set_entropy(
            rl_statistics[
                "entropy"
            ]
        )


    # ========================================================
    # DQN-SPECIFIC SIDEBAR STATISTICS
    # ========================================================

    # --------------------------------------------------------
    # LOSS
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_loss"
        )
        and
        "dqn_loss"
        in
        rl_statistics
    ):

        sidebar.set_dqn_loss(
            rl_statistics[
                "dqn_loss"
            ]
        )


    elif (
        hasattr(
            sidebar,
            "set_dqn_loss"
        )
        and
        "loss"
        in
        rl_statistics
    ):

        sidebar.set_dqn_loss(
            rl_statistics[
                "loss"
            ]
        )


    # --------------------------------------------------------
    # Q VALUE
    # --------------------------------------------------------

    if hasattr(
        sidebar,
        "set_dqn_q_value"
    ):

        dqn_q_value = rl_statistics.get(
            "q_value",
            rl_statistics.get(
                "last_q_value",
                0.0
            )
        )


        sidebar.set_dqn_q_value(
            dqn_q_value
        )


    # --------------------------------------------------------
    # TARGET Q
    # --------------------------------------------------------

    if hasattr(
        sidebar,
        "set_dqn_target_q"
    ):

        dqn_target_q = rl_statistics.get(
            "target_q",
            rl_statistics.get(
                "last_target_q",
                0.0
            )
        )


        sidebar.set_dqn_target_q(
            dqn_target_q
        )


    # --------------------------------------------------------
    # TD ERROR
    # --------------------------------------------------------

    if hasattr(
        sidebar,
        "set_dqn_td_error"
    ):

        dqn_td_error = rl_statistics.get(
            "td_error",
            rl_statistics.get(
                "last_td_error",
                0.0
            )
        )


        sidebar.set_dqn_td_error(
            dqn_td_error
        )


    # --------------------------------------------------------
    # REPLAY SIZE
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_replay_size"
        )
        and
        "replay_size"
        in
        rl_statistics
    ):

        sidebar.set_dqn_replay_size(
            rl_statistics[
                "replay_size"
            ]
        )


    elif (
        hasattr(
            sidebar,
            "set_dqn_replay_size"
        )
        and
        "replay_buffer_size"
        in
        rl_statistics
    ):

        sidebar.set_dqn_replay_size(
            rl_statistics[
                "replay_buffer_size"
            ]
        )


    # --------------------------------------------------------
    # TARGET NETWORK UPDATES
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_target_updates"
        )
        and
        "target_updates"
        in
        rl_statistics
    ):

        sidebar.set_dqn_target_updates(
            rl_statistics[
                "target_updates"
            ]
        )


    # --------------------------------------------------------
    # EXPLORATIONS
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_explorations"
        )
        and
        "explorations"
        in
        rl_statistics
    ):

        sidebar.set_dqn_explorations(
            rl_statistics[
                "explorations"
            ]
        )


    # --------------------------------------------------------
    # EXPLOITATIONS
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_exploitations"
        )
        and
        "exploitations"
        in
        rl_statistics
    ):

        sidebar.set_dqn_exploitations(
            rl_statistics[
                "exploitations"
            ]
        )


    # --------------------------------------------------------
    # EPSILON
    # --------------------------------------------------------

    if (
        hasattr(
            sidebar,
            "set_dqn_epsilon"
        )
        and
        "epsilon"
        in
        rl_statistics
    ):

        sidebar.set_dqn_epsilon(
            rl_statistics[
                "epsilon"
            ]
        )


    # ========================================================
    # N-STEP TREE BACKUP STATISTICS
    # ========================================================

    if hasattr(sidebar, "set_n_step") and "n_step" in rl_statistics:

        sidebar.set_n_step(rl_statistics["n_step"])


    if hasattr(sidebar, "set_n_step_tree_backup_return"):

        tree_return = rl_statistics.get(
            "tree_backup_return",
            rl_statistics.get("last_tree_backup_return", 0.0)
        )

        sidebar.set_n_step_tree_backup_return(tree_return)


    if hasattr(sidebar, "set_n_step_td_error"):

        sidebar.set_n_step_td_error(
            rl_statistics.get("td_error", rl_statistics.get("last_td_error", 0.0))
        )


    if hasattr(sidebar, "set_n_step_pending_transitions"):

        sidebar.set_n_step_pending_transitions(
            rl_statistics.get("pending_transitions", 0)
        )


    if hasattr(sidebar, "set_n_step_explorations"):

        sidebar.set_n_step_explorations(
            rl_statistics.get("explorations", 0)
        )


    if hasattr(sidebar, "set_n_step_exploitations"):

        sidebar.set_n_step_exploitations(
            rl_statistics.get("exploitations", 0)
        )


    if hasattr(sidebar, "set_n_step_epsilon") and "epsilon" in rl_statistics:

        sidebar.set_n_step_epsilon(rl_statistics["epsilon"])


    # ========================================================
    # ADVANTAGE / VALUE ESTIMATE
    # ========================================================

    if "advantage" in rl_statistics:

        try:

            sidebar.advantage = float(
                rl_statistics[
                    "advantage"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            pass


    if "value_estimate" in rl_statistics:

        try:

            sidebar.value_estimate = float(
                rl_statistics[
                    "value_estimate"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            pass


    # ========================================================
    # LATEST DECISION
    # ========================================================

    if (
        hasattr(
            sidebar,
            "set_latest_decision"
        )
        and
        getattr(
            agent,
            "last_group_size",
            None
        )
        is not None
    ):

        sidebar.set_latest_decision(
            group_size=agent.last_group_size,

            table_id=getattr(
                agent,
                "last_selected_table",
                "--"
            ),

            table_capacity=getattr(
                agent,
                "last_table_capacity",
                None
            ),

            result=getattr(
                agent,
                "last_decision_result",
                "--"
            ),

            reward=getattr(
                agent,
                "last_reward",
                getattr(
                    agent,
                    "current_reward",
                    0.0
                )
            ),

            algorithm=(
                "Expected SARSA"
                if current_algorithm_name
                ==
                ALGORITHM_EXPECTED_SARSA

                else (
                    "Actor-Critic"
                    if current_algorithm_name
                    ==
                    ALGORITHM_ACTOR_CRITIC

                    else (
                        "DQN"
                        if current_algorithm_name
                        ==
                        ALGORITHM_DQN

                        else "Default"
                    )
                )
            )
        )


    # ========================================================
    # SIDEBAR INTERNAL SYNC
    # ========================================================

    if hasattr(
        sidebar,
        "sync_algorithm_display"
    ):

        sidebar.sync_algorithm_display(
            rl_statistics
        )


    # ========================================================
    # ALLOCATION COUNTERS
    # ========================================================

    sidebar.set_total_decisions(
        agent.total_decisions
    )


    sidebar.set_successful_allocations(
        agent.successful_allocations
    )


    # ========================================================
    # SIDEBAR UPDATE
    # ========================================================

    sidebar.update(
        dt_seconds
    )


    # ========================================================
    # KITCHEN UPDATE
    # ========================================================

    kitchen.update(
        dt
    )


    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(
        BACKGROUND
    )


    # --------------------------------------------------------
    # FLOOR
    # --------------------------------------------------------

    screen.blit(
        floor,
        (
            floor_x,
            floor_y
        )
    )


    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    table_manager.draw(
        screen,
        HEADER_HEIGHT
    )


    # --------------------------------------------------------
    # CLEANING
    # --------------------------------------------------------

    draw_cleaning_animation()


    # --------------------------------------------------------
    # CUSTOMER SHOWCASE QUEUE
    # --------------------------------------------------------

    queue.draw(
        screen
    )


    # --------------------------------------------------------
    # RESTAURANT AGENT
    # --------------------------------------------------------

    agent_x = (
        AGENT_X
        -
        current_agent.get_width()
        //
        2
    )


    agent_y = (
        AGENT_Y
        +
        HEADER_HEIGHT
        -
        current_agent.get_height()
        //
        2
    )


    screen.blit(
        current_agent,
        (
            agent_x,
            agent_y
        )
    )


    # --------------------------------------------------------
    # KITCHEN
    # --------------------------------------------------------

    kitchen.draw()


    # --------------------------------------------------------
    # WAITING INPUT
    # --------------------------------------------------------

    waiting_input.draw(
        screen
    )


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header.draw()


    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
    #
    # Sidebar is drawn LAST so its full-height right column
    # remains visually clean and independent of the restaurant
    # and header rendering.
    #
    # --------------------------------------------------------

    sidebar.draw()


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()


# ============================================================
# FINALIZE RESULTS
# ============================================================

try:

    if hasattr(agent, "finalize_episode"):

        try:

            agent.finalize_episode()

        except Exception as exc:

            print(f"[MAIN] N-step finalization warning: {exc}")


    snapshot_current_algorithm()

    result_tracker.finish_simulation()


except Exception as exc:

    print(
        f"[MAIN] Result tracker finalization warning: {exc}"
    )


pygame.quit()

sys.exit()