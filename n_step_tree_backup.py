"""
METRIUS EATS - N-STEP TREE BACKUP

Online N-step Tree Backup for restaurant table allocation.

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

Action:
    0..7 -> T1..T8

The algorithm:
    1. Observes the current state.
    2. Builds the feasible action set.
    3. Selects an action using epsilon-greedy policy.
    4. Receives the immediate allocation reward.
    5. Stores the transition.
    6. Uses n-step Tree Backup to propagate future rewards.
    7. Updates the tabular Q-value.
"""

from collections import defaultdict, deque
import random


LEARNING_RATE = 0.08
DISCOUNT_FACTOR = 0.95
EPSILON = 0.10
N_STEP = 3

EXACT_FIT_REWARD = 15.0
ONE_UNUSED_SEAT_REWARD = 10.0
TWO_UNUSED_SEATS_REWARD = 5.0
LARGE_WASTE_REWARD = -5.0
INVALID_ACTION_REWARD = -100.0
WAIT_REWARD = -1.0

SUCCESS_REWARD = EXACT_FIT_REWARD
BEST_FIT_BONUS = 0.0
OVERSIZED_TABLE_PENALTY = abs(LARGE_WASTE_REWARD)

TABLE_CAPACITIES = (
    4,
    2,
    6,
    2,
    2,
    2,
    2,
    4,
)


