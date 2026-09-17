import pygame
import os
import random


# ============================================================
# CUSTOMER QUEUE
# ============================================================
#
# Handles:
#
#   - Customers waiting in queue
#   - Still / Intermediate / Closed blinking animation
#   - Automatic transparent-space cropping
#   - Customer resizing
#   - Queue positioning
#   - Adding customers to the BACK
#   - Removing customers from the FRONT
#   - Correct front-to-back sprite layering
#
#
# ASSET STRUCTURE:
#
# assets/
#   customers/
#
#       customer_1/
#           still.png
#           intermediate.png
#           closed.png
#
#       customer_2/
#           still.png
#           intermediate.png
#           closed.png
#
#       customer_3/
#           still.png
#           intermediate.png
#           closed.png
#
#       customer_4/
#           still.png
#           intermediate.png
#           closed.png
#
#       customer_5/
#           still.png
#           intermediate.png
#           closed.png
#
#       customer_6/
#           still.png
#           intermediate.png
#           closed.png
#
#
# CUSTOMER TYPES:
#
#   1 = customer_1
#   2 = customer_2
#   3 = customer_3
#   4 = customer_4
#   5 = customer_5
#   6 = customer_6
#
# ============================================================


# ============================================================
# CUSTOMER DISPLAY SIZE
# ============================================================

CUSTOMER_BASE_WIDTH = 110

CUSTOMER_BASE_HEIGHT = 152


# ============================================================
# QUEUE POSITION
# ============================================================

DEFAULT_FRONT_Y = 190

DEFAULT_QUEUE_X = 100

QUEUE_HORIZONTAL_OFFSET = 30

QUEUE_VERTICAL_OFFSET = 200


# ============================================================
# QUEUE SPACING
# ============================================================

DEFAULT_SPACING_Y = 88


# ============================================================
# BLINK SETTINGS
# ============================================================

BLINK_MIN_DELAY = 2.0

BLINK_MAX_DELAY = 5.0

INTERMEDIATE_DURATION = 0.07

CLOSED_DURATION = 0.09


# ============================================================
# CUSTOMER TYPES
# ============================================================
#
# All supported customer sprite folders.
#
# ============================================================

AVAILABLE_CUSTOMER_TYPES = {

    1: "customer_1",

    2: "customer_2",

    3: "customer_3",

    4: "customer_4",

    5: "customer_5",

    6: "customer_6"

}


# ============================================================
# QUEUE CUSTOMER
# ============================================================


