import pygame
import os
import random


# ============================================================
# TABLES.PY
# ============================================================
#
# METRIUS EATS
#
# Handles:
#
#   - Table configuration
#   - Table capacities
#   - Table occupancy
#   - Group sizes
#   - Base table images
#   - Customer-filled table images
#   - Loading c1.png / c2.png / c3.png ...
#   - Restoring empty tables
#   - Random table occupancy duration
#   - Automatically freeing tables
#
#
# IMPORTANT
# ----------
#
# This file DOES NOT decide which table should be selected.
#
# agent.py decides which table to use.
#
# TableManager executes the decision.
#
#
# TABLE FLOW
# ----------
#
#     FREE
#       |
#       | agent allocation
#       v
#     OCCUPIED
#       |
#       | random 7-10 seconds
#       v
#     FREE
#
#
# IMPORTANT
# ----------
#
# The 5-second delay AFTER a table becomes FREE is handled
# by agent.py.
#
# tables.py does NOT contain that delay.
#
# ============================================================


# ============================================================
# TABLE DISPLAY SIZES
# ============================================================

TABLE_SIX_MAX_WIDTH = 220
TABLE_SIX_MAX_HEIGHT = 220

TABLE_FOUR_MAX_WIDTH = 205
TABLE_FOUR_MAX_HEIGHT = 205

TABLE_TWO_MAX_WIDTH = 175
TABLE_TWO_MAX_HEIGHT = 175


# ============================================================
# TABLE OCCUPANCY TIME
# ============================================================
#
# Every time a group occupies a table, a new random duration
# between 7 and 10 seconds is generated.
#
# ============================================================

MIN_OCCUPANCY_TIME = 7.0
MAX_OCCUPANCY_TIME = 10.0


# ============================================================
# TABLE CONFIGURATION
# ============================================================
#
# Restaurant order:
#
# T1 -> table_6 -> capacity 4
# T2 -> table_4 -> capacity 2
# T3 -> table_2 -> capacity 6
# T4 -> table_3 -> capacity 2
# T5 -> table_4 -> capacity 2
# T6 -> table_1 -> capacity 2
# T7 -> table_1 -> capacity 2
# T8 -> table_6 -> capacity 4
#
# ============================================================

TABLE_CONFIG = [

    {
        "id": "T1",
        "folder": "table_6",
        "base": "table_6.png",
        "type": "four",
        "capacity": 4,
        "position": (360, 180)
    },

    {
        "id": "T2",
        "folder": "table_4",
        "base": "table_4.png",
        "type": "two",
        "capacity": 2,
        "position": (565, 180)
    },

    {
        "id": "T3",
        "folder": "table_2",
        "base": "table_2.png",
        "type": "six",
        "capacity": 6,
        "position": (770, 180)
    },

    {
        "id": "T4",
        "folder": "table_3",
        "base": "table_3.png",
        "type": "two",
        "capacity": 2,
        "position": (360, 365)
    },

    {
        "id": "T5",
        "folder": "table_4",
        "base": "table_4.png",
        "type": "two",
        "capacity": 2,
        "position": (770, 365)
    },

    {
        "id": "T6",
        "folder": "table_1",
        "base": "table_1.png",
        "type": "two",
        "capacity": 2,
        "position": (360, 550)
    },

    {
        "id": "T7",
        "folder": "table_1",
        "base": "table_1.png",
        "type": "two",
        "capacity": 2,
        "position": (565, 550)
    },

    {
        "id": "T8",
        "folder": "table_6",
        "base": "table_6.png",
        "type": "four",
        "capacity": 4,
        "position": (770, 550)
    }

]


# ============================================================
# TABLE
# ============================================================

