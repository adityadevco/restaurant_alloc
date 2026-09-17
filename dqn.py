"""
METRIUS EATS - DEEP Q-NETWORK

Live Deep Q-Network used by the restaurant table-allocation
simulation.

State:
    8 table-status values
    8 normalized table-capacity values
    1 normalized waiting-group size

Action:
    0..7 -> T1..T8

The action mask prevents DQN from selecting:
    - occupied tables
    - tables currently being cleaned
    - tables too small for the group

Learning:
    - epsilon-greedy action selection
    - replay buffer
    - online Q-network
    - target Q-network
    - masked Bellman target
    - Huber loss
"""

from collections import deque
import random
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except Exception:
    torch = None
    nn = None
    optim = None
    TORCH_AVAILABLE = False


ACTION_SIZE = 8
MAX_GROUP_SIZE = 6
MAX_TABLE_CAPACITY = 6
STATE_SIZE = ACTION_SIZE + ACTION_SIZE + 1

LEARNING_RATE = 0.001
DISCOUNT_FACTOR = 0.95

EPSILON_START = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995

BATCH_SIZE = 32
REPLAY_BUFFER_SIZE = 10000

TARGET_UPDATE_FREQUENCY = 100

HIDDEN_SIZE = 128
GRADIENT_CLIP = 5.0

EXACT_FIT_REWARD = 15.0
ONE_UNUSED_SEAT_REWARD = 10.0
TWO_UNUSED_SEATS_REWARD = 5.0
LARGE_WASTE_REWARD = -5.0

INVALID_ACTION_REWARD = -100.0
WAIT_REWARD = -1.0


if TORCH_AVAILABLE:
    DEVICE = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    if DEVICE.type == "cpu":
        try:
            torch.set_num_threads(1)
        except Exception:
            pass
else:
    DEVICE = "numpy"


def _get_tables(table_manager):
    if table_manager is None:
        return []

    return list(
        getattr(
            table_manager,
            "tables",
            []
        )
    )


def _capacity(table):
    try:
        value = getattr(
            table,
            "capacity",
            None
        )

        if value is None:
            value = getattr(
                table,
                "max_capacity",
                0
            )

        return int(value)

    except (TypeError, ValueError):
        return 0


def _occupied(table):
    return bool(
        getattr(
            table,
            "occupied",
            False
        )
    )


def _ready(
    index,
    table,
    ready_checker
):
    if _occupied(table):
        return False

    if ready_checker is None:
        return True

    try:
        return bool(
            ready_checker(index)
        )
    except Exception:
        return False


def encode_state(
    group_size,
    tables,
    ready_checker=None
):
    tables = list(tables)

    status = []
    capacities = []

    for index in range(ACTION_SIZE):

        if index >= len(tables):
            status.append(1.0)
            capacities.append(0.0)
            continue

        table = tables[index]

        if _occupied(table):
            status.append(1.0)

        elif ready_checker is not None:
            try:
                is_ready = bool(
                    ready_checker(index)
                )
            except Exception:
                is_ready = False

            status.append(
                0.0 if is_ready else 0.5
            )

        else:
            status.append(0.0)

        capacities.append(
            min(
                1.0,
                max(
                    0.0,
                    _capacity(table)
                    /
                    float(MAX_TABLE_CAPACITY)
                )
            )
        )

    try:
        group_size = int(group_size)
    except (TypeError, ValueError):
        group_size = 0

    group_size = max(
        0,
        min(
            MAX_GROUP_SIZE,
            group_size
        )
    )

    normalized_group = (
        group_size
        /
        float(MAX_GROUP_SIZE)
    )

    return np.asarray(
        status
        +
        capacities
        +
        [normalized_group],
        dtype=np.float32
    )


if TORCH_AVAILABLE:

    class QNetwork(nn.Module):

        def __init__(
            self,
            input_size=STATE_SIZE,
            output_size=ACTION_SIZE,
            hidden_size=HIDDEN_SIZE
        ):
            super().__init__()

            self.net = nn.Sequential(
                nn.Linear(
                    input_size,
                    hidden_size
                ),
                nn.ReLU(),
                nn.Linear(
                    hidden_size,
                    hidden_size
                ),
                nn.ReLU(),
                nn.Linear(
                    hidden_size,
                    output_size
                )
            )

        def forward(
            self,
            state
        ):
            return self.net(state)

