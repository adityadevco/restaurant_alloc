import pygame
import os
import sys


# ============================================================
# KITCHEN MODULE
# ============================================================
#
# Handles:
#
#   - One Chef
#   - One Work Table
#   - Chef animation
#   - Work table animation
#   - Correct kitchen layering
#
#
# LAYER ORDER
# ------------------------------------------------------------
#
# FLOOR
#   ↓
# CHEF
#   ↓
# WORK TABLE / BENCH
#
# ============================================================


# ============================================================
# PROJECT ROOT DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# ASSET DIRECTORIES
# ============================================================

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


# ============================================================
# CHEF DIRECTORY
# ============================================================

SHEF_DIR = os.path.join(
    ASSETS_DIR,
    "shef"
)


# ============================================================
# WORK TABLE DIRECTORY
# ============================================================
#
# Actual folder:
#
#     assets/work_table/work_table1/
#
# ============================================================

WORK_TABLE_DIR = os.path.join(
    ASSETS_DIR,
    "work_table",
    "work_table1"
)


# ============================================================
# KITCHEN CLASS
# ============================================================

class Kitchen:

    def __init__(self, screen):

        self.screen = screen


        # ====================================================
        # ====================================================
        # CHEF DISPLAY SIZE
        # ====================================================
        # ====================================================

        self.chef_max_width = 95

        self.chef_max_height = 125


        # ====================================================
        # ====================================================
        # WORK TABLE DISPLAY SIZE
        # ====================================================
        # ====================================================

        self.work_table_max_width = 165

        self.work_table_max_height = 165


        # ====================================================
        # ====================================================
        # LOAD CHEF STATES
        # ====================================================
        #
        # shef1.png
        # shef2.png
        # shef3.png
        #
        # ====================================================

        self.chef_states = [

            self.load_image(
                os.path.join(
                    SHEF_DIR,
                    "shef1.png"
                )
            ),

            self.load_image(
                os.path.join(
                    SHEF_DIR,
                    "shef2.png"
                )
            ),

            self.load_image(
                os.path.join(
                    SHEF_DIR,
                    "shef3.png"
                )
            )

        ]


        # ====================================================
        # ====================================================
        # LOAD WORK TABLE STATES
        # ====================================================
        #
        # state1.png
        # state2.png
        # state3.png
        #
        # ====================================================

        self.work_table_states = [

            self.load_image(
                os.path.join(
                    WORK_TABLE_DIR,
                    "state1.png"
                )
            ),

            self.load_image(
                os.path.join(
                    WORK_TABLE_DIR,
                    "state2.png"
                )
            ),

            self.load_image(
                os.path.join(
                    WORK_TABLE_DIR,
                    "state3.png"
                )
            )

        ]


        # ====================================================
        # ====================================================
        # SCALE CHEF STATES
        # ====================================================
        # ====================================================

        self.chef_states = [

            self.fit_image(
                image,
                self.chef_max_width,
                self.chef_max_height
            )

            for image in self.chef_states

        ]


        # ====================================================
        # ====================================================
        # SCALE WORK TABLE STATES
        # ====================================================
        # ====================================================

        self.work_table_states = [

            self.fit_image(
                image,
                self.work_table_max_width,
                self.work_table_max_height
            )

            for image in self.work_table_states

        ]


        # ====================================================
        # ====================================================
        # KITCHEN POSITION
        # ====================================================
        #
        # ONE chef + ONE work table.
        #
        # These are CENTER positions.
        #
        # The pair has been moved slightly RIGHT so that
        # the work table reaches the right-side cupboards.
        #
        # ====================================================


        # ====================================================
        # CHEF POSITION
        # ====================================================

        self.chef_position = (
            1000,
            160
        )


        # ====================================================
        # WORK TABLE POSITION
        # ====================================================

        self.work_table_position = (
            1000,
            240
        )


        # ====================================================
        # ====================================================
        # ANIMATION
        # ====================================================
        # ====================================================
        #
        # state1
        #    ↓
        # state2
        #    ↓
        # state3
        #    ↓
        # state1
        #    ↓
        #   LOOP
        #
        # ====================================================

        self.current_frame = 0

        self.animation_timer = 0

        self.animation_frame_time = 500


        # ====================================================
        # DEBUG INFORMATION
        # ====================================================

        print()

        print(
            "========================================"
        )

        print(
            "KITCHEN MODULE LOADED"
        )

        print(
            "========================================"
        )

        print()

        print(
            "Chef directory:"
        )

        print(
            SHEF_DIR
        )

        print()

        print(
            "Work table directory:"
        )

        print(
            WORK_TABLE_DIR
        )

        print()

        print(
            "Kitchen positions:"
        )

        print(
            f"Chef: {self.chef_position}"
        )

        print(
            f"Work Table: {self.work_table_position}"
        )

        print()

        print(
            "Layer order:"
        )

        print(
            "FLOOR -> CHEF -> WORK TABLE"
        )

        print()


    # ========================================================
    # ========================================================
    # LOAD IMAGE
    # ========================================================
    # ========================================================

    def load_image(
        self,
        path
    ):

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()


            print(
                f"[Kitchen] Loaded: "
                f"{os.path.basename(path)}"
            )


            print(
                f"[Kitchen] Size: "
                f"{image.get_width()} x "
                f"{image.get_height()}"
            )


            return image


        except FileNotFoundError:

            print()

            print(
                "========================================"
            )

            print(
                "KITCHEN ASSET NOT FOUND"
            )

            print(
                "========================================"
            )

            print()

            print(
                "Missing file:"
            )

            print(
                path
            )

            print()

            print(
                "Please check the asset path."
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
                "ERROR LOADING KITCHEN ASSET"
            )

            print(
                "========================================"
            )

            print()

            print(
                "File:"
            )

            print(
                path
            )

            print()

            print(
                "Pygame error:"
            )

            print(
                e
            )

            print()

            pygame.quit()

            sys.exit()


    # ========================================================
    # ========================================================
    # FIT IMAGE
    # ========================================================
    # ========================================================
    #
    # Keeps original aspect ratio.
    #
    # ========================================================

    def fit_image(
        self,
        image,
        max_width,
        max_height
    ):

        original_width = image.get_width()

        original_height = image.get_height()


        width_scale = (
            max_width /
            original_width
        )


        height_scale = (
            max_height /
            original_height
        )


        # ----------------------------------------------------
        # Keep original proportions
        # ----------------------------------------------------

        scale = min(
            width_scale,
            height_scale
        )


        new_width = int(
            original_width *
            scale
        )


        new_height = int(
            original_height *
            scale
        )


        return pygame.transform.smoothscale(
            image,
            (
                new_width,
                new_height
            )
        )


    # ========================================================
    # ========================================================
    # UPDATE
    # ========================================================
    # ========================================================

    def update(
        self,
        dt
    ):

        self.animation_timer += dt


        # ----------------------------------------------------
        # Move to next frame
        # ----------------------------------------------------

        if (
            self.animation_timer
            >= self.animation_frame_time
        ):

            self.animation_timer -= (
                self.animation_frame_time
            )


            self.current_frame += 1


            # ------------------------------------------------
            # Loop back to first frame
            # ------------------------------------------------

            if (
                self.current_frame
                >= len(self.chef_states)
            ):

                self.current_frame = 0


    # ========================================================
    # ========================================================
    # DRAW CENTERED IMAGE
    # ========================================================
    # ========================================================

    def draw_centered(
        self,
        image,
        position
    ):

        x, y = position


        draw_x = (
            x
            - image.get_width() // 2
        )


        draw_y = (
            y
            - image.get_height() // 2
        )


        self.screen.blit(
            image,
            (
                draw_x,
                draw_y
            )
        )


    # ========================================================
    # ========================================================
    # DRAW
    # ========================================================
    # ========================================================
    #
    # IMPORTANT Z-ORDER:
    #
    #      FLOOR
    #        ↓
    #      CHEF
    #        ↓
    #      WORK TABLE
    #
    # Chef is drawn first.
    #
    # Work table is drawn second.
    #
    # ========================================================

    def draw(self):

        # ====================================================
        # CURRENT CHEF FRAME
        # ====================================================

        current_chef = self.chef_states[
            self.current_frame
        ]


        # ====================================================
        # CURRENT WORK TABLE FRAME
        # ====================================================

        current_work_table = (
            self.work_table_states[
                self.current_frame
            ]
        )


        # ====================================================
        # CHEF
        # ====================================================

        self.draw_centered(
            current_chef,
            self.chef_position
        )


        # ====================================================
        # WORK TABLE / BENCH
        # ====================================================

        self.draw_centered(
            current_work_table,
            self.work_table_position
        )


    # ========================================================
    # ========================================================
    # POSITION CONTROL
    # ========================================================
    # ========================================================

    def set_chef_position(
        self,
        x,
        y
    ):

        self.chef_position = (
            x,
            y
        )


    # ========================================================
    # SET WORK TABLE POSITION
    # ========================================================

    def set_work_table_position(
        self,
        x,
        y
    ):

        self.work_table_position = (
            x,
            y
        )