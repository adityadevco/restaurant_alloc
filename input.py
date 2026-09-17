import pygame
import os


# ============================================================
# WAITING PEOPLE INPUT + RL AGENT MESSAGE
# ============================================================
#
# METRIUS EATS
#
# Bottom control / communication panel.
#
# The panel has TWO MAIN SIDES:
#
#
# LEFT
# ────────────────────────────────────────────────────────────
#
#     1. NEXT WAITING PEOPLE
#        User enters group sizes.
#
#     2. WAITING QUEUE
#        Displays the actual waiting array.
#
#
# RIGHT
# ────────────────────────────────────────────────────────────
#
#     RL AGENT
#
# Displays what the restaurant agent is currently deciding.
#
#
# IMPORTANT:
#
# This component DOES NOT decide which table to use.
#
# It only:
#
#     - accepts group sizes
#     - stores the waiting queue
#     - displays the queue
#     - displays agent messages
#     - notifies main.py when a new group is added
#
#
# The actual table-allocation logic belongs in main.py /
# the restaurant environment.
#
# ============================================================


# ============================================================
# COLORS
# ============================================================

BG_COLOR = (
    18,
    27,
    42
)


PANEL_COLOR = (
    22,
    32,
    48
)


INPUT_COLOR = (
    12,
    21,
    34
)


BORDER_COLOR = (
    69,
    108,
    145
)


BORDER_ACTIVE = (
    105,
    163,
    210
)


DIVIDER_COLOR = (
    55,
    82,
    108
)


TEXT_COLOR = (
    235,
    235,
    225
)


MUTED_TEXT = (
    145,
    157,
    170
)


TITLE_COLOR = (
    244,
    211,
    158
)


ACCENT_COLOR = (
    82,
    150,
    194
)


CURSOR_COLOR = (
    240,
    220,
    170
)


SELECTED_COLOR = (
    25,
    39,
    57
)


SCROLL_BG = (
    15,
    23,
    35
)


SCROLL_BAR = (
    83,
    117,
    148
)


AGENT_BORDER = (
    69,
    108,
    145
)


AGENT_ACCENT = (
    105,
    163,
    210
)


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_WIDTH = 1200

DEFAULT_HEIGHT = 116

DEFAULT_X = 0

DEFAULT_Y = 759


# ============================================================
# FONT SIZES
# ============================================================

TITLE_SIZE = 13

FONT_SIZE = 18

SMALL_SIZE = 12

AGENT_MESSAGE_SIZE = 18


# ============================================================
# LAYOUT
# ============================================================

LEFT_WIDTH_RATIO = 0.62

RIGHT_WIDTH_RATIO = 0.38

INPUT_WIDTH_RATIO = 0.50

QUEUE_WIDTH_RATIO = 0.50


# ============================================================
# QUEUE DISPLAY
# ============================================================

LINE_HEIGHT = 25

MAX_VISIBLE_ENTRIES = 3


# ============================================================
# GROUP SIZE LIMIT
# ============================================================
#
# The restaurant accepts a maximum of 6 people per group.
#
# Any value above this limit is rejected.
#
# ============================================================

MAX_GROUP_SIZE = 6


# ============================================================
# FONT LOADER
# ============================================================

def load_pixel_font(size):

    """
    Attempts to load a pixel-style font from:

        assets/fonts/

    Falls back to Consolas.
    """

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )


    font_directories = [

        os.path.join(
            base_dir,
            "assets",
            "fonts"
        ),

        os.path.join(
            base_dir,
            "assets"
        )

    ]


    preferred_names = [

        "PixelOperator.ttf",

        "PixelOperator-Bold.ttf",

        "PressStart2P.ttf",

        "PressStart2P-Regular.ttf",

        "Minecraft.ttf",

        "monogram.ttf",

        "pixel.ttf",

        "PixelFont.ttf"

    ]


    # ========================================================
    # SEARCH KNOWN FONT NAMES
    # ========================================================

    for directory in font_directories:

        if not os.path.exists(
            directory
        ):

            continue


        for font_name in preferred_names:

            path = os.path.join(
                directory,
                font_name
            )


            if os.path.isfile(
                path
            ):

                try:

                    return pygame.font.Font(
                        path,
                        size
                    )

                except pygame.error:

                    pass


    # ========================================================
    # SEARCH ALL FONT FILES
    # ========================================================

    fonts_directory = os.path.join(
        base_dir,
        "assets",
        "fonts"
    )


    if os.path.exists(
        fonts_directory
    ):

        for root, dirs, files in os.walk(
            fonts_directory
        ):

            for file in files:

                if file.lower().endswith(
                    (
                        ".ttf",
                        ".otf"
                    )
                ):

                    path = os.path.join(
                        root,
                        file
                    )


                    try:

                        return pygame.font.Font(
                            path,
                            size
                        )

                    except pygame.error:

                        pass


    # ========================================================
    # FALLBACK
    # ========================================================

    return pygame.font.SysFont(
        "consolas",
        size
    )