class NStepTreeBackupAlgorithm:

    def __init__(
        self,
        table_manager,
        learning_rate=LEARNING_RATE,
        discount_factor=DISCOUNT_FACTOR,
        epsilon=EPSILON,
        n_step=N_STEP,
        console_logging=True,
    ):
        self.table_manager = table_manager

        self.learning_rate = float(
            learning_rate
        )

        self.discount_factor = float(
            discount_factor
        )

        self.epsilon = max(
            0.0,
            min(
                1.0,
                float(epsilon)
            )
        )

        self.n_step = max(
            1,
            int(n_step)
        )

        self.console_logging = bool(
            console_logging
        )

        self.q_table = defaultdict(dict)

        self.transition_buffer = deque()

        self.total_updates = 0
        self.total_allocations = 0

        self.total_explorations = 0
        self.total_exploitations = 0

        self.total_reward = 0.0
        self.total_positive_rewards = 0.0
        self.total_penalties = 0.0

        self.invalid_action_count = 0
        self.wait_count = 0

        self.success_count = 0
        self.exact_fit_count = 0
        self.inefficient_allocation_count = 0
        self.waste_penalty_count = 0

        self.last_state = None
        self.last_action = None
        self.last_reward = 0.0
        self.last_next_state = None

        self.last_tree_backup_return = 0.0
        self.last_td_error = 0.0

        self.last_group_size = None
        self.last_table_capacity = None
        self.last_unused_seats = None

        self.last_feasible_actions = []
        self.feasible_table_count = 0

        self.last_action_was_exploration = False

        self._log(
            "[N-STEP TREE BACKUP] Initialized | "
            f"alpha={self.learning_rate:.2f}, "
            f"gamma={self.discount_factor:.2f}, "
            f"epsilon={self.epsilon:.2f}, "
            f"n={self.n_step}"
        )

    def _log(
        self,
        text
    ):
        if self.console_logging:
            print(
                text,
                flush=True
            )

    def set_table_manager(
        self,
        table_manager
    ):
        self.table_manager = table_manager

    def get_table_capacities(
        self,
        tables=None
    ):
        if tables is None:
            tables = getattr(
                self.table_manager,
                "tables",
                []
            )

        capacities = []

        for index in range(8):

            if index >= len(tables):

                capacities.append(
                    TABLE_CAPACITIES[index]
                )

                continue

            table = tables[index]

            try:

                capacity = int(
                    getattr(
                        table,
                        "capacity",
                        TABLE_CAPACITIES[index]
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                capacity = (
                    TABLE_CAPACITIES[index]
                )

            capacities.append(
                capacity
            )

        return tuple(
            capacities
        )

    def get_state(
        self,
        group_size,
        tables,
        ready_checker=None
    ):
        try:

            group_size = int(
                group_size
            )

        except (
            TypeError,
            ValueError
        ):

            group_size = 0

        state = [
            group_size
        ]

        for index in range(8):

            if index >= len(tables):

                state.append(
                    1
                )

                continue

            table = tables[index]

            if bool(
                getattr(
                    table,
                    "occupied",
                    False
                )
            ):

                state.append(
                    1
                )

                continue

            if ready_checker is not None:

                try:

                    if not ready_checker(index):

                        state.append(
                            2
                        )

                        continue

                except Exception:

                    state.append(
                        2
                    )

                    continue

            state.append(
                0
            )

        return tuple(
            state
        )

    def get_valid_actions(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        if tables is None:

            tables = getattr(
                self.table_manager,
                "tables",
                []
            )

        try:

            group_size = int(
                group_size
            )

        except (
            ValueError,
            TypeError
        ):

            return []

        if group_size <= 0:

            return []

        valid = []

        for index, table in enumerate(
            tables[:8]
        ):

            if bool(
                getattr(
                    table,
                    "occupied",
                    False
                )
            ):

                continue

            if ready_checker is not None:

                try:

                    if not ready_checker(index):

                        continue

                except Exception:

                    continue

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

            if capacity >= group_size:

                valid.append(
                    index
                )

        self.last_feasible_actions = list(
            valid
        )

        self.feasible_table_count = len(
            valid
        )

        return valid

    def _ensure_actions(
        self,
        state,
        actions
    ):
        if state not in self.q_table:

            self.q_table[state] = {}

        for action in actions:

            if action not in self.q_table[state]:

                self.q_table[state][action] = 0.0

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

    def _best_actions(
        self,
        state,
        valid_actions
    ):
        if not valid_actions:

            return []

        actions = sorted(
            set(
                int(action)
                for action in valid_actions
            )
        )

        self._ensure_actions(
            state,
            actions
        )

        best_value = max(
            self.q_table[state][
                action
            ]
            for action in actions
        )

        return [
            action
            for action in actions
            if abs(
                self.q_table[state][action]
                -
                best_value
            )
            < 1e-12
        ]

    def _greedy_action_from_ties(
        self,
        state,
        valid_actions
    ):
        best = self._best_actions(
            state,
            valid_actions
        )

        if not best:

            return None

        return min(
            best
        )

    def get_policy_probabilities(
        self,
        state,
        valid_actions
    ):
        if not valid_actions:

            return {}

        actions = sorted(
            set(
                int(action)
                for action in valid_actions
            )
        )

        self._ensure_actions(
            state,
            actions
        )

        greedy_action = (
            self._greedy_action_from_ties(
                state,
                actions
            )
        )

        if greedy_action is None:

            return {}

        action_count = len(
            actions
        )

        base_probability = (
            self.epsilon
            /
            action_count
        )

        probabilities = {
            action: base_probability
            for action in actions
        }

        probabilities[
            greedy_action
        ] += (
            1.0
            -
            self.epsilon
        )

        return probabilities

    def policy_probs(
        self,
        state,
        valid_actions
    ):
        return self.get_policy_probabilities(
            state,
            valid_actions
        )

    def choose_action(
        self,
        state,
        valid_actions
    ):
        if not valid_actions:

            self._log(
                "[N-STEP TREE BACKUP] "
                "No valid action."
            )

            return None

        actions = sorted(
            set(
                int(action)
                for action in valid_actions
            )
        )

        self._ensure_actions(
            state,
            actions
        )

        self.last_action_was_exploration = False

        if random.random() < self.epsilon:

            action = random.choice(
                actions
            )

            self.total_explorations += 1

            self.last_action_was_exploration = True

            self._log(
                "[N-STEP TREE BACKUP] "
                f"EXPLORE -> T{action + 1} "
                f"(epsilon={self.epsilon:.2f})"
            )

            return action

        action = (
            self._greedy_action_from_ties(
                state,
                actions
            )
        )

        self.total_exploitations += 1

        self._log(
            "[N-STEP TREE BACKUP] "
            f"EXPLOIT -> T{action + 1} "
            f"(Q={self.get_q_value(state, action):.3f})"
        )

        return action

    def select_action(
        self,
        state,
        valid_actions
    ):
        return self.choose_action(
            state,
            valid_actions
        )

    def greedy_action(
        self,
        state,
        valid_actions
    ):
        if not valid_actions:

            return None

        return (
            self._greedy_action_from_ties(
                state,
                valid_actions
            )
        )

    def get_expected_value(
        self,
        next_state,
        next_valid_actions
    ):
        if not next_valid_actions:

            return 0.0

        probabilities = (
            self.get_policy_probabilities(
                next_state,
                next_valid_actions
            )
        )

        return sum(
            probability
            *
            self.get_q_value(
                next_state,
                action
            )
            for action, probability
            in probabilities.items()
        )

    def expected_value(
        self,
        state,
        valid_actions=None
    ):
        if valid_actions is None:

            valid_actions = (
                self._valid_actions_from_state(
                    state
                )
            )

        return self.get_expected_value(
            state,
            valid_actions
        )

    def _valid_actions_from_state(
        self,
        state
    ):
        try:

            group_size = int(
                state[0]
            )

            statuses = list(
                state[1:]
            )

        except (
            IndexError,
            TypeError,
            ValueError
        ):

            return []

        if group_size <= 0:

            return []

        capacities = (
            self.get_table_capacities()
        )

        valid = []

        for index in range(
            min(
                8,
                len(statuses)
            )
        ):

            status = statuses[
                index
            ]

            if status != 0:

                continue

            if capacities[index] >= group_size:

                valid.append(
                    index
                )

        return valid

    @staticmethod
    def feasible_from_state(
        state
    ):
        try:

            if (
                len(state) == 9
                and
                isinstance(
                    state[0],
                    tuple
                )
            ):

                statuses = state[0]

                group_size = int(
                    state[1]
                )

                if group_size <= 0:

                    return []

            else:

                group_size = int(
                    state[0]
                )

                statuses = state[1:]

            if group_size <= 0:

                return []

            valid = []

            for index, capacity in enumerate(
                TABLE_CAPACITIES
            ):

                if index >= len(
                    statuses
                ):

                    break

                if statuses[index] != 0:

                    continue

                if capacity >= group_size:

                    valid.append(
                        index
                    )

            return valid

        except (
            TypeError,
            ValueError,
            IndexError
        ):

            return []

    def calculate_table_reward(
        self,
        group_size,
        selected_index,
        tables,
        valid_actions
    ):
        try:

            group_size = int(
                group_size
            )

            selected_index = int(
                selected_index
            )

        except (
            ValueError,
            TypeError
        ):

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        if group_size <= 0:

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        if selected_index not in valid_actions:

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        if (
            selected_index < 0
            or
            selected_index >= len(
                tables
            )
        ):

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        try:

            selected_capacity = int(
                getattr(
                    tables[
                        selected_index
                    ],
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

        if selected_capacity < group_size:

            self.invalid_action_count += 1

            return INVALID_ACTION_REWARD

        unused_seats = (
            selected_capacity
            -
            group_size
        )

        if unused_seats == 0:

            return EXACT_FIT_REWARD

        if unused_seats == 1:

            return ONE_UNUSED_SEAT_REWARD

        if unused_seats == 2:

            return TWO_UNUSED_SEATS_REWARD

        return LARGE_WASTE_REWARD

    def get_immediate_reward(
        self,
        group_size,
        selected_index,
        tables=None,
        ready_checker=None,
        success=True,
        valid_actions=None
    ):
        if tables is None:

            tables = getattr(
                self.table_manager,
                "tables",
                []
            )

        if not success:

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

            self._log(
                "[N-STEP TREE BACKUP] "
                f"Immediate reward -> "
                f"{reward:+.2f} "
                "(allocation failed)"
            )

            return reward

        if selected_index is None:

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

            return reward

        if valid_actions is None:

            valid_actions = (
                self.get_valid_actions(
                    group_size,
                    tables,
                    ready_checker
                )
            )

        reward = (
            self.calculate_table_reward(
                group_size,
                selected_index,
                tables,
                valid_actions
            )
        )

        if reward > 0:

            self.total_positive_rewards += (
                reward
            )

            self.success_count += 1

            try:

                capacity = int(
                    getattr(
                        tables[
                            int(
                                selected_index
                            )
                        ],
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

            self.total_penalties += abs(
                reward
            )

            if reward == (
                LARGE_WASTE_REWARD
            ):

                self.waste_penalty_count += 1

        return float(
            reward
        )

    def waiting_reward(
        self
    ):
        self.wait_count += 1

        self.total_reward += (
            WAIT_REWARD
        )

        self.total_penalties += abs(
            WAIT_REWARD
        )

        self._log(
            "[N-STEP TREE BACKUP] "
            f"Waiting reward -> "
            f"{WAIT_REWARD:+.2f}"
        )

        return WAIT_REWARD

    def _build_next_state(
        self,
        group_size,
        selected_index,
        tables,
        ready_checker
    ):
        return self.get_state(
            group_size,
            tables,
            ready_checker
        )

    def choose_table(
        self,
        group_size,
        ready_checker=None
    ):
        tables = getattr(
            self.table_manager,
            "tables",
            []
        )

        state = self.get_state(
            group_size,
            tables,
            ready_checker
        )

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
            "[N-STEP TREE BACKUP] NEW DECISION"
        )

        self._log(
            f"Group size  : {group_size}"
        )

        self._log(
            f"State       : {state}"
        )

        if not valid_actions:

            self._log(
                "Valid tables: NONE"
            )

            self._log(
                "[N-STEP TREE BACKUP] "
                "No suitable READY table."
            )

            self._log(
                "=================================================="
            )

            return None

        self._log(
            "Valid tables: "
            +
            ", ".join(
                f"T{index + 1}"
                for index
                in valid_actions
            )
        )

        capacities = (
            self.get_table_capacities(
                tables
            )
        )

        self._log(
            "Capacities   : "
            +
            ", ".join(
                f"T{index + 1}={capacities[index]}"
                for index
                in valid_actions
            )
        )

        action = self.choose_action(
            state,
            valid_actions
        )

        if action is None:

            return None

        capacity = capacities[
            action
        ]

        unused = (
            capacity
            -
            int(group_size)
        )

        reward = (
            self.calculate_table_reward(
                group_size,
                action,
                tables,
                valid_actions
            )
        )

        self.last_group_size = int(
            group_size
        )

        self.last_action = action

        self.last_table_capacity = (
            capacity
        )

        self.last_unused_seats = max(
            0,
            unused
        )

        self.last_reward = (
            reward
        )

        self._log(
            "[N-STEP TREE BACKUP] "
            f"Selected T{action + 1} | "
            f"capacity={capacity} | "
            f"unused={max(0, unused)} | "
            f"immediate reward={reward:+.2f}"
        )

        self._log(
            "=================================================="
        )

        return action

    def _tree_backup_return(
        self,
        transitions
    ):
        if not transitions:

            return 0.0

        transitions = list(
            transitions
        )

        first = transitions[0]

        if len(transitions) == 1:

            if first["terminal"]:

                return float(
                    first["reward"]
                )

            expected = (
                self.get_expected_value(
                    first["next_state"],
                    first["next_valid_actions"]
                )
            )

            return float(
                first["reward"]
                +
                self.discount_factor
                *
                expected
            )

        last = transitions[-1]

        if last["terminal"]:

            G = float(
                last["reward"]
            )

            start_index = (
                len(transitions)
                -
                2
            )

        else:

            G = (
                self.get_expected_value(
                    last["next_state"],
                    last["next_valid_actions"]
                )
            )

            start_index = (
                len(transitions)
                -
                1
            )

        for index in range(
            start_index,
            -1,
            -1
        ):

            transition = (
                transitions[index]
            )

            reward = float(
                transition["reward"]
            )

            if transition["terminal"]:

                G = reward

                continue

            next_state = (
                transition["next_state"]
            )

            next_valid_actions = list(
                transition[
                    "next_valid_actions"
                ]
            )

            probabilities = (
                self.get_policy_probabilities(
                    next_state,
                    next_valid_actions
                )
            )

            if not probabilities:

                G = reward

                continue

            next_action = None

            if (
                index + 1
                <
                len(transitions)
            ):

                next_action = (
                    transitions[
                        index + 1
                    ]["action"]
                )

            expected_other = 0.0

            for action, probability in (
                probabilities.items()
            ):

                if action == next_action:

                    continue

                expected_other += (
                    probability
                    *
                    self.get_q_value(
                        next_state,
                        action
                    )
                )

            if next_action is None:

                continuation = sum(
                    probability
                    *
                    self.get_q_value(
                        next_state,
                        action
                    )
                    for action, probability
                    in probabilities.items()
                )

            else:

                selected_probability = (
                    probabilities.get(
                        next_action,
                        0.0
                    )
                )

                continuation = (
                    expected_other
                    +
                    selected_probability
                    *
                    G
                )

            G = (
                reward
                +
                self.discount_factor
                *
                continuation
            )

        return float(
            G
        )

    def _update_oldest_transition(
        self
    ):
        if not self.transition_buffer:

            return None

        target = (
            self._tree_backup_return(
                self.transition_buffer
            )
        )

        transition = (
            self.transition_buffer[0]
        )

        state = (
            transition["state"]
        )

        action = int(
            transition["action"]
        )

        old_q = (
            self.get_q_value(
                state,
                action
            )
        )

        td_error = (
            target
            -
            old_q
        )

        new_q = (
            old_q
            +
            self.learning_rate
            *
            td_error
        )

        self.q_table[state][
            action
        ] = new_q

        self.total_updates += 1

        self.last_state = (
            state
        )

        self.last_action = (
            action
        )

        self.last_reward = float(
            transition["reward"]
        )

        self.last_next_state = (
            transition["next_state"]
        )

        self.last_tree_backup_return = (
            target
        )

        self.last_td_error = (
            td_error
        )

        self._log("")

        self._log(
            "--------------------------------------------------"
        )

        self._log(
            "[N-STEP TREE BACKUP] Q-VALUE UPDATE"
        )

        self._log(
            f"State       : {state}"
        )

        self._log(
            f"Action      : T{action + 1}"
        )

        self._log(
            f"Reward      : "
            f"{transition['reward']:+.2f}"
        )

        self._log(
            f"Tree Backup : "
            f"{target:+.3f}"
        )

        self._log(
            f"Old Q       : "
            f"{old_q:.3f}"
        )

        self._log(
            f"TD Error    : "
            f"{td_error:+.3f}"
        )

        self._log(
            f"New Q       : "
            f"{new_q:.3f}"
        )

        self._log(
            "--------------------------------------------------"
        )

        self.transition_buffer.popleft()

        return new_q

    def update_q_value(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions=None,
        terminal=False
    ):
        if state is None:

            return None

        if action is None:

            return None

        if next_state is None:

            return None

        transition = {
            "state": state,
            "action": int(action),
            "reward": float(reward),
            "next_state": next_state,
            "next_valid_actions": list(
                next_valid_actions or []
            ),
            "terminal": bool(
                terminal
            ),
        }

        self.transition_buffer.append(
            transition
        )

        if terminal:

            self.total_reward += (
                float(reward)
            )

        if (
            not terminal
            and
            len(
                self.transition_buffer
            )
            >=
            self.n_step
        ):

            return (
                self._update_oldest_transition()
            )

        if terminal:

            last_value = None

            while self.transition_buffer:

                last_value = (
                    self._update_oldest_transition()
                )

            return last_value

        return None

    def learn_after_allocation(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions=None,
        terminal=False
    ):
        self.total_allocations += 1

        self.total_reward += float(
            reward
        )

        return self.update_q_value(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            next_valid_actions=next_valid_actions,
            terminal=terminal
        )

    def finalize_episode(
        self
    ):
        if not self.transition_buffer:

            return None

        self.transition_buffer[-1][
            "terminal"
        ] = True

        last_value = None

        while self.transition_buffer:

            last_value = (
                self._update_oldest_transition()
            )

        return last_value

    def reset_episode_buffer(
        self
    ):
        self.transition_buffer.clear()

    def decay_epsilon(
        self,
        decay_rate=0.995,
        minimum=0.02
    ):
        old_epsilon = (
            self.epsilon
        )

        self.epsilon = max(
            float(minimum),
            self.epsilon
            *
            float(decay_rate)
        )

        if (
            old_epsilon
            !=
            self.epsilon
        ):

            self._log(
                "[N-STEP TREE BACKUP] "
                f"Epsilon: "
                f"{old_epsilon:.4f} -> "
                f"{self.epsilon:.4f}"
            )

    def set_epsilon(
        self,
        epsilon
    ):
        try:

            self.epsilon = max(
                0.0,
                min(
                    1.0,
                    float(epsilon)
                )
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    def set_learning_rate(
        self,
        value
    ):
        try:

            self.learning_rate = max(
                0.0,
                float(value)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    def set_discount_factor(
        self,
        value
    ):
        try:

            self.discount_factor = max(
                0.0,
                min(
                    1.0,
                    float(value)
                )
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    def set_n_step(
        self,
        value
    ):
        try:

            new_n = max(
                1,
                int(value)
            )

            if new_n != self.n_step:

                self.n_step = new_n

                self.reset_episode_buffer()

        except (
            ValueError,
            TypeError
        ):

            pass

    def get_statistics(
        self
    ):
        return {
            "algorithm":
                "N-STEP TREE BACKUP",

            "q_states":
                len(
                    self.q_table
                ),

            "q_updates":
                self.total_updates,

            "updates":
                self.total_updates,

            "allocations":
                self.total_allocations,

            "total_decisions":
                self.total_allocations,

            "successful_allocations":
                self.success_count,

            "successes":
                self.success_count,

            "explorations":
                self.total_explorations,

            "exploitations":
                self.total_exploitations,

            "total_reward":
                self.total_reward,

            "current_reward":
                self.last_reward,

            "best_reward":
                max(
                    0.0,
                    self.last_reward
                ),

            "total_positive_rewards":
                self.total_positive_rewards,

            "total_penalties":
                self.total_penalties,

            "penalties":
                self.total_penalties,

            "invalid_actions":
                self.invalid_action_count,

            "waits":
                self.wait_count,

            "exact_fits":
                self.exact_fit_count,

            "inefficient_allocations":
                self.inefficient_allocation_count,

            "waste_penalties":
                self.waste_penalty_count,

            "waste_penalty_count":
                self.waste_penalty_count,

            "epsilon":
                self.epsilon,

            "learning_rate":
                self.learning_rate,

            "discount_factor":
                self.discount_factor,

            "n_step":
                self.n_step,

            "tree_backup_return":
                self.last_tree_backup_return,

            "last_tree_backup_return":
                self.last_tree_backup_return,

            "td_error":
                self.last_td_error,

            "last_td_error":
                self.last_td_error,

            "pending_transitions":
                len(
                    self.transition_buffer
                ),

            "last_action":
                self.last_action,

            "last_group_size":
                self.last_group_size,

            "last_table_capacity":
                self.last_table_capacity,

            "last_unused_seats":
                self.last_unused_seats,

            "last_feasible_actions":
                list(
                    self.last_feasible_actions
                ),

            "feasible_table_count":
                self.feasible_table_count
        }

    def get_rl_statistics(
        self
    ):
        return self.get_statistics()

    def sync_statistics(
        self,
        statistics
    ):
        if not isinstance(
            statistics,
            dict
        ):

            return

        if "epsilon" in statistics:

            self.set_epsilon(
                statistics["epsilon"]
            )

        if "learning_rate" in statistics:

            self.set_learning_rate(
                statistics["learning_rate"]
            )

        if "discount_factor" in statistics:

            self.set_discount_factor(
                statistics["discount_factor"]
            )

        if "n_step" in statistics:

            value = statistics[
                "n_step"
            ]

            try:

                value = int(
                    value
                )

                if value != self.n_step:

                    self.n_step = max(
                        1,
                        value
                    )

            except (
                ValueError,
                TypeError
            ):

                pass

    def print_results(
        self
    ):
        stats = (
            self.get_statistics()
        )

        self._log("")

        self._log(
            "============================================================"
        )

        self._log(
            "          N-STEP TREE BACKUP - LIVE RESULTS"
        )

        self._log(
            "============================================================"
        )

        self._log(
            f"Q-table states      : "
            f"{stats['q_states']}"
        )

        self._log(
            f"Q-value updates     : "
            f"{stats['q_updates']}"
        )

        self._log(
            f"Allocations         : "
            f"{stats['allocations']}"
        )

        self._log(
            f"Successful fits     : "
            f"{stats['successes']}"
        )

        self._log(
            f"Exact fits          : "
            f"{stats['exact_fits']}"
        )

        self._log(
            f"Inefficient fits    : "
            f"{stats['inefficient_allocations']}"
        )

        self._log(
            f"Waste penalties     : "
            f"{stats['waste_penalties']}"
        )

        self._log(
            f"Invalid actions     : "
            f"{stats['invalid_actions']}"
        )

        self._log(
            f"Waiting events      : "
            f"{stats['waits']}"
        )

        self._log(
            f"Explorations        : "
            f"{stats['explorations']}"
        )

        self._log(
            f"Exploitations       : "
            f"{stats['exploitations']}"
        )

        self._log(
            f"Positive rewards    : "
            f"{stats['total_positive_rewards']:+.2f}"
        )

        self._log(
            f"Total penalties     : "
            f"{stats['total_penalties']:.2f}"
        )

        self._log(
            f"Total reward        : "
            f"{stats['total_reward']:+.2f}"
        )

        self._log(
            f"Tree-backup n       : "
            f"{stats['n_step']}"
        )

        self._log(
            f"Learning rate alpha : "
            f"{stats['learning_rate']:.2f}"
        )

        self._log(
            f"Discount gamma      : "
            f"{stats['discount_factor']:.2f}"
        )

        self._log(
            f"Epsilon             : "
            f"{stats['epsilon']:.4f}"
        )

        self._log(
            f"Last Tree Return    : "
            f"{stats['tree_backup_return']:+.3f}"
        )

        self._log(
            f"Last TD Error       : "
            f"{stats['td_error']:+.3f}"
        )

        self._log(
            "============================================================"
        )

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


NStepTreeBackup = (
    NStepTreeBackupAlgorithm
)

TreeBackupAlgorithm = (
    NStepTreeBackupAlgorithm
)

NStepTreeBackupAgent = (
    NStepTreeBackupAlgorithm
)