class QueueCustomer:

    """
    Represents one customer currently waiting in the queue.
    """

    def __init__(
        self,
        customer_folder,
        x,
        y,
        scale=1.0,
        max_width=CUSTOMER_BASE_WIDTH,
        max_height=CUSTOMER_BASE_HEIGHT,
        blink_enabled=True
    ):

        # ====================================================
        # BASIC INFORMATION
        # ====================================================

        self.customer_folder = customer_folder

        self.x = x

        self.y = y

        self.scale = scale

        self.max_width = max_width

        self.max_height = max_height

        self.blink_enabled = blink_enabled


        # ====================================================
        # CUSTOMER ID
        # ====================================================

        self.customer_id = None


        # ====================================================
        # CUSTOMER TYPE
        # ====================================================

        self.customer_type = None


        # ====================================================
        # ANIMATION STATE
        # ====================================================

        self.animation_state = "still"

        self.animation_timer = 0.0

        self.blink_timer = 0.0


        # ====================================================
        # RANDOM BLINK TIMING
        # ====================================================

        self.next_blink_time = random.uniform(
            BLINK_MIN_DELAY,
            BLINK_MAX_DELAY
        )


        # ====================================================
        # BLINK DURATIONS
        # ====================================================

        self.intermediate_duration = (
            INTERMEDIATE_DURATION
        )

        self.closed_duration = (
            CLOSED_DURATION
        )


        # ====================================================
        # IMAGE STORAGE
        # ====================================================

        self.images = {}


        # ====================================================
        # LOAD IMAGES
        # ====================================================

        self._load_images()


        # ====================================================
        # INITIAL FRAME
        # ====================================================

        self.image = self.images["still"]


        # ====================================================
        # INITIAL RECT
        # ====================================================

        self.rect = self.image.get_rect(
            center=(
                self.x,
                self.y
            )
        )


    # ========================================================
    # LOAD IMAGES
    # ========================================================

    def _load_images(self):

        states = [
            "still",
            "intermediate",
            "closed"
        ]

        loaded_images = {}


        # ====================================================
        # LOAD ALL AVAILABLE FRAMES
        # ====================================================

        for state in states:

            path = os.path.join(
                self.customer_folder,
                f"{state}.png"
            )


            # ------------------------------------------------
            # CHECK FILE
            # ------------------------------------------------

            if not os.path.exists(path):

                print(
                    "[QUEUE WARNING] "
                    f"Missing customer image: {path}"
                )

                continue


            # ------------------------------------------------
            # LOAD IMAGE
            # ------------------------------------------------

            try:

                image = pygame.image.load(
                    path
                ).convert_alpha()

            except pygame.error as e:

                print(
                    "[QUEUE WARNING] "
                    f"Could not load image: {path}"
                )

                print(e)

                continue


            loaded_images[state] = image


        # ====================================================
        # STILL IS REQUIRED
        # ====================================================

        if "still" not in loaded_images:

            raise FileNotFoundError(
                "Customer queue requires still.png:\n"
                f"{self.customer_folder}"
            )


        # ====================================================
        # FALLBACK FRAMES
        # ====================================================

        if "intermediate" not in loaded_images:

            loaded_images["intermediate"] = (
                loaded_images["still"]
            )


        if "closed" not in loaded_images:

            loaded_images["closed"] = (
                loaded_images["still"]
            )


        # ====================================================
        # COMMON BOUNDING RECTANGLE
        # ====================================================
        #
        # One common crop is used for all animation frames.
        #
        # This keeps the customer anchored while blinking.
        #
        # ====================================================

        bounding_rect = (
            self._get_common_bounding_rect(
                loaded_images
            )
        )


        # ====================================================
        # CROP + RESIZE
        # ====================================================

        for state in states:

            image = loaded_images[state]


            # ------------------------------------------------
            # Make sure crop is inside this particular image.
            # ------------------------------------------------

            safe_rect = bounding_rect.clip(
                image.get_rect()
            )


            # ------------------------------------------------
            # Crop transparent space
            # ------------------------------------------------

            cropped = image.subsurface(
                safe_rect
            ).copy()


            # ------------------------------------------------
            # Resize visible character
            # ------------------------------------------------

            cropped = self._fit_customer(
                cropped
            )


            self.images[state] = cropped


    # ========================================================
    # COMMON BOUNDING RECTANGLE
    # ========================================================

    def _get_common_bounding_rect(
        self,
        images
    ):

        combined_rect = None


        # ====================================================
        # FIND UNION OF VISIBLE PIXELS
        # ====================================================

        for image in images.values():

            rect = image.get_bounding_rect(
                min_alpha=1
            )


            # ------------------------------------------------
            # Ignore fully transparent images
            # ------------------------------------------------

            if (
                rect.width <= 0
                or
                rect.height <= 0
            ):

                continue


            # ------------------------------------------------
            # First rectangle
            # ------------------------------------------------

            if combined_rect is None:

                combined_rect = rect.copy()

                continue


            # ------------------------------------------------
            # Expand common rectangle
            # ------------------------------------------------

            combined_rect.union_ip(
                rect
            )


        # ====================================================
        # SAFETY FALLBACK
        # ====================================================

        if combined_rect is None:

            combined_rect = (
                images["still"].get_rect()
            )


        # ====================================================
        # KEEP INSIDE REFERENCE IMAGE
        # ====================================================

        reference = images["still"]

        combined_rect = combined_rect.clip(
            reference.get_rect()
        )


        return combined_rect


    # ========================================================
    # FIT CUSTOMER
    # ========================================================

    def _fit_customer(
        self,
        image
    ):

        original_width = image.get_width()

        original_height = image.get_height()


        # ====================================================
        # SAFETY
        # ====================================================

        if (
            original_width <= 0
            or
            original_height <= 0
        ):

            return image


        # ====================================================
        # TARGET SIZE
        # ====================================================

        target_width = (
            self.max_width
            *
            self.scale
        )


        target_height = (
            self.max_height
            *
            self.scale
        )


        # ====================================================
        # PROPORTIONAL SCALE
        # ====================================================

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


        # ====================================================
        # NEW DIMENSIONS
        # ====================================================

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


        # ====================================================
        # RESIZE
        # ====================================================

        return pygame.transform.smoothscale(
            image,
            (
                new_width,
                new_height
            )
        )


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        # ====================================================
        # BLINKING DISABLED
        # ====================================================

        if not self.blink_enabled:

            return


        # ====================================================
        # STILL
        # ====================================================

        if self.animation_state == "still":

            self.animation_timer += dt


            if (
                self.animation_timer
                >=
                self.next_blink_time
            ):

                self.animation_timer = 0.0

                self.blink_timer = 0.0

                self.animation_state = (
                    "intermediate"
                )

                self.image = (
                    self.images["intermediate"]
                )


        # ====================================================
        # INTERMEDIATE
        # ====================================================

        elif (
            self.animation_state
            ==
            "intermediate"
        ):

            self.blink_timer += dt


            if (
                self.blink_timer
                >=
                self.intermediate_duration
            ):

                self.blink_timer = 0.0

                self.animation_state = (
                    "closed"
                )

                self.image = (
                    self.images["closed"]
                )


        # ====================================================
        # CLOSED
        # ====================================================

        elif (
            self.animation_state
            ==
            "closed"
        ):

            self.blink_timer += dt


            if (
                self.blink_timer
                >=
                self.closed_duration
            ):

                self.animation_state = (
                    "still"
                )

                self.animation_timer = 0.0

                self.blink_timer = 0.0


                # --------------------------------------------
                # RANDOMIZE NEXT BLINK
                # --------------------------------------------

                self.next_blink_time = random.uniform(
                    BLINK_MIN_DELAY,
                    BLINK_MAX_DELAY
                )


                self.image = (
                    self.images["still"]
                )


        # ====================================================
        # UPDATE RECT
        # ====================================================

        self.rect = self.image.get_rect(
            center=(
                self.x,
                self.y
            )
        )


    # ========================================================
    # SET POSITION
    # ========================================================

    def set_position(
        self,
        x,
        y
    ):

        self.x = x

        self.y = y


        self.rect = self.image.get_rect(
            center=(
                self.x,
                self.y
            )
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):

        surface.blit(
            self.image,
            self.rect
        )