else:

    class QNetwork:

        def __init__(
            self,
            input_size=STATE_SIZE,
            output_size=ACTION_SIZE,
            hidden_size=HIDDEN_SIZE
        ):
            self.input_size = input_size
            self.output_size = output_size
            self.hidden_size = hidden_size

            rng = np.random.default_rng()

            self.w1 = (
                rng.normal(
                    0.0,
                    np.sqrt(
                        2.0 / input_size
                    ),
                    (
                        input_size,
                        hidden_size
                    )
                )
                .astype(np.float32)
            )

            self.b1 = np.zeros(
                hidden_size,
                dtype=np.float32
            )

            self.w2 = (
                rng.normal(
                    0.0,
                    np.sqrt(
                        2.0 / hidden_size
                    ),
                    (
                        hidden_size,
                        hidden_size
                    )
                )
                .astype(np.float32)
            )

            self.b2 = np.zeros(
                hidden_size,
                dtype=np.float32
            )

            self.w3 = (
                rng.normal(
                    0.0,
                    np.sqrt(
                        2.0 / hidden_size
                    ),
                    (
                        hidden_size,
                        output_size
                    )
                )
                .astype(np.float32)
            )

            self.b3 = np.zeros(
                output_size,
                dtype=np.float32
            )

        def predict(
            self,
            state
        ):
            x = np.asarray(
                state,
                dtype=np.float32
            )

            single = (
                x.ndim == 1
            )

            if single:
                x = x.reshape(
                    1,
                    -1
                )

            z1 = (
                x @ self.w1
                +
                self.b1
            )

            h1 = np.maximum(
                z1,
                0.0
            )

            z2 = (
                h1 @ self.w2
                +
                self.b2
            )

            h2 = np.maximum(
                z2,
                0.0
            )

            output = (
                h2 @ self.w3
                +
                self.b3
            )

            if single:
                return output[0]

            return output

        def copy_from(
            self,
            other
        ):
            self.w1 = other.w1.copy()
            self.b1 = other.b1.copy()

            self.w2 = other.w2.copy()
            self.b2 = other.b2.copy()

            self.w3 = other.w3.copy()
            self.b3 = other.b3.copy()

        def train_batch(
            self,
            states,
            actions,
            targets,
            learning_rate
        ):
            x = np.asarray(
                states,
                dtype=np.float32
            )

            actions = np.asarray(
                actions,
                dtype=np.int64
            )

            targets = np.asarray(
                targets,
                dtype=np.float32
            )

            batch_size = max(
                1,
                len(x)
            )

            z1 = (
                x @ self.w1
                +
                self.b1
            )

            h1 = np.maximum(
                z1,
                0.0
            )

            z2 = (
                h1 @ self.w2
                +
                self.b2
            )

            h2 = np.maximum(
                z2,
                0.0
            )

            q_values = (
                h2 @ self.w3
                +
                self.b3
            )

            selected_q = (
                q_values[
                    np.arange(
                        batch_size
                    ),
                    actions
                ]
            )

            errors = (
                selected_q
                -
                targets
            )

            abs_errors = np.abs(
                errors
            )

            delta = 1.0

            quadratic = (
                abs_errors
                <=
                delta
            )

            losses = np.where(
                quadratic,
                0.5 * errors * errors,
                delta * (
                    abs_errors
                    -
                    0.5 * delta
                )
            )

            loss = float(
                np.mean(
                    losses
                )
            )

            grad_selected = np.where(
                quadratic,
                errors,
                delta * np.sign(errors)
            )

            grad_selected /= float(
                batch_size
            )

            grad_output = np.zeros_like(
                q_values
            )

            grad_output[
                np.arange(
                    batch_size
                ),
                actions
            ] = grad_selected

            grad_w3 = (
                h2.T
                @
                grad_output
            )

            grad_b3 = (
                np.sum(
                    grad_output,
                    axis=0
                )
            )

            grad_h2 = (
                grad_output
                @
                self.w3.T
            )

            grad_z2 = (
                grad_h2
                *
                (z2 > 0)
            )

            grad_w2 = (
                h1.T
                @
                grad_z2
            )

            grad_b2 = (
                np.sum(
                    grad_z2,
                    axis=0
                )
            )

            grad_h1 = (
                grad_z2
                @
                self.w2.T
            )

            grad_z1 = (
                grad_h1
                *
                (z1 > 0)
            )

            grad_w1 = (
                x.T
                @
                grad_z1
            )

            grad_b1 = (
                np.sum(
                    grad_z1,
                    axis=0
                )
            )

            gradients = [
                grad_w1,
                grad_b1,
                grad_w2,
                grad_b2,
                grad_w3,
                grad_b3
            ]

            for gradient in gradients:
                np.clip(
                    gradient,
                    -GRADIENT_CLIP,
                    GRADIENT_CLIP,
                    out=gradient
                )

            self.w1 -= (
                learning_rate
                *
                grad_w1
            )

            self.b1 -= (
                learning_rate
                *
                grad_b1
            )

            self.w2 -= (
                learning_rate
                *
                grad_w2
            )

            self.b2 -= (
                learning_rate
                *
                grad_b2
            )

            self.w3 -= (
                learning_rate
                *
                grad_w3
            )

            self.b3 -= (
                learning_rate
                *
                grad_b3
            )

            return loss


