# ============================================================
# AGENT.PY
# ============================================================
#
# METRIUS EATS
#
# Restaurant Table Allocation Agent
#
# RESPONSIBILITIES:
#
#   - Select tables
#   - Switch allocation algorithms
#   - Process WaitingPeopleInput
#   - Track allocation statistics
#   - Track waiting-time statistics
#   - Track Expected SARSA statistics
#   - Detect OCCUPIED -> FREE transitions
#   - Run independent cleaning timers
#   - Report latest allocation decision
#
# TABLE TIMING:
#
#   OCCUPIED
#       |
#       | tables.py handles 7-10 sec occupancy
#       v
#   FREE
#       |
#       | agent.py handles 5 sec cleaning delay
#       v
#   READY
#
# IMPORTANT:
#
# WaitingPeopleInput owns the real waiting queue.
#
# CustomerQueue on the left side is only visual.
#
# ============================================================


import random
import math

import messages


# ============================================================
# EXPECTED SARSA
# ============================================================
#
# Expected SARSA lives in expected_sarsa.py.
#
# We import it here so the RestaurantAgent can switch to it
# without main.py needing to know implementation details.
#
# ============================================================

try:

    from expected_sarsa import (
        ExpectedSARSAAlgorithm
    )

except ImportError:

    ExpectedSARSAAlgorithm = None

    print()
    print("========================================")
    print("[AGENT WARNING]")
    print("Could not import expected_sarsa.py")
    print("Expected SARSA will fall back to Default.")
    print("========================================")
    print()


# ============================================================
# ALGORITHM NAMES
# ============================================================

ALGORITHM_DEFAULT = "DEFAULT"

ALGORITHM_Q_LEARNING = "Q-LEARNING"

ALGORITHM_SARSA = "SARSA"

ALGORITHM_EXPECTED_SARSA = "EXPECTED SARSA"

ALGORITHM_DQN = "DQN"


# ============================================================
# DEFAULT ALGORITHM
# ============================================================

DEFAULT_ALGORITHM = (
    ALGORITHM_DEFAULT
)


# ============================================================
# CLEANING DELAY
# ============================================================
#
# A table becomes FREE after tables.py finishes the
# customer's occupancy period.
#
# Then the agent waits 5 seconds before the table becomes
# READY again.
#
# ============================================================

FREE_TABLE_DELAY = 5.0


# ============================================================
# BASE ALGORITHM
# ============================================================


class BaseAlgorithm:

    """
    Base class for table allocation algorithms.
    """

    def __init__(
        self,
        table_manager
    ):

        self.table_manager = (
            table_manager
        )


    def choose_table(
        self,
        group_size
    ):

        raise NotImplementedError


# ============================================================
# TABLE HELPERS
# ============================================================


def _get_table_capacity(
    table
):

    """
    Safely retrieve a table's capacity.

    Supports the normal TableManager table objects and
    provides a small amount of compatibility for different
    table implementations.
    """

    capacity = getattr(
        table,
        "capacity",
        None
    )

    if capacity is None:

        capacity = getattr(
            table,
            "max_capacity",
            None
        )

    if capacity is None:

        capacity = getattr(
            table,
            "seats",
            None
        )

    try:

        return int(
            capacity
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


def _is_table_occupied(
    table
):

    return bool(
        getattr(
            table,
            "occupied",
            False
        )
    )


# ============================================================
# DEFAULT ALGORITHM
# ============================================================


class DefaultAlgorithm(
    BaseAlgorithm
):

    """
    Baseline allocation.

    Rule:

        1. Table must not be occupied.
        2. Table must be READY.
        3. Table capacity must fit group.
        4. Choose smallest suitable table.
        5. Tie -> lowest table index.
    """


    def choose_table(
        self,
        group_size
    ):

        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            return None


        # ----------------------------------------------------
        # Candidate tables
        # ----------------------------------------------------

        candidates = []


        for index, table in enumerate(
            self.table_manager.tables
        ):

            # -----------------------------------------------
            # Occupied?
            # -----------------------------------------------

            if _is_table_occupied(
                table
            ):

                continue


            # -----------------------------------------------
            # Capacity
            # -----------------------------------------------

            capacity = _get_table_capacity(
                table
            )

            if capacity < group_size:

                continue


            # -----------------------------------------------
            # Ready?
            #
            # Agent maintains cleaning state.
            # If the table is not marked as cleaning by the
            # agent, it is considered available.
            # -----------------------------------------------

            candidates.append(
                (
                    capacity,
                    index
                )
            )


        if not candidates:

            return None


        # ----------------------------------------------------
        # Smallest suitable table
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1]
            )
        )


        return candidates[0][1]


# ============================================================
# Q-LEARNING PLACEHOLDER
# ============================================================


class QLearningAlgorithm(
    BaseAlgorithm
):

    def __init__(
        self,
        table_manager
    ):

        super().__init__(
            table_manager
        )

        self.learning_rate = 0.1

        self.discount_factor = 0.95

        self.epsilon = 0.1

        self.q_table = {}


    def choose_table(
        self,
        group_size
    ):

        print(
            "[Q-LEARNING] Placeholder algorithm called."
        )

        return None


# ============================================================
# SARSA PLACEHOLDER
# ============================================================


class SARSAAlgorithm(
    BaseAlgorithm
):

    def __init__(
        self,
        table_manager
    ):

        super().__init__(
            table_manager
        )

        self.learning_rate = 0.1

        self.discount_factor = 0.95

        self.epsilon = 0.1

        self.q_table = {}


    def choose_table(
        self,
        group_size
    ):

        print(
            "[SARSA] Placeholder algorithm called."
        )

        return None


# ============================================================
# DQN PLACEHOLDER
# ============================================================


