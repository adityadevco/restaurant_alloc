import pygame
import os
import sys


# ============================================================
# HEADER COMPONENT
# ============================================================
#
# METRIUS EATS
#
# DYNAMIC HEADER
#
# The header now displays live simulation information:
#
#   - Day
#   - Restaurant time
#   - Customers served
#   - Average waiting time
#   - Satisfaction
#
# The Header does NOT make restaurant decisions.
# main.py / the simulation controls the data.
#
# ============================================================


# ============================================================
# PROJECT ROOT DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# ASSETS DIRECTORY
# ============================================================

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


# ============================================================
# CHEF HAT PATH
# ============================================================

CHEF_HAT_PATH = os.path.join(
    ASSETS_DIR,
    "chef_hat.png"
)


# ============================================================
# HEADER CLASS
# ============================================================

class Header:

    def __init__(
        self,
        screen
    ):

        self.screen = screen

        # ====================================================
        # HEADER POSITION
        # ====================================================

        self.x = 0
        self.y = 0

        # ====================================================
        # HEADER SIZE
        # ====================================================

        self.width = 1200
        self.height = 125

        # ====================================================
        # COLORS
        # ====================================================

        self.background_color = (
            25,
            27,
            40
        )

        self.panel_color = (
            17,
            27,
            42
        )

        self.border_color = (
            72,
            102,
            145
        )

        self.inner_border_color = (
            42,
            58,
            82
        )

        self.text_color = (
            238,
            240,
            243
        )

        self.title_color = (
            255,
            220,
            170
        )

        self.secondary_color = (
            165,
            180,
            200
        )

        self.subtitle_color = (
            160,
            177,
            197
        )

        self.green_color = (
            65,
            235,
            85
        )

        self.yellow_color = (
            255,
            190,
            50
        )

        self.face_color = (
            185,
            195,
            210
        )

        # ====================================================
        # CHEF HAT
        # ====================================================

        self.chef_hat = self.load_chef_hat()

        # ====================================================
        # FONTS
        # ====================================================

        self.title_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            28,
            True
        )

        self.subtitle_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            10,
            False
        )

        self.message_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            14,
            False
        )

        self.day_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            15,
            True
        )

        self.time_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            15,
            True
        )

        self.stats_label_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            11,
            False
        )

        self.stats_value_font = self.create_pixel_font(
            [
                "Press Start 2P",
                "Pixel Operator",
                "Pixel Operator Mono",
                "Minecraft",
                "Consolas"
            ],
            12,
            True
        )

        # ====================================================
        # LIVE SIMULATION DATA
        # ====================================================

        self.day = 1

        # Start exactly where the old static header started.
        self.simulation_minutes = (
            12 * 60 + 15
        )

        self.customers_served = 0

        self.average_wait_time = 0.0

        self.satisfaction = 5.0

        # ----------------------------------------------------
        # Simulation clock speed.
        #
        # 1 real second = 1 simulation minute.
        #
        # Change this value later if you want the restaurant
        # clock to move faster/slower.
        # ----------------------------------------------------

        self.simulation_minutes_per_second = 1.0

        # Used to prevent tiny floating point changes from
        # causing unnecessary display updates.
        self._last_displayed_time = None

        # ====================================================
        # HEADER LAYOUT
        # ====================================================

        self.logo_rect = pygame.Rect(
            30,
            15,
            385,
            90
        )

        self.message_x = 425
        self.message_y = 17

        self.time_rect = pygame.Rect(
            650,
            15,
            150,
            90
        )

        self.stats_rect = pygame.Rect(
            830,
            15,
            340,
            90
        )

        self.face_x = 615
        self.face_y = 82

    # ========================================================
    # LOAD CHEF HAT
    # ========================================================

    def load_chef_hat(
        self
    ):

        try:

            image = pygame.image.load(
                CHEF_HAT_PATH
            ).convert_alpha()

            max_width = 82
            max_height = 72

            original_width = image.get_width()
            original_height = image.get_height()

            scale_x = (
                max_width /
                original_width
            )

            scale_y = (
                max_height /
                original_height
            )

            scale = min(
                scale_x,
                scale_y
            )

            new_width = max(
                1,
                int(
                    original_width *
                    scale
                )
            )

            new_height = max(
                1,
                int(
                    original_height *
                    scale
                )
            )

            image = pygame.transform.smoothscale(
                image,
                (
                    new_width,
                    new_height
                )
            )

            print(
                "[Header] Loaded chef_hat.png"
            )

            print(
                "[Header] Chef hat size: "
                f"{new_width} x {new_height}"
            )

            return image

        except FileNotFoundError:

            print()
            print("========================================")
            print("HEADER ASSET NOT FOUND")
            print("========================================")
            print()
            print("Missing file:")
            print(CHEF_HAT_PATH)
            print()
            print("Expected:")
            print("assets/chef_hat.png")
            print()

            pygame.quit()
            sys.exit()

        except pygame.error as e:

            print()
            print("========================================")
            print("ERROR LOADING CHEF HAT")
            print("========================================")
            print()
            print(e)
            print()

            pygame.quit()
            sys.exit()

    # ========================================================
    # CREATE PIXEL FONT
    # ========================================================

    def create_pixel_font(
        self,
        font_names,
        size,
        bold=False
    ):

        for name in font_names:

            path = pygame.font.match_font(
                name
            )

            if path is not None:

                font = pygame.font.Font(
                    path,
                    size
                )

                if bold:
                    font.set_bold(True)

                return font

        font = pygame.font.SysFont(
            "monospace",
            size
        )

        if bold:
            font.set_bold(True)

        return font

    # ========================================================
    # DRAW PANEL
    # ========================================================

    def draw_panel(
        self,
        rect
    ):

        pygame.draw.rect(
            self.screen,
            self.panel_color,
            rect,
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            self.border_color,
            rect,
            width=2,
            border_radius=5
        )

        inner_rect = pygame.Rect(
            rect.x + 4,
            rect.y + 4,
            rect.width - 8,
            rect.height - 8
        )

        pygame.draw.rect(
            self.screen,
            self.inner_border_color,
            inner_rect,
            width=1,
            border_radius=3
        )

    # ========================================================
    # DRAW LOGO
    # ========================================================

    def draw_logo(self):

        self.draw_panel(
            self.logo_rect
        )

        hat_x = (
            self.logo_rect.x + 18
        )

        hat_y = (
            self.logo_rect.y + 9
        )

        self.screen.blit(
            self.chef_hat,
            (
                hat_x,
                hat_y
            )
        )

        title = self.title_font.render(
            "METRIUS EATS",
            True,
            self.title_color
        )

        title_x = (
            self.logo_rect.x + 105
        )

        title_y = (
            self.logo_rect.y + 19
        )

        self.screen.blit(
            title,
            (
                title_x,
                title_y
            )
        )

        subtitle = self.subtitle_font.render(
            "GOOD FOOD. SMARTER ALLOCATION.",
            True,
            self.subtitle_color
        )

        subtitle_x = (
            self.logo_rect.x + 108
        )

        subtitle_y = (
            self.logo_rect.y + 59
        )

        self.screen.blit(
            subtitle,
            (
                subtitle_x,
                subtitle_y
            )
        )

    # ========================================================
    # DRAW HAPPY FACE
    # ========================================================

    def draw_happy_face(
        self,
        center_x,
        center_y
    ):

        radius = 12

        pygame.draw.circle(
            self.screen,
            self.face_color,
            (
                center_x,
                center_y
            ),
            radius,
            width=2
        )

        pygame.draw.rect(
            self.screen,
            self.face_color,
            (
                center_x - 5,
                center_y - 4,
                2,
                3
            )
        )

        pygame.draw.rect(
            self.screen,
            self.face_color,
            (
                center_x + 3,
                center_y - 4,
                2,
                3
            )
        )

        smile_points = [
            (
                center_x - 6,
                center_y + 1
            ),
            (
                center_x - 4,
                center_y + 5
            ),
            (
                center_x,
                center_y + 7
            ),
            (
                center_x + 4,
                center_y + 5
            ),
            (
                center_x + 6,
                center_y + 1
            )
        ]

        pygame.draw.lines(
            self.screen,
            self.face_color,
            False,
            smile_points,
            2
        )

    # ========================================================
    # DRAW MESSAGE
    # ========================================================

    def draw_message(self):

        line1 = self.message_font.render(
            "More",
            True,
            self.text_color
        )

        line2 = self.message_font.render(
            "Happy Customers",
            True,
            self.text_color
        )

        line3 = self.message_font.render(
            "Every Day!",
            True,
            self.text_color
        )

        self.screen.blit(
            line1,
            (
                self.message_x + 2,
                self.message_y
            )
        )

        self.screen.blit(
            line2,
            (
                self.message_x,
                self.message_y + 21
            )
        )

        self.screen.blit(
            line3,
            (
                self.message_x + 2,
                self.message_y + 42
            )
        )

        self.draw_happy_face(
            self.face_x,
            self.face_y
        )

    # ========================================================
    # FORMAT TIME
    # ========================================================

    def get_time_string(self):

        total_minutes = int(
            self.simulation_minutes
        )

        minutes_in_day = 24 * 60

        normalized_minutes = (
            total_minutes %
            minutes_in_day
        )

        hour_24 = (
            normalized_minutes // 60
        )

        minute = (
            normalized_minutes % 60
        )

        if hour_24 == 0:

            hour_12 = 12

        elif hour_24 > 12:

            hour_12 = hour_24 - 12

        else:

            hour_12 = hour_24

        suffix = (
            "AM"
            if hour_24 < 12
            else "PM"
        )

        return (
            f"{hour_12}:"
            f"{minute:02d} "
            f"{suffix}"
        )

    # ========================================================
    # DRAW TIME PANEL
    # ========================================================

    def draw_time_panel(self):

        self.draw_panel(
            self.time_rect
        )

        day_text = self.day_font.render(
            f"DAY {self.day}",
            True,
            self.text_color
        )

        day_x = (
            self.time_rect.centerx
            -
            day_text.get_width() // 2
        )

        day_y = (
            self.time_rect.y + 9
        )

        self.screen.blit(
            day_text,
            (
                day_x,
                day_y
            )
        )

        pygame.draw.line(
            self.screen,
            self.border_color,
            (
                self.time_rect.x + 10,
                self.time_rect.y + 39
            ),
            (
                self.time_rect.right - 10,
                self.time_rect.y + 39
            ),
            1
        )

        sun_center = (
            self.time_rect.x + 31,
            self.time_rect.y + 65
        )

        pygame.draw.circle(
            self.screen,
            self.yellow_color,
            sun_center,
            10
        )

        ray_start = 15
        ray_end = 23

        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1)
        ]

        for dx, dy in directions:

            pygame.draw.line(
                self.screen,
                self.yellow_color,
                (
                    sun_center[0]
                    + dx * ray_start,
                    sun_center[1]
                    + dy * ray_start
                ),
                (
                    sun_center[0]
                    + dx * ray_end,
                    sun_center[1]
                    + dy * ray_end
                ),
                2
            )

        time_text = self.time_font.render(
            self.get_time_string(),
            True,
            self.text_color
        )

        time_x = (
            self.time_rect.x + 55
        )

        time_y = (
            self.time_rect.y + 52
        )

        self.screen.blit(
            time_text,
            (
                time_x,
                time_y
            )
        )

    # ========================================================
    # DRAW PIXEL STAR
    # ========================================================

    def draw_star(
        self,
        center_x,
        center_y,
        size,
        filled,
        color
    ):

        points = [
            (
                center_x,
                center_y - size
            ),
            (
                center_x + 3,
                center_y - 3
            ),
            (
                center_x + size,
                center_y - 3
            ),
            (
                center_x + 5,
                center_y + 2
            ),
            (
                center_x + 7,
                center_y + size
            ),
            (
                center_x,
                center_y + 5
            ),
            (
                center_x - 7,
                center_y + size
            ),
            (
                center_x - 5,
                center_y + 2
            ),
            (
                center_x - size,
                center_y - 3
            ),
            (
                center_x - 3,
                center_y - 3
            )
        ]

        if filled:

            pygame.draw.polygon(
                self.screen,
                color,
                points
            )

        else:

            pygame.draw.polygon(
                self.screen,
                color,
                points,
                width=2
            )

    # ========================================================
    # DRAW STATISTICS
    # ========================================================

    def draw_statistics(self):

        self.draw_panel(
            self.stats_rect
        )

        served_label = self.stats_label_font.render(
            "Customers Served:",
            True,
            self.secondary_color
        )

        served_value = self.stats_value_font.render(
            str(self.customers_served),
            True,
            self.text_color
        )

        self.screen.blit(
            served_label,
            (
                self.stats_rect.x + 13,
                self.stats_rect.y + 10
            )
        )

        served_value_x = (
            self.stats_rect.right
            -
            served_value.get_width()
            -
            42
        )

        self.screen.blit(
            served_value,
            (
                served_value_x,
                self.stats_rect.y + 10
            )
        )

        wait_label = self.stats_label_font.render(
            "Average Wait Time:",
            True,
            self.secondary_color
        )

        wait_value = self.stats_value_font.render(
            f"{self.average_wait_time:.1f} min",
            True,
            self.text_color
        )

        self.screen.blit(
            wait_label,
            (
                self.stats_rect.x + 13,
                self.stats_rect.y + 35
            )
        )

        wait_value_x = (
            self.stats_rect.right
            -
            wait_value.get_width()
            -
            42
        )

        self.screen.blit(
            wait_value,
            (
                wait_value_x,
                self.stats_rect.y + 35
            )
        )

        satisfaction_label = self.stats_label_font.render(
            "Satisfaction:",
            True,
            self.secondary_color
        )

        self.screen.blit(
            satisfaction_label,
            (
                self.stats_rect.x + 13,
                self.stats_rect.y + 60
            )
        )

        full_stars = int(
            self.satisfaction
        )

        star_size = 8

        star_start_x = (
            self.stats_rect.x + 222
        )

        star_y = (
            self.stats_rect.y + 68
        )

        for i in range(5):

            star_x = (
                star_start_x
                + i * 22
            )

            if i < full_stars:

                self.draw_star(
                    star_x,
                    star_y,
                    star_size,
                    True,
                    self.green_color
                )

            else:

                self.draw_star(
                    star_x,
                    star_y,
                    star_size,
                    False,
                    self.secondary_color
                )

    # ========================================================
    # UPDATE SIMULATION
    # ========================================================

    def update(
        self,
        dt_seconds,
        customers_served=None,
        average_wait_time=None,
        satisfaction=None
    ):

        """
        Update live header data.

        dt_seconds:
            Real elapsed seconds from pygame clock.

        Optional values:
            customers_served
            average_wait_time
            satisfaction

        These optional values allow main.py to connect the
        header to the actual simulation.
        """

        try:

            dt_seconds = float(
                dt_seconds
            )

        except (
            ValueError,
            TypeError
        ):

            dt_seconds = 0.0

        dt_seconds = max(
            0.0,
            dt_seconds
        )

        # ----------------------------------------------------
        # ADVANCE SIMULATION CLOCK
        # ----------------------------------------------------

        self.simulation_minutes += (
            dt_seconds
            *
            self.simulation_minutes_per_second
        )

        # ----------------------------------------------------
        # ADVANCE DAY
        # ----------------------------------------------------

        while self.simulation_minutes >= 24 * 60:

            self.simulation_minutes -= (
                24 * 60
            )

            self.day += 1

        # ----------------------------------------------------
        # LIVE CUSTOMERS SERVED
        # ----------------------------------------------------

        if customers_served is not None:

            try:

                self.customers_served = max(
                    0,
                    int(customers_served)
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        # ----------------------------------------------------
        # LIVE AVERAGE WAIT TIME
        # ----------------------------------------------------

        if average_wait_time is not None:

            try:

                self.average_wait_time = max(
                    0.0,
                    float(average_wait_time)
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        # ----------------------------------------------------
        # LIVE SATISFACTION
        # ----------------------------------------------------

        if satisfaction is not None:

            try:

                self.satisfaction = max(
                    0.0,
                    min(
                        5.0,
                        float(satisfaction)
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                pass

    # ========================================================
    # SET DAY
    # ========================================================

    def set_day(
        self,
        day
    ):

        try:

            self.day = max(
                1,
                int(day)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # SET TIME
    # ========================================================

    def set_time(
        self,
        time
    ):

        """
        Compatibility method.

        Accepts strings such as:
            "12:15 PM"

        The dynamic clock continues to work after this.
        """

        if not isinstance(
            time,
            str
        ):

            return

        try:

            parts = time.strip().upper().split()

            if len(parts) != 2:
                return

            clock_part = parts[0]
            suffix = parts[1]

            hour, minute = (
                clock_part.split(":")
            )

            hour = int(hour)
            minute = int(minute)

            if suffix == "PM" and hour != 12:
                hour += 12

            elif suffix == "AM" and hour == 12:
                hour = 0

            if (
                0 <= hour < 24
                and
                0 <= minute < 60
            ):

                self.simulation_minutes = (
                    hour * 60 + minute
                )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # SET CUSTOMERS SERVED
    # ========================================================

    def set_customers_served(
        self,
        value
    ):

        try:

            self.customers_served = max(
                0,
                int(value)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # SET AVERAGE WAIT TIME
    # ========================================================

    def set_average_wait_time(
        self,
        value
    ):

        try:

            self.average_wait_time = max(
                0.0,
                float(value)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # SET SATISFACTION
    # ========================================================

    def set_satisfaction(
        self,
        value
    ):

        try:

            self.satisfaction = max(
                0.0,
                min(
                    5.0,
                    float(value)
                )
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # SET SIMULATION SPEED
    # ========================================================

    def set_simulation_speed(
        self,
        minutes_per_second
    ):

        try:

            self.simulation_minutes_per_second = max(
                0.0,
                float(minutes_per_second)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # ========================================================
    # GET CURRENT TIME
    # ========================================================

    def get_current_time(self):

        return self.get_time_string()

    # ========================================================
    # DRAW HEADER
    # ========================================================

    def draw(self):

        pygame.draw.rect(
            self.screen,
            self.background_color,
            (
                self.x,
                self.y,
                self.width,
                self.height
            )
        )

        self.draw_logo()

        self.draw_message()

        self.draw_time_panel()

        self.draw_statistics()


# ============================================================
# END OF HEADER.PY
# ============================================================
