import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class Sidebar:
    def __init__(self, screen, x=1200, y=125, width=250, height=750, on_algorithm_changed=None, on_export_requested=None):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_algorithm_changed = on_algorithm_changed
        self.on_export_requested = on_export_requested

        self.background_color = (24, 27, 39)
        self.panel_color = (15, 24, 38)
        self.panel_alt_color = (18, 30, 47)
        self.border_color = (67, 96, 137)
        self.inner_border_color = (38, 55, 78)
        self.text_color = (238, 240, 243)
        self.secondary_color = (165, 180, 200)
        self.green_color = (55, 240, 100)
        self.green_dark_color = (30, 130, 75)
        self.red_color = (245, 75, 75)
        self.yellow_color = (255, 190, 50)
        self.blue_color = (75, 150, 230)
        self.disabled_color = (38, 53, 75)
        self.dashed_color = (75, 88, 108)
        self.bar_background_color = (25, 39, 58)
        self.overlay_color = (12, 19, 30)
        self.hover_color = (25, 48, 70)

        pixel_fonts = [
            "Press Start 2P",
            "Pixel Operator",
            "Pixel Operator Mono",
            "Minecraft",
            "Consolas"
        ]

        self.title_font = self.create_pixel_font(pixel_fonts, 21, True)
        self.section_font = self.create_pixel_font(pixel_fonts, 16, True)
        self.label_font = self.create_pixel_font(pixel_fonts, 13, False)
        self.value_font = self.create_pixel_font(pixel_fonts, 13, True)
        self.small_font = self.create_pixel_font(pixel_fonts, 11, False)
        self.algorithm_font = self.create_pixel_font(pixel_fonts, 13, False)
        self.algorithm_value_font = self.create_pixel_font(pixel_fonts, 11, True)
        self.branding_font = self.create_pixel_font(pixel_fonts, 11, False)

        self.algorithms = [
            "Default",
            "Expected SARSA",
            "N-step Tree Backup",
            "Actor-Critic",
            "DQN"
        ]

        self.selected_algorithm = "Default"
        self.selected_index = 0
        self.algorithm_buttons = []
        self.algorithm_hover_index = -1

        self.elapsed_seconds = 0.0
        self.current_customers = 0
        self.waiting_queue = 0
        self.waiting_time_seconds = 0.0
        self.tables_occupied = 0
        self.tables_ready = 0
        self.tables_cleaning = 0
        self.total_tables = 8

        self.average_wait_time = 0.0
        self.satisfaction = 5.0
        self.successful_allocations = 0
        self.total_decisions = 0
        self.allocation_accuracy = 0.0

        self.current_reward = 0.0
        self.best_reward = 0.0
        self.q_updates = 0
        self.episode = 0
        self.current_penalty = 0.0
        self.total_penalties = 0.0
        self.waste_penalties = 0
        self.last_penalty = 0.0

        self.actor_updates = 0
        self.critic_updates = 0
        self.actor_loss = 0.0
        self.critic_loss = 0.0
        self.total_reward = 0.0
        self.entropy = 0.0
        self.advantage = 0.0
        self.value_estimate = 0.0
        self.last_unused_seats = None
        self.feasible_table_count = 0

        self.dqn_loss = 0.0
        self.dqn_q_value = 0.0
        self.dqn_target_q = 0.0
        self.dqn_td_error = 0.0
        self.dqn_replay_size = 0
        self.dqn_target_updates = 0
        self.dqn_explorations = 0
        self.dqn_exploitations = 0
        self.dqn_epsilon = 0.0

        self.n_step = 3
        self.n_step_tree_backup_return = 0.0
        self.n_step_td_error = 0.0
        self.n_step_pending_transitions = 0
        self.n_step_explorations = 0
        self.n_step_exploitations = 0
        self.n_step_epsilon = 0.0

        self.algorithm_description = "Standard table allocation"
        self.algorithm_policy = "Best fit"
        self.algorithm_learning = "None"
        self.algorithm_exploration = "--"

        self.last_group_size = None
        self.last_selected_table = "--"
        self.last_table_capacity = None
        self.last_decision_result = "--"
        self.last_reward = None
        self.last_decision_algorithm = "Default"
        self.last_decision_time = 0.0
        self.last_decision_reason = "--"
        self.algorithm_info = {}

        self._last_decision_signature = None
        self._has_authoritative_total_reward = False

        self.panel_margin = 8
        panel_width = self.width - self.panel_margin * 2
        panel_x = self.x + self.panel_margin
        top = self.y + 5
        gap = 7

        self.algorithm_rect = pygame.Rect(
            panel_x,
            top,
            panel_width,
            205
        )

        self.status_rect = pygame.Rect(
            panel_x,
            self.algorithm_rect.bottom + gap,
            panel_width,
            135
        )

        self.decision_rect = pygame.Rect(
            panel_x,
            self.status_rect.bottom + gap,
            panel_width,
            145
        )

        performance_y = self.decision_rect.bottom + gap

        performance_height = (
            self.y
            + self.height
            - performance_y
        )

        self.performance_rect = pygame.Rect(
            panel_x,
            performance_y,
            panel_width,
            performance_height
        )

        self.export_rect = pygame.Rect(
            self.performance_rect.x + 12,
            self.performance_rect.bottom - 35,
            self.performance_rect.width - 24,
            26
        )

        self.export_hovered = False
        self.update_algorithm_narration()

    def create_pixel_font(self, font_names, size, bold=False):
        for name in font_names:
            path = pygame.font.match_font(name)

            if path is not None:
                font = pygame.font.Font(path, size)

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

    def _number(self, value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return float(default)

    def _integer(self, value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return int(default)

    def _pick(self, data, *keys, default=None):
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return default

    def _normalize_algorithm(self, algorithm):
        value = str(
            algorithm
        ).strip().upper().replace(
            "_",
            " "
        )

        value = " ".join(
            value.split()
        )

        mapping = {
            "DEFAULT": "Default",
            "EXPECTED SARSA": "Expected SARSA",
            "EXPECTEDSARSA": "Expected SARSA",
            "N STEP TREE BACKUP": "N-step Tree Backup",
            "N-STEP TREE BACKUP": "N-step Tree Backup",
            "NSTEP TREE BACKUP": "N-step Tree Backup",
            "TREE BACKUP": "N-step Tree Backup",
            "ACTOR-CRITIC": "Actor-Critic",
            "ACTOR CRITIC": "Actor-Critic",
            "Q-LEARNING": "Q-Learning",
            "Q LEARNING": "Q-Learning",
            "SARSA": "SARSA",
            "DQN": "DQN"
        }

        return mapping.get(
            value,
            str(algorithm).strip()
        )

    def format_time(self, seconds):
        total = max(
            0,
            self._integer(seconds)
        )

        return (
            f"{total // 60:02d} min "
            f"{total % 60:02d} sec"
        )

    def format_wait_time(self, value):
        return self.format_time(value)

    def draw_panel(self, rect):
        pygame.draw.rect(
            self.screen,
            self.panel_color,
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            self.border_color,
            rect,
            width=2,
            border_radius=7
        )

        inner = pygame.Rect(
            rect.x + 4,
            rect.y + 4,
            rect.width - 8,
            rect.height - 8
        )

        pygame.draw.rect(
            self.screen,
            self.inner_border_color,
            inner,
            width=1,
            border_radius=4
        )

        pygame.draw.line(
            self.screen,
            self.inner_border_color,
            (
                rect.x + 12,
                rect.y + 31
            ),
            (
                rect.right - 12,
                rect.y + 31
            ),
            1
        )

    def draw_section_title(self, rect, title, badge=None):
        surface = self.section_font.render(
            title,
            True,
            self.text_color
        )

        pygame.draw.rect(
            self.screen,
            self.green_color,
            (
                rect.x + 11,
                rect.y + 8,
                3,
                min(
                    surface.get_height(),
                    17
                )
            ),
            border_radius=1
        )

        self.screen.blit(
            surface,
            (
                rect.x + 20,
                rect.y + 7
            )
        )

        if badge:
            badge_surface = self.small_font.render(
                str(badge).upper(),
                True,
                self.green_color
            )

            badge_rect = pygame.Rect(
                rect.right
                - badge_surface.get_width()
                - 18,
                rect.y + 8,
                badge_surface.get_width() + 8,
                max(
                    16,
                    badge_surface.get_height() + 4
                )
            )

            pygame.draw.rect(
                self.screen,
                (10, 51, 40),
                badge_rect,
                border_radius=4
            )

            pygame.draw.rect(
                self.screen,
                self.green_dark_color,
                badge_rect,
                width=1,
                border_radius=4
            )

            self.screen.blit(
                badge_surface,
                (
                    badge_rect.x + 4,
                    badge_rect.y + 2
                )
            )

    def draw_arrow(self, x, y, color):
        pygame.draw.polygon(
            self.screen,
            color,
            [
                (x, y),
                (x + 7, y + 5),
                (x, y + 10)
            ]
        )

    def get_algorithm_button_rects(self):
        button_x = (
            self.algorithm_rect.x
            + 11
        )

        button_width = (
            self.algorithm_rect.width
            - 22
        )

        button_height = 27
        gap = 4
        first_y = (
            self.algorithm_rect.y
            + 37
        )

        return [
            pygame.Rect(
                button_x,
                first_y
                + i * (
                    button_height
                    + gap
                ),
                button_width,
                button_height
            )
            for i in range(
                len(self.algorithms)
            )
        ]

    def draw_algorithm_panel(self):
        self.draw_panel(
            self.algorithm_rect
        )

        self.draw_section_title(
            self.algorithm_rect,
            "ALGORITHM",
            "ACTIVE"
        )

        self.algorithm_buttons = (
            self.get_algorithm_button_rects()
        )

        mouse_pos = pygame.mouse.get_pos()
        self.algorithm_hover_index = -1

        for i, algorithm in enumerate(
            self.algorithms
        ):
            rect = self.algorithm_buttons[i]

            selected = (
                i == self.selected_index
            )

            hovered = rect.collidepoint(
                mouse_pos
            )

            if hovered:
                self.algorithm_hover_index = i

            if selected:
                background = (
                    10,
                    51,
                    40
                )

                border = self.green_color
                arrow_color = self.green_color
                text_color = self.text_color

            elif hovered:
                background = self.hover_color
                border = self.border_color
                arrow_color = self.blue_color
                text_color = self.text_color

            else:
                background = (
                    19,
                    32,
                    50
                )

                border = self.disabled_color
                arrow_color = (
                    45,
                    65,
                    90
                )

                text_color = self.secondary_color

            pygame.draw.rect(
                self.screen,
                background,
                rect,
                border_radius=4
            )

            pygame.draw.rect(
                self.screen,
                border,
                rect,
                width=2 if selected else 1,
                border_radius=4
            )

            if selected:
                pygame.draw.rect(
                    self.screen,
                    self.green_color,
                    (
                        rect.x + 1,
                        rect.y + 5,
                        2,
                        rect.height - 10
                    ),
                    border_radius=1
                )

            self.draw_arrow(
                rect.x + 9,
                rect.y + 8,
                arrow_color
            )

            text = self.algorithm_font.render(
                algorithm,
                True,
                text_color
            )

            text_y = (
                rect.centery
                - text.get_height() // 2
            )

            self.screen.blit(
                text,
                (
                    rect.x + 24,
                    text_y
                )
            )

        info_y = (
            self.algorithm_rect.bottom
            - 23
        )

        desc = self.algorithm_description

        if len(desc) > 31:
            desc = desc[:30] + "…"

        info = self.small_font.render(
            desc,
            True,
            self.secondary_color
        )

        self.screen.blit(
            info,
            (
                self.algorithm_rect.x + 12,
                info_y
            )
        )

    def handle_event(self, event):
        if (
            event.type
            != pygame.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return False

        if self.export_rect.collidepoint(
            event.pos
        ):
            print(
                "[SIDEBAR] PDF export requested."
            )

            if self.on_export_requested is not None:
                try:
                    self.on_export_requested()
                except TypeError:
                    self.on_export_requested(
                        self
                    )
            else:
                print(
                    "[SIDEBAR] "
                    "No PDF export callback is connected."
                )

            return True

        buttons = (
            self.get_algorithm_button_rects()
        )

        self.algorithm_buttons = buttons

        for i, rect in enumerate(buttons):
            if not rect.collidepoint(
                event.pos
            ):
                continue

            if i == self.selected_index:
                print(
                    f"[SIDEBAR] "
                    f"{self.algorithms[i]} "
                    "is already selected."
                )

                return False

            old_algorithm = (
                self.selected_algorithm
            )

            new_algorithm = (
                self.algorithms[i]
            )

            self.selected_index = i
            self.selected_algorithm = (
                new_algorithm
            )

            self.update_algorithm_narration()

            internal_algorithm = (
                self.get_internal_algorithm_name(
                    new_algorithm
                )
            )

            print()
            print(
                "========================================"
            )
            print(
                "[SIDEBAR] ALGORITHM CHANGED"
            )
            print(
                f"[SIDEBAR] "
                f"{old_algorithm} -> "
                f"{new_algorithm}"
            )
            print(
                f"[SIDEBAR] Internal: "
                f"{internal_algorithm}"
            )
            print(
                "========================================"
            )

            if self.on_algorithm_changed is not None:
                self.on_algorithm_changed(
                    internal_algorithm
                )

            return True

        return False

    def get_export_button_rect(self):
        return self.export_rect.copy()

    def get_internal_algorithm_name(self, algorithm):
        mapping = {
            "Default": "DEFAULT",
            "Expected SARSA": "EXPECTED SARSA",
            "N-step Tree Backup": "N-STEP TREE BACKUP",
            "Actor-Critic": "ACTOR-CRITIC",
            "Q-Learning": "Q-LEARNING",
            "SARSA": "SARSA",
            "DQN": "DQN"
        }

        return mapping.get(
            algorithm,
            str(algorithm).strip().upper()
        )

    def update_algorithm_narration(self):
        data = {
            "Default": (
                "Standard table allocation",
                "Best fit",
                "None",
                "--"
            ),
            "Expected SARSA": (
                "Learns from expected future reward",
                "Epsilon Greedy",
                "Expected Q-value",
                "ε = 0.10"
            ),
            "N-step Tree Backup": (
                "Backs up multiple future rewards",
                "Epsilon Greedy",
                "Tree Backup Return",
                "n = 3, ε = 0.10"
            ),
            "Actor-Critic": (
                "Learns policy and value together",
                "Stochastic Policy",
                "Actor + Critic",
                "Entropy guided"
            ),
            "Q-Learning": (
                "Learns the best future action",
                "Epsilon Greedy",
                "Maximum Q-value",
                "ε = 0.10"
            ),
            "SARSA": (
                "Learns from the next chosen action",
                "On-policy",
                "Next action Q",
                "ε = 0.10"
            ),
            "DQN": (
                "Neural network table selection",
                "Deep Q Network",
                "Replay learning",
                "ε-greedy"
            )
        }

        values = data.get(
            self.selected_algorithm,
            (
                "Algorithm active",
                "--",
                "--",
                "--"
            )
        )

        (
            self.algorithm_description,
            self.algorithm_policy,
            self.algorithm_learning,
            self.algorithm_exploration
        ) = values

    def draw_row(
        self,
        rect,
        label,
        value,
        y,
        value_color=None,
        label_color=None
    ):
        if value_color is None:
            value_color = self.text_color

        if label_color is None:
            label_color = self.secondary_color

        label_surface = self.label_font.render(
            str(label),
            True,
            label_color
        )

        value_text = str(value)

        max_value_width = max(
            55,
            rect.width - 105
        )

        value_surface = self.value_font.render(
            value_text,
            True,
            value_color
        )

        if value_surface.get_width() > max_value_width:
            value_surface = self.small_font.render(
                value_text,
                True,
                value_color
            )

        if value_surface.get_width() > max_value_width:
            trimmed = value_text

            while (
                trimmed
                and
                self.small_font.size(
                    trimmed + "…"
                )[0] > max_value_width
            ):
                trimmed = trimmed[:-1]

            value_surface = self.small_font.render(
                (
                    trimmed + "…"
                    if trimmed
                    else "…"
                ),
                True,
                value_color
            )

        self.screen.blit(
            label_surface,
            (
                rect.x + 12,
                y
            )
        )

        value_x = max(
            rect.x + 94,
            rect.right
            - value_surface.get_width()
            - 12
        )

        self.screen.blit(
            value_surface,
            (
                value_x,
                y
            )
        )

    def draw_status_panel(self):
        self.draw_panel(
            self.status_rect
        )

        self.draw_section_title(
            self.status_rect,
            "RESTAURANT STATUS"
        )

        base_y = (
            self.status_rect.y
            + 37
        )

        spacing = 19

        rows = [
            (
                "Simulation:",
                self.format_time(
                    self.elapsed_seconds
                ),
                self.text_color
            ),
            (
                "Customers:",
                self.current_customers,
                self.text_color
            ),
            (
                "Waiting:",
                f"{self.waiting_queue} groups",
                self.text_color
            ),
            (
                "Wait time:",
                self.format_wait_time(
                    self.waiting_time_seconds
                ),
                self.text_color
            )
        ]

        for i, (
            label,
            value,
            color
        ) in enumerate(rows):
            self.draw_row(
                self.status_rect,
                label,
                value,
                base_y + i * spacing,
                color
            )

        bottom_y = (
            self.status_rect.bottom
            - 27
        )

        ready_label = self.label_font.render(
            "Ready:",
            True,
            self.secondary_color
        )

        ready_value = self.value_font.render(
            str(self.tables_ready),
            True,
            self.green_color
        )

        cleaning_label = self.label_font.render(
            "Cleaning:",
            True,
            self.secondary_color
        )

        cleaning_value = self.value_font.render(
            str(self.tables_cleaning),
            True,
            self.yellow_color
        )

        ready_x = (
            self.status_rect.x
            + 12
        )

        cleaning_x = (
            self.status_rect.x
            + self.status_rect.width // 2
            + 2
        )

        self.screen.blit(
            ready_label,
            (
                ready_x,
                bottom_y
            )
        )

        self.screen.blit(
            ready_value,
            (
                ready_x
                + ready_label.get_width()
                + 7,
                bottom_y
            )
        )

        self.screen.blit(
            cleaning_label,
            (
                cleaning_x,
                bottom_y
            )
        )

        self.screen.blit(
            cleaning_value,
            (
                cleaning_x
                + cleaning_label.get_width()
                + 7,
                bottom_y
            )
        )

    def draw_decision_panel(self):
        self.draw_panel(
            self.decision_rect
        )

        self.draw_section_title(
            self.decision_rect,
            "LATEST DECISION"
        )

        base_y = (
            self.decision_rect.y
            + 37
        )

        spacing = 20

        group_text = (
            "--"
            if self.last_group_size is None
            else f"{self.last_group_size} people"
        )

        table_text = (
            self.last_selected_table
        )

        if (
            self.last_table_capacity is not None
            and table_text != "--"
        ):
            table_text = (
                f"{table_text} "
                f"({self.last_table_capacity})"
            )

        if self.last_decision_result == "SUCCESS":
            result_color = self.green_color
        elif self.last_decision_result == "FAILED":
            result_color = self.red_color
        else:
            result_color = self.secondary_color

        if self.last_reward is None:
            reward_text = "--"
            reward_color = self.secondary_color
        else:
            reward_value = self._number(
                self.last_reward
            )

            reward_text = (
                f"{reward_value:+.1f}"
            )

            reward_color = (
                self.green_color
                if reward_value >= 0
                else self.red_color
            )

        rows = [
            (
                "Group:",
                group_text,
                self.text_color
            ),
            (
                "Selected:",
                table_text,
                self.text_color
            ),
            (
                "Result:",
                self.last_decision_result,
                result_color
            ),
            (
                "Reward:",
                reward_text,
                reward_color
            ),
            (
                "By:",
                self.last_decision_algorithm,
                self.blue_color
            )
        ]

        for i, (
            label,
            value,
            color
        ) in enumerate(rows):
            self.draw_row(
                self.decision_rect,
                label,
                value,
                base_y + i * spacing,
                color
            )

    def _reward_color(self, value):
        return (
            self.green_color
            if self._number(value) >= 0
            else self.red_color
        )

    def _performance_rows(self):
        reward = self._number(
            self.current_reward
        )

        penalty = self._number(
            self.current_penalty
        )

        total = self._number(
            self.total_reward
        )

        if self.selected_algorithm == "Default":
            return [
                (
                    "Reward:",
                    "--",
                    self.dashed_color
                ),
                (
                    "Policy:",
                    "Best fit",
                    self.blue_color
                ),
                (
                    "Learning:",
                    "None",
                    self.dashed_color
                ),
                (
                    "Decisions:",
                    self.total_decisions,
                    self.text_color
                )
            ]

        if self.selected_algorithm == "Expected SARSA":
            penalty_text = (
                "--"
                if penalty == 0
                else f"{penalty:+.1f}"
            )

            return [
                (
                    "Reward:",
                    f"{reward:+.1f}",
                    self._reward_color(reward)
                ),
                (
                    "Penalty:",
                    penalty_text,
                    (
                        self.dashed_color
                        if penalty == 0
                        else self.red_color
                    )
                ),
                (
                    "Policy:",
                    self.algorithm_policy,
                    self.blue_color
                ),
                (
                    "Learning:",
                    self.algorithm_learning,
                    self.text_color
                ),
                (
                    "Explore:",
                    self.algorithm_exploration,
                    self.yellow_color
                ),
                (
                    "Q Updates:",
                    self.q_updates,
                    self.text_color
                ),
                (
                    "Best Reward:",
                    f"{self.best_reward:+.1f}",
                    self._reward_color(
                        self.best_reward
                    )
                ),
                (
                    "Total Reward:",
                    f"{total:+.1f}",
                    self._reward_color(total)
                )
            ]

        if self.selected_algorithm == "N-step Tree Backup":
            penalty_text = (
                "--"
                if penalty == 0
                else f"{penalty:+.1f}"
            )

            return [
                (
                    "Reward:",
                    f"{reward:+.1f}",
                    self._reward_color(reward)
                ),
                (
                    "Penalty:",
                    penalty_text,
                    (
                        self.dashed_color
                        if penalty == 0
                        else self.red_color
                    )
                ),
                (
                    "Policy:",
                    "Epsilon Greedy",
                    self.blue_color
                ),
                (
                    "Learning:",
                    "Tree Backup Return",
                    self.text_color
                ),
                (
                    "n-step:",
                    self.n_step,
                    self.yellow_color
                ),
                (
                    "Explore:",
                    f"ε = {self.n_step_epsilon:.2f}",
                    self.yellow_color
                ),
                (
                    "Q Updates:",
                    self.q_updates,
                    self.text_color
                ),
                (
                    "Tree Return:",
                    f"{self.n_step_tree_backup_return:+.2f}",
                    self._reward_color(
                        self.n_step_tree_backup_return
                    )
                ),
                (
                    "TD Error:",
                    f"{self.n_step_td_error:+.2f}",
                    self._reward_color(
                        self.n_step_td_error
                    )
                ),
                (
                    "Pending:",
                    self.n_step_pending_transitions,
                    self.secondary_color
                ),
                (
                    "Total Reward:",
                    f"{total:+.1f}",
                    self._reward_color(total)
                )
            ]

        if self.selected_algorithm == "Actor-Critic":
            penalty_text = (
                "--"
                if penalty == 0
                else f"{penalty:+.1f}"
            )

            return [
                (
                    "Reward:",
                    f"{reward:+.1f}",
                    self._reward_color(reward)
                ),
                (
                    "Penalty:",
                    penalty_text,
                    (
                        self.dashed_color
                        if penalty == 0
                        else self.red_color
                    )
                ),
                (
                    "Policy:",
                    "Stochastic Policy",
                    self.blue_color
                ),
                (
                    "Learning:",
                    "Actor + Critic",
                    self.text_color
                ),
                (
                    "Updates:",
                    f"A:{self.actor_updates} C:{self.critic_updates}",
                    self.text_color
                ),
                (
                    "Entropy:",
                    f"{self.entropy:.3f}",
                    self.yellow_color
                ),
                (
                    "Advantage:",
                    f"{self.advantage:+.3f}",
                    self._reward_color(
                        self.advantage
                    )
                ),
                (
                    "Value:",
                    f"{self.value_estimate:+.3f}",
                    self.blue_color
                ),
                (
                    "Loss A/C:",
                    f"A:{self.actor_loss:.3f} C:{self.critic_loss:.3f}",
                    self.secondary_color
                ),
                (
                    "Feasible:",
                    self.feasible_table_count,
                    self.text_color
                ),
                (
                    "Total Reward:",
                    f"{total:+.1f}",
                    self._reward_color(total)
                )
            ]

        if self.selected_algorithm == "DQN":
            penalty_text = (
                "--"
                if penalty == 0
                else f"{penalty:+.1f}"
            )

            return [
                (
                    "Reward:",
                    f"{reward:+.1f}",
                    self._reward_color(reward)
                ),
                (
                    "Penalty:",
                    penalty_text,
                    (
                        self.dashed_color
                        if penalty == 0
                        else self.red_color
                    )
                ),
                (
                    "Policy:",
                    "Deep Q Network",
                    self.blue_color
                ),
                (
                    "Explore:",
                    f"ε = {self.dqn_epsilon:.2f}",
                    self.yellow_color
                ),
                (
                    "Updates:",
                    self.q_updates,
                    self.text_color
                ),
                (
                    "Loss:",
                    f"{self.dqn_loss:.3f}",
                    self.secondary_color
                ),
                (
                    "Q → Target:",
                    f"{self.dqn_q_value:.2f} → {self.dqn_target_q:.2f}",
                    self.secondary_color
                ),
                (
                    "TD Error:",
                    f"{self.dqn_td_error:+.3f}",
                    self._reward_color(
                        self.dqn_td_error
                    )
                ),
                (
                    "Replay:",
                    self.dqn_replay_size,
                    self.text_color
                ),
                (
                    "Explore / Exploit:",
                    f"{self.dqn_explorations} / {self.dqn_exploitations}",
                    self.secondary_color
                ),
                (
                    "Total Reward:",
                    f"{total:+.1f}",
                    self._reward_color(total)
                )
            ]

        return [
            (
                "Reward:",
                f"{reward:+.1f}",
                self._reward_color(reward)
            ),
            (
                "Policy:",
                self.algorithm_policy,
                self.blue_color
            ),
            (
                "Learning:",
                self.algorithm_learning,
                self.text_color
            ),
            (
                "Updates:",
                self.q_updates,
                self.text_color
            )
        ]

    def draw_performance_panel(self):
        self.draw_panel(
            self.performance_rect
        )

        self.draw_section_title(
            self.performance_rect,
            "AI PERFORMANCE",
            "LIVE"
        )

        rows = self._performance_rows()

        base_y = (
            self.performance_rect.y
            + 37
        )

        available_bottom = (
            self.export_rect.y
            - 8
        )

        if len(rows) >= 11:
            preferred_spacing = 16
        elif len(rows) >= 8:
            preferred_spacing = 18
        else:
            preferred_spacing = 21

        if len(rows) > 1:
            max_spacing = max(
                13,
                (
                    available_bottom
                    - base_y
                )
                // (len(rows) - 1)
            )

            spacing = min(
                preferred_spacing,
                max_spacing
            )
        else:
            spacing = preferred_spacing

        for i, (
            label,
            value,
            color
        ) in enumerate(rows):
            self.draw_row(
                self.performance_rect,
                label,
                value,
                base_y + spacing * i,
                color
            )

    def draw_export_button(self):
        self.export_hovered = (
            self.export_rect.collidepoint(
                pygame.mouse.get_pos()
            )
        )

        if self.export_hovered:
            background = (
                20,
                74,
                59
            )

            border = self.green_color
            text_color = self.text_color

        else:
            background = (
                21,
                35,
                55
            )

            border = self.disabled_color
            text_color = self.secondary_color

        pygame.draw.rect(
            self.screen,
            background,
            self.export_rect,
            border_radius=4
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.export_rect,
            width=2 if self.export_hovered else 1,
            border_radius=4
        )

        x = (
            self.export_rect.x
            + 12
        )

        y = (
            self.export_rect.y
            + 6
        )

        pygame.draw.line(
            self.screen,
            text_color,
            (x + 5, y),
            (x + 5, y + 8),
            2
        )

        pygame.draw.line(
            self.screen,
            text_color,
            (x + 2, y + 6),
            (x + 5, y + 9),
            2
        )

        pygame.draw.line(
            self.screen,
            text_color,
            (x + 8, y + 6),
            (x + 5, y + 9),
            2
        )

        pygame.draw.line(
            self.screen,
            text_color,
            (x + 1, y + 12),
            (x + 9, y + 12),
            2
        )

        label = self.small_font.render(
            "EXPORT RESULTS PDF",
            True,
            text_color
        )

        self.screen.blit(
            label,
            (
                self.export_rect.centerx
                - label.get_width() // 2
                + 5,
                self.export_rect.centery
                - label.get_height() // 2
            )
        )

    def draw_branding(self):
        center_x = (
            self.x
            + self.width // 2
        )

        line1 = self.branding_font.render(
            "Smarter allocation",
            True,
            self.text_color
        )

        line2 = self.branding_font.render(
            "Happier dining!",
            True,
            self.text_color
        )

        self.screen.blit(
            line1,
            (
                center_x
                - line1.get_width() // 2,
                self.y
                + self.height
                + 5
            )
        )

        self.screen.blit(
            line2,
            (
                center_x
                - line2.get_width() // 2,
                self.y
                + self.height
                + 21
            )
        )

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

        self.draw_algorithm_panel()
        self.draw_status_panel()
        self.draw_decision_panel()
        self.draw_performance_panel()
        self.draw_export_button()

    def update(self, dt_seconds):
        try:
            self.elapsed_seconds += max(
                0.0,
                float(dt_seconds)
            )
        except (ValueError, TypeError):
            pass

    def set_export_callback(self, callback):
        self.on_export_requested = callback

    def set_algorithm(self, algorithm):
        if algorithm is None:
            return

        normalized = self._normalize_algorithm(
            algorithm
        )

        if normalized not in self.algorithms:
            return

        changed = (
            self.selected_algorithm
            != normalized
        )

        self.selected_algorithm = normalized

        self.selected_index = (
            self.algorithms.index(
                normalized
            )
        )

        self.update_algorithm_narration()

        if not changed:
            return

        self.current_reward = 0.0
        self.current_penalty = 0.0
        self.q_updates = 0
        self.total_reward = 0.0
        self._has_authoritative_total_reward = False

        if normalized == "Actor-Critic":
            self.actor_updates = 0
            self.critic_updates = 0
            self.actor_loss = 0.0
            self.critic_loss = 0.0
            self.entropy = 0.0
            self.advantage = 0.0
            self.value_estimate = 0.0
            self.feasible_table_count = 0

        elif normalized == "DQN":
            self.dqn_loss = 0.0
            self.dqn_q_value = 0.0
            self.dqn_target_q = 0.0
            self.dqn_td_error = 0.0
            self.dqn_replay_size = 0
            self.dqn_target_updates = 0
            self.dqn_explorations = 0
            self.dqn_exploitations = 0
            self.dqn_epsilon = 0.0

        elif normalized == "N-step Tree Backup":
            self.n_step_tree_backup_return = 0.0
            self.n_step_td_error = 0.0
            self.n_step_pending_transitions = 0
            self.n_step_explorations = 0
            self.n_step_exploitations = 0
            self.n_step_epsilon = 0.10

    def set_current_customers(self, value):
        self.current_customers = max(
            0,
            self._integer(value)
        )

    def set_waiting_queue(self, value):
        self.waiting_queue = max(
            0,
            self._integer(value)
        )

    def set_waiting_time(self, value):
        self.waiting_time_seconds = max(
            0.0,
            self._number(value)
        )

    def set_waiting_time_minutes(self, value):
        self.waiting_time_seconds = max(
            0.0,
            self._number(value) * 60.0
        )

    def sync_waiting_time(self, waiting_time_seconds):
        self.set_waiting_time(
            waiting_time_seconds
        )

    def set_average_wait_time(self, value):
        self.average_wait_time = max(
            0.0,
            self._number(value)
        )

    def set_tables_occupied(
        self,
        occupied,
        total=None
    ):
        self.tables_occupied = max(
            0,
            self._integer(occupied)
        )

        if total is not None:
            self.total_tables = max(
                1,
                self._integer(
                    total,
                    8
                )
            )

    def set_tables_ready(self, value):
        self.tables_ready = max(
            0,
            self._integer(value)
        )

    def set_tables_cleaning(self, value):
        self.tables_cleaning = max(
            0,
            self._integer(value)
        )

    def set_satisfaction(self, value):
        self.satisfaction = max(
            0.0,
            min(
                5.0,
                self._number(
                    value,
                    5.0
                )
            )
        )

    def set_episode(self, value):
        self.episode = max(
            0,
            self._integer(value)
        )

    def set_current_reward(self, value):
        self.current_reward = self._number(
            value
        )

        self.current_penalty = (
            self.current_reward
            if self.current_reward < 0
            else 0.0
        )

    def set_best_reward(self, value):
        self.best_reward = self._number(
            value
        )

    def set_penalty(self, value):
        self.current_penalty = self._number(
            value
        )

        self.last_penalty = (
            self.current_penalty
        )

    def set_total_penalties(self, value):
        self.total_penalties = max(
            0.0,
            self._number(value)
        )

    def set_waste_penalties(self, value):
        self.waste_penalties = max(
            0,
            self._integer(value)
        )

    def set_actor_updates(self, value):
        self.actor_updates = max(
            0,
            self._integer(value)
        )

    def set_critic_updates(self, value):
        self.critic_updates = max(
            0,
            self._integer(value)
        )

    def set_actor_loss(self, value):
        self.actor_loss = self._number(
            value
        )

    def set_critic_loss(self, value):
        self.critic_loss = self._number(
            value
        )

    def set_total_reward(self, value):
        self.total_reward = self._number(
            value
        )

        self._has_authoritative_total_reward = True

    def set_entropy(self, value):
        self.entropy = self._number(
            value
        )

    def set_q_updates(self, value):
        self.q_updates = max(
            0,
            self._integer(value)
        )

    def set_allocation_accuracy(self, value):
        self.allocation_accuracy = max(
            0.0,
            min(
                100.0,
                self._number(value)
            )
        )

    def set_total_decisions(self, value):
        self.total_decisions = max(
            0,
            self._integer(value)
        )

    def set_successful_allocations(self, value):
        self.successful_allocations = max(
            0,
            self._integer(value)
        )

    def set_latest_decision(
        self,
        group_size=None,
        table_id="--",
        table_capacity=None,
        result="--",
        reward=None,
        algorithm=None,
        reason=None
    ):
        self.last_group_size = group_size

        self.last_selected_table = (
            table_id
            if table_id
            else "--"
        )

        self.last_table_capacity = (
            table_capacity
        )

        self.last_decision_result = (
            str(result).upper()
            if result
            else "--"
        )

        self.last_reward = reward

        if algorithm is not None:
            self.last_decision_algorithm = (
                self._normalize_algorithm(
                    algorithm
                )
            )

        if reason is not None:
            self.last_decision_reason = (
                str(reason)
            )

        signature = (
            self.last_group_size,
            self.last_selected_table,
            self.last_table_capacity,
            self.last_decision_result,
            self._number(
                reward,
                0.0
            )
        )

        if (
            signature
            != self._last_decision_signature
        ):
            self._last_decision_signature = (
                signature
            )

            if (
                not self._has_authoritative_total_reward
                and reward is not None
            ):
                self.total_reward += (
                    self._number(reward)
                )

    def sync_latest_decision(self, decision):
        if not isinstance(
            decision,
            dict
        ):
            return

        self.set_latest_decision(
            group_size=decision.get(
                "group_size"
            ),
            table_id=decision.get(
                "table",
                "--"
            ),
            table_capacity=decision.get(
                "capacity"
            ),
            result=decision.get(
                "result",
                "--"
            ),
            reward=decision.get(
                "reward"
            ),
            algorithm=decision.get(
                "algorithm"
            ),
            reason=decision.get(
                "reason"
            )
        )

    def set_decision_reason(self, reason):
        self.last_decision_reason = (
            "--"
            if reason is None
            else str(reason)
        )

    def set_algorithm_info(self, info):
        if not isinstance(
            info,
            dict
        ):
            return

        self.algorithm_info = dict(
            info
        )

        if "Description" in info:
            self.algorithm_description = str(
                info["Description"]
            )

        if "Policy" in info:
            self.algorithm_policy = str(
                info["Policy"]
            )

        if "Learning" in info:
            self.algorithm_learning = str(
                info["Learning"]
            )

        if "Epsilon" in info:
            self.algorithm_exploration = str(
                info["Epsilon"]
            )

    def set_table_counts(
        self,
        occupied=None,
        ready=None,
        cleaning=None,
        total=None
    ):
        if occupied is not None:
            self.set_tables_occupied(
                occupied
            )

        if ready is not None:
            self.set_tables_ready(
                ready
            )

        if cleaning is not None:
            self.set_tables_cleaning(
                cleaning
            )

        if total is not None:
            self.total_tables = max(
                1,
                self._integer(
                    total,
                    8
                )
            )

    def sync_rl_statistics(self, statistics):
        if not isinstance(
            statistics,
            dict
        ):
            return

        merged = dict(
            statistics
        )

        nested_keys = (
            "actor_critic",
            "actor_critic_stats",
            "Actor-Critic",
            "actor_critic_statistics",
            "dqn",
            "dqn_stats",
            "DQN",
            "n_step",
            "n_step_tree_backup",
            "n_step_tree_backup_stats"
        )

        for key in nested_keys:
            nested = statistics.get(key)

            if isinstance(
                nested,
                dict
            ):
                merged.update(
                    nested
                )

        algorithm = self._pick(
            merged,
            "algorithm",
            "algorithm_name",
            default=None
        )

        if algorithm is not None:
            normalized = (
                self._normalize_algorithm(
                    algorithm
                )
            )

            if normalized in self.algorithms:
                self.selected_algorithm = (
                    normalized
                )

                self.selected_index = (
                    self.algorithms.index(
                        normalized
                    )
                )

        value = self._pick(
            merged,
            "episode",
            "step",
            "iteration",
            default=None
        )

        if value is not None:
            self.set_episode(
                value
            )

        value = self._pick(
            merged,
            "current_reward",
            "last_reward",
            "reward",
            default=None
        )

        if value is not None:
            self.set_current_reward(
                value
            )

        value = self._pick(
            merged,
            "best_reward",
            "max_reward",
            default=None
        )

        if value is not None:
            self.set_best_reward(
                value
            )

        q_value = self._pick(
            merged,
            "q_updates",
            "updates",
            "update_count",
            "learning_updates",
            default=None
        )

        if q_value is not None:
            self.set_q_updates(
                q_value
            )

        decisions = self._pick(
            merged,
            "total_decisions",
            "decisions",
            default=None
        )

        if decisions is not None:
            self.set_total_decisions(
                decisions
            )

        successes = self._pick(
            merged,
            "successful_allocations",
            "successes",
            default=None
        )

        if successes is not None:
            self.set_successful_allocations(
                successes
            )

        accuracy = self._pick(
            merged,
            "allocation_accuracy",
            "accuracy",
            default=None
        )

        if accuracy is not None:
            self.set_allocation_accuracy(
                accuracy
            )

        penalty = self._pick(
            merged,
            "penalty",
            "last_penalty",
            default=None
        )

        if penalty is not None:
            self.set_penalty(
                penalty
            )

        total_penalty = self._pick(
            merged,
            "total_penalties",
            "penalties",
            default=None
        )

        if total_penalty is not None:
            self.set_total_penalties(
                total_penalty
            )

        waste = self._pick(
            merged,
            "waste_penalties",
            "waste_penalty_count",
            default=None
        )

        if waste is not None:
            self.set_waste_penalties(
                waste
            )

        actor_updates = self._pick(
            merged,
            "actor_updates",
            "actor_update_count",
            "actor_steps",
            "policy_updates",
            default=None
        )

        critic_updates = self._pick(
            merged,
            "critic_updates",
            "critic_update_count",
            "critic_steps",
            "value_updates",
            default=None
        )

        if actor_updates is not None:
            self.set_actor_updates(
                actor_updates
            )

        if critic_updates is not None:
            self.set_critic_updates(
                critic_updates
            )

        if self.selected_algorithm == "Actor-Critic":
            fallback_updates = self._pick(
                merged,
                "q_updates",
                "updates",
                "update_count",
                "learning_updates",
                default=None
            )

            if (
                actor_updates is None
                and fallback_updates is not None
            ):
                self.set_actor_updates(
                    fallback_updates
                )

            if (
                critic_updates is None
                and fallback_updates is not None
            ):
                self.set_critic_updates(
                    fallback_updates
                )

            if (
                self.q_updates == 0
                and fallback_updates is not None
            ):
                self.set_q_updates(
                    fallback_updates
                )

        actor_loss = self._pick(
            merged,
            "actor_loss",
            "last_actor_loss",
            "policy_loss",
            "last_policy_loss",
            default=None
        )

        critic_loss = self._pick(
            merged,
            "critic_loss",
            "last_critic_loss",
            "value_loss",
            "last_value_loss",
            default=None
        )

        if actor_loss is not None:
            self.set_actor_loss(
                actor_loss
            )

        if critic_loss is not None:
            self.set_critic_loss(
                critic_loss
            )

        total_reward = self._pick(
            merged,
            "total_reward",
            "episode_reward",
            "cumulative_reward",
            "return",
            "total_return",
            default=None
        )

        if total_reward is not None:
            self.set_total_reward(
                total_reward
            )

        entropy = self._pick(
            merged,
            "entropy",
            "policy_entropy",
            "action_entropy",
            default=None
        )

        if entropy is not None:
            self.set_entropy(
                entropy
            )

        advantage = self._pick(
            merged,
            "advantage",
            "last_advantage",
            "td_advantage",
            "last_td_error",
            default=None
        )

        if advantage is not None:
            self.advantage = self._number(
                advantage
            )

        value_estimate = self._pick(
            merged,
            "value_estimate",
            "value",
            "state_value",
            "critic_value",
            "v_value",
            default=None
        )

        if value_estimate is not None:
            self.value_estimate = self._number(
                value_estimate
            )

        feasible = self._pick(
            merged,
            "feasible_table_count",
            "feasible_actions",
            "valid_actions",
            "available_actions",
            default=None
        )

        if feasible is not None:
            if isinstance(
                feasible,
                (list, tuple, set)
            ):
                self.feasible_table_count = (
                    len(feasible)
                )
            else:
                self.feasible_table_count = max(
                    0,
                    self._integer(feasible)
                )

        n_value = self._pick(
            merged,
            "n_step",
            "n",
            default=None
        )

        if n_value is not None:
            self.n_step = max(
                1,
                self._integer(
                    n_value,
                    3
                )
            )

        tree_return = self._pick(
            merged,
            "tree_backup_return",
            "last_tree_backup_return",
            "n_step_return",
            "return_value",
            default=None
        )

        if tree_return is not None:
            self.n_step_tree_backup_return = (
                self._number(
                    tree_return
                )
            )

        td_error = self._pick(
            merged,
            "td_error",
            "n_step_td_error",
            "last_td_error",
            default=None
        )

        if td_error is not None:
            if self.selected_algorithm == "N-step Tree Backup":
                self.n_step_td_error = (
                    self._number(td_error)
                )

            elif self.selected_algorithm == "DQN":
                self.dqn_td_error = (
                    self._number(td_error)
                )

        pending = self._pick(
            merged,
            "pending_transitions",
            "n_step_pending_transitions",
            "pending",
            default=None
        )

        if pending is not None:
            self.n_step_pending_transitions = max(
                0,
                self._integer(pending)
            )

        explorations = self._pick(
            merged,
            "n_step_explorations",
            "explorations",
            "exploration_count",
            default=None
        )

        exploitations = self._pick(
            merged,
            "n_step_exploitations",
            "exploitations",
            "exploitation_count",
            default=None
        )

        epsilon = self._pick(
            merged,
            "n_step_epsilon",
            "epsilon",
            default=None
        )

        if self.selected_algorithm == "N-step Tree Backup":
            if explorations is not None:
                self.n_step_explorations = max(
                    0,
                    self._integer(
                        explorations
                    )
                )

            if exploitations is not None:
                self.n_step_exploitations = max(
                    0,
                    self._integer(
                        exploitations
                    )
                )

            if epsilon is not None:
                self.n_step_epsilon = max(
                    0.0,
                    min(
                        1.0,
                        self._number(
                            epsilon,
                            0.10
                        )
                    )
                )

        dqn_loss = self._pick(
            merged,
            "dqn_loss",
            "loss",
            "last_loss",
            default=None
        )

        dqn_q = self._pick(
            merged,
            "last_q_value",
            "q_value",
            "current_q",
            default=None
        )

        dqn_target = self._pick(
            merged,
            "target_q",
            "target_value",
            "target",
            default=None
        )

        replay = self._pick(
            merged,
            "replay_size",
            "memory_size",
            "buffer_size",
            default=None
        )

        target_updates = self._pick(
            merged,
            "target_updates",
            "target_update_count",
            default=None
        )

        if dqn_loss is not None:
            self.dqn_loss = self._number(
                dqn_loss
            )

        if dqn_q is not None:
            self.dqn_q_value = self._number(
                dqn_q
            )

        if dqn_target is not None:
            self.dqn_target_q = self._number(
                dqn_target
            )

        if replay is not None:
            self.dqn_replay_size = max(
                0,
                self._integer(replay)
            )

        if target_updates is not None:
            self.dqn_target_updates = max(
                0,
                self._integer(target_updates)
            )

        if self.selected_algorithm == "DQN":
            if explorations is not None:
                self.dqn_explorations = max(
                    0,
                    self._integer(
                        explorations
                    )
                )

            if exploitations is not None:
                self.dqn_exploitations = max(
                    0,
                    self._integer(
                        exploitations
                    )
                )

            if epsilon is not None:
                self.dqn_epsilon = max(
                    0.0,
                    min(
                        1.0,
                        self._number(
                            epsilon
                        )
                    )
                )

        unused = self._pick(
            merged,
            "unused_seats",
            "last_unused_seats",
            default=None
        )

        if unused is not None:
            self.last_unused_seats = max(
                0,
                self._integer(unused)
            )

        self.update_algorithm_narration()

    def sync_algorithm_display(self, statistics):
        self.sync_rl_statistics(
            statistics
        )

    def set_n_step(self, value):
        self.n_step = max(
            1,
            self._integer(
                value,
                3
            )
        )

    def set_n_step_tree_backup_return(self, value):
        self.n_step_tree_backup_return = (
            self._number(value)
        )

    def set_n_step_td_error(self, value):
        self.n_step_td_error = (
            self._number(value)
        )

    def set_n_step_pending_transitions(self, value):
        self.n_step_pending_transitions = max(
            0,
            self._integer(value)
        )

    def set_n_step_explorations(self, value):
        self.n_step_explorations = max(
            0,
            self._integer(value)
        )

    def set_n_step_exploitations(self, value):
        self.n_step_exploitations = max(
            0,
            self._integer(value)
        )

    def set_n_step_epsilon(self, value):
        self.n_step_epsilon = max(
            0.0,
            min(
                1.0,
                self._number(value)
            )
        )

    def set_dqn_loss(self, value):
        self.dqn_loss = self._number(value)

    def set_dqn_q_value(self, value):
        self.dqn_q_value = self._number(value)

    def set_dqn_target_q(self, value):
        self.dqn_target_q = self._number(value)

    def set_dqn_td_error(self, value):
        self.dqn_td_error = self._number(value)

    def set_dqn_replay_size(self, value):
        self.dqn_replay_size = max(
            0,
            self._integer(value)
        )

    def set_dqn_target_updates(self, value):
        self.dqn_target_updates = max(
            0,
            self._integer(value)
        )

    def set_dqn_explorations(self, value):
        self.dqn_explorations = max(
            0,
            self._integer(value)
        )

    def set_dqn_exploitations(self, value):
        self.dqn_exploitations = max(
            0,
            self._integer(value)
        )

    def set_dqn_epsilon(self, value):
        self.dqn_epsilon = max(
            0.0,
            min(
                1.0,
                self._number(value)
            )
        )

    def reset_performance(self):
        self.successful_allocations = 0
        self.total_decisions = 0
        self.allocation_accuracy = 0.0
        self.current_reward = 0.0
        self.best_reward = 0.0
        self.current_penalty = 0.0
        self.total_penalties = 0.0
        self.waste_penalties = 0
        self.last_penalty = 0.0
        self.q_updates = 0
        self.episode = 0

        self.actor_updates = 0
        self.critic_updates = 0
        self.actor_loss = 0.0
        self.critic_loss = 0.0
        self.total_reward = 0.0
        self.entropy = 0.0
        self.advantage = 0.0
        self.value_estimate = 0.0
        self.last_unused_seats = None
        self.feasible_table_count = 0

        self.dqn_loss = 0.0
        self.dqn_q_value = 0.0
        self.dqn_target_q = 0.0
        self.dqn_td_error = 0.0
        self.dqn_replay_size = 0
        self.dqn_target_updates = 0
        self.dqn_explorations = 0
        self.dqn_exploitations = 0
        self.dqn_epsilon = 0.0

        self.n_step = 3
        self.n_step_tree_backup_return = 0.0
        self.n_step_td_error = 0.0
        self.n_step_pending_transitions = 0
        self.n_step_explorations = 0
        self.n_step_exploitations = 0
        self.n_step_epsilon = 0.0

        self._last_decision_signature = None
        self._has_authoritative_total_reward = False