class DQNAlgorithm:

    def __init__(
        self,
        table_manager,
        learning_rate=LEARNING_RATE,
        discount_factor=DISCOUNT_FACTOR,
        epsilon=EPSILON_START,
        epsilon_min=EPSILON_MIN,
        epsilon_decay=EPSILON_DECAY,
        batch_size=BATCH_SIZE,
        replay_buffer_size=REPLAY_BUFFER_SIZE,
        target_update_frequency=TARGET_UPDATE_FREQUENCY,
        console_logging=True
    ):

        self.table_manager = (
            table_manager
        )

        self.learning_rate = float(
            learning_rate
        )

        self.discount_factor = float(
            discount_factor
        )

        self.epsilon = float(
            epsilon
        )

        self.epsilon_min = float(
            epsilon_min
        )

        self.epsilon_decay = float(
            epsilon_decay
        )

        self.batch_size = max(
            1,
            int(batch_size)
        )

        self.replay_buffer = deque(
            maxlen=max(
                1,
                int(replay_buffer_size)
            )
        )

        self.target_update_frequency = max(
            1,
            int(
                target_update_frequency
            )
        )

        self.console_logging = bool(
            console_logging
        )

        self.device = DEVICE

        self.online_network = (
            QNetwork()
        )

        self.target_network = (
            QNetwork()
        )

        if TORCH_AVAILABLE:

            self.online_network = (
                self.online_network.to(
                    self.device
                )
            )

            self.target_network = (
                self.target_network.to(
                    self.device
                )
            )

            self.target_network.load_state_dict(
                self.online_network.state_dict()
            )

            self.target_network.eval()

            self.optimizer = optim.Adam(
                self.online_network.parameters(),
                lr=self.learning_rate
            )

        else:

            self.target_network.copy_from(
                self.online_network
            )

            self.optimizer = None

        self.network = (
            self.online_network
        )

        self.total_updates = 0
        self.target_updates = 0

        self.total_decisions = 0

        self.total_explorations = 0
        self.total_exploitations = 0

        self.total_reward = 0.0
        self.total_positive_rewards = 0.0
        self.total_penalties = 0.0

        self.successful_allocations = 0

        self.exact_fit_count = 0
        self.inefficient_allocation_count = 0
        self.waste_penalty_count = 0
        self.invalid_action_count = 0
        self.wait_count = 0

        self.last_state = None
        self.last_next_state = None
        self.last_action = None
        self.last_reward = 0.0

        self.last_group_size = None
        self.last_table_capacity = None
        self.last_unused_seats = None

        self.last_feasible_actions = []
        self.feasible_table_count = 0

        self.last_loss = 0.0
        self.last_q_value = 0.0
        self.last_target_q = 0.0
        self.last_td_error = 0.0

        self.best_reward = 0.0

        self.ready_checker = None

        self.last_action_was_exploration = False

        self._log(
            "[DQN] Initialized | "
            f"device={self.device} | "
            f"PyTorch={TORCH_AVAILABLE} | "
            f"lr={self.learning_rate:.4f} | "
            f"gamma={self.discount_factor:.2f} | "
            f"epsilon={self.epsilon:.3f}"
        )

        if not TORCH_AVAILABLE:

            self._log(
                "[DQN] PyTorch not available. "
                "Using NumPy neural-network fallback."
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
        self.table_manager = (
            table_manager
        )

    def set_ready_checker(
        self,
        ready_checker
    ):
        self.ready_checker = (
            ready_checker
        )

    def get_state(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        if tables is None:
            tables = _get_tables(
                self.table_manager
            )

        checker = (
            ready_checker
            if ready_checker is not None
            else self.ready_checker
        )

        return encode_state(
            group_size,
            tables,
            checker
        )

    def get_valid_actions(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        if tables is None:
            tables = _get_tables(
                self.table_manager
            )

        checker = (
            ready_checker
            if ready_checker is not None
            else self.ready_checker
        )

        try:
            group_size = int(
                group_size
            )
        except (
            TypeError,
            ValueError
        ):
            return []

        if group_size <= 0:
            return []

        valid = []

        for index, table in enumerate(
            tables[:ACTION_SIZE]
        ):

            if _occupied(table):
                continue

            if not _ready(
                index,
                table,
                checker
            ):
                continue

            if _capacity(table) < group_size:
                continue

            valid.append(
                index
            )

        self.last_feasible_actions = (
            list(valid)
        )

        self.feasible_table_count = (
            len(valid)
        )

        return valid

    def _state_tensor(
        self,
        state
    ):
        return torch.as_tensor(
            state,
            dtype=torch.float32,
            device=self.device
        ).unsqueeze(0)

    def get_q_values(
        self,
        state
    ):
        if TORCH_AVAILABLE:

            with torch.no_grad():

                return (
                    self.online_network(
                        self._state_tensor(
                            state
                        )
                    )
                    .squeeze(0)
                )

        return np.asarray(
            self.online_network.predict(
                state
            ),
            dtype=np.float32
        )

    def choose_action(
        self,
        state,
        valid_actions,
        explore=True
    ):
        valid_actions = list(
            valid_actions
        )

        if not valid_actions:
            return None

        self.last_action_was_exploration = False

        if (
            explore
            and
            random.random()
            <
            self.epsilon
        ):

            action = random.choice(
                valid_actions
            )

            self.total_explorations += 1

            self.last_action_was_exploration = (
                True
            )

            self._log(
                "[DQN] EXPLORE -> "
                f"T{action + 1} "
                f"(epsilon={self.epsilon:.3f})"
            )

            return action

        q_values = (
            self.get_q_values(
                state
            )
        )

        q_values = [
            float(
                q_values[index].item()
                if TORCH_AVAILABLE
                else q_values[index]
            )
            for index in valid_actions
        ]

        best_value = max(
            q_values
        )

        best_actions = [
            action
            for action, value in zip(
                valid_actions,
                q_values
            )
            if abs(
                value
                -
                best_value
            ) < 1e-8
        ]

        action = random.choice(
            best_actions
        )

        self.total_exploitations += 1

        self._log(
            "[DQN] EXPLOIT -> "
            f"T{action + 1} "
            f"(Q={best_value:.4f})"
        )

        return action

    def calculate_table_reward(
        self,
        group_size,
        selected_index,
        tables=None,
        valid_actions=None
    ):
        if tables is None:
            tables = _get_tables(
                self.table_manager
            )

        if valid_actions is None:

            valid_actions = (
                self.get_valid_actions(
                    group_size,
                    tables
                )
            )

        try:

            group_size = int(
                group_size
            )

            selected_index = int(
                selected_index
            )

        except (
            TypeError,
            ValueError
        ):

            return INVALID_ACTION_REWARD

        if selected_index not in valid_actions:
            return INVALID_ACTION_REWARD

        if (
            selected_index < 0
            or
            selected_index >= len(
                tables
            )
        ):
            return INVALID_ACTION_REWARD

        capacity = _capacity(
            tables[
                selected_index
            ]
        )

        if capacity < group_size:
            return INVALID_ACTION_REWARD

        unused = (
            capacity
            -
            group_size
        )

        if unused == 0:
            return EXACT_FIT_REWARD

        if unused == 1:
            return ONE_UNUSED_SEAT_REWARD

        if unused == 2:
            return TWO_UNUSED_SEAT_REWARD

        return LARGE_WASTE_REWARD

    def _record_reward(
        self,
        reward
    ):
        reward = float(
            reward
        )

        self.last_reward = reward

        self.total_reward += reward

        if reward > 0:

            self.total_positive_rewards += (
                reward
            )

        elif reward < 0:

            self.total_penalties += abs(
                reward
            )

        if reward == EXACT_FIT_REWARD:

            self.exact_fit_count += 1

        elif reward in (
            ONE_UNUSED_SEAT_REWARD,
            TWO_UNUSED_SEATS_REWARD
        ):

            self.inefficient_allocation_count += 1

        elif reward == LARGE_WASTE_REWARD:

            self.waste_penalty_count += 1

    def get_immediate_reward(
        self,
        group_size,
        selected_index,
        tables=None,
        ready_checker=None,
        success=True,
        valid_actions=None
    ):
        if (
            not success
            or
            selected_index is None
        ):

            reward = (
                INVALID_ACTION_REWARD
            )

            self.invalid_action_count += 1

        else:

            reward = (
                self.calculate_table_reward(
                    group_size,
                    selected_index,
                    tables,
                    valid_actions
                )
            )

            if reward == INVALID_ACTION_REWARD:
                self.invalid_action_count += 1

        self._record_reward(
            reward
        )

        return float(
            reward
        )

    def waiting_reward(
        self
    ):
        self.wait_count += 1

        self._record_reward(
            WAIT_REWARD
        )

        return WAIT_REWARD

    def record_wait(
        self
    ):
        return self.waiting_reward()

    def _build_next_state(
        self,
        group_size,
        selected_index,
        tables,
        ready_checker
    ):
        next_status = []
        capacities = []

        for index in range(
            ACTION_SIZE
        ):

            if index >= len(tables):

                next_status.append(
                    1.0
                )

                capacities.append(
                    0.0
                )

                continue

            table = tables[
                index
            ]

            if index == selected_index:

                next_status.append(
                    1.0
                )

            elif _occupied(table):

                next_status.append(
                    1.0
                )

            elif ready_checker is not None:

                try:

                    ready = bool(
                        ready_checker(
                            index
                        )
                    )

                except Exception:

                    ready = False

                next_status.append(
                    0.0
                    if ready
                    else 0.5
                )

            else:

                next_status.append(
                    0.0
                )

            capacities.append(
                min(
                    1.0,
                    max(
                        0.0,
                        _capacity(table)
                        /
                        float(
                            MAX_TABLE_CAPACITY
                        )
                    )
                )
            )

        try:
            group_size = int(
                group_size
            )
        except (
            TypeError,
            ValueError
        ):
            group_size = 0

        group_size = max(
            0,
            min(
                MAX_GROUP_SIZE,
                group_size
            )
        )

        return np.asarray(
            next_status
            +
            capacities
            +
            [
                group_size
                /
                float(
                    MAX_GROUP_SIZE
                )
            ],
            dtype=np.float32
        )

    def _next_valid_actions(
        self,
        group_size,
        tables,
        selected_index,
        ready_checker
    ):
        valid = []

        for index, table in enumerate(
            tables[:ACTION_SIZE]
        ):

            if index == selected_index:
                continue

            if _occupied(table):
                continue

            if not _ready(
                index,
                table,
                ready_checker
            ):
                continue

            if _capacity(table) >= int(
                group_size
            ):
                valid.append(
                    index
                )

        return valid

    def remember(
        self,
        state,
        action,
        reward,
        next_state,
        done,
        next_valid_actions
    ):
        self.replay_buffer.append(
            (
                np.asarray(
                    state,
                    dtype=np.float32
                ).copy(),

                int(action),

                float(reward),

                np.asarray(
                    next_state,
                    dtype=np.float32
                ).copy(),

                bool(done),

                tuple(
                    int(index)
                    for index
                    in next_valid_actions
                )
            )
        )

    def _learn_torch(
        self,
        batch
    ):
        (
            states,
            actions,
            rewards,
            next_states,
            dones,
            next_valid_actions
        ) = zip(*batch)

        states_tensor = torch.as_tensor(
            np.asarray(
                states
            ),
            dtype=torch.float32,
            device=self.device
        )

        actions_tensor = torch.as_tensor(
            actions,
            dtype=torch.long,
            device=self.device
        )

        rewards_tensor = torch.as_tensor(
            rewards,
            dtype=torch.float32,
            device=self.device
        )

        next_states_tensor = torch.as_tensor(
            np.asarray(
                next_states
            ),
            dtype=torch.float32,
            device=self.device
        )

        dones_tensor = torch.as_tensor(
            dones,
            dtype=torch.float32,
            device=self.device
        )

        current_q = (
            self.online_network(
                states_tensor
            )
            .gather(
                1,
                actions_tensor.unsqueeze(1)
            )
            .squeeze(1)
        )

        with torch.no_grad():

            target_next_q_all = (
                self.target_network(
                    next_states_tensor
                )
            )

            next_q_values = []

            for row_index, valid_actions in enumerate(
                next_valid_actions
            ):

                if (
                    dones[row_index]
                    or
                    not valid_actions
                ):

                    next_q_values.append(
                        0.0
                    )

                    continue

                best_next = max(
                    float(
                        target_next_q_all[
                            row_index,
                            action
                        ].item()
                    )
                    for action
                    in valid_actions
                )

                next_q_values.append(
                    best_next
                )

            next_q_tensor = torch.as_tensor(
                next_q_values,
                dtype=torch.float32,
                device=self.device
            )

            target_q = (
                rewards_tensor
                +
                self.discount_factor
                *
                (
                    1.0
                    -
                    dones_tensor
                )
                *
                next_q_tensor
            )

        loss = (
            nn.functional.smooth_l1_loss(
                current_q,
                target_q
            )
        )

        self.optimizer.zero_grad(
            set_to_none=True
        )

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.online_network.parameters(),
            GRADIENT_CLIP
        )

        self.optimizer.step()

        self.last_q_value = float(
            current_q[0].item()
        )

        self.last_target_q = float(
            target_q[0].item()
        )

        self.last_td_error = (
            self.last_target_q
            -
            self.last_q_value
        )

        return float(
            loss.item()
        )

    def _learn_numpy(
        self,
        batch
    ):
        (
            states,
            actions,
            rewards,
            next_states,
            dones,
            next_valid_actions
        ) = zip(*batch)

        targets = []

        for reward, next_state, done, valid_actions in zip(
            rewards,
            next_states,
            dones,
            next_valid_actions
        ):

            if done or not valid_actions:

                target = float(
                    reward
                )

            else:

                next_q = (
                    self.target_network.predict(
                        next_state
                    )
                )

                best_next = max(
                    float(
                        next_q[action]
                    )
                    for action
                    in valid_actions
                )

                target = (
                    float(reward)
                    +
                    self.discount_factor
                    *
                    best_next
                )

            targets.append(
                target
            )

        loss = (
            self.online_network.train_batch(
                states,
                actions,
                targets,
                self.learning_rate
            )
        )

        last_q = (
            self.online_network.predict(
                states[-1]
            )
        )

        self.last_q_value = float(
            last_q[
                int(actions[-1])
            ]
        )

        self.last_target_q = float(
            targets[-1]
        )

        self.last_td_error = (
            self.last_target_q
            -
            self.last_q_value
        )

        return float(
            loss
        )

    def learn(
        self
    ):
        if len(
            self.replay_buffer
        ) < self.batch_size:

            return None

        batch = random.sample(
            self.replay_buffer,
            self.batch_size
        )

        if TORCH_AVAILABLE:

            loss = self._learn_torch(
                batch
            )

        else:

            loss = self._learn_numpy(
                batch
            )

        self.last_loss = float(
            loss
        )

        self.total_updates += 1

        if (
            self.total_updates
            %
            self.target_update_frequency
            ==
            0
        ):

            if TORCH_AVAILABLE:

                self.target_network.load_state_dict(
                    self.online_network.state_dict()
                )

            else:

                self.target_network.copy_from(
                    self.online_network
                )

            self.target_updates += 1

            self._log(
                "[DQN] Target network synchronized | "
                f"updates={self.total_updates}"
            )

        return self.last_loss

    def update_q_value(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions=None,
        terminal=False
    ):
        if (
            state is None
            or
            action is None
            or
            next_state is None
        ):
            return False

        if next_valid_actions is None:
            next_valid_actions = []

        self.remember(
            state,
            action,
            reward,
            next_state,
            terminal,
            next_valid_actions
        )

        self.last_state = (
            np.asarray(
                state,
                dtype=np.float32
            )
        )

        self.last_next_state = (
            np.asarray(
                next_state,
                dtype=np.float32
            )
        )

        self.last_action = int(
            action
        )

        self.last_reward = float(
            reward
        )

        loss = self.learn()

        return (
            True
            if loss is not None
            else False
        )

    def learn_after_allocation(
        self,
        state,
        action,
        reward,
        next_state,
        next_valid_actions=None,
        terminal=False
    ):
        return self.update_q_value(
            state,
            action,
            reward,
            next_state,
            next_valid_actions,
            terminal
        )

    def choose_table(
        self,
        group_size,
        ready_checker=None
    ):
        tables = _get_tables(
            self.table_manager
        )

        checker = (
            ready_checker
            if ready_checker is not None
            else self.ready_checker
        )

        try:
            group_size = int(
                group_size
            )
        except (
            TypeError,
            ValueError
        ):
            return None

        state = self.get_state(
            group_size,
            tables,
            checker
        )

        valid_actions = (
            self.get_valid_actions(
                group_size,
                tables,
                checker
            )
        )

        self.last_group_size = (
            group_size
        )

        self.last_feasible_actions = (
            list(valid_actions)
        )

        self.feasible_table_count = (
            len(valid_actions)
        )

        if not valid_actions:

            self.wait_count += 1

            self._record_reward(
                WAIT_REWARD
            )

            self._log(
                "[DQN] No suitable READY table."
            )

            return None

        action = self.choose_action(
            state,
            valid_actions,
            explore=True
        )

        if action is None:
            return None

        capacity = _capacity(
            tables[action]
        )

        unused = max(
            0,
            capacity
            -
            group_size
        )

        reward = (
            self.calculate_table_reward(
                group_size,
                action,
                tables,
                valid_actions
            )
        )

        next_state = (
            self._build_next_state(
                group_size,
                action,
                tables,
                checker
            )
        )

        next_valid_actions = (
            self._next_valid_actions(
                group_size,
                tables,
                action,
                checker
            )
        )

        self.remember(
            state,
            action,
            reward,
            next_state,
            False,
            next_valid_actions
        )

        loss = self.learn()

        self.total_decisions += 1

        self.successful_allocations += 1

        self._record_reward(
            reward
        )

        self.last_state = (
            state
        )

        self.last_next_state = (
            next_state
        )

        self.last_action = (
            action
        )

        self.last_table_capacity = (
            capacity
        )

        self.last_unused_seats = (
            unused
        )

        self.best_reward = max(
            self.best_reward,
            reward
        )

        q_values = (
            self.get_q_values(
                state
            )
        )

        if TORCH_AVAILABLE:

            self.last_q_value = float(
                q_values[
                    action
                ].item()
            )

        else:

            self.last_q_value = float(
                q_values[
                    action
                ]
            )

        self._log(
            "=================================================="
        )

        self._log(
            "[DQN] NEW DECISION"
        )

        self._log(
            f"Group size  : {group_size}"
        )

        self._log(
            f"State       : "
            f"{tuple(np.round(state, 3))}"
        )

        self._log(
            "Valid tables: "
            +
            ", ".join(
                f"T{index + 1}"
                for index
                in valid_actions
            )
        )

        mode = (
            "EXPLORE"
            if self.last_action_was_exploration
            else "EXPLOIT"
        )

        self._log(
            f"[DQN] {mode} -> "
            f"T{action + 1} "
            f"(Q={self.last_q_value:.4f})"
        )

        self._log(
            f"[DQN] Selected T{action + 1} | "
            f"capacity={capacity} | "
            f"unused={unused} | "
            f"immediate reward={reward:+.2f}"
        )

        if loss is not None:

            self._log(
                f"[DQN] Learning | "
                f"loss={self.last_loss:.6f} | "
                f"target={self.last_target_q:.4f} | "
                f"TD={self.last_td_error:+.4f}"
            )

        self._log(
            "=================================================="
        )

        self.decay_epsilon()

        return int(
            action
        )

    def update_after_decision(
        self,
        state=None,
        action=None,
        reward=None,
        next_state=None,
        done=False,
        next_valid_actions=None
    ):
        if (
            state is not None
            and
            action is not None
            and
            reward is not None
            and
            next_state is not None
        ):
            return self.update_q_value(
                state,
                action,
                reward,
                next_state,
                next_valid_actions,
                done
            )

        return self.last_loss

    def greedy_action(
        self,
        group_size,
        ready_checker=None
    ):
        tables = _get_tables(
            self.table_manager
        )

        valid = (
            self.get_valid_actions(
                group_size,
                tables,
                ready_checker
            )
        )

        if not valid:
            return None

        state = self.get_state(
            group_size,
            tables,
            ready_checker
        )

        return self.choose_action(
            state,
            valid,
            explore=False
        )

    def get_table_q_values(
        self,
        group_size,
        ready_checker=None
    ):
        tables = _get_tables(
            self.table_manager
        )

        state = self.get_state(
            group_size,
            tables,
            ready_checker
        )

        q_values = (
            self.get_q_values(
                state
            )
        )

        result = {}

        for index in range(
            min(
                ACTION_SIZE,
                len(tables)
            )
        ):

            if TORCH_AVAILABLE:

                value = float(
                    q_values[
                        index
                    ].item()
                )

            else:

                value = float(
                    q_values[
                        index
                    ]
                )

            result[index] = value

        return result

    def decay_epsilon(
        self
    ):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon
            *
            self.epsilon_decay
        )

    def set_epsilon(
        self,
        epsilon
    ):
        self.epsilon = max(
            self.epsilon_min,
            min(
                1.0,
                float(epsilon)
            )
        )

    def reset_learning(
        self
    ):
        self.online_network = (
            QNetwork()
        )

        self.target_network = (
            QNetwork()
        )

        if TORCH_AVAILABLE:

            self.online_network = (
                self.online_network.to(
                    self.device
                )
            )

            self.target_network = (
                self.target_network.to(
                    self.device
                )
            )

            self.target_network.load_state_dict(
                self.online_network.state_dict()
            )

            self.target_network.eval()

            self.optimizer = optim.Adam(
                self.online_network.parameters(),
                lr=self.learning_rate
            )

        else:

            self.target_network.copy_from(
                self.online_network
            )

            self.optimizer = None

        self.network = (
            self.online_network
        )

        self.replay_buffer.clear()

        self.epsilon = (
            EPSILON_START
        )

        self.total_updates = 0
        self.target_updates = 0

        self.last_loss = 0.0
        self.last_q_value = 0.0
        self.last_target_q = 0.0
        self.last_td_error = 0.0

    def reset_statistics(
        self
    ):
        self.total_updates = 0
        self.target_updates = 0

        self.total_decisions = 0

        self.total_explorations = 0
        self.total_exploitations = 0

        self.total_reward = 0.0
        self.total_positive_rewards = 0.0
        self.total_penalties = 0.0

        self.successful_allocations = 0

        self.exact_fit_count = 0
        self.inefficient_allocation_count = 0
        self.waste_penalty_count = 0
        self.invalid_action_count = 0
        self.wait_count = 0

        self.last_reward = 0.0
        self.best_reward = 0.0

        self.last_loss = 0.0
        self.last_q_value = 0.0
        self.last_target_q = 0.0
        self.last_td_error = 0.0

    def get_statistics(
        self
    ):
        allocation_accuracy = 0.0

        if self.total_decisions > 0:

            allocation_accuracy = (
                self.successful_allocations
                /
                self.total_decisions
                *
                100.0
            )

        return {
            "algorithm":
                "DQN",

            "episode":
                self.total_decisions,

            "q_updates":
                self.total_updates,

            "updates":
                self.total_updates,

            "total_decisions":
                self.total_decisions,

            "allocations":
                self.total_decisions,

            "successful_allocations":
                self.successful_allocations,

            "successes":
                self.successful_allocations,

            "allocation_accuracy":
                allocation_accuracy,

            "explorations":
                self.total_explorations,

            "exploitations":
                self.total_exploitations,

            "epsilon":
                self.epsilon,

            "epsilon_min":
                self.epsilon_min,

            "current_reward":
                self.last_reward,

            "best_reward":
                self.best_reward,

            "total_reward":
                self.total_reward,

            "average_reward":
                (
                    self.total_reward
                    /
                    self.total_decisions
                    if self.total_decisions
                    else 0.0
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

            "loss":
                self.last_loss,

            "dqn_loss":
                self.last_loss,

            "last_q_value":
                self.last_q_value,

            "q_value":
                self.last_q_value,

            "target_q":
                self.last_target_q,

            "last_target_q":
                self.last_target_q,

            "td_error":
                self.last_td_error,

            "last_td_error":
                self.last_td_error,

            "replay_size":
                len(
                    self.replay_buffer
                ),

            "replay_buffer_size":
                len(
                    self.replay_buffer
                ),

            "batch_size":
                self.batch_size,

            "learning_rate":
                self.learning_rate,

            "discount_factor":
                self.discount_factor,

            "target_updates":
                self.target_updates,

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
                self.feasible_table_count,

            "device":
                str(
                    self.device
                ),

            "pytorch_available":
                TORCH_AVAILABLE
        }

    def get_rl_statistics(
        self
    ):
        return self.get_statistics()

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
            "                     DQN RESULTS"
        )

        self._log(
            "============================================================"
        )

        self._log(
            f"Decisions           : "
            f"{stats['total_decisions']}"
        )

        self._log(
            f"Successful          : "
            f"{stats['successful_allocations']}"
        )

        self._log(
            f"Total reward        : "
            f"{stats['total_reward']:+.2f}"
        )

        self._log(
            f"Q updates           : "
            f"{stats['q_updates']}"
        )

        self._log(
            f"Target updates      : "
            f"{stats['target_updates']}"
        )

        self._log(
            f"Replay size         : "
            f"{stats['replay_size']}"
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
            f"Epsilon             : "
            f"{stats['epsilon']:.4f}"
        )

        self._log(
            f"Loss                : "
            f"{stats['loss']:.6f}"
        )

        self._log(
            f"Q                   : "
            f"{stats['last_q_value']:.4f}"
        )

        self._log(
            f"Target Q            : "
            f"{stats['target_q']:.4f}"
        )

        self._log(
            f"TD error            : "
            f"{stats['td_error']:+.4f}"
        )

        self._log(
            f"Backend             : "
            f"{'PyTorch' if TORCH_AVAILABLE else 'NumPy fallback'}"
        )

        self._log(
            "============================================================"
        )


DQN = DQNAlgorithm
DQNAgent = DQNAlgorithm
DeepQNetworkAlgorithm = DQNAlgorithm
DeepQNAlgorithm = DQNAlgorithm