# ============================================================
# CUSTOMER QUEUE MANAGER
# ============================================================


class CustomerQueue:

    """
    Controls the complete waiting queue.


    ===========================================================
    QUEUE ORDER
    ===========================================================

        customers[0]
            = FRONT

        customers[1]
            = SECOND

        customers[2]
            = THIRD

        customers[-1]
            = BACK / NEWEST


    ===========================================================
    POSITIONING
    ===========================================================

    The queue extends DOWNWARD:

        FRONT
          ↓
        SECOND
          ↓
        THIRD
          ↓
        BACK


    ===========================================================
    LAYERING
    ===========================================================

    Because customers are physically arranged from TOP to
    BOTTOM, the customer farther DOWN the screen should be
    visually closer to the viewer.

    Therefore:

        FRONT / TOP
            ↓
        SECOND
            ↓
        THIRD
            ↓
        BACK / BOTTOM


    Correct drawing order:

        FRONT
        SECOND
        THIRD
        BACK


    Pygame draws later sprites on top.

    Therefore:

        BACK / BOTTOM = highest visual layer
        FRONT / TOP    = lowest visual layer


    ===========================================================
    CUSTOMER TYPES
    ===========================================================

    Supported customer types:

        1 = customer_1
        2 = customer_2
        3 = customer_3
        4 = customer_4
        5 = customer_5
        6 = customer_6


    ===========================================================
    ADDING
    ===========================================================

    New customers are ALWAYS appended to the BACK.


    ===========================================================
    REMOVING
    ===========================================================

    The FRONT customer is always customers[0].
    """

    def __init__(
        self,
        assets_root,
        queue_x,
        front_y=DEFAULT_FRONT_Y,
        spacing_y=DEFAULT_SPACING_Y,
        customer_scale=1.0,
        max_customers=6,
        customer_max_width=CUSTOMER_BASE_WIDTH,
        customer_max_height=CUSTOMER_BASE_HEIGHT
    ):

        # ====================================================
        # PATHS
        # ====================================================

        self.assets_root = assets_root

        self.customers_root = os.path.join(
            assets_root,
            "customers"
        )


        # ====================================================
        # QUEUE X POSITION
        # ====================================================

        self.queue_x = (
            queue_x
            +
            QUEUE_HORIZONTAL_OFFSET
        )


        # ====================================================
        # QUEUE Y POSITION
        # ====================================================

        self.front_y = (
            front_y
            +
            QUEUE_VERTICAL_OFFSET
        )


        # ====================================================
        # SPACING
        # ====================================================

        self.spacing_y = spacing_y


        # ====================================================
        # CUSTOMER SIZE
        # ====================================================

        self.customer_scale = (
            customer_scale
        )

        self.customer_max_width = (
            customer_max_width
        )

        self.customer_max_height = (
            customer_max_height
        )


        # ====================================================
        # MAXIMUM QUEUE SIZE
        # ====================================================

        self.max_customers = max_customers


        # ====================================================
        # CUSTOMER LIST
        # ====================================================

        self.customers = []


        # ====================================================
        # UNIQUE CUSTOMER ID
        # ====================================================

        self.next_customer_id = 0


    # ========================================================
    # ADD CUSTOMER
    # ========================================================

    def add_customer(
        self,
        customer_type=1
    ):

        # ====================================================
        # QUEUE CAPACITY
        # ====================================================

        if (
            len(self.customers)
            >=
            self.max_customers
        ):

            print(
                "[QUEUE] Queue is full."
            )

            return None


        # ====================================================
        # CUSTOMER TYPE VALIDATION
        # ====================================================

        if customer_type not in AVAILABLE_CUSTOMER_TYPES:

            print(
                "[QUEUE WARNING] "
                f"Unknown customer type: {customer_type}"
            )

            print(
                "[QUEUE] Available customer types: "
                f"{list(AVAILABLE_CUSTOMER_TYPES.keys())}"
            )

            return None


        # ====================================================
        # CUSTOMER FOLDER
        # ====================================================

        customer_folder_name = (
            AVAILABLE_CUSTOMER_TYPES[
                customer_type
            ]
        )


        customer_folder = os.path.join(
            self.customers_root,
            customer_folder_name
        )


        # ====================================================
        # CHECK FOLDER
        # ====================================================

        if not os.path.isdir(
            customer_folder
        ):

            print(
                "[QUEUE WARNING] "
                "Customer folder not found:"
            )

            print(
                customer_folder
            )

            return None


        # ====================================================
        # BACK INDEX
        # ====================================================

        queue_index = len(
            self.customers
        )


        # ====================================================
        # CALCULATE Y
        # ====================================================

        customer_y = (
            self.front_y
            +
            (
                queue_index
                *
                self.spacing_y
            )
        )


        # ====================================================
        # CREATE CUSTOMER
        # ====================================================

        customer = QueueCustomer(

            customer_folder=(
                customer_folder
            ),

            x=(
                self.queue_x
            ),

            y=(
                customer_y
            ),

            scale=(
                self.customer_scale
            ),

            max_width=(
                self.customer_max_width
            ),

            max_height=(
                self.customer_max_height
            ),

            blink_enabled=True
        )


        # ====================================================
        # ASSIGN CUSTOMER TYPE
        # ====================================================

        customer.customer_type = (
            customer_type
        )


        # ====================================================
        # ASSIGN UNIQUE ID
        # ====================================================

        customer.customer_id = (
            self.next_customer_id
        )

        self.next_customer_id += 1


        # ====================================================
        # ADD TO BACK
        # ====================================================

        self.customers.append(
            customer
        )


        # ====================================================
        # DEBUG
        # ====================================================

        print(
            f"[QUEUE] Customer "
            f"{customer.customer_id} "
            f"(Type {customer.customer_type}) "
            f"joined BACK."
        )

        print(
            f"[QUEUE] Sprite folder: "
            f"{customer_folder_name}"
        )

        print(
            f"[QUEUE] Position: "
            f"({customer.x}, {customer.y})"
        )

        print(
            f"[QUEUE] Queue size: "
            f"{len(self.customers)}"
        )


        return customer


    # ========================================================
    # REMOVE FRONT CUSTOMER
    # ========================================================

    def remove_front_customer(
        self
    ):

        if not self.customers:

            return None


        # ====================================================
        # REMOVE FIRST CUSTOMER
        # ====================================================

        customer = self.customers.pop(
            0
        )


        print(
            f"[QUEUE] Customer "
            f"{customer.customer_id} "
            f"(Type {customer.customer_type}) "
            f"left FRONT."
        )


        # ====================================================
        # MOVE REMAINING CUSTOMERS
        # ====================================================

        self._reposition()


        return customer


    # ========================================================
    # REMOVE SPECIFIC CUSTOMER
    # ========================================================

    def remove_customer(
        self,
        customer
    ):

        if (
            customer
            not in
            self.customers
        ):

            return None


        self.customers.remove(
            customer
        )


        self._reposition()


        return customer


    # ========================================================
    # REPOSITION QUEUE
    # ========================================================

    def _reposition(
        self
    ):

        for index, customer in enumerate(
            self.customers
        ):

            new_y = (
                self.front_y
                +
                (
                    index
                    *
                    self.spacing_y
                )
            )


            customer.set_position(
                self.queue_x,
                new_y
            )


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        for customer in self.customers:

            customer.update(
                dt
            )


    # ========================================================
    # DRAW
    # ========================================================
    #
    # CRITICAL LAYERING
    #
    # Queue:
    #
    #     [FRONT, SECOND, THIRD, BACK]
    #
    #
    # Draw order:
    #
    #     FRONT
    #     SECOND
    #     THIRD
    #     BACK
    #
    #
    # The BACK is drawn last and therefore appears on the
    # highest visual layer.
    #
    # ========================================================

    def draw(
        self,
        surface
    ):

        # ----------------------------------------------------
        # DO NOT reverse this list.
        # ----------------------------------------------------

        for customer in self.customers:

            customer.draw(
                surface
            )


    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self
    ):

        return len(
            self.customers
        )


    # ========================================================
    # EMPTY
    # ========================================================

    def is_empty(
        self
    ):

        return (
            len(
                self.customers
            )
            ==
            0
        )


    # ========================================================
    # FULL
    # ========================================================

    def is_full(
        self
    ):

        return (
            len(
                self.customers
            )
            >=
            self.max_customers
        )


    # ========================================================
    # GET FRONT CUSTOMER
    # ========================================================

    def get_front_customer(
        self
    ):

        if not self.customers:

            return None


        return self.customers[0]


    # ========================================================
    # GET BACK CUSTOMER
    # ========================================================

    def get_back_customer(
        self
    ):

        if not self.customers:

            return None


        return self.customers[-1]


    # ========================================================
    # GET ALL CUSTOMERS
    # ========================================================

    def get_customers(
        self
    ):

        return self.customers


# ============================================================
# END OF QUEUE.PY
# ============================================================