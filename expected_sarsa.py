"""
============================================================
METRIUS EATS - EXPECTED SARSA
============================================================

Online Expected SARSA.

There is NO separate training phase.

The algorithm learns during the actual restaurant simulation:

    state -> action -> reward -> next state -> Q update


============================================================
STATE
============================================================

State:

    (
        group_size,
        status_T1,
        status_T2,
        ...
        status_T8
    )

Status:

    0 = READY
    1 = OCCUPIED
    2 = CLEANING


============================================================
ACTION
============================================================

Action:

    table index 0..7

IMPORTANT:

A table is VALID when:

    - it is READY
    - it has enough capacity

A larger table is NOT automatically invalid.

For example:

    1 person -> 2 seat table   VALID
    1 person -> 4 seat table   VALID
    1 person -> 6 seat table   VALID

Expected SARSA learns which choice is better
through the reward signal.


============================================================
REWARD PHILOSOPHY
============================================================

Exact fit:

    4 people -> 4 seat table
    +15

One unused seat:

    3 people -> 4 seat table
    +10

Two unused seats:

    1 person -> 3 seat table
    +5

Three or more unused seats:

    1 person -> 4/6 seat table
    -5

INVALID:

    6 people -> 2 seat table
    -100

WAIT:

    No suitable READY table
    -1


The important idea is:

    VALID != GOOD

A large table can be valid but receive
a penalty when it wastes too much capacity.

This allows Expected SARSA to LEARN
the best allocation policy.
"""

from collections import defaultdict
import random


# ============================================================
# HYPERPARAMETERS
# ============================================================

LEARNING_RATE = 0.20
DISCOUNT_FACTOR = 0.90
EPSILON = 0.10


# ============================================================
# REWARDS
# ============================================================

# Exact capacity match.
EXACT_FIT_REWARD = 15.0

# One unused seat.
ONE_UNUSED_SEAT_REWARD = 10.0

# Two unused seats.
TWO_UNUSED_SEATS_REWARD = 5.0

# Three or more unused seats.
# This is now a REAL PENALTY.
LARGE_WASTE_REWARD = -5.0

# Impossible / invalid action.
INVALID_ACTION_REWARD = -100.0

# No suitable table available.
WAIT_REWARD = -1.0


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================
#
# These names may be referenced by older parts of the project.
#
# They are intentionally kept here so existing imports do not
# break.
#

SUCCESS_REWARD = EXACT_FIT_REWARD

BEST_FIT_BONUS = 0.0

# Kept for compatibility with older project code.
# The actual oversized-table penalty is represented by
# LARGE_WASTE_REWARD.
OVERSIZED_TABLE_PENALTY = abs(
    LARGE_WASTE_REWARD
)


# ============================================================
# EXPECTED SARSA
# ============================================================