class Table:

    """
    Represents one restaurant table.

    Example:

        T1

        capacity = 4

        occupied = True

        group_size = 4

        occupancy_duration = 8.37

        occupancy_timer = 3.12
    """

    def __init__(
        self,
        table_id,
        folder_path,
        base_filename,
        table_type,
        capacity,
        position
    ):

        # ====================================================
        # BASIC INFORMATION
        # ====================================================

        self.table_id = table_id

        self.folder_path = folder_path

        self.base_filename = base_filename

        self.table_type = table_type

        self.capacity = capacity

        self.position = position

        # ====================================================
        # STATE
        # ====================================================
        #
        # False = FREE
        # True  = OCCUPIED
        #
        # There is intentionally NO "assigned" state.
        #
        # ====================================================

        self.occupied = False

        self.group_size = 0

        # ====================================================
        # OCCUPANCY TIMER
        # ====================================================

        self.occupancy_timer = 0.0

        self.occupancy_duration = 0.0

        # ====================================================
        # IMAGES
        # ====================================================

        self.base_image = None

        self.current_image = None

        # ====================================================
        # LOAD BASE IMAGE
        # ====================================================

        self.load_base_image()

    # ========================================================
    # LOAD BASE IMAGE
    # ========================================================

    def load_base_image(
        self
    ):

        path = os.path.join(
            self.folder_path,
            self.base_filename
        )

        # ====================================================
        # CHECK FILE
        # ====================================================

        if not os.path.exists(path):

            raise FileNotFoundError(
                "Table image not found:\n"
                f"{path}"
            )

        # ====================================================
        # LOAD IMAGE
        # ====================================================

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

        except pygame.error as e:

            raise RuntimeError(
                f"Could not load table image:\n"
                f"{path}\n\n"
                f"{e}"
            )

        # ====================================================
        # FIT TABLE
        # ====================================================

        self.base_image = fit_table(
            image,
            self.table_type
        )

        # ====================================================
        # INITIAL IMAGE
        # ====================================================
        #
        # Every table starts FREE.
        #
        # ====================================================

        self.current_image = self.base_image

    # ========================================================
    # GET CUSTOMER IMAGE PATH
    # ========================================================

    def get_customer_image_path(
        self,
        group_size
    ):

        # ====================================================
        # VALIDATE
        # ====================================================

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return None

        # ====================================================
        # NORMAL NAMING
        #
        # c1.png
        # c2.png
        # c3.png
        # ...
        # ====================================================

        normal_filename = (
            f"c{group_size}.png"
        )

        normal_path = os.path.join(
            self.folder_path,
            normal_filename
        )

        if os.path.exists(
            normal_path
        ):

            return normal_path

        # ====================================================
        # SPECIAL TABLE_1 CASE
        #
        # table_1 has:
        #
        #     c1.png
        #     c1c2.png
        #
        # For group size 2 use c1c2.png.
        # ====================================================

        if (
            self.folder_name == "table_1"
            and
            group_size == 2
        ):

            combined_path = os.path.join(
                self.folder_path,
                "c1c2.png"
            )

            if os.path.exists(
                combined_path
            ):

                return combined_path

        # ====================================================
        # NOT FOUND
        # ====================================================

        return None

    # ========================================================
    # LOAD CUSTOMER IMAGE
    # ========================================================

    def load_customer_image(
        self,
        group_size
    ):

        path = self.get_customer_image_path(
            group_size
        )

        # ====================================================
        # FILE NOT FOUND
        # ====================================================

        if path is None:

            print(
                "[TABLE WARNING] Missing customer "
                f"image for {self.table_id}: "
                f"c{group_size}.png"
            )

            return False

        # ====================================================
        # LOAD
        # ====================================================

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

        except pygame.error as e:

            print(
                "[TABLE WARNING] Could not load:"
            )

            print(
                path
            )

            print(
                e
            )

            return False

        # ====================================================
        # FIT TO TABLE SIZE
        # ====================================================

        image = fit_image_to_size(
            image,
            self.base_image.get_size()
        )

        # ====================================================
        # TRANSPARENT CANVAS
        # ====================================================

        target_width = (
            self.base_image.get_width()
        )

        target_height = (
            self.base_image.get_height()
        )

        final_image = pygame.Surface(
            (
                target_width,
                target_height
            ),
            pygame.SRCALPHA
        )

        final_image.fill(
            (
                0,
                0,
                0,
                0
            )
        )

        # ====================================================
        # CENTER CUSTOMER IMAGE
        # ====================================================

        x = (
            target_width
            -
            image.get_width()
        ) // 2

        y = (
            target_height
            -
            image.get_height()
        ) // 2

        final_image.blit(
            image,
            (
                x,
                y
            )
        )

        # ====================================================
        # SET CURRENT IMAGE
        # ====================================================

        self.current_image = final_image

        return True

    # ========================================================
    # OCCUPY TABLE
    # ========================================================

    def occupy(
        self,
        group_size
    ):

        """
        Make the table OCCUPIED immediately.

        The agent calls this only after its 5-second
        post-free delay has completed.

        This function starts a fresh 7-10 second dining timer.
        """

        # ====================================================
        # VALIDATE GROUP SIZE
        # ====================================================

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            print(
                f"[TABLE] Invalid group size: "
                f"{group_size}"
            )

            return False

        # ====================================================
        # POSITIVE GROUP SIZE
        # ====================================================

        if group_size <= 0:

            print(
                f"[TABLE] Invalid group size: "
                f"{group_size}"
            )

            return False

        # ====================================================
        # CAPACITY
        # ====================================================

        if group_size > self.capacity:

            print(
                f"[TABLE] {self.table_id} cannot fit "
                f"{group_size} people. "
                f"Capacity = {self.capacity}"
            )

            return False

        # ====================================================
        # ALREADY OCCUPIED
        # ====================================================

        if self.occupied:

            print(
                f"[TABLE] {self.table_id} is already occupied."
            )

            return False

        # ====================================================
        # SET OCCUPIED
        # ====================================================

        self.occupied = True

        self.group_size = group_size

        # ====================================================
        # RESET TIMER
        # ====================================================

        self.occupancy_timer = 0.0

        # ====================================================
        # NEW RANDOM DINING TIME
        # ====================================================

        self.occupancy_duration = random.uniform(
            MIN_OCCUPANCY_TIME,
            MAX_OCCUPANCY_TIME
        )

        # ====================================================
        # LOAD CUSTOMER VISUAL
        # ====================================================

        visual_loaded = (
            self.load_customer_image(
                group_size
            )
        )

        if visual_loaded:

            print(
                f"[TABLE] {self.table_id} "
                f"customer visual loaded for "
                f"{group_size} people."
            )

        else:

            print(
                f"[TABLE] {self.table_id} "
                f"customer visual not found for "
                f"{group_size} people."
            )

        # ====================================================
        # DEBUG
        # ====================================================

        print(
            f"[TABLE] {self.table_id} -> OCCUPIED"
        )

        print(
            f"[TABLE TIMER] {self.table_id} "
            f"occupied for "
            f"{self.occupancy_duration:.2f} seconds."
        )

        return True

    # ========================================================
    # UPDATE TABLE
    # ========================================================

    def update(
        self,
        dt
    ):

        """
        Update the 7-10 second occupancy timer.

        When the timer finishes:

            OCCUPIED -> FREE
        """

        # ====================================================
        # TABLE FREE
        # ====================================================

        if not self.occupied:

            return

        # ====================================================
        # DELTA TIME
        # ====================================================

        try:

            dt_seconds = (
                float(dt) / 1000.0
            )

        except (
            ValueError,
            TypeError
        ):

            return

        if dt_seconds < 0:

            dt_seconds = 0.0

        # ====================================================
        # ADVANCE TIMER
        # ====================================================

        self.occupancy_timer += (
            dt_seconds
        )

        # ====================================================
        # DINING FINISHED
        # ====================================================

        if (
            self.occupancy_timer
            >=
            self.occupancy_duration
        ):

            print(
                f"[TABLE TIMER] {self.table_id} "
                f"finished after "
                f"{self.occupancy_timer:.2f} seconds."
            )

            self.free()

    # ========================================================
    # FREE TABLE
    # ========================================================

    def free(
        self
    ):

        """
        Make the table FREE.

        IMPORTANT:

        This function ONLY makes the table free.

        agent.py detects this transition and starts the
        5-second delay before the next queue allocation.
        """

        # ====================================================
        # ALREADY FREE
        # ====================================================

        if not self.occupied:

            self.group_size = 0

            self.current_image = (
                self.base_image
            )

            return

        # ====================================================
        # SET FREE
        # ====================================================

        self.occupied = False

        self.group_size = 0

        # ====================================================
        # RESET TIMER
        # ====================================================

        self.occupancy_timer = 0.0

        self.occupancy_duration = 0.0

        # ====================================================
        # RESTORE BASE TABLE
        # ====================================================

        self.current_image = (
            self.base_image
        )

        # ====================================================
        # DEBUG
        # ====================================================

        print(
            f"[TABLE] {self.table_id} -> FREE"
        )

    # ========================================================
    # CHECK AVAILABILITY
    # ========================================================

    def is_available(
        self,
        group_size
    ):

        """
        Return True only if:

            - table is FREE
            - group fits
        """

        # ====================================================
        # VALIDATE
        # ====================================================

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return False

        if group_size <= 0:

            return False

        # ====================================================
        # OCCUPIED
        # ====================================================

        if self.occupied:

            return False

        # ====================================================
        # CAPACITY
        # ====================================================

        if self.capacity < group_size:

            return False

        # ====================================================
        # AVAILABLE
        # ====================================================

        return True

    # ========================================================
    # GET REMAINING OCCUPANCY TIME
    # ========================================================

    def get_remaining_time(
        self
    ):

        if not self.occupied:

            return 0.0

        remaining = (
            self.occupancy_duration
            -
            self.occupancy_timer
        )

        return max(
            0.0,
            remaining
        )

    # ========================================================
    # GET STATUS
    # ========================================================

    def get_status(
        self
    ):

        if self.occupied:

            return "OCCUPIED"

        return "FREE"

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface,
        header_height=125
    ):

        x, y = self.position

        screen_x = x

        screen_y = (
            y
            +
            header_height
        )

        draw_x = (
            screen_x
            -
            self.current_image.get_width() // 2
        )

        draw_y = (
            screen_y
            -
            self.current_image.get_height() // 2
        )

        surface.blit(
            self.current_image,
            (
                draw_x,
                draw_y
            )
        )

    # ========================================================
    # FOLDER NAME
    # ========================================================

    @property
    def folder_name(
        self
    ):

        return os.path.basename(
            self.folder_path
        )