# ============================================================
# WAITING PEOPLE INPUT CLASS
# ============================================================

class WaitingPeopleInput:

    """
    Bottom waiting-group input and agent message component.

    Layout:

        ┌───────────────────────────────────────────────────────┐
        │                                                       │
        │  INPUT             QUEUE       │     AGENT            │
        │                                                       │
        └───────────────────────────────────────────────────────┘


    Example:

        Input:

            4 ENTER
            3 ENTER
            6 ENTER


        Queue:

            [4, 3, 6]


        Agent:

            "I will assign 6 people to T5."


    IMPORTANT:

    The component does not perform table allocation.

    When a new group is entered, the optional callback:

        on_group_added(group_size)

    is called.

    main.py can use that callback to invoke the baseline
    restaurant agent.
    """


    def __init__(
        self,
        x=DEFAULT_X,
        y=DEFAULT_Y,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        on_group_added=None
    ):

        # ====================================================
        # MAIN RECT
        # ====================================================

        self.x = x

        self.y = y

        self.width = width

        self.height = height


        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )


        # ====================================================
        # GROUP ADDED CALLBACK
        # ====================================================
        #
        # main.py can provide:
        #
        #     on_group_added(group_size)
        #
        # This keeps input.py independent from the restaurant
        # allocation system.
        #
        # ====================================================

        self.on_group_added = (
            on_group_added
        )


        # ====================================================
        # MAIN LEFT / RIGHT SPLIT
        # ====================================================

        self.left_width = int(
            self.width
            *
            LEFT_WIDTH_RATIO
        )


        self.right_width = (
            self.width
            -
            self.left_width
        )


        self.left_rect = pygame.Rect(
            self.x,
            self.y,
            self.left_width,
            self.height
        )


        self.right_rect = pygame.Rect(
            self.x
            +
            self.left_width,
            self.y,
            self.right_width,
            self.height
        )


        # ====================================================
        # LEFT SIDE SUBDIVISION
        # ====================================================

        self.input_width = int(
            self.left_width
            *
            INPUT_WIDTH_RATIO
        )


        self.queue_width = (
            self.left_width
            -
            self.input_width
        )


        self.input_rect = pygame.Rect(
            self.x,
            self.y,
            self.input_width,
            self.height
        )


        self.queue_rect = pygame.Rect(
            self.x
            +
            self.input_width,
            self.y,
            self.queue_width,
            self.height
        )


        # ====================================================
        # WAITING GROUP ARRAY
        # ====================================================

        self.waiting_groups = []


        # ====================================================
        # CURRENT TEXT INPUT
        # ====================================================

        self.current_input = ""


        # ====================================================
        # SELECTED QUEUE ITEM
        # ====================================================

        self.selected_index = -1


        # ====================================================
        # SCROLL
        # ====================================================

        self.scroll_offset = 0


        # ====================================================
        # INPUT ACTIVE
        # ====================================================

        self.active = False


        # ====================================================
        # CURSOR
        # ====================================================

        self.cursor_visible = True

        self.cursor_timer = 0

        self.cursor_blink_time = 500


        # ====================================================
        # AGENT MESSAGE
        # ====================================================

        self.agent_message = (
            "Waiting for the next allocation..."
        )


        self.agent_message_active = False


        # ====================================================
        # AGENT DECISION DATA
        # ====================================================

        self.agent_group = None

        self.agent_table = None


        # ====================================================
        # FONTS
        # ====================================================

        self.title_font = load_pixel_font(
            TITLE_SIZE
        )


        self.font = load_pixel_font(
            FONT_SIZE
        )


        self.small_font = load_pixel_font(
            SMALL_SIZE
        )


        self.agent_font = load_pixel_font(
            AGENT_MESSAGE_SIZE
        )


        # ====================================================
        # PLACEHOLDER
        # ====================================================

        self.placeholder = (
            "Enter group size..."
        )


    # ========================================================
    # SET GROUP CALLBACK
    # ========================================================

    def set_group_added_callback(
        self,
        callback
    ):

        """
        Sets or replaces the callback used when a new group
        is successfully added.

        Example:

            waiting_input.set_group_added_callback(
                handle_new_group
            )
        """

        self.on_group_added = callback


    # ========================================================
    # NOTIFY GROUP ADDED
    # ========================================================

    def _notify_group_added(
        self,
        group_size
    ):

        """
        Notifies the restaurant controller that a new group
        has entered the waiting queue.
        """

        if self.on_group_added is None:

            return


        try:

            self.on_group_added(
                group_size
            )

        except Exception as e:

            print()
            print(
                "[WAITING INPUT ERROR] "
                "Group-added callback failed."
            )

            print(
                e
            )

            print()


    # ========================================================
    # WAITING ARRAY
    # ========================================================

    def get_waiting_people(
        self
    ):

        """
        Returns a COPY of the waiting array.

        Example:

            [5, 2, 3]
        """

        return self.waiting_groups.copy()


    # ========================================================

    def get_array(
        self
    ):

        """
        Alias for get_waiting_people().
        """

        return self.waiting_groups.copy()


    # ========================================================

    def get_queue(
        self
    ):

        """
        Returns the current waiting queue.
        """

        return self.waiting_groups.copy()


    # ========================================================
    # ADD GROUP
    # ========================================================

    def add_group(
        self,
        group_size
    ):

        """
        Adds a group directly to the queue.

        The maximum allowed group size is MAX_GROUP_SIZE
        (currently 6 people).

        Example:

            add_group(6)

        Queue:

            [5, 2, 3, 6]

        After successfully adding the group, the callback
        supplied by main.py is called.
        """

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return False


        if (
            group_size <= 0
            or
            group_size > MAX_GROUP_SIZE
        ):

            return False


        # ====================================================
        # ADD TO WAITING QUEUE
        # ====================================================

        self.waiting_groups.append(
            group_size
        )


        # ====================================================
        # SELECT NEWEST GROUP
        # ====================================================

        self.selected_index = (
            len(
                self.waiting_groups
            )
            -
            1
        )


        self._ensure_selected_visible()


        # ====================================================
        # NOTIFY MAIN CONTROLLER
        # ====================================================

        self._notify_group_added(
            group_size
        )


        return True


    # ========================================================
    # REMOVE GROUP
    # ========================================================

    def remove_group(
        self,
        index=None
    ):

        """
        Removes a waiting group.

        If index is None,
        the last group is removed.
        """

        if not self.waiting_groups:

            return


        if index is None:

            index = (
                len(
                    self.waiting_groups
                )
                -
                1
            )


        if (
            index < 0
            or
            index >= len(
                self.waiting_groups
            )
        ):

            return


        self.waiting_groups.pop(
            index
        )


        if not self.waiting_groups:

            self.selected_index = -1

        else:

            self.selected_index = min(
                self.selected_index,
                len(
                    self.waiting_groups
                )
                -
                1
            )


        self._clamp_scroll()


    # ========================================================
    # POP NEXT GROUP
    # ========================================================

    def pop_next_group(
        self
    ):

        """
        Removes and returns the FIRST waiting group.

        Intended for the restaurant agent.

        Example:

            [5, 2, 3]

        pop_next_group()

            returns 5

        Queue becomes:

            [2, 3]
        """

        if not self.waiting_groups:

            return None


        group = self.waiting_groups.pop(
            0
        )


        # ====================================================
        # UPDATE SELECTION
        # ====================================================

        if self.waiting_groups:

            if self.selected_index > 0:

                self.selected_index -= 1

            elif (
                self.selected_index
                >=
                len(
                    self.waiting_groups
                )
            ):

                self.selected_index = (
                    len(
                        self.waiting_groups
                    )
                    -
                    1
                )

        else:

            self.selected_index = -1


        self._clamp_scroll()


        return group


    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self
    ):

        """
        Clears the complete waiting queue.
        """

        self.waiting_groups.clear()

        self.current_input = ""

        self.selected_index = -1

        self.scroll_offset = 0


    # ========================================================
    # SET AGENT MESSAGE
    # ========================================================

    def set_agent_message(
        self,
        message
    ):

        """
        Sets the message displayed on the right side.

        Example:

            set_agent_message(
                "Checking available tables..."
            )
        """

        if message is None:

            self.agent_message = ""

        else:

            self.agent_message = str(
                message
            )


        self.agent_message_active = True


    # ========================================================
    # SET AGENT DECISION
    # ========================================================

    def set_agent_decision(
        self,
        group_size,
        table_name
    ):

        """
        Convenience function for the restaurant agent.

        Example:

            set_agent_decision(
                6,
                "T5"
            )

        Displays:

            I will assign 6 people to T5.
        """

        self.agent_group = group_size

        self.agent_table = table_name


        if group_size == 1:

            self.agent_message = (
                f"I will assign "
                f"1 person to "
                f"{table_name}."
            )

        else:

            self.agent_message = (
                f"I will assign "
                f"{group_size} people to "
                f"{table_name}."
            )


        self.agent_message_active = True


    # ========================================================
    # SET AGENT STATUS
    # ========================================================

    def set_agent_status(
        self,
        message
    ):

        """
        Updates the agent panel with a status message.

        Useful for the baseline allocation flow.

        Examples:

            "Group of 6 detected."

            "Checking available tables..."

            "T3 selected."

            "No suitable table available."
        """

        self.set_agent_message(
            message
        )


    # ========================================================
    # CLEAR AGENT MESSAGE
    # ========================================================

    def clear_agent_message(
        self
    ):

        """
        Clears the current agent decision.
        """

        self.agent_message = (
            "Waiting for the next allocation..."
        )

        self.agent_group = None

        self.agent_table = None

        self.agent_message_active = False


    # ========================================================
    # SUBMIT INPUT
    # ========================================================

    def _submit_current_input(
        self
    ):

        """
        Converts current input into an integer and adds it
        to the waiting array.
        """

        if not self.current_input:

            return


        try:

            group_size = int(
                self.current_input
            )

        except ValueError:

            self.current_input = ""

            return


        # ====================================================
        # REJECT INVALID VALUES
        # ====================================================

        if (
            group_size <= 0
            or
            group_size > MAX_GROUP_SIZE
        ):

            self.current_input = ""

            return


        # ====================================================
        # ADD GROUP
        # ====================================================

        self.waiting_groups.append(
            group_size
        )


        # ====================================================
        # SELECT LATEST ITEM
        # ====================================================

        self.selected_index = (
            len(
                self.waiting_groups
            )
            -
            1
        )


        # ====================================================
        # CLEAR INPUT
        # ====================================================

        self.current_input = ""


        # ====================================================
        # MAKE LATEST ITEM VISIBLE
        # ====================================================

        self._ensure_selected_visible()


        # ====================================================
        # CURSOR RESET
        # ====================================================

        self.cursor_visible = True

        self.cursor_timer = 0


        # ====================================================
        # NOTIFY RESTAURANT CONTROLLER
        # ====================================================

        self._notify_group_added(
            group_size
        )


    # ========================================================
    # HANDLE EVENTS
    # ========================================================

    def handle_event(
        self,
        event
    ):

        # ====================================================
        # MOUSE BUTTON
        # ====================================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            # ------------------------------------------------
            # LEFT CLICK
            # ------------------------------------------------

            if event.button == 1:

                if self.input_rect.collidepoint(
                    event.pos
                ):

                    self.active = True


                elif self.queue_rect.collidepoint(
                    event.pos
                ):

                    self.active = False

                    self._select_queue_entry(
                        event.pos
                    )


                else:

                    self.active = False


            # ------------------------------------------------
            # MOUSE WHEEL UP
            # ------------------------------------------------

            if event.button == 4:

                if self.queue_rect.collidepoint(
                    event.pos
                ):

                    self.scroll_offset -= 1

                    self._clamp_scroll()


            # ------------------------------------------------
            # MOUSE WHEEL DOWN
            # ------------------------------------------------

            elif event.button == 5:

                if self.queue_rect.collidepoint(
                    event.pos
                ):

                    self.scroll_offset += 1

                    self._clamp_scroll()


        # ====================================================
        # MOUSE WHEEL EVENT
        # ====================================================

        if event.type == pygame.MOUSEWHEEL:

            mouse_pos = pygame.mouse.get_pos()


            if self.queue_rect.collidepoint(
                mouse_pos
            ):

                self.scroll_offset -= (
                    event.y
                )

                self._clamp_scroll()


        # ====================================================
        # KEYBOARD
        # ====================================================

        if (
            event.type == pygame.KEYDOWN
            and
            self.active
        ):

            # ------------------------------------------------
            # ENTER
            # ------------------------------------------------

            if event.key == pygame.K_RETURN:

                self._submit_current_input()

                return


            # ------------------------------------------------
            # BACKSPACE
            # ------------------------------------------------

            if event.key == pygame.K_BACKSPACE:

                if (
                    pygame.key.get_mods()
                    &
                    pygame.KMOD_CTRL
                ):

                    self.current_input = ""

                elif self.current_input:

                    self.current_input = (
                        self.current_input[:-1]
                    )


                self.cursor_visible = True

                self.cursor_timer = 0

                return


            # ------------------------------------------------
            # ESCAPE
            # ------------------------------------------------

            if event.key == pygame.K_ESCAPE:

                self.current_input = ""

                self.active = False

                return


            # ------------------------------------------------
            # UP
            # ------------------------------------------------

            if event.key == pygame.K_UP:

                if self.waiting_groups:

                    if self.selected_index == -1:

                        self.selected_index = (
                            len(
                                self.waiting_groups
                            )
                            -
                            1
                        )

                    elif self.selected_index > 0:

                        self.selected_index -= 1


                    self._ensure_selected_visible()


                return


            # ------------------------------------------------
            # DOWN
            # ------------------------------------------------

            if event.key == pygame.K_DOWN:

                if self.waiting_groups:

                    if self.selected_index == -1:

                        self.selected_index = 0

                    elif self.selected_index < (
                        len(
                            self.waiting_groups
                        )
                        -
                        1
                    ):

                        self.selected_index += 1


                    self._ensure_selected_visible()


                return


            # ------------------------------------------------
            # DELETE
            # ------------------------------------------------

            if event.key == pygame.K_DELETE:

                if (
                    self.selected_index >= 0
                    and
                    self.selected_index
                    <
                    len(
                        self.waiting_groups
                    )
                ):

                    self.remove_group(
                        self.selected_index
                    )


                return


            # ------------------------------------------------
            # CTRL + A
            # ------------------------------------------------

            if (
                event.key == pygame.K_a
                and
                (
                    pygame.key.get_mods()
                    &
                    pygame.KMOD_CTRL
                )
            ):

                self.current_input = ""

                self.cursor_visible = True

                self.cursor_timer = 0

                return


            # ------------------------------------------------
            # NUMERIC INPUT
            # ------------------------------------------------

            if event.unicode:

                if event.unicode.isdigit():

                    # ------------------------------------------------
                    # GROUP SIZE LIMIT
                    # ------------------------------------------------
                    #
                    # Do not allow the user to type a value greater
                    # than MAX_GROUP_SIZE.
                    #
                    # ------------------------------------------------

                    proposed_input = (
                        self.current_input
                        +
                        event.unicode
                    )

                    try:

                        proposed_value = int(
                            proposed_input
                        )

                    except ValueError:

                        proposed_value = (
                            MAX_GROUP_SIZE + 1
                        )


                    if (
                        proposed_value
                        <=
                        MAX_GROUP_SIZE
                    ):

                        self.current_input = (
                            proposed_input
                        )


                        self.cursor_visible = True

                        self.cursor_timer = 0


    # ========================================================
    # SELECT QUEUE ENTRY
    # ========================================================

    def _select_queue_entry(
        self,
        mouse_pos
    ):

        mx, my = mouse_pos


        content_top = (
            self.queue_rect.y
            +
            34
        )


        relative_y = (
            my
            -
            content_top
        )


        if relative_y < 0:

            return


        clicked_line = (
            relative_y
            //
            LINE_HEIGHT
        )


        index = (
            clicked_line
            +
            self.scroll_offset
        )


        if (
            index >= 0
            and
            index < len(
                self.waiting_groups
            )
        ):

            self.selected_index = index

            self._ensure_selected_visible()


    # ========================================================
    # CLAMP SCROLL
    # ========================================================

    def _clamp_scroll(
        self
    ):

        max_scroll = max(
            0,
            len(
                self.waiting_groups
            )
            -
            MAX_VISIBLE_ENTRIES
        )


        self.scroll_offset = max(
            0,
            min(
                self.scroll_offset,
                max_scroll
            )
        )


    # ========================================================
    # ENSURE SELECTED VISIBLE
    # ========================================================

    def _ensure_selected_visible(
        self
    ):

        if self.selected_index < 0:

            return


        if (
            self.selected_index
            <
            self.scroll_offset
        ):

            self.scroll_offset = (
                self.selected_index
            )


        elif (
            self.selected_index
            >=
            self.scroll_offset
            +
            MAX_VISIBLE_ENTRIES
        ):

            self.scroll_offset = (
                self.selected_index
                -
                MAX_VISIBLE_ENTRIES
                +
                1
            )


        self._clamp_scroll()


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        # ----------------------------------------------------
        # Cursor blink
        # ----------------------------------------------------

        self.cursor_timer += dt


        if (
            self.cursor_timer
            >=
            self.cursor_blink_time
        ):

            self.cursor_timer = 0

            self.cursor_visible = (
                not self.cursor_visible
            )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):

        # ====================================================
        # OUTER PANEL
        # ====================================================

        pygame.draw.rect(
            surface,
            BG_COLOR,
            self.rect,
            border_radius=8
        )


        # ====================================================
        # OUTER BORDER
        # ====================================================

        pygame.draw.rect(
            surface,
            (
                BORDER_ACTIVE
                if self.active
                else BORDER_COLOR
            ),
            self.rect,
            width=3,
            border_radius=8
        )


        # ====================================================
        # INNER PANEL
        # ====================================================

        inner_rect = pygame.Rect(
            self.x + 5,
            self.y + 5,
            self.width - 10,
            self.height - 10
        )


        pygame.draw.rect(
            surface,
            PANEL_COLOR,
            inner_rect,
            width=1,
            border_radius=5
        )


        # ====================================================
        # MAIN VERTICAL DIVIDER
        # ====================================================

        divider_x = (
            self.x
            +
            self.left_width
        )


        pygame.draw.line(
            surface,
            DIVIDER_COLOR,
            (
                divider_x,
                self.y + 10
            ),
            (
                divider_x,
                self.y
                +
                self.height
                -
                10
            ),
            2
        )


        # ====================================================
        # LEFT INPUT / QUEUE DIVIDER
        # ====================================================

        left_divider_x = (
            self.x
            +
            self.input_width
        )


        pygame.draw.line(
            surface,
            DIVIDER_COLOR,
            (
                left_divider_x,
                self.y + 10
            ),
            (
                left_divider_x,
                self.y
                +
                self.height
                -
                10
            ),
            1
        )


        # ====================================================
        # DRAW INPUT
        # ====================================================

        self._draw_input_section(
            surface
        )


        # ====================================================
        # DRAW QUEUE
        # ====================================================

        self._draw_queue_section(
            surface
        )


        # ====================================================
        # DRAW AGENT
        # ====================================================

        self._draw_agent_section(
            surface
        )


    # ========================================================
    # DRAW INPUT SECTION
    # ========================================================

    def _draw_input_section(
        self,
        surface
    ):

        # ====================================================
        # TITLE
        # ====================================================

        title = self.title_font.render(
            "NEXT WAITING PEOPLE",
            True,
            TITLE_COLOR
        )


        surface.blit(
            title,
            (
                self.input_rect.x + 20,
                self.y + 9
            )
        )


        # ====================================================
        # SUBTITLE
        # ====================================================

        subtitle = self.small_font.render(
            "ADD THE NEXT GROUP",
            True,
            MUTED_TEXT
        )


        surface.blit(
            subtitle,
            (
                self.input_rect.x + 20,
                self.y + 29
            )
        )


        # ====================================================
        # INPUT BOX
        # ====================================================

        input_box = pygame.Rect(
            self.input_rect.x + 16,
            self.y + 55,
            self.input_rect.width - 32,
            43
        )


        pygame.draw.rect(
            surface,
            INPUT_COLOR,
            input_box,
            border_radius=4
        )


        pygame.draw.rect(
            surface,
            (
                BORDER_ACTIVE
                if self.active
                else BORDER_COLOR
            ),
            input_box,
            width=2,
            border_radius=4
        )


        # ====================================================
        # INPUT TEXT
        # ====================================================

        if self.current_input:

            text = self.font.render(
                self.current_input,
                True,
                TEXT_COLOR
            )

        else:

            text = self.font.render(
                self.placeholder,
                True,
                MUTED_TEXT
            )


        text_y = (
            input_box.centery
            -
            text.get_height() // 2
        )


        surface.blit(
            text,
            (
                input_box.x + 12,
                text_y
            )
        )


        # ====================================================
        # CURSOR
        # ====================================================

        if (
            self.active
            and
            self.cursor_visible
        ):

            if self.current_input:

                cursor_text = self.font.render(
                    self.current_input,
                    True,
                    TEXT_COLOR
                )


                cursor_x = (
                    input_box.x
                    +
                    12
                    +
                    cursor_text.get_width()
                    +
                    2
                )

            else:

                cursor_x = (
                    input_box.x
                    +
                    12
                )


            pygame.draw.rect(
                surface,
                CURSOR_COLOR,
                (
                    cursor_x,
                    input_box.y + 8,
                    2,
                    25
                )
            )


        # ====================================================
        # ENTER HINT
        # ====================================================

        hint = self.small_font.render(
            "ENTER = ADD",
            True,
            ACCENT_COLOR
        )


        hint_rect = hint.get_rect()


        surface.blit(
            hint,
            (
                input_box.right
                -
                hint_rect.width
                -
                10,
                input_box.bottom
                -
                hint_rect.height
                -
                5
            )
        )


    # ========================================================
    # DRAW QUEUE SECTION
    # ========================================================

    def _draw_queue_section(
        self,
        surface
    ):

        # ====================================================
        # TITLE
        # ====================================================

        title = self.title_font.render(
            "WAITING QUEUE",
            True,
            TITLE_COLOR
        )


        surface.blit(
            title,
            (
                self.queue_rect.x + 20,
                self.y + 9
            )
        )


        # ====================================================
        # ARRAY
        # ====================================================

        array_text = self.small_font.render(
            str(
                self.waiting_groups
            ),
            True,
            MUTED_TEXT
        )


        array_x = (
            self.queue_rect.right
            -
            array_text.get_width()
            -
            20
        )


        surface.blit(
            array_text,
            (
                array_x,
                self.y + 10
            )
        )


        # ====================================================
        # QUEUE BOX
        # ====================================================

        queue_box = pygame.Rect(
            self.queue_rect.x + 16,
            self.y + 34,
            self.queue_rect.width - 32,
            self.height - 44
        )


        pygame.draw.rect(
            surface,
            INPUT_COLOR,
            queue_box,
            border_radius=4
        )


        pygame.draw.rect(
            surface,
            BORDER_COLOR,
            queue_box,
            width=1,
            border_radius=4
        )


        # ====================================================
        # CLIP
        # ====================================================

        old_clip = surface.get_clip()


        surface.set_clip(
            queue_box
        )


        # ====================================================
        # EMPTY
        # ====================================================

        if not self.waiting_groups:

            empty_text = self.small_font.render(
                "No waiting groups",
                True,
                MUTED_TEXT
            )


            surface.blit(
                empty_text,
                (
                    queue_box.x + 12,
                    queue_box.y + 9
                )
            )


        # ====================================================
        # ENTRIES
        # ====================================================

        visible_start = (
            self.scroll_offset
        )


        visible_end = min(
            len(
                self.waiting_groups
            ),
            visible_start
            +
            MAX_VISIBLE_ENTRIES
        )


        for index in range(
            visible_start,
            visible_end
        ):

            line_number = (
                index
                -
                self.scroll_offset
            )


            line_y = (
                queue_box.y
                +
                5
                +
                line_number
                *
                LINE_HEIGHT
            )


            # ------------------------------------------------
            # SELECTED
            # ------------------------------------------------

            if index == self.selected_index:

                selected_rect = pygame.Rect(
                    queue_box.x + 5,
                    line_y - 2,
                    queue_box.width - 10,
                    LINE_HEIGHT
                )


                pygame.draw.rect(
                    surface,
                    SELECTED_COLOR,
                    selected_rect,
                    border_radius=3
                )


            # ------------------------------------------------
            # NUMBER
            # ------------------------------------------------

            index_text = self.small_font.render(
                f"{index + 1:02d}",
                True,
                ACCENT_COLOR
            )


            surface.blit(
                index_text,
                (
                    queue_box.x + 10,
                    line_y + 4
                )
            )


            # ------------------------------------------------
            # GROUP SIZE
            # ------------------------------------------------

            group_size = (
                self.waiting_groups[index]
            )


            group_text = self.font.render(
                str(group_size),
                True,
                TEXT_COLOR
            )


            surface.blit(
                group_text,
                (
                    queue_box.x + 45,
                    line_y
                )
            )


            # ------------------------------------------------
            # PEOPLE
            # ------------------------------------------------

            people_label = (
                "PERSON"
                if group_size == 1
                else
                "PEOPLE"
            )


            people_text = self.small_font.render(
                people_label,
                True,
                MUTED_TEXT
            )


            surface.blit(
                people_text,
                (
                    queue_box.x + 88,
                    line_y + 5
                )
            )


        # ====================================================
        # RESTORE CLIP
        # ====================================================

        surface.set_clip(
            old_clip
        )


        # ====================================================
        # SCROLLBAR
        # ====================================================

        if (
            len(
                self.waiting_groups
            )
            >
            MAX_VISIBLE_ENTRIES
        ):

            self._draw_scrollbar(
                surface,
                queue_box
            )


    # ========================================================
    # DRAW SCROLLBAR
    # ========================================================

    def _draw_scrollbar(
        self,
        surface,
        queue_box
    ):

        track_rect = pygame.Rect(
            queue_box.right - 8,
            queue_box.y + 5,
            3,
            queue_box.height - 10
        )


        pygame.draw.rect(
            surface,
            SCROLL_BG,
            track_rect,
            border_radius=2
        )


        total = len(
            self.waiting_groups
        )


        max_scroll = max(
            1,
            total
            -
            MAX_VISIBLE_ENTRIES
        )


        thumb_height = max(
            12,
            int(
                track_rect.height
                *
                MAX_VISIBLE_ENTRIES
                /
                max(
                    1,
                    total
                )
            )
        )


        thumb_y = (
            track_rect.y
            +
            int(
                (
                    track_rect.height
                    -
                    thumb_height
                )
                *
                (
                    self.scroll_offset
                    /
                    max_scroll
                )
            )
        )


        pygame.draw.rect(
            surface,
            SCROLL_BAR,
            (
                track_rect.x,
                thumb_y,
                track_rect.width,
                thumb_height
            ),
            border_radius=2
        )


    # ========================================================
    # DRAW AGENT SECTION
    # ========================================================

    def _draw_agent_section(
        self,
        surface
    ):

        # ====================================================
        # AGENT TITLE
        # ====================================================

        title = self.title_font.render(
            "RL AGENT",
            True,
            TITLE_COLOR
        )


        surface.blit(
            title,
            (
                self.right_rect.x + 20,
                self.y + 9
            )
        )


        # ====================================================
        # STATUS
        # ====================================================

        if self.agent_message_active:

            status = self.small_font.render(
                "DECISION",
                True,
                ACCENT_COLOR
            )

        else:

            status = self.small_font.render(
                "WAITING",
                True,
                MUTED_TEXT
            )


        status_rect = status.get_rect()


        surface.blit(
            status,
            (
                self.right_rect.right
                -
                status_rect.width
                -
                20,
                self.y + 10
            )
        )


        # ====================================================
        # MESSAGE BOX
        # ====================================================

        message_rect = pygame.Rect(
            self.right_rect.x + 16,
            self.y + 34,
            self.right_rect.width - 32,
            self.height - 44
        )


        pygame.draw.rect(
            surface,
            INPUT_COLOR,
            message_rect,
            border_radius=4
        )


        pygame.draw.rect(
            surface,
            (
                AGENT_ACCENT
                if self.agent_message_active
                else AGENT_BORDER
            ),
            message_rect,
            width=1,
            border_radius=4
        )


        # ====================================================
        # MESSAGE
        # ====================================================

        self._draw_wrapped_agent_message(
            surface,
            message_rect
        )


    # ========================================================
    # WRAPPED AGENT MESSAGE
    # ========================================================

    def _draw_wrapped_agent_message(
        self,
        surface,
        rect
    ):

        message = (
            self.agent_message
        )


        if not message:

            return


        # ----------------------------------------------------
        # Split words
        # ----------------------------------------------------

        words = message.split()


        lines = []

        current_line = ""


        max_width = (
            rect.width
            -
            24
        )


        for word in words:

            test_line = (
                word
                if not current_line
                else
                current_line
                +
                " "
                +
                word
            )


            test_surface = self.agent_font.render(
                test_line,
                True,
                TEXT_COLOR
            )


            if (
                test_surface.get_width()
                <=
                max_width
            ):

                current_line = test_line

            else:

                if current_line:

                    lines.append(
                        current_line
                    )


                current_line = word


        if current_line:

            lines.append(
                current_line
            )


        # ----------------------------------------------------
        # Limit to two lines
        # ----------------------------------------------------

        lines = lines[:2]


        # ----------------------------------------------------
        # Draw
        # ----------------------------------------------------

        total_height = (
            len(lines)
            *
            (
                self.agent_font.get_height()
                +
                4
            )
        )


        start_y = (
            rect.centery
            -
            total_height // 2
        )


        for i, line in enumerate(
            lines
        ):

            text = self.agent_font.render(
                line,
                True,
                TEXT_COLOR
            )


            text_x = (
                rect.x
                +
                12
            )


            text_y = (
                start_y
                +
                i
                *
                (
                    self.agent_font.get_height()
                    +
                    4
                )
            )


            surface.blit(
                text,
                (
                    text_x,
                    text_y
                )
            )


    # ========================================================
    # RL STATE
    # ========================================================

    def get_state(
        self
    ):

        """
        Returns the current state used by the environment.
        """

        people = (
            self.get_waiting_people()
        )


        return {

            "waiting_people": people,

            "queue_length": len(
                people
            ),

            "agent_message": (
                self.agent_message
            ),

            "agent_group": (
                self.agent_group
            ),

            "agent_table": (
                self.agent_table
            )

        }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    pygame.init()


    # ========================================================
    # WINDOW
    # ========================================================

    SCREEN_WIDTH = 1200

    SCREEN_HEIGHT = 875


    screen = pygame.display.set_mode(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
    )


    pygame.display.set_caption(
        "METRIUS EATS - Waiting People Input"
    )


    clock = pygame.time.Clock()


    # ========================================================
    # TEST CALLBACK
    # ========================================================

    def test_group_added(
        group_size
    ):

        print(
            f"[TEST] New group added: "
            f"{group_size}"
        )


    # ========================================================
    # CREATE COMPONENT
    # ========================================================

    waiting_input = WaitingPeopleInput(

        x=0,

        y=(
            SCREEN_HEIGHT
            -
            DEFAULT_HEIGHT
        ),

        width=SCREEN_WIDTH,

        height=DEFAULT_HEIGHT,

        on_group_added=test_group_added

    )


    # ========================================================
    # TEST DATA
    # ========================================================

    waiting_input.add_group(5)

    waiting_input.add_group(2)

    waiting_input.add_group(3)

    # This should be rejected because the maximum is 6.
    waiting_input.add_group(7)


    # ========================================================
    # TEST AGENT MESSAGE
    # ========================================================

    waiting_input.set_agent_decision(
        6,
        "T5"
    )


    # ========================================================
    # MAIN LOOP
    # ========================================================

    running = True


    while running:

        dt = clock.tick(
            60
        )


        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False


            waiting_input.handle_event(
                event
            )


        # ====================================================
        # UPDATE
        # ====================================================

        waiting_input.update(
            dt
        )


        # ====================================================
        # BACKGROUND
        # ====================================================

        screen.fill(
            (
                9,
                15,
                25
            )
        )


        # ====================================================
        # DRAW
        # ====================================================

        waiting_input.draw(
            screen
        )


        # ====================================================
        # DEBUG ARRAY
        # ====================================================

        debug_font = pygame.font.SysFont(
            "consolas",
            15
        )


        debug_text = debug_font.render(
            (
                "WAITING QUEUE = "
                +
                str(
                    waiting_input
                    .get_waiting_people()
                )
            ),
            True,
            (
                210,
                210,
                210
            )
        )


        screen.blit(
            debug_text,
            (
                20,
                20
            )
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        pygame.display.flip()


    pygame.quit()