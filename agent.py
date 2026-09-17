import math
import messages

try:
    from n_step_tree_backup import NStepTreeBackupAlgorithm
except ImportError:
    NStepTreeBackupAlgorithm = None

try:
    from expected_sarsa import ExpectedSARSAAlgorithm
except ImportError:
    ExpectedSARSAAlgorithm = None
    print()
    print("========================================")
    print("[AGENT WARNING]")
    print("Could not import expected_sarsa.py")
    print("Expected SARSA will fall back to Default.")
    print("========================================")
    print()

ACTOR_CRITIC_IMPORT_ERROR = None

try:
    from actor_critic import ActorCriticAlgorithm
except Exception as exc:
    ActorCriticAlgorithm = None
    ACTOR_CRITIC_IMPORT_ERROR = exc
    print()
    print("========================================")
    print("[ACTOR-CRITIC IMPORT ERROR]")
    print(f"{type(exc).__name__}: {exc}")
    print("Actor-Critic is unavailable.")
    print("========================================")
    print()

DQN_IMPORT_ERROR = None

try:
    from dqn import DQNAlgorithm as IntegratedDQNAlgorithm
except Exception as exc:
    IntegratedDQNAlgorithm = None
    DQN_IMPORT_ERROR = exc
    print()
    print("========================================")
    print("[AGENT WARNING]")
    print("Could not import dqn.py")
    print(f"[AGENT WARNING] Reason: {exc}")
    print("DQN is unavailable until dqn.py is fixed.")
    print("========================================")
    print()

ALGORITHM_DEFAULT = "DEFAULT"
ALGORITHM_Q_LEARNING = "Q-LEARNING"
ALGORITHM_SARSA = "SARSA"
ALGORITHM_EXPECTED_SARSA = "EXPECTED SARSA"
ALGORITHM_ACTOR_CRITIC = "ACTOR-CRITIC"
ALGORITHM_DQN = "DQN"
ALGORITHM_N_STEP_TREE_BACKUP = "N-STEP TREE BACKUP"

DEFAULT_ALGORITHM = ALGORITHM_DEFAULT
FREE_TABLE_DELAY = 5.0


class BaseAlgorithm:
    def __init__(self, table_manager):
        self.table_manager = table_manager

    def choose_table(self, group_size):
        raise NotImplementedError


def _get_table_capacity(table):
    capacity = getattr(table, "capacity", None)

    if capacity is None:
        capacity = getattr(table, "max_capacity", None)

    if capacity is None:
        capacity = getattr(table, "seats", None)

    try:
        return int(capacity)
    except (TypeError, ValueError):
        return 0


def _is_table_occupied(table):
    return bool(getattr(table, "occupied", False))


class DefaultAlgorithm(BaseAlgorithm):
    def choose_table(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return None

        candidates = []

        for index, table in enumerate(self.table_manager.tables):
            if _is_table_occupied(table):
                continue

            capacity = _get_table_capacity(table)

            if capacity < group_size:
                continue

            candidates.append((capacity, index))

        if not candidates:
            return None

        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][1]


class QLearningAlgorithm(BaseAlgorithm):
    def __init__(self, table_manager):
        super().__init__(table_manager)
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1
        self.q_table = {}

    def choose_table(self, group_size):
        print("[Q-LEARNING] Placeholder algorithm called.")
        return None


class SARSAAlgorithm(BaseAlgorithm):
    def __init__(self, table_manager):
        super().__init__(table_manager)
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1
        self.q_table = {}

    def choose_table(self, group_size):
        print("[SARSA] Placeholder algorithm called.")
        return None


class DQNAlgorithm(BaseAlgorithm):
    def __init__(self, table_manager):
        super().__init__(table_manager)
        self.learning_rate = 0.001
        self.discount_factor = 0.95
        self.epsilon = 0.1
        self.network = None
        self.target_network = None
        self.replay_buffer = []

    def choose_table(self, group_size):
        print("[DQN] Placeholder algorithm called.")
        return None


def create_algorithm(algorithm_name, table_manager):
    if algorithm_name == ALGORITHM_DEFAULT:
        return DefaultAlgorithm(table_manager)

    if algorithm_name == ALGORITHM_Q_LEARNING:
        return QLearningAlgorithm(table_manager)

    if algorithm_name == ALGORITHM_SARSA:
        return SARSAAlgorithm(table_manager)

    if algorithm_name == ALGORITHM_EXPECTED_SARSA:
        if ExpectedSARSAAlgorithm is None:
            print("[AGENT ERROR] Expected SARSA unavailable.")
            print("[AGENT] Falling back to DEFAULT.")
            return DefaultAlgorithm(table_manager)

        return ExpectedSARSAAlgorithm(table_manager)

    if algorithm_name == ALGORITHM_ACTOR_CRITIC:
        if ActorCriticAlgorithm is None:
            reason = ACTOR_CRITIC_IMPORT_ERROR

            message = (
                "[AGENT ERROR] Actor-Critic was requested, "
                "but actor_critic.py could not be loaded."
            )

            if reason is not None:
                message += (
                    f" Import error: "
                    f"{type(reason).__name__}: {reason}"
                )

            raise RuntimeError(message)

        try:
            algorithm = ActorCriticAlgorithm(
                table_manager
            )
        except Exception as exc:
            raise RuntimeError(
                "Actor-Critic initialization failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        if not isinstance(
            algorithm,
            ActorCriticAlgorithm
        ):
            raise RuntimeError(
                "Actor-Critic initialization returned "
                "an unexpected algorithm instance."
            )

        print(
            "[AGENT] Actor-Critic instance created: "
            f"{type(algorithm).__name__}"
        )

        return algorithm

    if algorithm_name == ALGORITHM_DQN:
        if IntegratedDQNAlgorithm is None:
            print()
            print("========================================")
            print("[AGENT ERROR] REAL DQN COULD NOT BE LOADED")

            if DQN_IMPORT_ERROR is not None:
                print(f"[AGENT ERROR] {DQN_IMPORT_ERROR}")

            print(
                "[AGENT ERROR] Make sure dqn.py is in the "
                "same folder as agent.py."
            )
            print("========================================")
            print()

            return DefaultAlgorithm(table_manager)

        return IntegratedDQNAlgorithm(table_manager)

    if algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
        if NStepTreeBackupAlgorithm is None:
            print()
            print("========================================")
            print(
                "[AGENT ERROR] N-step Tree Backup "
                "COULD NOT BE LOADED"
            )
            print(
                "[AGENT ERROR] Make sure "
                "n_step_tree_backup.py is in the "
                "same folder as agent.py."
            )
            print("========================================")
            print()

            return DefaultAlgorithm(table_manager)

        return NStepTreeBackupAlgorithm(table_manager)

    print(
        f"[AGENT WARNING] Unknown algorithm: "
        f"{algorithm_name}"
    )
    print("[AGENT] Falling back to DEFAULT.")
    return DefaultAlgorithm(table_manager)