class DQNAlgorithm(
    BaseAlgorithm
):

    def __init__(
        self,
        table_manager
    ):

        super().__init__(
            table_manager
        )

        self.learning_rate = 0.001

        self.discount_factor = 0.95

        self.epsilon = 0.1

        self.network = None

        self.target_network = None

        self.replay_buffer = []


    def choose_table(
        self,
        group_size
    ):

        print(
            "[DQN] Placeholder algorithm called."
        )

        return None


# ============================================================
# ALGORITHM FACTORY
# ============================================================


def create_algorithm(
    algorithm_name,
    table_manager
):

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if algorithm_name == ALGORITHM_DEFAULT:

        return DefaultAlgorithm(
            table_manager
        )


    # --------------------------------------------------------
    # Q-LEARNING
    # --------------------------------------------------------

    if algorithm_name == ALGORITHM_Q_LEARNING:

        return QLearningAlgorithm(
            table_manager
        )


    # --------------------------------------------------------
    # SARSA
    # --------------------------------------------------------

    if algorithm_name == ALGORITHM_SARSA:

        return SARSAAlgorithm(
            table_manager
        )


    # --------------------------------------------------------
    # EXPECTED SARSA
    # --------------------------------------------------------

    if algorithm_name == ALGORITHM_EXPECTED_SARSA:

        if ExpectedSARSAAlgorithm is None:

            print(
                "[AGENT ERROR] Expected SARSA unavailable."
            )

            print(
                "[AGENT] Falling back to DEFAULT."
            )

            return DefaultAlgorithm(
                table_manager
            )

        return ExpectedSARSAAlgorithm(
            table_manager
        )


    # --------------------------------------------------------
    # DQN
    # --------------------------------------------------------

    if algorithm_name == ALGORITHM_DQN:

        return DQNAlgorithm(
            table_manager
        )


    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    print(
        f"[AGENT WARNING] Unknown algorithm: "
        f"{algorithm_name}"
    )

    print(
        "[AGENT] Falling back to DEFAULT."
    )

    return DefaultAlgorithm(
        table_manager
    )


# ============================================================
# RESTAURANT AGENT
# ============================================================