class ExpectedSARSAAlgorithm:

    def __init__(
        self,
        table_manager,
        learning_rate=LEARNING_RATE,
        discount_factor=DISCOUNT_FACTOR,
        epsilon=EPSILON,
        console_logging=True,
    ):

        self.table_manager = table_manager

        self.learning_rate = float(
            learning_rate
        )

        self.discount_factor = float(
            discount_factor
        )

        self.epsilon = float(
            epsilon
        )

        self.console_logging = bool(
            console_logging
        )

        # ====================================================
        # Q TABLE
        # ====================================================

        self.q_table = defaultdict(dict)

        # ====================================================
        # LIVE STATISTICS
        # ====================================================

        self.total_updates = 0

        self.total_allocations = 0

        self.total_explorations = 0

        self.total_exploitations = 0

        self.total_reward = 0.0

        # ====================================================
        # REWARD STATISTICS
        # ====================================================

        self.total_positive_rewards = 0.0

        self.total_penalties = 0.0

        self.invalid_action_count = 0

        self.wait_count = 0

        self.success_count = 0

        self.exact_fit_count = 0

        self.inefficient_allocation_count = 0

        # Number of valid allocations that received the
        # large-waste penalty.
        self.waste_penalty_count = 0

        # ====================================================
        # LAST TRANSITION
        # ====================================================

        self.last_state = None

        self.last_action = None

        self.last_reward = 0.0

        self.last_next_state = None

        self.last_expected_value = 0.0

        self._log(
            "[EXPECTED SARSA] Initialized | "
            f"alpha={self.learning_rate:.2f}, "
            f"gamma={self.discount_factor:.2f}, "
            f"epsilon={self.epsilon:.2f}"
        )

    # ========================================================
    # LOGGING
    # ========================================================

    def _log(
        self,
        text
    ):

        if self.console_logging:

            print(
                text,
                flush=True
            )

    # ========================================================
    # STATE
    # ========================================================

    def get_state(
        self,
        group_size,
        tables,
        ready_checker=None,
    ):
        """
        Build the current state.

        State:

            (
                group_size,
                status_T1,
                status_T2,
                ...
                status_T8
            )

        Status:

            0 = READY
            1 = OCCUPIED
            2 = CLEANING
        """

        state = [
            int(group_size)
        ]

        for index, table in enumerate(
            tables
        ):

            # ------------------------------------------------
            # OCCUPIED
            # ------------------------------------------------

            if bool(
                getattr(
                    table,
                    "occupied",
                    False
                )
            ):

                state.append(1)

                continue

            # ------------------------------------------------
            # CLEANING
            # ------------------------------------------------

            if ready_checker is not None:

                try:

                    if not ready_checker(index):

                        state.append(2)

                        continue

                except Exception:

                    pass

            # ------------------------------------------------
            # READY
            # ------------------------------------------------

            state.append(0)

        return tuple(
            state
        )

    # ========================================================
    # VALID ACTIONS
    # ========================================================

    def get_valid_actions(
        self,
        group_size,
        tables,
        ready_checker=None,
    ):
        """
        Return all VALID tables.

        A table is valid when:

            1. It is not occupied.
            2. It is READY.
            3. It has enough capacity.

        IMPORTANT:

        We DO NOT require:

            table.capacity == group_size

        A larger table is still a valid action.

        Example:

            1 person -> 2 seat table  VALID
            1 person -> 4 seat table  VALID
            1 person -> 6 seat table  VALID

        Expected SARSA learns which is better
        using the reward.
        """

        valid = []

        # ====================================================
        # GROUP SIZE
        # ====================================================

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return valid

        if group_size <= 0:

            return valid

        # ====================================================
        # TABLES
        # ====================================================

        for index, table in enumerate(
            tables
        ):

            # ------------------------------------------------
            # OCCUPIED
            # ------------------------------------------------

            if bool(
                getattr(
                    table,
                    "occupied",
                    False
                )
            ):

                continue

            # ------------------------------------------------
            # READY / CLEANING
            # ------------------------------------------------

            if ready_checker is not None:

                try:

                    if not ready_checker(index):

                        continue

                except Exception:

                    continue

            # ------------------------------------------------
            # CAPACITY
            # ------------------------------------------------

            try:

                capacity = int(
                    getattr(
                        table,
                        "capacity",
                        0
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                continue

            # ------------------------------------------------
            # IMPORTANT
            # ------------------------------------------------
            #
            # Only reject if the group physically cannot
            # fit.
            #
            # Larger tables remain valid.
            #
            # ------------------------------------------------

            if capacity >= group_size:

                valid.append(
                    index
                )

        return valid

    # ========================================================
    # Q TABLE
    # ========================================================

    def _ensure_actions(
        self,
        state,
        actions
    ):

        for action in actions:

            if action not in self.q_table[state]:

                self.q_table[state][action] = 0.0

    # --------------------------------------------------------

    def get_q_value(
        self,
        state,
        action
    ):

        return float(
            self.q_table[state].get(
                action,
                0.0
            )
        )

    # ========================================================
    # POLICY
    # ========================================================

    def _best_actions(
        self,
        state,
        valid_actions
    ):

        if not valid_actions:

            return []

        self._ensure_actions(
            state,
            valid_actions
        )

        best_value = max(
            self.q_table[state][action]
            for action in valid_actions
        )

        return [
            action
            for action in valid_actions
            if self.q_table[state][action]
            == best_value
        ]

    # --------------------------------------------------------

    def choose_action(
        self,
        state,
        valid_actions
    ):
        """
        Epsilon-greedy action selection.

        With probability epsilon:

            EXPLORE

        Otherwise:

            EXPLOIT
        """

        if not valid_actions:

            self._log(
                "[EXPECTED SARSA] No valid action."
            )

            return None

        self._ensure_actions(
            state,
            valid_actions
        )

        # ====================================================
        # EXPLORE
        # ====================================================

        if random.random() < self.epsilon:

            action = random.choice(
                list(valid_actions)
            )

            self.total_explorations += 1

            self._log(
                f"[EXPECTED SARSA] EXPLORE -> "
                f"T{action + 1} "
                f"(epsilon={self.epsilon:.2f})"
            )

            return action

        # ====================================================
        # EXPLOIT
        # ====================================================

        best = self._best_actions(
            state,
            valid_actions
        )

        action = random.choice(
            best
        )

        self.total_exploitations += 1

        self._log(
            f"[EXPECTED SARSA] EXPLOIT -> "
            f"T{action + 1} "
            f"(Q={self.get_q_value(state, action):.3f})"
        )

        return action

    # ========================================================
    # EXPECTED VALUE
    # ========================================================

    def get_expected_value(
        self,
        next_state,
        next_valid_actions
    ):
        """
        Calculate:

            E[Q(S', A')]

        under the epsilon-greedy policy.
        """

        if not next_valid_actions:

            return 0.0

        self._ensure_actions(
            next_state,
            next_valid_actions
        )

        actions = list(
            next_valid_actions
        )

        best_actions = self._best_actions(
            next_state,
            actions
        )

        n = len(
            actions
        )

        n_best = len(
            best_actions
        )

        if n <= 0 or n_best <= 0:

            return 0.0

        # ----------------------------------------------------
        # Every action gets exploration probability.
        # ----------------------------------------------------

        base_probability = (
            self.epsilon
            /
            n
        )

        # ----------------------------------------------------
        # Best actions additionally get exploitation
        # probability.
        # ----------------------------------------------------

        best_bonus = (
            (1.0 - self.epsilon)
            /
            n_best
        )

        expected = 0.0

        for action in actions:

            probability = (
                base_probability
            )

            if action in best_actions:

                probability += (
                    best_bonus
                )

            expected += (
                probability
                *
                self.get_q_value(
                    next_state,
                    action
                )
            )

        return expected

    # ========================================================
    # REWARD
    # ========================================================

    def calculate_table_reward(
        self,
        group_size,
        selected_index,
        tables,
        valid_actions
    ):
        """
        Calculate the reward for selecting a table.

        ------------------------------------------------------
        PERFECT FIT
        ------------------------------------------------------

            group = table capacity

            +15

        ------------------------------------------------------
        ONE UNUSED SEAT
        ------------------------------------------------------

            capacity - group = 1

            +10

        ------------------------------------------------------
        TWO UNUSED SEATS
        ------------------------------------------------------

            capacity - group = 2

            +5

        ------------------------------------------------------
        THREE OR MORE UNUSED SEATS
        ------------------------------------------------------

            capacity - group >= 3

            -5

        ------------------------------------------------------
        INVALID
        ------------------------------------------------------

            -100

        IMPORTANT:

        A larger table is NOT invalid.

        The algorithm is being taught:

            "You CAN use this table,
             but wasting too much capacity
             is a bad decision."

        Expected SARSA then learns which actions
        produce better long-term rewards.
        """

        # ====================================================
        # GROUP SIZE
        # ====================================================

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return INVALID_ACTION_REWARD

        if group_size <= 0:

            return INVALID_ACTION_REWARD

        # ====================================================
        # INVALID ACTION
        # ====================================================

        if selected_index not in valid_actions:

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        # ====================================================
        # TABLE INDEX
        # ====================================================

        try:

            selected_index = int(
                selected_index
            )

        except (
            ValueError,
            TypeError
        ):

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        # ====================================================
        # RANGE CHECK
        # ====================================================

        if (
            selected_index < 0
            or
            selected_index >= len(
                tables
            )
        ):

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        # ====================================================
        # CAPACITY
        # ====================================================

        try:

            selected_capacity = int(
                getattr(
                    tables[selected_index],
                    "capacity",
                    0
                )
            )

        except (
            ValueError,
            TypeError
        ):

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        # ====================================================
        # PHYSICAL CAPACITY CHECK
        # ====================================================

        if selected_capacity < group_size:

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        # ====================================================
        # UNUSED SEATS
        # ====================================================

        unused_seats = (
            selected_capacity
            -
            group_size
        )

        # ====================================================
        # EXACT FIT
        # ====================================================

        if unused_seats == 0:

            reward = (
                EXACT_FIT_REWARD
            )

        # ====================================================
        # ONE UNUSED SEAT
        # ====================================================

        elif unused_seats == 1:

            reward = (
                ONE_UNUSED_SEAT_REWARD
            )

        # ====================================================
        # TWO UNUSED SEATS
        # ====================================================

        elif unused_seats == 2:

            reward = (
                TWO_UNUSED_SEATS_REWARD
            )

        # ====================================================
        # THREE OR MORE UNUSED SEATS
        # ====================================================

        else:

            reward = (
                LARGE_WASTE_REWARD
            )

        return float(
            reward
        )

    # ========================================================
    # IMMEDIATE REWARD
    # ========================================================

    def get_immediate_reward(
        self,
        group_size,
        selected_index,
        tables=None,
        ready_checker=None,
        success=True,
        valid_actions=None,
    ):
        """
        Compatibility method used by RestaurantAgent.

        Supported call:

            get_immediate_reward(
                group_size,
                action,
                tables,
                ready_checker=...
            )

        If valid_actions are not supplied,
        they are calculated automatically.
        """

        # ====================================================
        # FAILED ALLOCATION
        # ====================================================

        if not success:

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

            self.total_penalties += (
                abs(reward)
            )

            self._log(
                "[EXPECTED SARSA] "
                f"Immediate reward -> "
                f"{reward:+.2f} "
                "(allocation failed)"
            )

            return reward

        # ====================================================
        # DEFAULT TABLE LIST
        # ====================================================

        if tables is None:

            tables = (
                self.table_manager.tables
            )

        # ====================================================
        # NO ACTION
        # ====================================================

        if selected_index is None:

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

            self.total_penalties += (
                abs(reward)
            )

            self._log(
                "[EXPECTED SARSA] "
                f"Immediate reward -> "
                f"{reward:+.2f} "
                "(no table selected)"
            )

            return reward

        # ====================================================
        # CONVERT ACTION
        # ====================================================

        try:

            selected_index = int(
                selected_index
            )

        except (
            ValueError,
            TypeError
        ):

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

            self.total_penalties += (
                abs(reward)
            )

            self._log(
                "[EXPECTED SARSA] "
                f"Immediate reward -> "
                f"{reward:+.2f} "
                "(invalid table index)"
            )

            return reward

        # ====================================================
        # VALID ACTIONS
        # ====================================================

        if valid_actions is None:

            valid_actions = (
                self.get_valid_actions(
                    group_size,
                    tables,
                    ready_checker=ready_checker
                )
            )

        # ====================================================
        # CALCULATE
        # ====================================================

        reward = (
            self.calculate_table_reward(
                group_size=group_size,
                selected_index=selected_index,
                tables=tables,
                valid_actions=valid_actions
            )
        )

        # ====================================================
        # REWARD STATISTICS
        # ====================================================

        if reward > 0:

            self.total_positive_rewards += (
                reward
            )

            self.success_count += 1

            try:

                capacity = int(
                    getattr(
                        tables[selected_index],
                        "capacity",
                        0
                    )
                )

                unused = (
                    capacity
                    -
                    int(group_size)
                )

                if unused == 0:

                    self.exact_fit_count += 1

                elif unused > 0:

                    self.inefficient_allocation_count += 1

            except Exception:

                pass

        elif reward < 0:

            self.total_penalties += (
                abs(reward)
            )

            # ------------------------------------------------
            # Valid allocation but too much wasted capacity.
            # ------------------------------------------------

            if selected_index in valid_actions:

                try:

                    capacity = int(
                        getattr(
                            tables[selected_index],
                            "capacity",
                            0
                        )
                    )

                    unused = (
                        capacity
                        -
                        int(group_size)
                    )

                    if unused >= 3:

                        self.waste_penalty_count += 1

                except Exception:

                    pass

        # ====================================================
        # LOG
        # ====================================================

        table_id = (
            f"T{selected_index + 1}"
        )

        try:

            capacity = int(
                getattr(
                    tables[selected_index],
                    "capacity",
                    0
                )
            )

        except Exception:

            capacity = 0

        unused_seats = (
            capacity
            -
            int(group_size)
        )

        if reward < 0 and selected_index in valid_actions:

            reward_reason = (
                "WASTE PENALTY"
            )

        elif reward == EXACT_FIT_REWARD:

            reward_reason = (
                "EXACT FIT"
            )

        elif reward == ONE_UNUSED_SEAT_REWARD:

            reward_reason = (
                "1 UNUSED SEAT"
            )

        elif reward == TWO_UNUSED_SEATS_REWARD:

            reward_reason = (
                "2 UNUSED SEATS"
            )

        else:

            reward_reason = (
                "INVALID"
            )

        self._log(
            "[EXPECTED SARSA] "
            f"Immediate reward for {table_id} -> "
            f"{reward:+.2f} "
            f"| capacity={capacity} "
            f"| group={group_size} "
            f"| unused={max(0, unused_seats)} "
            f"| {reward_reason}"
        )

        return float(
            reward
        )

    # ========================================================
    # WAITING REWARD
    # ========================================================

    def waiting_reward(
        self
    ):
        """
        Reward when no suitable READY table is available.

        This is intentionally only -1.

        Waiting is undesirable, but it is not as bad as
        making an invalid table assignment.
        """

        self.wait_count += 1

        self.total_reward += (
            WAIT_REWARD
        )

        self.total_penalties += (
            abs(WAIT_REWARD)
        )

        self._log(
            "[EXPECTED SARSA] "
            f"Waiting reward -> "
            f"{WAIT_REWARD:+.2f}"
        )

        return WAIT_REWARD

    # ========================================================
    # DECISION
    # ========================================================

    def choose_table(
        self,
        group_size,
        ready_checker=None
    ):
        """
        Choose a table.

        Returns:

            0..7

        or:

            None
        """

        tables = (
            self.table_manager.tables
        )

        # ====================================================
        # STATE
        # ====================================================

        state = (
            self.get_state(
                group_size,
                tables,
                ready_checker
            )
        )

        # ====================================================
        # VALID ACTIONS
        # ====================================================

        valid_actions = (
            self.get_valid_actions(
                group_size,
                tables,
                ready_checker
            )
        )

        self._log("")

        self._log(
            "=================================================="
        )

        self._log(
            "[EXPECTED SARSA] NEW DECISION"
        )

        self._log(
            f"Group size  : {group_size}"
        )

        self._log(
            f"State       : {state}"
        )

        # ====================================================
        # NO ACTION
        # ====================================================

        if not valid_actions:

            self._log(
                "Valid tables: NONE"
            )

            self._log(
                "[EXPECTED SARSA] "
                "No suitable READY table."
            )

            self._log(
                "=================================================="
            )

            return None

        # ====================================================
        # VALID TABLES
        # ====================================================

        self._log(
            "Valid tables: "
            +
            ", ".join(
                f"T{i + 1}"
                for i in valid_actions
            )
        )

        # ====================================================
        # SHOW CAPACITIES
        # ====================================================

        capacity_text = []

        for index in valid_actions:

            try:

                capacity = int(
                    getattr(
                        tables[index],
                        "capacity",
                        0
                    )
                )

            except Exception:

                capacity = 0

            capacity_text.append(
                f"T{index + 1}={capacity}"
            )

        self._log(
            "Capacities   : "
            +
            ", ".join(
                capacity_text
            )
        )

        # ====================================================
        # CHOOSE ACTION
        # ====================================================

        action = (
            self.choose_action(
                state,
                valid_actions
            )
        )

        if action is None:

            self._log(
                "=================================================="
            )

            return None

        # ====================================================
        # IMMEDIATE REWARD
        # ====================================================

        reward = (
            self.calculate_table_reward(
                group_size,
                action,
                tables,
                valid_actions
            )
        )

        try:

            selected_capacity = int(
                getattr(
                    tables[action],
                    "capacity",
                    0
                )
            )

        except Exception:

            selected_capacity = 0

        unused_seats = (
            selected_capacity
            -
            int(group_size)
        )

        self._log(
            f"[EXPECTED SARSA] "
            f"Selected T{action + 1} | "
            f"capacity={selected_capacity} | "
            f"unused={max(0, unused_seats)} | "
            f"immediate reward={reward:+.2f}"
        )

        self._log(
            "=================================================="
        )

        return action

    # ========================================================
    # Q UPDATE
    # ========================================================

    def update_q_value(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions,
        terminal=False,
    ):
        """
        Expected SARSA:

        Q(S,A) <- Q(S,A) +
                  alpha[
                      R
                      +
                      gamma * E[Q(S',A')]
                      -
                      Q(S,A)
                  ]
        """

        old_q = (
            self.get_q_value(
                state,
                action
            )
        )

        # ====================================================
        # EXPECTED NEXT VALUE
        # ====================================================

        if (
            terminal
            or
            not next_valid_actions
        ):

            expected_next = 0.0

        else:

            expected_next = (
                self.get_expected_value(
                    next_state,
                    next_valid_actions
                )
            )

        # ====================================================
        # TARGET
        # ====================================================

        target = (
            float(reward)
            +
            self.discount_factor
            *
            expected_next
        )

        # ====================================================
        # TD ERROR
        # ====================================================

        td_error = (
            target
            -
            old_q
        )

        # ====================================================
        # NEW Q
        # ====================================================

        new_q = (
            old_q
            +
            self.learning_rate
            *
            td_error
        )

        self.q_table[state][action] = (
            new_q
        )

        # ====================================================
        # STATISTICS
        # ====================================================

        self.total_updates += 1

        self.total_reward += (
            float(reward)
        )

        self.last_state = (
            state
        )

        self.last_action = (
            action
        )

        self.last_reward = (
            float(reward)
        )

        self.last_next_state = (
            next_state
        )

        self.last_expected_value = (
            expected_next
        )

        # ====================================================
        # LOG
        # ====================================================

        self._log("")

        self._log(
            "--------------------------------------------------"
        )

        self._log(
            "[EXPECTED SARSA] Q-VALUE UPDATE"
        )

        self._log(
            f"State       : {state}"
        )

        self._log(
            f"Action      : T{action + 1}"
        )

        self._log(
            f"Reward      : {reward:+.2f}"
        )

        self._log(
            f"Old Q       : {old_q:.3f}"
        )

        self._log(
            f"Expected Q' : {expected_next:.3f}"
        )

        self._log(
            f"Target      : {target:.3f}"
        )

        self._log(
            f"TD Error    : {td_error:+.3f}"
        )

        self._log(
            f"New Q       : {new_q:.3f}"
        )

        self._log(
            "--------------------------------------------------"
        )

        return new_q

    # ========================================================
    # LEARN AFTER ALLOCATION
    # ========================================================

    def learn_after_allocation(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions,
    ):
        """
        Perform one Expected SARSA update.

        Transition:

            S -> A -> R -> S'

        followed by:

            Q update
        """

        self.total_allocations += 1

        return (
            self.update_q_value(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                next_valid_actions=next_valid_actions
            )
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_statistics(
        self
    ):

        return {

            "q_states":
                len(
                    self.q_table
                ),

            "q_updates":
                self.total_updates,

            "allocations":
                self.total_allocations,

            "explorations":
                self.total_explorations,

            "exploitations":
                self.total_exploitations,

            "total_reward":
                self.total_reward,

            "total_positive_rewards":
                self.total_positive_rewards,

            "total_penalties":
                self.total_penalties,

            "invalid_actions":
                self.invalid_action_count,

            "waits":
                self.wait_count,

            "successes":
                self.success_count,

            "exact_fits":
                self.exact_fit_count,

            "inefficient_allocations":
                self.inefficient_allocation_count,

            "waste_penalties":
                self.waste_penalty_count,

            "epsilon":
                self.epsilon,

            "learning_rate":
                self.learning_rate,

            "discount_factor":
                self.discount_factor,

        }

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    def print_results(
        self
    ):

        s = (
            self.get_statistics()
        )

        self._log("")

        self._log(
            "============================================================"
        )

        self._log(
            "              EXPECTED SARSA - LIVE RESULTS"
        )

        self._log(
            "============================================================"
        )

        self._log(
            f"Q-table states      : "
            f"{s['q_states']}"
        )

        self._log(
            f"Q-value updates     : "
            f"{s['q_updates']}"
        )

        self._log(
            f"Allocations         : "
            f"{s['allocations']}"
        )

        self._log(
            f"Successful fits     : "
            f"{s['successes']}"
        )

        self._log(
            f"Exact fits          : "
            f"{s['exact_fits']}"
        )

        self._log(
            f"Inefficient fits    : "
            f"{s['inefficient_allocations']}"
        )

        self._log(
            f"Waste penalties     : "
            f"{s['waste_penalties']}"
        )

        self._log(
            f"Invalid actions     : "
            f"{s['invalid_actions']}"
        )

        self._log(
            f"Waiting events      : "
            f"{s['waits']}"
        )

        self._log(
            f"Explorations        : "
            f"{s['explorations']}"
        )

        self._log(
            f"Exploitations       : "
            f"{s['exploitations']}"
        )

        self._log(
            f"Positive rewards    : "
            f"{s['total_positive_rewards']:+.2f}"
        )

        self._log(
            f"Total penalties     : "
            f"{s['total_penalties']:.2f}"
        )

        self._log(
            f"Total reward        : "
            f"{s['total_reward']:+.2f}"
        )

        self._log(
            f"Learning rate alpha : "
            f"{s['learning_rate']:.2f}"
        )

        self._log(
            f"Discount gamma      : "
            f"{s['discount_factor']:.2f}"
        )

        self._log(
            f"Epsilon             : "
            f"{s['epsilon']:.2f}"
        )

        self._log(
            "============================================================"
        )

    # ========================================================
    # PRINT Q TABLE
    # ========================================================

    def print_q_table(
        self
    ):

        self._log("")

        self._log(
            "============================================================"
        )

        self._log(
            "                 LEARNED Q-TABLE"
        )

        self._log(
            "============================================================"
        )

        if not self.q_table:

            self._log(
                "(empty)"
            )

        else:

            for state, actions in (
                self.q_table.items()
            ):

                values = ", ".join(
                    f"T{action + 1}={value:.3f}"
                    for action, value
                    in sorted(
                        actions.items()
                    )
                )

                self._log(
                    f"State {state} -> "
                    f"{values}"
                )

        self._log(
            "============================================================"
        )

    # ========================================================
    # EPSILON DECAY
    # ========================================================

    def decay_epsilon(
        self,
        decay_rate=0.995,
        minimum=0.02,
    ):

        old = (
            self.epsilon
        )

        self.epsilon = max(
            float(minimum),
            self.epsilon
            *
            float(decay_rate)
        )

        if old != self.epsilon:

            self._log(
                "[EXPECTED SARSA] "
                f"Epsilon: "
                f"{old:.4f} -> "
                f"{self.epsilon:.4f}"
            )

    # ========================================================
    # SET EPSILON
    # ========================================================

    def set_epsilon(
        self,
        epsilon
    ):

        self.epsilon = max(
            0.0,
            min(
                1.0,
                float(epsilon)
            )
        )


# ============================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================

ExpectedSARSA = ExpectedSARSAAlgorithm