# ============================================================
# FIT TABLE
# ============================================================

def fit_table(
    image,
    table_type
):

    original_width = (
        image.get_width()
    )

    original_height = (
        image.get_height()
    )

    # ========================================================
    # MAX SIZE
    # ========================================================

    if table_type == "six":

        max_width = TABLE_SIX_MAX_WIDTH

        max_height = TABLE_SIX_MAX_HEIGHT

    elif table_type == "four":

        max_width = TABLE_FOUR_MAX_WIDTH

        max_height = TABLE_FOUR_MAX_HEIGHT

    else:

        max_width = TABLE_TWO_MAX_WIDTH

        max_height = TABLE_TWO_MAX_HEIGHT

    # ========================================================
    # SCALE
    # ========================================================

    width_scale = (
        max_width
        /
        original_width
    )

    height_scale = (
        max_height
        /
        original_height
    )

    scale = min(
        width_scale,
        height_scale
    )

    # ========================================================
    # NEW SIZE
    # ========================================================

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

    # ========================================================
    # SCALE IMAGE
    # ========================================================

    return pygame.transform.smoothscale(
        image,
        (
            new_width,
            new_height
        )
    )


# ============================================================
# FIT IMAGE TO TARGET
# ============================================================

def fit_image_to_size(
    image,
    target_size
):

    target_width, target_height = (
        target_size
    )

    original_width = (
        image.get_width()
    )

    original_height = (
        image.get_height()
    )

    # ========================================================
    # INVALID IMAGE
    # ========================================================

    if (
        original_width <= 0
        or
        original_height <= 0
    ):

        return image

    # ========================================================
    # SCALE
    # ========================================================

    width_scale = (
        target_width
        /
        original_width
    )

    height_scale = (
        target_height
        /
        original_height
    )

    scale = min(
        width_scale,
        height_scale
    )

    # ========================================================
    # NEW SIZE
    # ========================================================

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

    # ========================================================
    # SCALE
    # ========================================================

    return pygame.transform.smoothscale(
        image,
        (
            new_width,
            new_height
        )
    )