class RestaurantAgent:

    """
    Main restaurant allocation agent.

    main.py communicates only with this class.

    Responsibilities:

        - allocation decisions
        - algorithm switching
        - queue processing
        - cleaning timers
        - performance statistics
        - latest decision information
    """
    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        table_manager,
        algorithm=DEFAULT_ALGORITHM
    ):

        self.table_manager = (
            table_manager
        )


        # ----------------------------------------------------
        # Algorithm
        # ----------------------------------------------------

        self.algorithm_name = (
            self._normalize_algorithm_name(
                algorithm
            )
        )

        self.algorithm = create_algorithm(
            self.algorithm_name,
            self.table_manager
        )


        # ----------------------------------------------------
        # Allocation statistics
        # ----------------------------------------------------

        self.total_decisions = 0

        self.successful_allocations = 0

        self.failed_allocations = 0


        # ----------------------------------------------------
        # Customer statistics
        # ----------------------------------------------------

        self.total_customers_served = 0


        # ----------------------------------------------------
        # Waiting-time statistics
        # ----------------------------------------------------

        self.simulation_elapsed_seconds = 0.0

        self.waiting_records = []

        self.completed_wait_times = []

        # Current waiting clock for the REAL WaitingPeopleInput
        # queue. It runs while at least one group is waiting and
        # pauses (without resetting) when the queue is empty.
        self.waiting_time_seconds = 0.0
        self.waiting_queue_active = False


        # ----------------------------------------------------
        # Queue processing
        # ----------------------------------------------------

        self.processing_queue = False


        # ----------------------------------------------------
        # Table state tracking
        # ----------------------------------------------------

        self.previous_occupied = {}

        self.free_timers = {}

        self.just_cleaned_tables = []

        # Tracks the last countdown number sent to the
        # in-game agent/chat message for each cleaning table.
        self.cleaning_message_seconds = {}


        # ----------------------------------------------------
        # RL statistics
        # ----------------------------------------------------

        self.current_reward = 0.0

        self.best_reward = 0.0

        self.q_updates = 0


        # ----------------------------------------------------
        # Latest decision
        # ----------------------------------------------------

        self.last_group_size = None

        self.last_selected_table = "--"

        self.last_table_capacity = None

        self.last_decision_result = "--"

        self.last_reward = None

        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )


        # ----------------------------------------------------
        # Initialize table states
        # ----------------------------------------------------

        self._initialize_table_states()


        # ----------------------------------------------------
        # Startup
        # ----------------------------------------------------

        print()

        print(
            "========================================"
        )

        print(
            "RESTAURANT AGENT INITIALIZED"
        )

        print(
            "========================================"
        )

        print(
            f"Active algorithm: "
            f"{self.algorithm_name}"
        )

        print(
            f"Cleaning delay: "
            f"{FREE_TABLE_DELAY:.0f} seconds"
        )

        print()


    # ========================================================
    # NORMALIZE ALGORITHM NAME
    # ========================================================

    def _normalize_algorithm_name(
        self,
        algorithm_name
    ):

        if algorithm_name is None:

            return DEFAULT_ALGORITHM


        value = str(
            algorithm_name
        ).strip().upper()


        mapping = {

            "DEFAULT":
                ALGORITHM_DEFAULT,

            "EXPECTED SARSA":
                ALGORITHM_EXPECTED_SARSA,

            "EXPECTED_SARSA":
                ALGORITHM_EXPECTED_SARSA,

            "Q-LEARNING":
                ALGORITHM_Q_LEARNING,

            "Q_LEARNING":
                ALGORITHM_Q_LEARNING,

            "SARSA":
                ALGORITHM_SARSA,

            "DQN":
                ALGORITHM_DQN
        }


        return mapping.get(
            value,
            ALGORITHM_DEFAULT
        )


    # ========================================================
    # DISPLAY ALGORITHM NAME
    # ========================================================

    def _display_algorithm_name(
        self
    ):

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
        ):

            return "Expected SARSA"


        if (
            self.algorithm_name
            ==
            ALGORITHM_Q_LEARNING
        ):

            return "Q-Learning"


        if (
            self.algorithm_name
            ==
            ALGORITHM_DEFAULT
        ):

            return "Default"


        return self.algorithm_name


    # ========================================================
    # INITIAL TABLE STATES
    # ========================================================

    def _initialize_table_states(
        self
    ):

        for index, table in enumerate(
            self.table_manager.tables
        ):

            self.previous_occupied[index] = (
                _is_table_occupied(
                    table
                )
            )


    # ========================================================
    # CHECK IF TABLE IS READY
    # ========================================================

    def is_table_ready(
        self,
        table_index
    ):

        if table_index in self.free_timers:

            return False


        if table_index < 0:

            return False


        if table_index >= len(
            self.table_manager.tables
        ):

            return False


        table = (
            self.table_manager.tables[
                table_index
            ]
        )


        if _is_table_occupied(
            table
        ):

            return False


        return True


    # ========================================================
    # GET READY TABLE INDICES
    # ========================================================

    def get_ready_table_indices(
        self
    ):

        ready = []


        for index, table in enumerate(
            self.table_manager.tables
        ):

            if self.is_table_ready(
                index
            ):

                ready.append(
                    index
                )


        return ready


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
        waiting_input=None
    ):

        try:

            dt_value = float(dt)

        except (
            TypeError,
            ValueError
        ):

            return


        if dt_value < 0:

            dt_value = 0.0


        # Pygame Clock.tick() returns milliseconds.
        # tables.py and main.py pass that value directly.
        # The agent cleaning timer, however, works in seconds.
        #
        # Example:
        #     16 ms -> 0.016 seconds
        #
        # Without this conversion, one frame could be treated
        # as 16 seconds, causing the 5-second cleaning timer to
        # finish immediately.
        dt_seconds = dt_value / 1000.0


        self.simulation_elapsed_seconds += (
            dt_seconds
        )

        # ----------------------------------------------------
        # REAL WAITING-QUEUE TIMER
        # ----------------------------------------------------
        #
        # WaitingPeopleInput is the real queue.
        # CustomerQueue is only visual.
        #
        # Queue has groups -> timer runs.
        # Queue is empty    -> timer pauses.
        #
        # IMPORTANT: it is NOT reset when the queue becomes
        # empty.
        # ----------------------------------------------------

        if waiting_input is not None:

            try:
                waiting_people = (
                    waiting_input.get_waiting_people()
                )
                queue_has_groups = bool(
                    waiting_people
                )
            except Exception:
                queue_has_groups = False

            self.waiting_queue_active = (
                queue_has_groups
            )

            if queue_has_groups:
                self.waiting_time_seconds += (
                    dt_seconds
                )


        # ----------------------------------------------------
        # Clear per-frame clean notifications
        # ----------------------------------------------------

        self.just_cleaned_tables = []


        # ----------------------------------------------------
        # Detect OCCUPIED -> FREE
        # ----------------------------------------------------

        for index, table in enumerate(
            self.table_manager.tables
        ):

            occupied = (
                _is_table_occupied(
                    table
                )
            )

            previous = (
                self.previous_occupied.get(
                    index,
                    occupied
                )
            )


            # ------------------------------------------------
            # OCCUPIED -> FREE
            # ------------------------------------------------

            if previous and not occupied:

                self.free_timers[index] = 0.0

                self.cleaning_message_seconds[index] = 5

                # Immediately show the first cleaning message.
                if (
                    waiting_input is not None
                    and hasattr(
                        waiting_input,
                        "set_agent_message"
                    )
                ):

                    try:

                        table_name = getattr(
                            table,
                            "table_id",
                            f"T{index + 1}"
                        )

                        waiting_input.set_agent_message(
                            messages.cleaning_table_message(
                                table_name,
                                5
                            )
                        )

                    except Exception as exc:

                        print(
                            f"[AGENT] Cleaning message warning: {exc}"
                        )

                print(
                    f"[AGENT] "
                    f"{getattr(table, 'table_id', f'T{index + 1}')} "
                    f"is FREE. Cleaning started."
                )


            self.previous_occupied[index] = (
                occupied
            )


        # ----------------------------------------------------
        # Update cleaning timers
        # ----------------------------------------------------

        finished = []


        for index in list(
            self.free_timers.keys()
        ):

            # Table may have become occupied again.
            # Safety guard.
            if (
                index >= len(
                    self.table_manager.tables
                )
            ):

                finished.append(
                    index
                )

                self.cleaning_message_seconds.pop(
                    index,
                    None
                )

                continue


            table = (
                self.table_manager.tables[
                    index
                ]
            )


            if _is_table_occupied(
                table
            ):

                finished.append(
                    index
                )

                self.cleaning_message_seconds.pop(
                    index,
                    None
                )

                continue


            self.free_timers[index] += (
                dt_seconds
            )


            # ------------------------------------------------
            # LIVE CLEANING COUNTDOWN
            # ------------------------------------------------

            remaining_seconds = (
                self.get_table_wait_time(
                    index
                )
            )

            countdown_seconds = max(
                1,
                int(
                    math.ceil(
                        remaining_seconds
                    )
                )
            )

            last_message_seconds = (
                self.cleaning_message_seconds.get(
                    index
                )
            )

            if (
                countdown_seconds
                !=
                last_message_seconds
            ):

                self.cleaning_message_seconds[index] = (
                    countdown_seconds
                )

                if (
                    waiting_input is not None
                    and hasattr(
                        waiting_input,
                        "set_agent_message"
                    )
                ):

                    try:

                        table_name = getattr(
                            table,
                            "table_id",
                            f"T{index + 1}"
                        )

                        waiting_input.set_agent_message(
                            messages.cleaning_table_message(
                                table_name,
                                countdown_seconds
                            )
                        )

                    except Exception as exc:

                        print(
                            f"[AGENT] Cleaning message warning: {exc}"
                        )


            # ------------------------------------------------
            # Cleaning complete
            # ------------------------------------------------

            if (
                self.free_timers[index]
                >=
                FREE_TABLE_DELAY
            ):

                table_name = getattr(
                    table,
                    "table_id",
                    f"T{index + 1}"
                )


                finished.append(
                    index
                )


                self.just_cleaned_tables.append(
                    table_name
                )

                self.cleaning_message_seconds.pop(
                    index,
                    None
                )

                if (
                    waiting_input is not None
                    and hasattr(
                        waiting_input,
                        "set_agent_message"
                    )
                ):

                    try:

                        waiting_input.set_agent_message(
                            messages.table_clean_message(
                                table_name
                            )
                        )

                    except Exception as exc:

                        print(
                            f"[AGENT] Ready message warning: {exc}"
                        )


                print(
                    f"[AGENT] "
                    f"{table_name} is clean and ready."
                )


        # ----------------------------------------------------
        # Remove finished timers
        # ----------------------------------------------------

        for index in finished:

            self.free_timers.pop(
                index,
                None
            )


    # ========================================================
    # CHOOSE TABLE
    # ========================================================

    def choose_table(
        self,
        group_size
    ):

        self.total_decisions += 1


        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            self.failed_allocations += 1

            return None


        print()

        print(
            "----------------------------------------"
        )

        print(
            "[AGENT] New allocation request"
        )

        print(
            f"[AGENT] Group size: "
            f"{group_size}"
        )

        print(
            f"[AGENT] Algorithm: "
            f"{self.algorithm_name}"
        )


        # ----------------------------------------------------
        # Expected SARSA
        # ----------------------------------------------------

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
        ):

            try:

                table_index = (
                    self.algorithm.choose_table(
                        group_size,
                        ready_checker=self.is_table_ready
                    )
                )

            except TypeError:

                table_index = (
                    self.algorithm.choose_table(
                        group_size
                    )
                )


        # ----------------------------------------------------
        # Other algorithms
        # ----------------------------------------------------

        else:

            table_index = (
                self._choose_table_without_counting(
                    group_size
                )
            )


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        if table_index is None:

            self.failed_allocations += 1

            print(
                "[AGENT] No suitable table available."
            )

            print(
                "----------------------------------------"
            )

            return None


        print(
            f"[AGENT] Selected table index: "
            f"{table_index}"
        )

        print(
            "----------------------------------------"
        )


        return table_index


    # ========================================================
    # CHOOSE WITHOUT INCREMENTING DECISION COUNT
    # ========================================================

    def _choose_table_without_counting(
        self,
        group_size
    ):

        if (
            self.algorithm_name
            ==
            ALGORITHM_DEFAULT
        ):

            # Default algorithm needs to respect cleaning.
            return self._default_ready_table(
                group_size
            )


        try:

            return self.algorithm.choose_table(
                group_size
            )

        except Exception as exc:

            print(
                f"[AGENT WARNING] Algorithm error: "
                f"{exc}"
            )

            return None


    # ========================================================
    # DEFAULT READY TABLE
    # ========================================================

    def _default_ready_table(
        self,
        group_size
    ):

        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            return None


        candidates = []


        for index, table in enumerate(
            self.table_manager.tables
        ):

            if not self.is_table_ready(
                index
            ):

                continue


            capacity = _get_table_capacity(
                table
            )


            if capacity < group_size:

                continue


            candidates.append(
                (
                    capacity,
                    index
                )
            )


        if not candidates:

            return None


        candidates.sort(
            key=lambda item: (
                item[0],
                item[1]
            )
        )


        return candidates[0][1]


    # ========================================================
    # ALLOCATE GROUP
    # ========================================================

    def allocate_group(
        self,
        group_size
    ):

        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            return None


        # ----------------------------------------------------
        # Make one decision
        # ----------------------------------------------------

        table_index = self.choose_table(
            group_size
        )


        # ----------------------------------------------------
        # No table
        # ----------------------------------------------------

        if table_index is None:

            self._record_failed_decision(
                group_size
            )

            return None


        # ----------------------------------------------------
        # Validate index
        # ----------------------------------------------------

        if not isinstance(
            table_index,
            int
        ):

            try:

                table_index = int(
                    table_index
                )

            except (
                TypeError,
                ValueError
            ):

                self._record_failed_decision(
                    group_size
                )

                return None


        if (
            table_index < 0
            or
            table_index >= len(
                self.table_manager.tables
            )
        ):

            print(
                "[AGENT] Invalid table index."
            )

            self._record_failed_decision(
                group_size
            )

            return None


        # ----------------------------------------------------
        # Validate READY state
        # ----------------------------------------------------

        if not self.is_table_ready(
            table_index
        ):

            print(
                "[AGENT] Selected table is not READY."
            )

            self._record_failed_decision(
                group_size
            )

            return None


        table = (
            self.table_manager.tables[
                table_index
            ]
        )


        table_name = getattr(
            table,
            "table_id",
            f"T{table_index + 1}"
        )


        table_capacity = _get_table_capacity(
            table
        )


        # ----------------------------------------------------
        # Validate capacity
        # ----------------------------------------------------

        if table_capacity < group_size:

            print(
                "[AGENT] Selected table is too small."
            )

            self._record_failed_decision(
                group_size,
                table_name,
                table_capacity,
                -100.0
            )

            return None

        # ----------------------------------------------------
        # Capture valid actions BEFORE occupancy changes the
        # state. This is needed for S -> A -> R -> S'.
        # ----------------------------------------------------

        valid_actions_before = None

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
        ):

            try:

                valid_actions_before = (
                    self.algorithm.get_valid_actions(
                        group_size,
                        self.table_manager.tables,
                        ready_checker=self.is_table_ready
                    )
                )

            except TypeError:

                try:

                    valid_actions_before = (
                        self.algorithm.get_valid_actions(
                            group_size,
                            self.table_manager.tables
                        )
                    )

                except Exception:

                    valid_actions_before = None

            except Exception:

                valid_actions_before = None


        # ====================================================
        # EXPECTED SARSA:
        #
        # S -> A -> R -> S'
        # ====================================================

        previous_state = None

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
        ):

            try:

                previous_state = (
                    self.algorithm.get_state(
                        group_size,
                        self.table_manager.tables,
                        ready_checker=self.is_table_ready
                    )
                )

            except TypeError:

                try:

                    previous_state = (
                        self.algorithm.get_state(
                            group_size,
                            self.table_manager.tables
                        )
                    )

                except Exception:

                    previous_state = None

            except Exception:

                previous_state = None


        # ----------------------------------------------------
        # Determine reward
        # ----------------------------------------------------

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
            and
            hasattr(
                self.algorithm,
                "get_immediate_reward"
            )
        ):

            reward = self.algorithm.get_immediate_reward(
                group_size,
                table_index,
                self.table_manager.tables,
                ready_checker=self.is_table_ready,
                success=True,
                valid_actions=valid_actions_before
            )

        else:

            reward = self._calculate_reward(
                group_size,
                table_index,
                table_capacity,
                valid_actions=valid_actions_before
            )


        # ----------------------------------------------------
        # Actually occupy the table
        # ----------------------------------------------------

        allocation_success = (
            self._occupy_table(
                table,
                group_size
            )
        )


        if not allocation_success:

            self._record_failed_decision(
                group_size,
                table_name,
                table_capacity,
                reward
            )

            return None


        # ====================================================
        # SUCCESS
        # ====================================================

        self.successful_allocations += 1

        self.total_customers_served += (
            group_size
        )


        self.current_reward = (
            float(reward)
        )


        if self.current_reward > self.best_reward:

            self.best_reward = (
                self.current_reward
            )


        # ----------------------------------------------------
        # Latest decision
        # ----------------------------------------------------

        self.last_group_size = (
            group_size
        )

        self.last_selected_table = (
            table_name
        )

        self.last_table_capacity = (
            table_capacity
        )

        self.last_decision_result = (
            "SUCCESS"
        )

        self.last_reward = (
            float(reward)
        )

        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )


        # ----------------------------------------------------
        # Expected SARSA learning
        # ----------------------------------------------------

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
        ):

            try:

                next_state = (
                    self.algorithm.get_state(
                        group_size,
                        self.table_manager.tables,
                        ready_checker=self.is_table_ready
                    )
                )

            except TypeError:

                try:

                    next_state = (
                        self.algorithm.get_state(
                            group_size,
                            self.table_manager.tables
                        )
                    )

                except Exception:

                    next_state = None

            except Exception:

                next_state = None


            # Next valid actions are calculated AFTER the selected
            # table becomes occupied.
            next_valid_actions = []

            try:

                next_valid_actions = (
                    self.algorithm.get_valid_actions(
                        group_size,
                        self.table_manager.tables,
                        ready_checker=self.is_table_ready
                    )
                )

            except TypeError:

                try:

                    next_valid_actions = (
                        self.algorithm.get_valid_actions(
                            group_size,
                            self.table_manager.tables
                        )
                    )

                except Exception:

                    next_valid_actions = []

            except Exception:

                next_valid_actions = []


            if (
                previous_state is not None
                and
                next_state is not None
                and
                hasattr(
                    self.algorithm,
                    "learn_after_allocation"
                )
            ):

                try:

                    result = (
                        self.algorithm.learn_after_allocation(
                            previous_state,
                            table_index,
                            reward,
                            next_state,
                            next_valid_actions
                        )
                    )

                    if result is not False:

                        self.q_updates += 1

                except Exception as exc:

                    print(
                        "[AGENT] Expected SARSA learning "
                        f"warning: {exc}"
                    )


        # ----------------------------------------------------
        # Console
        # ----------------------------------------------------

        print()

        print(
            "========================================"
        )

        print(
            "[AGENT] ALLOCATION SUCCESS"
        )

        print(
            f"Group: "
            f"{group_size}"
        )

        print(
            f"Table: "
            f"{table_name}"
        )

        print(
            f"Capacity: "
            f"{table_capacity}"
        )

        print(
            f"Reward: "
            f"{reward:+.2f}"
        )

        print(
            f"Algorithm: "
            f"{self.algorithm_name}"
        )

        print(
            "========================================"
        )

        print()


        return table


    # ========================================================
    # OCCUPY TABLE
    # ========================================================

    def _occupy_table(
        self,
        table,
        group_size
    ):

        """
        Try the common TableManager/table APIs without
        forcing one specific tables.py implementation.
        """

        # ----------------------------------------------------
        # Method 1: assign_customers
        # ----------------------------------------------------

        if hasattr(
            table,
            "assign_customers"
        ):

            try:

                result = table.assign_customers(
                    group_size
                )

                return (
                    result is not False
                )

            except TypeError:

                try:

                    result = table.assign_customers()

                    return (
                        result is not False
                    )

                except Exception:

                    pass

            except Exception:

                pass


        # ----------------------------------------------------
        # Method 2: seat_customers
        # ----------------------------------------------------

        if hasattr(
            table,
            "seat_customers"
        ):

            try:

                result = table.seat_customers(
                    group_size
                )

                return (
                    result is not False
                )

            except Exception:

                pass


        # ----------------------------------------------------
        # Method 3: occupy
        # ----------------------------------------------------

        if hasattr(
            table,
            "occupy"
        ):

            try:

                result = table.occupy(
                    group_size
                )

                return (
                    result is not False
                )

            except TypeError:

                try:

                    result = table.occupy()

                    return (
                        result is not False
                    )

                except Exception:

                    pass

            except Exception:

                pass


        # ----------------------------------------------------
        # TableManager method
        # ----------------------------------------------------

        for method_name in (
            "assign_table",
            "occupy_table",
            "seat_group",
            "allocate_table"
        ):

            if not hasattr(
                self.table_manager,
                method_name
            ):

                continue


            method = getattr(
                self.table_manager,
                method_name
            )


            try:

                result = method(
                    table,
                    group_size
                )

                return (
                    result is not False
                )

            except TypeError:

                try:

                    result = method(
                        table
                    )

                    return (
                        result is not False
                    )

                except Exception:

                    continue

            except Exception:

                continue


        # ----------------------------------------------------
        # Last-resort direct state
        # ----------------------------------------------------
        #
        # This keeps compatibility with simple table objects.
        #
        # tables.py remains responsible for the actual
        # occupancy duration.
        # ----------------------------------------------------

        if hasattr(
            table,
            "occupied"
        ):

            try:

                table.occupied = True

                return True

            except Exception:

                pass


        return False


    # ========================================================
    # CALCULATE REWARD
    # ========================================================

    def _calculate_reward(
        self,
        group_size,
        table_index,
        table_capacity,
        valid_actions=None
    ):
        """
        Calculate allocation reward.

        A larger table is still VALID when it can seat the group.
        The reward teaches Expected SARSA which valid choice is
        more efficient.

        Reward policy:
            exact fit       -> +15
            1 unused seat   -> +10
            2 unused seats  -> +5
            3+ unused seats -> +1
            invalid         -> -100
        """

        try:
            group_size = int(group_size)
            table_index = int(table_index)
            table_capacity = int(table_capacity)
        except (TypeError, ValueError):
            return -100.0

        if group_size <= 0:
            return -100.0

        if table_capacity < group_size:
            return -100.0

        if valid_actions is not None:
            if table_index not in valid_actions:
                return -100.0

        unused_seats = table_capacity - group_size

        if unused_seats == 0:
            return 15.0

        if unused_seats == 1:
            return 10.0

        if unused_seats == 2:
            return 5.0

        return 1.0


    # ========================================================
    # FAILED DECISION
    # ========================================================

    def _record_failed_decision(
        self,
        group_size,
        table_name="--",
        table_capacity=None,
        reward=None
    ):

        self.failed_allocations += 1


        if reward is None:

            reward = -100.0


        self.current_reward = (
            float(reward)
        )


        self.last_group_size = (
            group_size
        )

        self.last_selected_table = (
            table_name
            if table_name
            else "--"
        )

        self.last_table_capacity = (
            table_capacity
        )

        self.last_decision_result = (
            "FAILED"
        )

        self.last_reward = (
            float(reward)
        )

        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )


    # ========================================================
    # PROCESS WAITING QUEUE
    # ========================================================

    def process_waiting_queue(
        self,
        waiting_input,
        dt=0
    ):

        if waiting_input is None:

            return None


        if self.processing_queue:

            return None


        self.processing_queue = True


        try:

            # ------------------------------------------------
            # Get waiting groups
            # ------------------------------------------------

            waiting_people = (
                waiting_input.get_waiting_people()
            )


            if not waiting_people:

                return None


            # ------------------------------------------------
            # Normalize queue
            # ------------------------------------------------

            groups = []


            for item in waiting_people:

                try:

                    # Some queue versions store plain
                    # integers.
                    if isinstance(
                        item,
                        (int, float)
                    ):

                        groups.append(
                            (
                                int(item),
                                None
                            )
                        )

                    # Some store dictionaries.
                    elif isinstance(
                        item,
                        dict
                    ):

                        size = (
                            item.get(
                                "group_size",
                                item.get(
                                    "people",
                                    item.get(
                                        "size",
                                        0
                                    )
                                )
                            )
                        )

                        try:

                            size = int(
                                size
                            )

                        except (
                            TypeError,
                            ValueError
                        ):

                            continue


                        groups.append(
                            (
                                size,
                                item
                            )
                        )

                    # Some store tuples/lists.
                    elif isinstance(
                        item,
                        (list, tuple)
                    ):

                        if len(item) == 0:

                            continue


                        try:

                            size = int(
                                item[0]
                            )

                        except (
                            TypeError,
                            ValueError
                        ):

                            continue


                        groups.append(
                            (
                                size,
                                item
                            )
                        )

                    else:

                        try:

                            groups.append(
                                (
                                    int(item),
                                    item
                                )
                            )

                        except (
                            TypeError,
                            ValueError
                        ):

                            continue


                except Exception:

                    continue


            if not groups:

                return None


            # ------------------------------------------------
            # Find first compatible group
            # ------------------------------------------------
            #
            # A large first group should not permanently block
            # a smaller group behind it.
            #
            # Only ONE group is allocated per frame.
            #
            # ------------------------------------------------

            selected_queue_index = None

            selected_group_size = None


            for queue_index, item in enumerate(
                groups
            ):

                group_size = item[0]


                # Quickly check whether a compatible READY
                # table exists.
                if self._has_suitable_ready_table(
                    group_size
                ):

                    selected_queue_index = (
                        queue_index
                    )

                    selected_group_size = (
                        group_size
                    )

                    break


            # ------------------------------------------------
            # No compatible table
            # ------------------------------------------------

            if selected_queue_index is None:

                return None


            print()

            print(
                "========================================"
            )

            print(
                "[AGENT QUEUE] Processing waiting group"
            )

            print(
                f"[AGENT QUEUE] Group: "
                f"{selected_group_size}"
            )

            print(
                f"[AGENT QUEUE] Queue index: "
                f"{selected_queue_index}"
            )

            print(
                "========================================"
            )


            # ------------------------------------------------
            # Allocate
            # ------------------------------------------------

            table = (
                self.allocate_group(
                    selected_group_size
                )
            )


            if table is None:

                return None


            # ------------------------------------------------
            # Update agent message
            # ------------------------------------------------

            table_name = getattr(
                table,
                "table_id",
                f"T{self._find_table_index(table) + 1}"
            )


            if hasattr(
                waiting_input,
                "set_agent_decision"
            ):

                try:

                    waiting_input.set_agent_decision(
                        selected_group_size,
                        table_name
                    )

                except Exception:

                    pass


            # ------------------------------------------------
            # Remove selected group
            # ------------------------------------------------

            self._remove_waiting_group(
                waiting_input,
                selected_queue_index,
                selected_group_size
            )

            # Preserve the accumulated waiting time as a
            # completed record. The live timer itself is not
            # reset; it pauses if no groups remain.
            if self.waiting_time_seconds > 0:

                self.completed_wait_times.append(
                    self.waiting_time_seconds
                )


            print(
                f"[AGENT QUEUE] "
                f"{selected_group_size} people "
                f"assigned to {table_name}."
            )


            return table


        finally:

            self.processing_queue = False


    # ========================================================
    # HAS SUITABLE READY TABLE
    # ========================================================

    def _has_suitable_ready_table(
        self,
        group_size
    ):

        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            return False


        for index, table in enumerate(
            self.table_manager.tables
        ):

            if not self.is_table_ready(
                index
            ):

                continue


            capacity = _get_table_capacity(
                table
            )


            if capacity >= group_size:

                return True


        return False


    # ========================================================
    # FIND TABLE INDEX
    # ========================================================

    def _find_table_index(
        self,
        table
    ):

        for index, current_table in enumerate(
            self.table_manager.tables
        ):

            if current_table is table:

                return index


        return 0


    # ========================================================
    # REMOVE WAITING GROUP
    # ========================================================

    def _remove_waiting_group(
        self,
        waiting_input,
        queue_index,
        group_size
    ):

        # ----------------------------------------------------
        # Preferred API
        # ----------------------------------------------------

        if hasattr(
            waiting_input,
            "remove_group"
        ):

            try:

                waiting_input.remove_group(
                    queue_index
                )

                return True

            except Exception:

                pass


        # ----------------------------------------------------
        # Direct list compatibility
        # ----------------------------------------------------

        for attribute_name in (
            "waiting_people",
            "waiting_groups",
            "queue"
        ):

            if not hasattr(
                waiting_input,
                attribute_name
            ):

                continue


            records = getattr(
                waiting_input,
                attribute_name
            )


            if isinstance(
                records,
                list
            ):

                if (
                    queue_index >= 0
                    and
                    queue_index < len(records)
                ):

                    records.pop(
                        queue_index
                    )

                    return True


        return False


    # ========================================================
    # SET ALGORITHM
    # ========================================================

    def set_algorithm(
        self,
        algorithm_name,
        waiting_input=None
    ):

        new_algorithm_name = (
            self._normalize_algorithm_name(
                algorithm_name
            )
        )


        # ----------------------------------------------------
        # Same algorithm
        # ----------------------------------------------------

        if (
            new_algorithm_name
            ==
            self.algorithm_name
        ):

            return False


        old_algorithm = (
            self.algorithm_name
        )


        # ----------------------------------------------------
        # Change
        # ----------------------------------------------------

        self.algorithm_name = (
            new_algorithm_name
        )


        self.algorithm = create_algorithm(
            self.algorithm_name,
            self.table_manager
        )


        # ----------------------------------------------------
        # Reset current RL display values
        # ----------------------------------------------------

        self.current_reward = 0.0

        self.q_updates = 0


        # ----------------------------------------------------
        # Console
        # ----------------------------------------------------

        print()

        print(
            "========================================"
        )

        print(
            "[AGENT] ALGORITHM SWITCHED"
        )

        print(
            f"[AGENT] "
            f"{old_algorithm}"
            f" -> "
            f"{self.algorithm_name}"
        )

        print(
            "========================================"
        )

        print()


        # ----------------------------------------------------
        # Communication message
        # ----------------------------------------------------

        if (
            waiting_input is not None
            and
            hasattr(
                waiting_input,
                "set_agent_message"
            )
        ):

            try:

                if (
                    self.algorithm_name
                    ==
                    ALGORITHM_EXPECTED_SARSA
                ):

                    waiting_input.set_agent_message(
                        messages.expected_sarsa_switched_message()
                    )

                elif (
                    self.algorithm_name
                    ==
                    ALGORITHM_DEFAULT
                ):

                    waiting_input.set_agent_message(
                        messages.default_algorithm_switched_message()
                    )

                else:

                    waiting_input.set_agent_message(
                        messages.algorithm_switched_message(
                            self.algorithm_name
                        )
                    )

            except Exception as exc:

                print(
                    f"[AGENT] Message warning: {exc}"
                )


        return True


    # ========================================================
    # GET ALGORITHM NAME
    # ========================================================

    def get_algorithm_name(
        self
    ):

        return self.algorithm_name


    # ========================================================
    # GET LATEST DECISION
    # ========================================================

    def get_latest_decision(
        self
    ):

        return {

            "group_size":
                self.last_group_size,

            "table":
                self.last_selected_table,

            "capacity":
                self.last_table_capacity,

            "result":
                self.last_decision_result,

            "reward":
                self.last_reward,

            "algorithm":
                self.last_decision_algorithm
        }


    # ========================================================
    # RL STATISTICS
    # ========================================================

    def get_rl_statistics(
        self
    ):

        accuracy = 0.0


        if self.total_decisions > 0:

            accuracy = (
                self.successful_allocations
                /
                self.total_decisions
                *
                100.0
            )


        statistics = {

            "algorithm":
                self.algorithm_name,

            "episode":
                self.total_decisions,

            "current_reward":
                self.current_reward,

            "best_reward":
                self.best_reward,

            "q_updates":
                self.q_updates,

            "allocation_accuracy":
                accuracy
        }

        if (
            self.algorithm_name
            ==
            ALGORITHM_EXPECTED_SARSA
            and
            hasattr(
                self.algorithm,
                "get_statistics"
            )
        ):

            try:

                sarsa_stats = (
                    self.algorithm.get_statistics()
                )

                statistics.update({

                    "total_reward":
                        sarsa_stats.get(
                            "total_reward",
                            0.0
                        ),

                    "total_penalties":
                        sarsa_stats.get(
                            "total_penalties",
                            0.0
                        ),

                    "epsilon":
                        sarsa_stats.get(
                            "epsilon",
                            0.10
                        )
                })

            except Exception:

                pass

        return statistics


    # ========================================================
    # GENERAL STATISTICS
    # ========================================================

    def get_statistics(
        self
    ):

        return {

            "algorithm":
                self.algorithm_name,

            "total_decisions":
                self.total_decisions,

            "successful_allocations":
                self.successful_allocations,

            "customers_served":
                self.total_customers_served,

            "average_wait_time":
                self.get_average_wait_time(),

            "waiting_time_seconds":
                self.get_waiting_time_seconds(),

            "waiting_queue_active":
                self.waiting_queue_active,

            "satisfaction":
                self.get_satisfaction(),

            "failed_allocations":
                self.failed_allocations,

            "current_reward":
                self.current_reward,

            "best_reward":
                self.best_reward,

            "q_updates":
                self.q_updates
        }


    # ========================================================
    # CURRENT WAIT TIME
    # ========================================================

    def get_waiting_time_seconds(
        self
    ):

        return float(
            self.waiting_time_seconds
        )


    # ========================================================
    # AVERAGE WAIT TIME
    # ========================================================

    def get_average_wait_time(
        self
    ):

        if not self.completed_wait_times:

            return 0.0


        return (
            sum(
                self.completed_wait_times
            )
            /
            len(
                self.completed_wait_times
            )
            /
            60.0
        )


    # ========================================================
    # SATISFACTION
    # ========================================================

    def get_satisfaction(
        self
    ):

        if self.total_decisions <= 0:

            return 5.0


        if self.successful_allocations <= 0:

            return 1.0


        accuracy = (
            self.successful_allocations
            /
            self.total_decisions
        )


        # Keep satisfaction within 1-5.
        return max(
            1.0,
            min(
                5.0,
                1.0
                +
                accuracy * 4.0
            )
        )


    # ========================================================
    # GET TABLE COUNTS
    # ========================================================

    def get_table_counts(
        self
    ):

        occupied = 0

        ready = 0

        cleaning = 0


        for index, table in enumerate(
            self.table_manager.tables
        ):

            if _is_table_occupied(
                table
            ):

                occupied += 1

            elif index in self.free_timers:

                cleaning += 1

            else:

                ready += 1


        return {

            "occupied":
                occupied,

            "ready":
                ready,

            "cleaning":
                cleaning,

            "total":
                len(
                    self.table_manager.tables
                )
        }

    


    # ========================================================
    # GET TABLE CLEANING TIME REMAINING
    # ========================================================
    #
    # Returns the remaining cleaning time for a table.
    #
    # This MUST be inside RestaurantAgent because main.py calls:
    #
    #     agent.get_table_wait_time(table_index)
    #
    # ========================================================

    def get_table_wait_time(
        self,
        table_index
    ):

        try:

            table_index = int(
                table_index
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0


        if table_index not in self.free_timers:

            return 0.0


        elapsed = (
            self.free_timers[
                table_index
            ]
        )


        remaining = (
            FREE_TABLE_DELAY
            -
            elapsed
        )


        return max(
            0.0,
            remaining
        )


    # ========================================================
    # PRINT STATISTICS
    # ========================================================

    def print_statistics(
        self
    ):

        statistics = (
            self.get_statistics()
        )


        print()

        print(
            "========================================"
        )

        print(
            "AGENT STATISTICS"
        )

        print(
            "========================================"
        )

        print(
            f"Algorithm: "
            f"{statistics['algorithm']}"
        )

        print(
            f"Total decisions: "
            f"{statistics['total_decisions']}"
        )

        print(
            f"Successful allocations: "
            f"{statistics['successful_allocations']}"
        )

        print(
            f"Customers served: "
            f"{statistics['customers_served']}"
        )

        print(
            f"Failed allocations: "
            f"{statistics['failed_allocations']}"
        )

        print(
            f"Average wait time: "
            f"{statistics['average_wait_time']:.2f} min"
        )

        print(
            f"Satisfaction: "
            f"{statistics['satisfaction']:.2f}/5"
        )

        print(
            f"Current reward: "
            f"{statistics['current_reward']:.2f}"
        )

        print(
            f"Best reward: "
            f"{statistics['best_reward']:.2f}"
        )

        print(
            f"Q updates: "
            f"{statistics['q_updates']}"
        )

        print(
            "========================================"
        )

        print()


# ============================================================
# END OF AGENT.PY
# ============================================================