class RestaurantAgent:
    def __init__(
        self,
        table_manager,
        algorithm=DEFAULT_ALGORITHM
    ):
        self.table_manager = table_manager

        self.algorithm_name = self._normalize_algorithm_name(
            algorithm
        )

        self.algorithm = create_algorithm(
            self.algorithm_name,
            self.table_manager
        )

        if (
            self.algorithm_name == ALGORITHM_ACTOR_CRITIC
            and not isinstance(
                self.algorithm,
                ActorCriticAlgorithm
            )
        ):
            raise RuntimeError(
                "Actor-Critic was requested but the "
                "agent did not receive an ActorCriticAlgorithm."
            )

        self._attach_algorithm_context()

        self.total_decisions = 0
        self.successful_allocations = 0
        self.failed_allocations = 0
        self.total_customers_served = 0

        self.simulation_elapsed_seconds = 0.0

        self.waiting_records = []
        self.completed_wait_times = []
        self.waiting_time_seconds = 0.0
        self.waiting_queue_active = False
        self.processing_queue = False

        self.previous_occupied = {}
        self.free_timers = {}
        self.just_cleaned_tables = []
        self.cleaning_message_seconds = {}

        self.current_reward = 0.0
        self.best_reward = 0.0
        self.q_updates = 0

        self.last_group_size = None
        self.last_selected_table = "--"
        self.last_table_capacity = None
        self.last_decision_result = "--"
        self.last_reward = None
        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )

        self._actor_critic_pending = None

        self._initialize_table_states()

        print()
        print("========================================")
        print("RESTAURANT AGENT INITIALIZED")
        print("========================================")
        print(f"Active algorithm: {self.algorithm_name}")
        print(
            f"Algorithm object: "
            f"{type(self.algorithm).__name__}"
        )
        print(
            f"Cleaning delay: "
            f"{FREE_TABLE_DELAY:.0f} seconds"
        )
        print()

    def _normalize_algorithm_name(self, algorithm_name):
        if algorithm_name is None:
            return DEFAULT_ALGORITHM

        value = str(algorithm_name).strip().upper()

        mapping = {
            "DEFAULT": ALGORITHM_DEFAULT,
            "EXPECTED SARSA": ALGORITHM_EXPECTED_SARSA,
            "EXPECTED_SARSA": ALGORITHM_EXPECTED_SARSA,
            "ACTOR-CRITIC": ALGORITHM_ACTOR_CRITIC,
            "ACTOR CRITIC": ALGORITHM_ACTOR_CRITIC,
            "ACTOR_CRITIC": ALGORITHM_ACTOR_CRITIC,
            "Q-LEARNING": ALGORITHM_Q_LEARNING,
            "Q_LEARNING": ALGORITHM_Q_LEARNING,
            "SARSA": ALGORITHM_SARSA,
            "DQN": ALGORITHM_DQN,
            "N-STEP TREE BACKUP": ALGORITHM_N_STEP_TREE_BACKUP,
            "N STEP TREE BACKUP": ALGORITHM_N_STEP_TREE_BACKUP,
            "N_STEP TREE BACKUP": ALGORITHM_N_STEP_TREE_BACKUP,
            "N_STEP_TREE_BACKUP": ALGORITHM_N_STEP_TREE_BACKUP,
            "TREE BACKUP": ALGORITHM_N_STEP_TREE_BACKUP,
            "NSTEP TREE BACKUP": ALGORITHM_N_STEP_TREE_BACKUP
        }

        return mapping.get(
            value,
            ALGORITHM_DEFAULT
        )

    def _display_algorithm_name(self):
        if self.algorithm_name == ALGORITHM_EXPECTED_SARSA:
            return "Expected SARSA"

        if self.algorithm_name == ALGORITHM_Q_LEARNING:
            return "Q-Learning"

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            return "Actor-Critic"

        if self.algorithm_name == ALGORITHM_DEFAULT:
            return "Default"

        if self.algorithm_name == ALGORITHM_DQN:
            return "DQN"

        if self.algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
            return "N-step Tree Backup"

        return self.algorithm_name

    def _attach_algorithm_context(self):
        if self.algorithm_name in (
            ALGORITHM_EXPECTED_SARSA,
            ALGORITHM_ACTOR_CRITIC,
            ALGORITHM_DQN,
            ALGORITHM_N_STEP_TREE_BACKUP
        ):
            if hasattr(
                self.algorithm,
                "ready_checker"
            ):
                self.algorithm.ready_checker = (
                    self.is_table_ready
                )

            if hasattr(
                self.algorithm,
                "set_ready_checker"
            ):
                try:
                    self.algorithm.set_ready_checker(
                        self.is_table_ready
                    )
                except Exception:
                    pass

    def _initialize_table_states(self):
        for index, table in enumerate(
            self.table_manager.tables
        ):
            self.previous_occupied[index] = (
                _is_table_occupied(table)
            )

    def is_table_ready(self, table_index):
        try:
            table_index = int(table_index)
        except (TypeError, ValueError):
            return False

        if table_index in self.free_timers:
            return False

        if table_index < 0:
            return False

        if table_index >= len(
            self.table_manager.tables
        ):
            return False

        table = self.table_manager.tables[
            table_index
        ]

        if _is_table_occupied(table):
            return False

        return True

    def get_ready_table_indices(self):
        ready = []

        for index in range(
            len(self.table_manager.tables)
        ):
            if self.is_table_ready(index):
                ready.append(index)

        return ready

    def update(self, dt, waiting_input=None):
        try:
            dt_value = float(dt)
        except (TypeError, ValueError):
            return

        if dt_value < 0:
            dt_value = 0.0

        dt_seconds = dt_value / 1000.0

        self.simulation_elapsed_seconds += dt_seconds

        if waiting_input is not None:
            try:
                waiting_people = (
                    waiting_input.get_waiting_people()
                )
                queue_has_groups = bool(waiting_people)
            except Exception:
                queue_has_groups = False

            self.waiting_queue_active = queue_has_groups

            if queue_has_groups:
                self.waiting_time_seconds += dt_seconds

        self.just_cleaned_tables = []

        for index, table in enumerate(
            self.table_manager.tables
        ):
            occupied = _is_table_occupied(table)

            previous = self.previous_occupied.get(
                index,
                occupied
            )

            if previous and not occupied:
                self.free_timers[index] = 0.0
                self.cleaning_message_seconds[index] = 5

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

            self.previous_occupied[index] = occupied

        finished = []

        for index in list(self.free_timers.keys()):
            if index >= len(
                self.table_manager.tables
            ):
                finished.append(index)
                self.cleaning_message_seconds.pop(
                    index,
                    None
                )
                continue

            table = self.table_manager.tables[index]

            if _is_table_occupied(table):
                finished.append(index)
                self.cleaning_message_seconds.pop(
                    index,
                    None
                )
                continue

            self.free_timers[index] += dt_seconds

            remaining_seconds = self.get_table_wait_time(
                index
            )

            countdown_seconds = max(
                1,
                int(math.ceil(remaining_seconds))
            )

            last_message_seconds = (
                self.cleaning_message_seconds.get(index)
            )

            if countdown_seconds != last_message_seconds:
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

            if (
                self.free_timers[index]
                >= FREE_TABLE_DELAY
            ):
                table_name = getattr(
                    table,
                    "table_id",
                    f"T{index + 1}"
                )

                finished.append(index)

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

        for index in finished:
            self.free_timers.pop(index, None)

    def choose_table(self, group_size):
        self.total_decisions += 1

        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            self.failed_allocations += 1
            return None

        print()
        print("----------------------------------------")
        print("[AGENT] New allocation request")
        print(f"[AGENT] Group size: {group_size}")
        print(f"[AGENT] Algorithm: {self.algorithm_name}")
        print(
            f"[AGENT] Algorithm object: "
            f"{type(self.algorithm).__name__}"
        )

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            try:
                table_index = self._choose_actor_critic_table(
                    group_size
                )
            except Exception as exc:
                print(
                    "[AGENT] Actor-Critic decision error: "
                    f"{exc}"
                )
                self._actor_critic_pending = None
                table_index = None

        elif self.algorithm_name == ALGORITHM_EXPECTED_SARSA:
            try:
                table_index = self.algorithm.choose_table(
                    group_size,
                    ready_checker=self.is_table_ready
                )
            except TypeError:
                table_index = self.algorithm.choose_table(
                    group_size
                )
            except Exception as exc:
                print(
                    "[AGENT] Expected SARSA decision error: "
                    f"{exc}"
                )
                table_index = None

        elif self.algorithm_name == ALGORITHM_DQN:
            try:
                table_index = self.algorithm.choose_table(
                    group_size,
                    ready_checker=self.is_table_ready
                )
            except TypeError:
                table_index = self.algorithm.choose_table(
                    group_size
                )
            except Exception as exc:
                print(
                    "[AGENT] DQN decision error: "
                    f"{exc}"
                )
                table_index = None

        elif self.algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
            try:
                table_index = self.algorithm.choose_table(
                    group_size,
                    ready_checker=self.is_table_ready
                )
            except TypeError:
                table_index = self.algorithm.choose_table(
                    group_size
                )
            except Exception as exc:
                print(
                    "[AGENT] N-step Tree Backup decision error: "
                    f"{exc}"
                )
                table_index = None

        else:
            table_index = self._choose_table_without_counting(
                group_size
            )

        if table_index is None:
            self.failed_allocations += 1
            print("[AGENT] No suitable table available.")
            print("----------------------------------------")
            return None

        print(
            f"[AGENT] Selected table index: {table_index}"
        )
        print("----------------------------------------")

        return table_index

    def _choose_table_without_counting(self, group_size):
        if self.algorithm_name == ALGORITHM_DEFAULT:
            return self._default_ready_table(group_size)

        try:
            return self.algorithm.choose_table(group_size)
        except Exception as exc:
            print(
                f"[AGENT WARNING] Algorithm error: {exc}"
            )
            return None

    def _default_ready_table(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return None

        candidates = []

        for index, table in enumerate(
            self.table_manager.tables
        ):
            if not self.is_table_ready(index):
                continue

            capacity = _get_table_capacity(table)

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

    def _get_algorithm_state(self, group_size):
        if not hasattr(
            self.algorithm,
            "get_state"
        ):
            return None

        try:
            return self.algorithm.get_state(
                group_size,
                self.table_manager.tables,
                ready_checker=self.is_table_ready
            )
        except TypeError:
            try:
                return self.algorithm.get_state(
                    group_size,
                    self.table_manager.tables
                )
            except Exception:
                try:
                    return self.algorithm.get_state(
                        group_size
                    )
                except Exception:
                    return None
        except Exception:
            return None

    def _get_algorithm_valid_actions(self, group_size):
        if not hasattr(
            self.algorithm,
            "get_valid_actions"
        ):
            return []

        try:
            actions = self.algorithm.get_valid_actions(
                group_size,
                self.table_manager.tables,
                ready_checker=self.is_table_ready
            )

            return list(actions) if actions is not None else []

        except TypeError:
            try:
                actions = self.algorithm.get_valid_actions(
                    group_size,
                    self.table_manager.tables
                )

                return list(actions) if actions is not None else []

            except Exception:
                try:
                    actions = self.algorithm.get_valid_actions(
                        group_size
                    )

                    return list(actions) if actions is not None else []

                except Exception:
                    return []

        except Exception:
            return []

    def _get_actor_critic_feasible_actions(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return []

        if group_size <= 0:
            return []

        feasible = []

        for index, table in enumerate(
            self.table_manager.tables
        ):
            if not self.is_table_ready(index):
                continue

            capacity = _get_table_capacity(table)

            if capacity < group_size:
                continue

            feasible.append(index)

        return feasible

    def _choose_actor_critic_table(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return None

        if group_size <= 0:
            return None

        if not isinstance(
            self.algorithm,
            ActorCriticAlgorithm
        ):
            raise RuntimeError(
                "Actor-Critic requested, but active "
                f"algorithm object is "
                f"{type(self.algorithm).__name__}."
            )

        feasible = self._get_actor_critic_feasible_actions(
            group_size
        )

        if hasattr(
            self.algorithm,
            "last_feasible_actions"
        ):
            self.algorithm.last_feasible_actions = list(
                feasible
            )

        if hasattr(
            self.algorithm,
            "feasible_table_count"
        ):
            self.algorithm.feasible_table_count = len(
                feasible
            )

        print(
            f"[ACTOR-CRITIC] Feasible tables: "
            f"{[f'T{i + 1}' for i in feasible]}"
        )

        if not feasible:
            self._actor_critic_pending = None

            if hasattr(
                self.algorithm,
                "last_action"
            ):
                self.algorithm.last_action = None

            if hasattr(
                self.algorithm,
                "last_group_size"
            ):
                self.algorithm.last_group_size = group_size

            if hasattr(
                self.algorithm,
                "failed_allocations"
            ):
                self.algorithm.failed_allocations += 1

            if hasattr(
                self.algorithm,
                "last_feasible_actions"
            ):
                self.algorithm.last_feasible_actions = []

            return None

        state = self._get_algorithm_state(
            group_size
        )

        if state is None:
            raise RuntimeError(
                "Actor-Critic could not create a valid state."
            )

        if not hasattr(
            self.algorithm,
            "select_action"
        ):
            raise RuntimeError(
                "Actor-Critic does not provide select_action()."
            )

        details = self.algorithm.select_action(
            state,
            feasible,
            greedy=not getattr(
                self.algorithm,
                "training",
                True
            ),
            return_details=True
        )

        if (
            not details
            or details.get("action") is None
        ):
            self._actor_critic_pending = None
            return None

        try:
            table_index = int(
                details["action"]
            )
        except (TypeError, ValueError):
            self._actor_critic_pending = None
            return None

        if table_index not in feasible:
            self._actor_critic_pending = None
            return None

        table = self.table_manager.tables[
            table_index
        ]

        capacity = _get_table_capacity(
            table
        )

        reward = self._calculate_reward(
            group_size,
            table_index,
            capacity,
            valid_actions=feasible
        )

        unused = max(
            0,
            capacity - group_size
        )

        valid = (
            table_index in feasible
            and capacity >= group_size
            and self.is_table_ready(table_index)
        )

        if hasattr(
            self.algorithm,
            "total_decisions"
        ):
            self.algorithm.total_decisions += 1

        if hasattr(
            self.algorithm,
            "last_action"
        ):
            self.algorithm.last_action = table_index

        if hasattr(
            self.algorithm,
            "last_group_size"
        ):
            self.algorithm.last_group_size = group_size

        if hasattr(
            self.algorithm,
            "last_reward"
        ):
            self.algorithm.last_reward = float(reward)

        if hasattr(
            self.algorithm,
            "current_reward"
        ):
            self.algorithm.current_reward = float(reward)

        if hasattr(
            self.algorithm,
            "last_unused_seats"
        ):
            self.algorithm.last_unused_seats = int(
                unused
            )

        if hasattr(
            self.algorithm,
            "last_state"
        ):
            self.algorithm.last_state = state

        if hasattr(
            self.algorithm,
            "last_log_probability"
        ):
            self.algorithm.last_log_probability = (
                details.get("log_prob")
            )

        if hasattr(
            self.algorithm,
            "last_value"
        ):
            self.algorithm.last_value = (
                details.get("value")
            )

        if hasattr(
            self.algorithm,
            "last_entropy"
        ):
            self.algorithm.last_entropy = float(
                details.get(
                    "entropy",
                    0.0
                )
            )

        if hasattr(
            self.algorithm,
            "last_policy_probabilities"
        ):
            self.algorithm.last_policy_probabilities = list(
                details.get(
                    "probabilities",
                    []
                )
            )

        if hasattr(
            self.algorithm,
            "last_table_capacity"
        ):
            self.algorithm.last_table_capacity = capacity

        self._actor_critic_pending = {
            "state": state,
            "action": table_index,
            "reward": float(reward),
            "unused": int(unused),
            "valid": bool(valid),
            "details": details,
            "group_size": group_size,
            "capacity": capacity
        }

        print(
            f"[ACTOR-CRITIC] Selected: "
            f"T{table_index + 1} "
            f"({capacity})"
        )

        print(
            f"[ACTOR-CRITIC] Reward: "
            f"{reward:+.2f}"
        )

        print(
            f"[ACTOR-CRITIC] Unused seats: "
            f"{unused}"
        )

        return table_index

    def _learn_actor_critic(
        self,
        previous_state,
        table_index,
        reward,
        next_state
    ):
        if self.algorithm_name != ALGORITHM_ACTOR_CRITIC:
            return False

        pending = self._actor_critic_pending

        if not isinstance(
            pending,
            dict
        ):
            return False

        try:
            pending_action = int(
                pending.get(
                    "action",
                    -1
                )
            )
        except (TypeError, ValueError):
            return False

        if pending_action != int(table_index):
            return False

        details = pending.get(
            "details"
        )

        if details is None:
            return False

        if not hasattr(
            self.algorithm,
            "_update_networks"
        ):
            return False

        try:
            reward = float(reward)

            if hasattr(
                self.algorithm,
                "successful_allocations"
            ):
                self.algorithm.successful_allocations += 1

            if hasattr(
                self.algorithm,
                "total_reward"
            ):
                self.algorithm.total_reward += reward

            if hasattr(
                self.algorithm,
                "total_penalties"
            ) and reward < 0:
                self.algorithm.total_penalties += abs(
                    reward
                )

            if hasattr(
                self.algorithm,
                "exact_fit_count"
            ) and reward == 15.0:
                self.algorithm.exact_fit_count += 1

            elif hasattr(
                self.algorithm,
                "one_unused_count"
            ) and reward == 10.0:
                self.algorithm.one_unused_count += 1

            elif hasattr(
                self.algorithm,
                "two_unused_count"
            ) and reward == 5.0:
                self.algorithm.two_unused_count += 1

            elif (
                hasattr(
                    self.algorithm,
                    "large_waste_count"
                )
                and reward == -5.0
            ):
                self.algorithm.large_waste_count += 1

                if hasattr(
                    self.algorithm,
                    "waste_penalty_count"
                ):
                    self.algorithm.waste_penalty_count += 1

            action = int(table_index)

            if hasattr(
                self.algorithm,
                "table_action_counts"
            ):
                self.algorithm.table_action_counts[action] += 1

            if hasattr(
                self.algorithm,
                "table_reward_totals"
            ):
                self.algorithm.table_reward_totals[action] += reward

            if hasattr(
                self.algorithm,
                "table_best_rewards"
            ):
                attempts = (
                    self.algorithm.table_action_counts[action]
                    if hasattr(
                        self.algorithm,
                        "table_action_counts"
                    )
                    else 1
                )

                if (
                    attempts == 1
                    or reward
                    > self.algorithm.table_best_rewards[action]
                ):
                    self.algorithm.table_best_rewards[action] = reward

            if (
                hasattr(
                    self.algorithm,
                    "best_reward"
                )
                and reward > self.algorithm.best_reward
            ):
                self.algorithm.best_reward = reward

            updated = self.algorithm._update_networks(
                reward=reward,
                next_state=next_state,
                done=False,
                details=details
            )

            if not updated:
                print(
                    "[AGENT] Actor-Critic network update "
                    "did not execute."
                )
                return False

            self._actor_critic_pending = None

            self.q_updates = int(
                getattr(
                    self.algorithm,
                    "q_updates",
                    self.q_updates
                )
            )

            try:
                ac_stats = self.algorithm.get_statistics()

                print(
                    f"[ACTOR-CRITIC] Actor update: "
                    f"{ac_stats.get('actor_updates', 0)}"
                )

                print(
                    f"[ACTOR-CRITIC] Critic update: "
                    f"{ac_stats.get('critic_updates', 0)}"
                )

                print(
                    f"[ACTOR-CRITIC] Actor loss: "
                    f"{ac_stats.get('actor_loss', 0.0):+.4f}"
                )

                print(
                    f"[ACTOR-CRITIC] Critic loss: "
                    f"{ac_stats.get('critic_loss', 0.0):+.4f}"
                )

                print(
                    f"[ACTOR-CRITIC] Advantage: "
                    f"{ac_stats.get('advantage', 0.0):+.4f}"
                )

                print(
                    f"[ACTOR-CRITIC] Value: "
                    f"{ac_stats.get('value_estimate', 0.0):+.4f}"
                )

            except Exception:
                pass

            return True

        except Exception as exc:
            print(
                "[AGENT] Actor-Critic learning warning: "
                f"{exc}"
            )
            return False

    def _record_actor_critic_failure(
        self,
        group_size,
        reward=-100.0
    ):
        pending = self._actor_critic_pending

        if pending is None:
            return

        try:
            if hasattr(
                self.algorithm,
                "failed_allocations"
            ):
                self.algorithm.failed_allocations += 1

            if hasattr(
                self.algorithm,
                "invalid_allocations"
            ):
                self.algorithm.invalid_allocations += 1

            if hasattr(
                self.algorithm,
                "current_reward"
            ):
                self.algorithm.current_reward = float(
                    reward
                )

            if hasattr(
                self.algorithm,
                "last_reward"
            ):
                self.algorithm.last_reward = float(
                    reward
                )

            if hasattr(
                self.algorithm,
                "total_reward"
            ):
                self.algorithm.total_reward += float(
                    reward
                )

            if (
                hasattr(
                    self.algorithm,
                    "total_penalties"
                )
                and reward < 0
            ):
                self.algorithm.total_penalties += abs(
                    float(reward)
                )

        except Exception:
            pass

        self._actor_critic_pending = None

    def allocate_group(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return None

        previous_state = None
        valid_actions_before = None

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            previous_state = self._get_algorithm_state(
                group_size
            )

            valid_actions_before = (
                self._get_actor_critic_feasible_actions(
                    group_size
                )
            )

        elif self.algorithm_name in (
            ALGORITHM_EXPECTED_SARSA,
            ALGORITHM_N_STEP_TREE_BACKUP
        ):
            previous_state = self._get_algorithm_state(
                group_size
            )

            if self.algorithm_name == ALGORITHM_EXPECTED_SARSA:
                valid_actions_before = (
                    self._get_algorithm_valid_actions(
                        group_size
                    )
                )

        table_index = self.choose_table(
            group_size
        )

        if table_index is None:
            self._record_failed_decision(
                group_size
            )
            return None

        if not isinstance(
            table_index,
            int
        ):
            try:
                table_index = int(
                    table_index
                )
            except (TypeError, ValueError):
                self._record_failed_decision(
                    group_size
                )
                return None

        if (
            table_index < 0
            or table_index >= len(
                self.table_manager.tables
            )
        ):
            print("[AGENT] Invalid table index.")

            if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                self._record_actor_critic_failure(
                    group_size,
                    -100.0
                )

            self._record_failed_decision(
                group_size
            )
            return None

        if not self.is_table_ready(
            table_index
        ):
            print(
                "[AGENT] Selected table is not READY."
            )

            if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                self._record_actor_critic_failure(
                    group_size,
                    -100.0
                )

            self._record_failed_decision(
                group_size,
                reward=-100.0
            )
            return None

        table = self.table_manager.tables[
            table_index
        ]

        table_name = getattr(
            table,
            "table_id",
            f"T{table_index + 1}"
        )

        table_capacity = _get_table_capacity(
            table
        )

        if table_capacity < group_size:
            print(
                "[AGENT] Selected table is too small."
            )

            if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                self._record_actor_critic_failure(
                    group_size,
                    -100.0
                )

            self._record_failed_decision(
                group_size,
                table_name,
                table_capacity,
                -100.0
            )
            return None

        if (
            self.algorithm_name
            == ALGORITHM_EXPECTED_SARSA
            and hasattr(
                self.algorithm,
                "get_immediate_reward"
            )
        ):
            try:
                reward = (
                    self.algorithm.get_immediate_reward(
                        group_size,
                        table_index,
                        self.table_manager.tables,
                        ready_checker=self.is_table_ready,
                        success=True,
                        valid_actions=valid_actions_before
                    )
                )
            except TypeError:
                reward = self._calculate_reward(
                    group_size,
                    table_index,
                    table_capacity,
                    valid_actions=valid_actions_before
                )

        elif (
            self.algorithm_name
            == ALGORITHM_N_STEP_TREE_BACKUP
            and hasattr(
                self.algorithm,
                "calculate_table_reward"
            )
        ):
            try:
                reward, _, _ = (
                    self.algorithm.calculate_table_reward(
                        group_size,
                        table_index
                    )
                )
            except Exception:
                reward = self._calculate_reward(
                    group_size,
                    table_index,
                    table_capacity,
                    valid_actions=valid_actions_before
                )

        elif self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            pending = self._actor_critic_pending

            if (
                isinstance(
                    pending,
                    dict
                )
                and int(
                    pending.get(
                        "action",
                        -1
                    )
                ) == table_index
            ):
                reward = float(
                    pending.get(
                        "reward",
                        0.0
                    )
                )
            else:
                reward = self._calculate_reward(
                    group_size,
                    table_index,
                    table_capacity,
                    valid_actions=valid_actions_before
                )

        else:
            reward = self._calculate_reward(
                group_size,
                table_index,
                table_capacity,
                valid_actions=valid_actions_before
            )

        allocation_success = self._occupy_table(
            table,
            group_size
        )

        if not allocation_success:
            if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                self._record_actor_critic_failure(
                    group_size,
                    -100.0
                )

            self._record_failed_decision(
                group_size,
                table_name,
                table_capacity,
                -100.0
            )
            return None

        self.successful_allocations += 1
        self.total_customers_served += group_size

        self.current_reward = float(
            reward
        )

        if self.current_reward > self.best_reward:
            self.best_reward = self.current_reward

        self.last_group_size = group_size
        self.last_selected_table = table_name
        self.last_table_capacity = table_capacity
        self.last_decision_result = "SUCCESS"
        self.last_reward = float(reward)
        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )

        next_state = None

        if self.algorithm_name in (
            ALGORITHM_ACTOR_CRITIC,
            ALGORITHM_EXPECTED_SARSA,
            ALGORITHM_N_STEP_TREE_BACKUP
        ):
            next_state = self._get_algorithm_state(
                group_size
            )

        if (
            self.algorithm_name == ALGORITHM_ACTOR_CRITIC
            and previous_state is not None
            and next_state is not None
        ):
            self._learn_actor_critic(
                previous_state,
                table_index,
                reward,
                next_state
            )

        elif (
            self.algorithm_name in (
                ALGORITHM_EXPECTED_SARSA,
                ALGORITHM_N_STEP_TREE_BACKUP
            )
            and previous_state is not None
            and next_state is not None
            and hasattr(
                self.algorithm,
                "learn_after_allocation"
            )
        ):
            next_valid_actions = (
                self._get_algorithm_valid_actions(
                    group_size
                )
            )

            try:
                if (
                    self.algorithm_name
                    == ALGORITHM_N_STEP_TREE_BACKUP
                ):
                    result = (
                        self.algorithm.learn_after_allocation(
                            previous_state,
                            table_index,
                            reward,
                            next_state,
                            next_valid_actions,
                            terminal=False
                        )
                    )
                else:
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

            except TypeError:
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
                        "[AGENT] Learning warning: "
                        f"{exc}"
                    )

            except Exception as exc:
                print(
                    "[AGENT] Learning warning: "
                    f"{exc}"
                )

        print()
        print("========================================")
        print("[AGENT] ALLOCATION SUCCESS")
        print(f"Group: {group_size}")
        print(f"Table: {table_name}")
        print(f"Capacity: {table_capacity}")
        print(f"Reward: {reward:+.2f}")
        print(f"Algorithm: {self.algorithm_name}")

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            try:
                ac_stats = (
                    self.algorithm.get_statistics()
                )

                print(
                    f"Actor updates: "
                    f"{ac_stats.get('actor_updates', 0)}"
                )

                print(
                    f"Critic updates: "
                    f"{ac_stats.get('critic_updates', 0)}"
                )

                print(
                    f"Actor loss: "
                    f"{ac_stats.get('actor_loss', 0.0):+.4f}"
                )

                print(
                    f"Critic loss: "
                    f"{ac_stats.get('critic_loss', 0.0):+.4f}"
                )

                print(
                    f"Advantage: "
                    f"{ac_stats.get('advantage', 0.0):+.4f}"
                )

                print(
                    f"Value: "
                    f"{ac_stats.get('value_estimate', 0.0):+.4f}"
                )

            except Exception:
                pass

        print("========================================")
        print()

        return table

    def _occupy_table(self, table, group_size):
        if hasattr(
            table,
            "assign_customers"
        ):
            try:
                result = table.assign_customers(
                    group_size
                )
                return result is not False
            except TypeError:
                try:
                    result = table.assign_customers()
                    return result is not False
                except Exception:
                    pass
            except Exception:
                pass

        if hasattr(
            table,
            "seat_customers"
        ):
            try:
                result = table.seat_customers(
                    group_size
                )
                return result is not False
            except Exception:
                pass

        if hasattr(
            table,
            "occupy"
        ):
            try:
                result = table.occupy(
                    group_size
                )
                return result is not False
            except TypeError:
                try:
                    result = table.occupy()
                    return result is not False
                except Exception:
                    pass
            except Exception:
                pass

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
                return result is not False
            except TypeError:
                try:
                    result = method(
                        table
                    )
                    return result is not False
                except Exception:
                    continue
            except Exception:
                continue

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

    def _calculate_reward(
        self,
        group_size,
        table_index,
        table_capacity,
        valid_actions=None
    ):
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

        unused_seats = (
            table_capacity - group_size
        )

        if unused_seats == 0:
            return 15.0

        if unused_seats == 1:
            return 10.0

        if unused_seats == 2:
            return 5.0

        return -5.0

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

        self.current_reward = float(
            reward
        )

        self.last_group_size = group_size

        self.last_selected_table = (
            table_name if table_name else "--"
        )

        self.last_table_capacity = (
            table_capacity
        )

        self.last_decision_result = "FAILED"

        self.last_reward = float(
            reward
        )

        self.last_decision_algorithm = (
            self._display_algorithm_name()
        )

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
            try:
                waiting_people = (
                    waiting_input.get_waiting_people()
                )
            except Exception:
                waiting_people = []

            if not waiting_people:
                return None

            groups = []

            for item in waiting_people:
                try:
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

                    elif isinstance(
                        item,
                        dict
                    ):
                        size = item.get(
                            "group_size",
                            item.get(
                                "people",
                                item.get(
                                    "size",
                                    0
                                )
                            )
                        )

                        try:
                            size = int(size)
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

            selected_queue_index = None
            selected_group_size = None

            for queue_index, item in enumerate(
                groups
            ):
                group_size = item[0]

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

            if selected_queue_index is None:
                return None

            print()
            print("========================================")
            print("[AGENT QUEUE] Processing waiting group")
            print(
                f"[AGENT QUEUE] Group: "
                f"{selected_group_size}"
            )
            print(
                f"[AGENT QUEUE] Queue index: "
                f"{selected_queue_index}"
            )
            print("========================================")

            table = self.allocate_group(
                selected_group_size
            )

            if table is None:
                return None

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

            self._remove_waiting_group(
                waiting_input,
                selected_queue_index,
                selected_group_size
            )

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

    def _has_suitable_ready_table(
        self,
        group_size
    ):
        try:
            group_size = int(group_size)
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

    def _remove_waiting_group(
        self,
        waiting_input,
        queue_index,
        group_size
    ):
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
                    and queue_index < len(
                        records
                    )
                ):
                    records.pop(
                        queue_index
                    )
                    return True

        return False

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

        if new_algorithm_name == self.algorithm_name:
            return False

        old_algorithm = self.algorithm_name

        if old_algorithm in (
            ALGORITHM_N_STEP_TREE_BACKUP,
            ALGORITHM_ACTOR_CRITIC
        ):
            self.finalize_episode()

        self._actor_critic_pending = None

        new_algorithm = create_algorithm(
            new_algorithm_name,
            self.table_manager
        )

        if (
            new_algorithm_name == ALGORITHM_ACTOR_CRITIC
            and not isinstance(
                new_algorithm,
                ActorCriticAlgorithm
            )
        ):
            raise RuntimeError(
                "Actor-Critic was requested but the "
                "new algorithm instance is invalid."
            )

        self.algorithm_name = (
            new_algorithm_name
        )

        self.algorithm = new_algorithm

        self._attach_algorithm_context()

        self.current_reward = 0.0
        self.q_updates = 0

        print()
        print("========================================")
        print("[AGENT] ALGORITHM SWITCHED")
        print(
            f"[AGENT] "
            f"{old_algorithm} -> "
            f"{self.algorithm_name}"
        )
        print(
            f"[AGENT] Active object: "
            f"{type(self.algorithm).__name__}"
        )
        print("========================================")
        print()

        if (
            waiting_input is not None
            and hasattr(
                waiting_input,
                "set_agent_message"
            )
        ):
            try:
                if self.algorithm_name == ALGORITHM_EXPECTED_SARSA:
                    waiting_input.set_agent_message(
                        messages.expected_sarsa_switched_message()
                    )

                elif self.algorithm_name == ALGORITHM_DEFAULT:
                    waiting_input.set_agent_message(
                        messages.default_algorithm_switched_message()
                    )

                elif self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                    waiting_input.set_agent_message(
                        "Actor-Critic algorithm activated."
                    )

                elif self.algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
                    waiting_input.set_agent_message(
                        "N-step Tree Backup algorithm activated."
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

    def finalize_episode(self):
        if not hasattr(
            self.algorithm,
            "finalize_episode"
        ):
            return 0

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            pending = self._actor_critic_pending

            if pending is None:
                return 0

            try:
                details = pending.get(
                    "details"
                )

                reward = float(
                    pending.get(
                        "reward",
                        0.0
                    )
                )

                if (
                    details is not None
                    and hasattr(
                        self.algorithm,
                        "_update_networks"
                    )
                ):
                    self.algorithm._update_networks(
                        reward=reward,
                        next_state=None,
                        done=True,
                        details=details
                    )

                    self._actor_critic_pending = None

                    self.q_updates = int(
                        getattr(
                            self.algorithm,
                            "q_updates",
                            self.q_updates
                        )
                    )

                    return 1

            except Exception as exc:
                print(
                    "[AGENT] Actor-Critic finalize warning: "
                    f"{exc}"
                )

            return 0

        if self.algorithm_name != (
            ALGORITHM_N_STEP_TREE_BACKUP
        ):
            return 0

        try:
            updates = self.algorithm.finalize_episode()

            try:
                updates = int(updates)
            except (
                TypeError,
                ValueError
            ):
                updates = 0

            if updates > 0:
                self.q_updates += updates

            return updates

        except Exception as exc:
            print(
                "[AGENT] Episode finalize warning: "
                f"{exc}"
            )
            return 0

    def reset_episode(self):
        self._actor_critic_pending = None

        if hasattr(
            self.algorithm,
            "reset_episode"
        ):
            try:
                return bool(
                    self.algorithm.reset_episode()
                )
            except Exception:
                pass

        if (
            self.algorithm_name
            == ALGORITHM_N_STEP_TREE_BACKUP
        ):
            if hasattr(
                self.algorithm,
                "reset_episode_buffer"
            ):
                try:
                    self.algorithm.reset_episode_buffer()
                    return True
                except Exception:
                    pass

        return False

    def get_algorithm_name(self):
        return self.algorithm_name

    def get_latest_decision(self):
        return {
            "group_size": self.last_group_size,
            "table": self.last_selected_table,
            "capacity": self.last_table_capacity,
            "result": self.last_decision_result,
            "reward": self.last_reward,
            "algorithm": self.last_decision_algorithm
        }

    def get_rl_statistics(self):
        accuracy = 0.0

        if self.total_decisions > 0:
            accuracy = (
                self.successful_allocations
                / self.total_decisions
                * 100.0
            )

        statistics = {
            "algorithm": self.algorithm_name,
            "episode": self.total_decisions,
            "current_reward": self.current_reward,
            "best_reward": self.best_reward,
            "q_updates": self.q_updates,
            "allocation_accuracy": accuracy
        }

        if hasattr(
            self.algorithm,
            "get_statistics"
        ):
            try:
                algorithm_stats = (
                    self.algorithm.get_statistics()
                )

                if isinstance(
                    algorithm_stats,
                    dict
                ):
                    protected = {
                        "algorithm",
                        "episode",
                        "current_reward",
                        "best_reward",
                        "q_updates",
                        "allocation_accuracy"
                    }

                    for key, value in algorithm_stats.items():
                        if key not in protected:
                            statistics[key] = value

                    if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                        for key in (
                            "actor_updates",
                            "critic_updates",
                            "actor_loss",
                            "critic_loss",
                            "advantage",
                            "last_advantage",
                            "entropy",
                            "value_estimate",
                            "value",
                            "total_reward",
                            "average_reward",
                            "total_learning_reward",
                            "total_penalties",
                            "penalties",
                            "waste_penalties",
                            "waste_penalty_count",
                            "last_unused_seats",
                            "feasible_table_count",
                            "last_action",
                            "last_group_size",
                            "last_table_capacity",
                            "last_feasible_actions"
                        ):
                            if key in algorithm_stats:
                                statistics[key] = (
                                    algorithm_stats[key]
                                )

                        statistics["q_updates"] = (
                            algorithm_stats.get(
                                "q_updates",
                                self.q_updates
                            )
                        )

                    elif self.algorithm_name == ALGORITHM_DQN:
                        for key in (
                            "loss",
                            "dqn_loss",
                            "last_q_value",
                            "q_value",
                            "target_q",
                            "td_error",
                            "replay_size",
                            "replay_buffer_size",
                            "target_updates",
                            "explorations",
                            "exploitations",
                            "epsilon",
                            "total_reward",
                            "total_penalties",
                            "waste_penalties",
                            "waste_penalty_count",
                            "last_unused_seats",
                            "feasible_table_count",
                            "last_action",
                            "last_feasible_actions",
                            "last_table_capacity"
                        ):
                            if key in algorithm_stats:
                                statistics[key] = (
                                    algorithm_stats[key]
                                )

                    elif self.algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
                        for key in (
                            "n_step",
                            "tree_backup_return",
                            "last_tree_backup_return",
                            "td_error",
                            "pending_transitions",
                            "explorations",
                            "exploitations",
                            "epsilon",
                            "total_reward",
                            "total_penalties",
                            "waste_penalties",
                            "waste_penalty_count",
                            "last_action",
                            "last_group_size",
                            "last_table_capacity",
                            "last_unused_seats",
                            "last_feasible_actions",
                            "feasible_table_count"
                        ):
                            if key in algorithm_stats:
                                statistics[key] = (
                                    algorithm_stats[key]
                                )

            except Exception as exc:
                print(
                    f"[AGENT] RL statistics warning: {exc}"
                )

        return statistics

    def get_dqn_statistics(self):
        if self.algorithm_name != ALGORITHM_DQN:
            return {}

        if not hasattr(
            self.algorithm,
            "get_statistics"
        ):
            return {}

        try:
            statistics = (
                self.algorithm.get_statistics()
            )
        except Exception:
            return {}

        if not isinstance(
            statistics,
            dict
        ):
            return {}

        keys = (
            "loss",
            "dqn_loss",
            "last_q_value",
            "q_value",
            "target_q",
            "td_error",
            "replay_size",
            "replay_buffer_size",
            "target_updates",
            "explorations",
            "exploitations",
            "epsilon",
            "total_reward",
            "average_reward",
            "total_penalties",
            "penalties",
            "waste_penalties",
            "waste_penalty_count",
            "allocation_accuracy",
            "last_action",
            "last_group_size",
            "last_table_capacity",
            "last_unused_seats",
            "last_feasible_actions",
            "feasible_table_count"
        )

        return {
            key: statistics[key]
            for key in keys
            if key in statistics
        }

    def get_n_step_tree_backup_statistics(self):
        if self.algorithm_name != ALGORITHM_N_STEP_TREE_BACKUP:
            return {}

        if not hasattr(
            self.algorithm,
            "get_statistics"
        ):
            return {}

        try:
            statistics = (
                self.algorithm.get_statistics()
            )
        except Exception:
            return {}

        if not isinstance(
            statistics,
            dict
        ):
            return {}

        keys = (
            "n_step",
            "tree_backup_return",
            "last_tree_backup_return",
            "td_error",
            "pending_transitions",
            "explorations",
            "exploitations",
            "epsilon",
            "total_reward",
            "average_reward",
            "total_penalties",
            "penalties",
            "waste_penalties",
            "waste_penalty_count",
            "q_updates",
            "allocation_accuracy",
            "last_action",
            "last_group_size",
            "last_table_capacity",
            "last_unused_seats",
            "last_feasible_actions",
            "feasible_table_count"
        )

        return {
            key: statistics[key]
            for key in keys
            if key in statistics
        }

    def get_actor_critic_statistics(self):
        if self.algorithm_name != ALGORITHM_ACTOR_CRITIC:
            return {}

        if not hasattr(
            self.algorithm,
            "get_statistics"
        ):
            return {}

        try:
            statistics = (
                self.algorithm.get_statistics()
            )
        except Exception:
            return {}

        if not isinstance(
            statistics,
            dict
        ):
            return {}

        keys = (
            "actor_updates",
            "critic_updates",
            "actor_loss",
            "critic_loss",
            "advantage",
            "last_advantage",
            "entropy",
            "value_estimate",
            "value",
            "total_reward",
            "average_reward",
            "total_learning_reward",
            "total_penalties",
            "penalties",
            "waste_penalties",
            "waste_penalty_count",
            "q_updates",
            "allocation_accuracy",
            "last_action",
            "last_group_size",
            "last_table_capacity",
            "last_unused_seats",
            "last_feasible_actions",
            "feasible_table_count"
        )

        return {
            key: statistics[key]
            for key in keys
            if key in statistics
        }

    def get_statistics(self):
        statistics = {
            "algorithm": self.algorithm_name,
            "total_decisions": self.total_decisions,
            "successful_allocations": (
                self.successful_allocations
            ),
            "customers_served": (
                self.total_customers_served
            ),
            "average_wait_time": (
                self.get_average_wait_time()
            ),
            "waiting_time_seconds": (
                self.get_waiting_time_seconds()
            ),
            "waiting_queue_active": (
                self.waiting_queue_active
            ),
            "satisfaction": self.get_satisfaction(),
            "failed_allocations": (
                self.failed_allocations
            ),
            "current_reward": self.current_reward,
            "best_reward": self.best_reward,
            "q_updates": self.q_updates
        }

        if hasattr(
            self.algorithm,
            "get_statistics"
        ):
            try:
                algorithm_stats = (
                    self.algorithm.get_statistics()
                )

                protected_keys = {
                    "algorithm",
                    "total_decisions",
                    "successful_allocations",
                    "customers_served",
                    "average_wait_time",
                    "waiting_time_seconds",
                    "waiting_queue_active",
                    "satisfaction",
                    "failed_allocations",
                    "current_reward",
                    "best_reward"
                }

                if isinstance(
                    algorithm_stats,
                    dict
                ):
                    for key, value in algorithm_stats.items():
                        if key not in protected_keys:
                            statistics[key] = value

                    if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
                        statistics["q_updates"] = (
                            algorithm_stats.get(
                                "q_updates",
                                self.q_updates
                            )
                        )

            except Exception:
                pass

        return statistics

    def get_waiting_time_seconds(self):
        return float(
            self.waiting_time_seconds
        )

    def get_average_wait_time(self):
        if not self.completed_wait_times:
            return 0.0

        return (
            sum(self.completed_wait_times)
            / len(self.completed_wait_times)
            / 60.0
        )

    def get_satisfaction(self):
        if self.total_decisions <= 0:
            return 5.0

        if self.successful_allocations <= 0:
            return 1.0

        accuracy = (
            self.successful_allocations
            / self.total_decisions
        )

        return max(
            1.0,
            min(
                5.0,
                1.0 + accuracy * 4.0
            )
        )

    def get_table_counts(self):
        occupied = 0
        ready = 0
        cleaning = 0

        for index, table in enumerate(
            self.table_manager.tables
        ):
            if _is_table_occupied(table):
                occupied += 1
            elif index in self.free_timers:
                cleaning += 1
            else:
                ready += 1

        return {
            "occupied": occupied,
            "ready": ready,
            "cleaning": cleaning,
            "total": len(
                self.table_manager.tables
            )
        }

    def get_table_wait_time(
        self,
        table_index
    ):
        try:
            table_index = int(table_index)
        except (
            TypeError,
            ValueError
        ):
            return 0.0

        if table_index not in self.free_timers:
            return 0.0

        elapsed = self.free_timers[
            table_index
        ]

        remaining = (
            FREE_TABLE_DELAY - elapsed
        )

        return max(
            0.0,
            remaining
        )

    def print_statistics(self):
        statistics = self.get_statistics()

        print()
        print("========================================")
        print("AGENT STATISTICS")
        print("========================================")

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

        if self.algorithm_name == ALGORITHM_ACTOR_CRITIC:
            if "total_reward" in statistics:
                print(
                    f"Actor-Critic total reward: "
                    f"{statistics['total_reward']:.2f}"
                )

            if "actor_updates" in statistics:
                print(
                    f"Actor updates: "
                    f"{statistics['actor_updates']}"
                )

            if "critic_updates" in statistics:
                print(
                    f"Critic updates: "
                    f"{statistics['critic_updates']}"
                )

            if "actor_loss" in statistics:
                print(
                    f"Actor loss: "
                    f"{statistics['actor_loss']:+.4f}"
                )

            if "critic_loss" in statistics:
                print(
                    f"Critic loss: "
                    f"{statistics['critic_loss']:+.4f}"
                )

            if "advantage" in statistics:
                print(
                    f"Advantage: "
                    f"{statistics['advantage']:+.4f}"
                )

            if "value_estimate" in statistics:
                print(
                    f"Value estimate: "
                    f"{statistics['value_estimate']:+.4f}"
                )

            if "entropy" in statistics:
                print(
                    f"Entropy: "
                    f"{statistics['entropy']:.4f}"
                )

            if "penalties" in statistics:
                print(
                    f"Penalties: "
                    f"{statistics['penalties']}"
                )

            if "waste_penalties" in statistics:
                print(
                    f"Waste penalties: "
                    f"{statistics['waste_penalties']}"
                )

        if self.algorithm_name == ALGORITHM_DQN:
            if "total_reward" in statistics:
                print(
                    f"DQN total reward: "
                    f"{statistics['total_reward']:.2f}"
                )

            if "loss" in statistics:
                print(
                    f"DQN loss: "
                    f"{statistics['loss']:.4f}"
                )

            elif "dqn_loss" in statistics:
                print(
                    f"DQN loss: "
                    f"{statistics['dqn_loss']:.4f}"
                )

            if "replay_size" in statistics:
                print(
                    f"DQN replay size: "
                    f"{statistics['replay_size']}"
                )

            elif "replay_buffer_size" in statistics:
                print(
                    f"DQN replay size: "
                    f"{statistics['replay_buffer_size']}"
                )

            if "epsilon" in statistics:
                print(
                    f"DQN epsilon: "
                    f"{statistics['epsilon']:.4f}"
                )

            if "target_updates" in statistics:
                print(
                    f"DQN target updates: "
                    f"{statistics['target_updates']}"
                )

        if self.algorithm_name == ALGORITHM_N_STEP_TREE_BACKUP:
            if "total_reward" in statistics:
                print(
                    f"N-step Tree Backup total reward: "
                    f"{statistics['total_reward']:.2f}"
                )

            if "n_step" in statistics:
                print(
                    f"N-step horizon: "
                    f"{statistics['n_step']}"
                )

            if "tree_backup_return" in statistics:
                print(
                    f"Tree Backup return: "
                    f"{statistics['tree_backup_return']:.4f}"
                )

            elif "last_tree_backup_return" in statistics:
                print(
                    f"Tree Backup return: "
                    f"{statistics['last_tree_backup_return']:.4f}"
                )

            if "td_error" in statistics:
                print(
                    f"TD error: "
                    f"{statistics['td_error']:.4f}"
                )

            if "pending_transitions" in statistics:
                print(
                    f"Pending transitions: "
                    f"{statistics['pending_transitions']}"
                )

            if "epsilon" in statistics:
                print(
                    f"Epsilon: "
                    f"{statistics['epsilon']:.4f}"
                )

            if "explorations" in statistics:
                print(
                    f"Explorations: "
                    f"{statistics['explorations']}"
                )

            if "exploitations" in statistics:
                print(
                    f"Exploitations: "
                    f"{statistics['exploitations']}"
                )

        if self.algorithm_name == ALGORITHM_EXPECTED_SARSA:
            if "total_reward" in statistics:
                print(
                    f"Expected SARSA total reward: "
                    f"{statistics['total_reward']:.2f}"
                )

            if "total_penalties" in statistics:
                print(
                    f"Total penalties: "
                    f"{statistics['total_penalties']}"
                )

            if "waste_penalties" in statistics:
                print(
                    f"Waste penalties: "
                    f"{statistics['waste_penalties']}"
                )

            if "epsilon" in statistics:
                print(
                    f"Epsilon: "
                    f"{statistics['epsilon']:.4f}"
                )

        print("========================================")
        print()