# ============================================================
# TABLE MANAGER
# ============================================================

class TableManager:

    """
    Controls all restaurant tables.

    TableManager:

        - creates tables
        - executes allocations
        - updates occupancy timers
        - frees finished tables
        - draws tables

    It does NOT choose the table.
    """

    def __init__(
        self,
        assets_root
    ):

        # ====================================================
        # ROOT
        # ====================================================

        self.assets_root = assets_root

        self.tables_root = os.path.join(
            assets_root,
            "tables"
        )

        # ====================================================
        # TABLE LIST
        # ====================================================

        self.tables = []

        # ====================================================
        # CREATE TABLES
        # ====================================================

        for config in TABLE_CONFIG:

            folder_path = os.path.join(
                self.tables_root,
                config["folder"]
            )

            # =================================================
            # CHECK FOLDER
            # =================================================

            if not os.path.isdir(
                folder_path
            ):

                raise FileNotFoundError(
                    "Table folder not found:\n"
                    f"{folder_path}"
                )

            # =================================================
            # CREATE TABLE
            # =================================================

            table = Table(

                table_id=config["id"],

                folder_path=folder_path,

                base_filename=config["base"],

                table_type=config["type"],

                capacity=config["capacity"],

                position=config["position"]

            )

            self.tables.append(
                table
            )

            # =================================================
            # DEBUG
            # =================================================

            print(
                f"[TABLES] Created "
                f"{config['id']} | "
                f"Capacity: {config['capacity']} | "
                f"Folder: {config['folder']}"
            )

    # ========================================================
    # GET TABLE
    # ========================================================

    def get_table(
        self,
        table_index
    ):

        try:

            table_index = int(
                table_index
            )

        except (
            ValueError,
            TypeError
        ):

            return None

        if (
            table_index < 0
            or
            table_index >= len(
                self.tables
            )
        ):

            return None

        return self.tables[
            table_index
        ]

    # ========================================================
    # GET TABLE BY ID
    # ========================================================

    def get_table_by_id(
        self,
        table_id
    ):

        for table in self.tables:

            if table.table_id == table_id:

                return table

        return None

    # ========================================================
    # OCCUPY TABLE
    # ========================================================

    def occupy_table(
        self,
        table_index,
        group_size
    ):

        """
        Execute the agent's table decision.

        The table becomes OCCUPIED immediately.

        The agent has already waited its 5 seconds before
        calling this function.
        """

        table = self.get_table(
            table_index
        )

        if table is None:

            print(
                f"[TABLES] Invalid table index: "
                f"{table_index}"
            )

            return False

        return table.occupy(
            group_size
        )

    # ========================================================
    # OCCUPY TABLE BY ID
    # ========================================================

    def occupy_table_by_id(
        self,
        table_id,
        group_size
    ):

        table = self.get_table_by_id(
            table_id
        )

        if table is None:

            print(
                f"[TABLES] Unknown table: "
                f"{table_id}"
            )

            return False

        return table.occupy(
            group_size
        )

    # ========================================================
    # FREE TABLE
    # ========================================================

    def free_table(
        self,
        table_index
    ):

        table = self.get_table(
            table_index
        )

        if table is None:

            return False

        table.free()

        return True

    # ========================================================
    # FREE TABLE BY ID
    # ========================================================

    def free_table_by_id(
        self,
        table_id
    ):

        table = self.get_table_by_id(
            table_id
        )

        if table is None:

            return False

        table.free()

        return True

    # ========================================================
    # GET AVAILABLE TABLES
    # ========================================================

    def get_available_tables(
        self,
        group_size
    ):

        available = []

        for index, table in enumerate(
            self.tables
        ):

            if table.is_available(
                group_size
            ):

                available.append(
                    index
                )

        return available

    # ========================================================
    # GET AVAILABLE TABLE OBJECTS
    # ========================================================

    def get_available_table_objects(
        self,
        group_size
    ):

        available = []

        for table in self.tables:

            if table.is_available(
                group_size
            ):

                available.append(
                    table
                )

        return available

    # ========================================================
    # UPDATE ALL TABLES
    # ========================================================

    def update(
        self,
        dt
    ):

        """
        Update every table.

        Each occupied table has its own independent
        7-10 second timer.

        When a timer finishes, the table automatically
        becomes FREE.
        """

        for table in self.tables:

            table.update(
                dt
            )

    # ========================================================
    # GET OCCUPIED COUNT
    # ========================================================

    def get_occupied_count(
        self
    ):

        count = 0

        for table in self.tables:

            if table.occupied:

                count += 1

        return count

    # ========================================================
    # GET FREE COUNT
    # ========================================================

    def get_free_count(
        self
    ):

        return (
            len(
                self.tables
            )
            -
            self.get_occupied_count()
        )

    # ========================================================
    # GET TOTAL COUNT
    # ========================================================

    def get_total_count(
        self
    ):

        return len(
            self.tables
        )

    # ========================================================
    # DRAW ALL TABLES
    # ========================================================

    def draw(
        self,
        surface,
        header_height=125
    ):

        for table in self.tables:

            table.draw(
                surface,
                header_height
            )

    # ========================================================
    # PRINT STATUS
    # ========================================================

    def print_status(
        self
    ):

        print()

        print(
            "========================================"
        )

        print(
            "TABLE STATUS"
        )

        print(
            "========================================"
        )

        for table in self.tables:

            if table.occupied:

                remaining = (
                    table.get_remaining_time()
                )

                print(
                    f"{table.table_id} | "
                    f"Capacity: {table.capacity} | "
                    f"Status: OCCUPIED | "
                    f"Group: {table.group_size} | "
                    f"Remaining: {remaining:.2f}s"
                )

            else:

                print(
                    f"{table.table_id} | "
                    f"Capacity: {table.capacity} | "
                    f"Status: FREE | "
                    f"Group: 0"
                )

        print()


# ============================================================
# END OF TABLES.PY
# ============================================================