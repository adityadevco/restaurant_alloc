import random

try:
    import numpy as np
except ImportError as exc:
    raise ImportError(
        "Actor-Critic requires NumPy, but NumPy is not installed in the Python "
        "environment running this project. Run: python -m pip install numpy"
    ) from exc

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.distributions import Categorical
except ImportError as exc:
    raise ImportError(
        "Actor-Critic requires PyTorch, but PyTorch is not installed in the "
        "Python environment running this project. Run: python -m pip install torch"
    ) from exc

SEED = 42
ACTION_SIZE = 8
MAX_GROUP_SIZE = 6
MAX_TABLE_CAPACITY = 6
STATE_SIZE = 17

ACTOR_LR = 0.001
CRITIC_LR = 0.001
GAMMA = 0.95
ENTROPY_COEFFICIENT = 0.01
GRADIENT_CLIP = 5.0
REWARD_SCALE = 20.0

EXACT_FIT_REWARD = 15.0
ONE_UNUSED_REWARD = 10.0
TWO_UNUSED_REWARD = 5.0
LARGE_WASTE_REWARD = -5.0
INVALID_ACTION_PENALTY = -100.0
WAIT_REWARD = -1.0

SUCCESS_REWARD = EXACT_FIT_REWARD
INVALID_ACTION_REWARD = INVALID_ACTION_PENALTY
LARGE_WASTE_PENALTY = LARGE_WASTE_REWARD

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

try:
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass


def _get_table_list(table_manager):
    if table_manager is None:
        return []

    tables = getattr(table_manager, "tables", None)

    if tables is not None:
        try:
            return list(tables)
        except TypeError:
            pass

    getter = getattr(table_manager, "get_tables", None)

    if callable(getter):
        try:
            return list(getter())
        except Exception:
            pass

    return []


def _get_table_capacity(table):
    if table is None:
        return 0

    if isinstance(table, dict):
        for key in ("capacity", "seats", "max_people", "max_capacity"):
            if key in table:
                try:
                    return int(table[key])
                except (TypeError, ValueError):
                    pass
        return 0

    for key in ("capacity", "seats", "max_people", "max_capacity"):
        value = getattr(table, key, None)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass

    return 0


def _is_table_occupied(table):
    if table is None:
        return True

    if isinstance(table, dict):
        if "occupied" in table:
            return bool(table["occupied"])

        status = str(table.get("status", "")).upper()

        if status in ("OCCUPIED", "CLEANING"):
            return True

        if table.get("group") is not None or table.get("customer") is not None:
            return True

        return False

    occupied = getattr(table, "occupied", None)

    if occupied is not None:
        return bool(occupied)

    status = str(getattr(table, "status", "")).upper()

    if status in ("OCCUPIED", "CLEANING"):
        return True

    if (
        getattr(table, "group", None) is not None
        or getattr(table, "customer", None) is not None
    ):
        return True

    return False


def encode_state(table_manager, group_size, ready_checker=None):
    tables = _get_table_list(table_manager)

    statuses = []
    capacities = []

    try:
        group_size = int(group_size)
    except (TypeError, ValueError):
        group_size = 0

    for index in range(ACTION_SIZE):
        if index >= len(tables):
            statuses.append(1.0)
            capacities.append(0.0)
            continue

        table = tables[index]
        capacity = _get_table_capacity(table)

        capacities.append(
            max(
                0.0,
                min(
                    1.0,
                    capacity / float(MAX_TABLE_CAPACITY)
                )
            )
        )

        if _is_table_occupied(table):
            statuses.append(1.0)
            continue

        if ready_checker is not None:
            try:
                if not ready_checker(index):
                    statuses.append(0.5)
                    continue
            except Exception:
                pass

        statuses.append(0.0)

    normalized_group_size = (
        max(
            0,
            min(MAX_GROUP_SIZE, group_size)
        )
        / float(MAX_GROUP_SIZE)
    )

    return np.asarray(
        statuses + capacities + [normalized_group_size],
        dtype=np.float32
    )


class ActorNetwork(nn.Module):
    def __init__(
        self,
        input_size=STATE_SIZE,
        action_size=ACTION_SIZE
    ):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_size)
        )

    def forward(self, x):
        return self.net(x)


class CriticNetwork(nn.Module):
    def __init__(self, input_size=STATE_SIZE):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


class ActorCriticAlgorithm:
    algorithm_name = "ACTOR-CRITIC"
    def __init__(
        self,
        table_manager,
        actor_lr=ACTOR_LR,
        critic_lr=CRITIC_LR,
        gamma=GAMMA,
        entropy_coefficient=ENTROPY_COEFFICIENT,
        seed=SEED
    ):
        self.table_manager = table_manager
        self.ready_checker = None

        self.actor_lr = float(actor_lr)
        self.critic_lr = float(critic_lr)
        self.gamma = float(gamma)
        self.entropy_coefficient = float(entropy_coefficient)
        self.seed = int(seed)

        self.rng = random.Random(self.seed)
        self.training = True

        self.actor = ActorNetwork().to(DEVICE)
        self.critic = CriticNetwork().to(DEVICE)

        self.actor_optimizer = optim.Adam(
            self.actor.parameters(),
            lr=self.actor_lr
        )

        self.critic_optimizer = optim.Adam(
            self.critic.parameters(),
            lr=self.critic_lr
        )

        self.reset_statistics()

        print(
            "[ACTOR-CRITIC] Initialized | "
            f"device={DEVICE} | "
            f"state_size={STATE_SIZE} | "
            f"actions={ACTION_SIZE}"
        )

    def set_table_manager(self, table_manager):
        self.table_manager = table_manager

    def set_training(self, enabled):
        self.training = bool(enabled)

    def set_ready_checker(self, checker):
        self.ready_checker = checker

    def get_state(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        if tables is not None:
            temporary_manager = type(
                "_TemporaryTableManager",
                (),
                {
                    "tables": list(tables)
                }
            )()

            checker = (
                ready_checker
                if ready_checker is not None
                else self.ready_checker
            )

            return encode_state(
                temporary_manager,
                group_size,
                checker
            )

        checker = (
            ready_checker
            if ready_checker is not None
            else self.ready_checker
        )

        return encode_state(
            self.table_manager,
            group_size,
            checker
        )

    def get_feasible_actions(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            return []

        if group_size <= 0 or group_size > MAX_GROUP_SIZE:
            return []

        if tables is None:
            tables = _get_table_list(self.table_manager)
        else:
            tables = list(tables)

        checker = (
            ready_checker
            if ready_checker is not None
            else self.ready_checker
        )

        feasible = []

        for index, table in enumerate(tables[:ACTION_SIZE]):
            if _is_table_occupied(table):
                continue

            capacity = _get_table_capacity(table)

            if capacity < group_size:
                continue

            if checker is not None:
                try:
                    if not checker(index):
                        continue
                except Exception:
                    continue

            feasible.append(index)

        return feasible

    def get_valid_actions(
        self,
        group_size,
        tables=None,
        ready_checker=None
    ):
        return self.get_feasible_actions(
            group_size,
            tables=tables,
            ready_checker=ready_checker
        )

    def _masked_distribution(
        self,
        logits,
        feasible_actions
    ):
        if not feasible_actions:
            return None

        valid_actions = []

        for action in feasible_actions:
            try:
                action = int(action)
            except (TypeError, ValueError):
                continue

            if 0 <= action < ACTION_SIZE:
                valid_actions.append(action)

        if not valid_actions:
            return None

        masked_logits = torch.full_like(
            logits,
            -1e9
        )

        indices = torch.as_tensor(
            valid_actions,
            dtype=torch.long,
            device=logits.device
        )

        masked_logits[indices] = logits[indices]

        return Categorical(logits=masked_logits)

    def select_action(
        self,
        state,
        feasible_actions,
        greedy=False,
        return_details=False
    ):
        if not feasible_actions:
            result = {
                "action": None,
                "log_prob": None,
                "value": None,
                "state_tensor": None,
                "distribution": None,
                "entropy": 0.0,
                "probabilities": []
            }

            return result if return_details else None

        state_array = np.asarray(
            state,
            dtype=np.float32
        ).reshape(-1)

        if state_array.size != STATE_SIZE:
            raise ValueError(
                "Actor-Critic expected "
                f"state size {STATE_SIZE}, "
                f"received {state_array.size}"
            )

        state_tensor = torch.as_tensor(
            state_array,
            dtype=torch.float32,
            device=DEVICE
        ).unsqueeze(0)

        logits = self.actor(state_tensor).squeeze(0)

        distribution = self._masked_distribution(
            logits,
            feasible_actions
        )

        if distribution is None:
            return None

        if greedy:
            action_tensor = torch.argmax(
                distribution.probs
            ).long()

            action = int(action_tensor.item())
        else:
            action_tensor = distribution.sample()
            action = int(action_tensor.item())

        log_probability = distribution.log_prob(
            action_tensor
        )

        value = self.critic(
            state_tensor
        ).squeeze(0)

        entropy = distribution.entropy()

        probabilities = (
            distribution.probs
            .detach()
            .cpu()
            .numpy()
            .astype(float)
            .tolist()
        )

        details = {
            "action": action,
            "log_prob": log_probability,
            "value": value,
            "state_tensor": state_tensor,
            "distribution": distribution,
            "entropy": float(
                entropy.detach()
                .cpu()
                .item()
            ),
            "probabilities": probabilities
        }

        return details if return_details else action

    def calculate_table_reward(
        self,
        group_size,
        table_index,
        tables=None,
        valid_actions=None
    ):
        if tables is None:
            tables = _get_table_list(
                self.table_manager
            )
        else:
            tables = list(tables)

        try:
            group_size = int(group_size)
            table_index = int(table_index)
        except (TypeError, ValueError):
            return INVALID_ACTION_PENALTY, 0, False

        if group_size <= 0 or group_size > MAX_GROUP_SIZE:
            return INVALID_ACTION_PENALTY, 0, False

        if table_index < 0 or table_index >= len(tables):
            return INVALID_ACTION_PENALTY, 0, False

        table = tables[table_index]
        capacity = _get_table_capacity(table)

        if capacity <= 0:
            return INVALID_ACTION_PENALTY, 0, False

        if capacity < group_size:
            return (
                INVALID_ACTION_PENALTY,
                max(0, capacity - group_size),
                False
            )

        if _is_table_occupied(table):
            return (
                INVALID_ACTION_PENALTY,
                capacity - group_size,
                False
            )

        checker = self.ready_checker

        if checker is not None:
            try:
                if not checker(table_index):
                    return (
                        INVALID_ACTION_PENALTY,
                        capacity - group_size,
                        False
                    )
            except Exception:
                return (
                    INVALID_ACTION_PENALTY,
                    capacity - group_size,
                    False
                )

        unused = capacity - group_size

        if unused == 0:
            reward = EXACT_FIT_REWARD
        elif unused == 1:
            reward = ONE_UNUSED_REWARD
        elif unused == 2:
            reward = TWO_UNUSED_REWARD
        else:
            reward = LARGE_WASTE_REWARD

        return float(reward), int(unused), True

    def get_immediate_reward(
        self,
        group_size,
        selected_index,
        tables=None,
        ready_checker=None,
        success=True,
        valid_actions=None
    ):
        if not success:
            return INVALID_ACTION_PENALTY

        if selected_index is None:
            return INVALID_ACTION_PENALTY

        old_checker = self.ready_checker

        if ready_checker is not None:
            self.ready_checker = ready_checker

        try:
            reward, _, _ = self.calculate_table_reward(
                group_size,
                selected_index,
                tables=tables,
                valid_actions=valid_actions
            )

            return float(reward)
        finally:
            self.ready_checker = old_checker

    def waiting_reward(self, group_size=None):
        return self.record_wait(group_size)

    def record_wait(self, group_size=None):
        self.wait_count += 1

        self.current_reward = WAIT_REWARD
        self.last_reward = WAIT_REWARD
        self.last_group_size = group_size
        self.total_reward += WAIT_REWARD
        self.total_penalties += abs(WAIT_REWARD)

        return WAIT_REWARD

    def _prepare_transition(
        self,
        state,
        action,
        reward,
        details
    ):
        self.pending_transition = {
            "state": np.asarray(
                state,
                dtype=np.float32
            ).reshape(-1).copy(),
            "action": int(action),
            "reward": float(reward),
            "details": details
        }

    def _update_networks(
        self,
        reward,
        next_state=None,
        done=False,
        details=None
    ):
        if not self.training:
            return False

        if details is None:
            return False

        log_probability = details.get("log_prob")
        value = details.get("value")
        state_tensor = details.get("state_tensor")
        distribution = details.get("distribution")

        if (
            log_probability is None
            or value is None
            or state_tensor is None
        ):
            return False

        scaled_reward = float(reward) / REWARD_SCALE

        reward_tensor = torch.tensor(
            scaled_reward,
            dtype=torch.float32,
            device=DEVICE
        )

        if next_state is not None and not done:
            next_array = np.asarray(
                next_state,
                dtype=np.float32
            ).reshape(-1)

            if next_array.size != STATE_SIZE:
                return False

            next_tensor = torch.as_tensor(
                next_array,
                dtype=torch.float32,
                device=DEVICE
            ).unsqueeze(0)

            with torch.no_grad():
                next_value = self.critic(
                    next_tensor
                ).squeeze(0)

            target = (
                reward_tensor
                + self.gamma * next_value
            )
        else:
            target = reward_tensor

        target_value = float(
            target.detach()
            .cpu()
            .item()
        )

        advantage = target - value
        advantage_for_actor = advantage.detach()

        critic_loss = 0.5 * advantage.pow(2)

        self.critic_optimizer.zero_grad(
            set_to_none=True
        )

        critic_loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.critic.parameters(),
            GRADIENT_CLIP
        )

        self.critic_optimizer.step()

        if distribution is not None:
            entropy = distribution.entropy()
        else:
            entropy = torch.tensor(
                0.0,
                dtype=torch.float32,
                device=DEVICE
            )

        actor_loss = (
            -log_probability * advantage_for_actor
            - self.entropy_coefficient * entropy
        )

        self.actor_optimizer.zero_grad(
            set_to_none=True
        )

        actor_loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.actor.parameters(),
            GRADIENT_CLIP
        )

        self.actor_optimizer.step()

        self.actor_updates += 1
        self.critic_updates += 1
        self.q_updates += 1

        self.total_learning_reward += scaled_reward

        self.last_actor_loss = float(
            actor_loss.detach()
            .cpu()
            .item()
        )

        self.last_critic_loss = float(
            critic_loss.detach()
            .cpu()
            .item()
        )

        self.last_entropy = float(
            entropy.detach()
            .cpu()
            .item()
        )

        self.last_advantage = float(
            advantage.detach()
            .cpu()
            .item()
        )

        self.value_estimate = float(
            value.detach()
            .cpu()
            .item()
        )

        self.last_target = target_value
        self.last_td_error = self.last_advantage

        return True

    def learn_after_allocation(
        self,
        previous_state,
        action,
        reward,
        next_state,
        next_valid_actions=None,
        terminal=False
    ):
        if previous_state is None or action is None:
            return False

        try:
            action = int(action)
        except (TypeError, ValueError):
            return False

        details = None

        if self.pending_transition is not None:
            try:
                if int(
                    self.pending_transition["action"]
                ) == action:
                    details = self.pending_transition["details"]
            except (
                TypeError,
                ValueError,
                KeyError
            ):
                pass

        if details is None:
            state_array = np.asarray(
                previous_state,
                dtype=np.float32
            ).reshape(-1)

            if state_array.size != STATE_SIZE:
                return False

            details = self.select_action(
                state_array,
                [action],
                greedy=True,
                return_details=True
            )

        if details is None:
            return False

        result = self._update_networks(
            reward=float(reward),
            next_state=next_state,
            done=bool(terminal),
            details=details
        )

        self.pending_transition = None

        return bool(result)

    def choose_table(self, group_size):
        try:
            group_size = int(group_size)
        except (TypeError, ValueError):
            self._record_invalid()
            return None

        if group_size <= 0 or group_size > MAX_GROUP_SIZE:
            self._record_invalid()
            self.last_group_size = group_size
            return None

        feasible = self.get_feasible_actions(group_size)

        self.last_feasible_actions = list(feasible)
        self.feasible_table_count = len(feasible)

        if not feasible:
            self.last_action = None
            self.last_group_size = group_size
            self.last_table_capacity = None
            self.last_reward = 0.0
            self.current_reward = 0.0
            self.last_policy_probabilities = []
            return None

        state = self.get_state(group_size)

        details = self.select_action(
            state,
            feasible,
            greedy=not self.training,
            return_details=True
        )

        if details is None or details.get("action") is None:
            self._record_invalid()
            return None

        action = int(details["action"])

        reward, unused, valid = self.calculate_table_reward(
            group_size,
            action
        )

        tables = _get_table_list(
            self.table_manager
        )

        capacity = 0

        if 0 <= action < len(tables):
            capacity = _get_table_capacity(
                tables[action]
            )

        self.total_decisions += 1
        self.last_action = action
        self.last_group_size = group_size
        self.last_table_capacity = capacity
        self.last_unused_seats = unused
        self.last_state = state
        self.last_reward = float(reward)
        self.current_reward = float(reward)

        self.last_log_probability = details["log_prob"]
        self.last_value = details["value"]
        self.last_policy_probabilities = list(
            details["probabilities"]
        )
        self.last_entropy = float(
            details["entropy"]
        )

        self.total_reward += float(reward)

        if reward < 0:
            self.total_penalties += abs(float(reward))

        if valid:
            self.successful_allocations += 1

            if unused == 0:
                self.exact_fit_count += 1
            elif unused == 1:
                self.one_unused_count += 1
            elif unused == 2:
                self.two_unused_count += 1
            else:
                self.large_waste_count += 1
                self.waste_penalty_count += 1
        else:
            self.failed_allocations += 1
            self.invalid_allocations += 1

        self.table_action_counts[action] += 1
        self.table_reward_totals[action] += float(reward)

        if (
            self.table_action_counts[action] == 1
            or reward > self.table_best_rewards[action]
        ):
            self.table_best_rewards[action] = float(reward)

        if (
            self.total_decisions == 1
            or reward > self.best_reward
        ):
            self.best_reward = float(reward)

        self._prepare_transition(
            state,
            action,
            reward,
            details
        )

        return action

    def _record_invalid(self):
        self.total_decisions += 1
        self.failed_allocations += 1
        self.invalid_allocations += 1

        self.last_action = None
        self.last_reward = INVALID_ACTION_PENALTY
        self.current_reward = INVALID_ACTION_PENALTY

        self.total_reward += INVALID_ACTION_PENALTY
        self.total_penalties += abs(
            INVALID_ACTION_PENALTY
        )

    def update_after_decision(
        self,
        reward,
        next_state=None,
        done=True
    ):
        if self.pending_transition is None:
            return False

        return self._finish_pending(
            reward,
            next_state,
            done
        )

    def _finish_pending(
        self,
        reward,
        next_state=None,
        done=False
    ):
        if self.pending_transition is None:
            return False

        transition = self.pending_transition

        result = self._update_networks(
            reward=float(
                transition["reward"]
            ),
            next_state=next_state,
            done=done,
            details=transition["details"]
        )

        self.pending_transition = None

        return bool(result)

    def greedy_action(self, group_size):
        previous_training = self.training

        try:
            self.training = False
            return self.choose_table(group_size)
        finally:
            self.training = previous_training

    def get_policy_probabilities(self):
        return list(self.last_policy_probabilities)

    def get_table_learning_stats(self):
        tables = _get_table_list(
            self.table_manager
        )

        results = []

        for index in range(ACTION_SIZE):
            capacity = 0

            if index < len(tables):
                capacity = _get_table_capacity(
                    tables[index]
                )

            attempts = self.table_action_counts[index]
            total = self.table_reward_totals[index]

            average = (
                total / attempts
                if attempts
                else 0.0
            )

            results.append({
                "table": f"T{index + 1}",
                "capacity": capacity,
                "attempts": attempts,
                "total_reward": total,
                "average_reward": average,
                "best_reward": self.table_best_rewards[index]
            })

        return results

    def finalize_episode(self):
        if self.pending_transition is None:
            return 0

        result = self._finish_pending(
            self.pending_transition["reward"],
            next_state=None,
            done=True
        )

        return 1 if result else 0

    def reset_episode(self):
        self.pending_transition = None

    def reset_learning(self):
        self.actor = ActorNetwork().to(DEVICE)
        self.critic = CriticNetwork().to(DEVICE)

        self.actor_optimizer = optim.Adam(
            self.actor.parameters(),
            lr=self.actor_lr
        )

        self.critic_optimizer = optim.Adam(
            self.critic.parameters(),
            lr=self.critic_lr
        )

        self.reset_statistics()

    def reset_statistics(self):
        self.total_decisions = 0
        self.successful_allocations = 0
        self.failed_allocations = 0
        self.invalid_allocations = 0
        self.wait_count = 0

        self.actor_updates = 0
        self.critic_updates = 0
        self.q_updates = 0

        self.total_reward = 0.0
        self.total_learning_reward = 0.0
        self.current_reward = 0.0
        self.best_reward = 0.0
        self.total_penalties = 0.0

        self.waste_penalty_count = 0

        self.exact_fit_count = 0
        self.one_unused_count = 0
        self.two_unused_count = 0
        self.large_waste_count = 0

        self.last_action = None
        self.last_group_size = None
        self.last_table_capacity = None
        self.last_unused_seats = 0

        self.last_reward = 0.0
        self.last_state = None

        self.last_log_probability = None
        self.last_value = None

        self.last_entropy = 0.0
        self.last_actor_loss = 0.0
        self.last_critic_loss = 0.0
        self.last_advantage = 0.0
        self.value_estimate = 0.0
        self.last_target = 0.0
        self.last_td_error = 0.0

        self.pending_transition = None

        self.last_policy_probabilities = []
        self.last_feasible_actions = []
        self.feasible_table_count = 0

        self.table_action_counts = [0] * ACTION_SIZE
        self.table_reward_totals = [0.0] * ACTION_SIZE
        self.table_best_rewards = [0.0] * ACTION_SIZE

    def get_statistics(self):
        average_reward = (
            self.total_reward / self.total_decisions
            if self.total_decisions
            else 0.0
        )

        allocation_accuracy = (
            self.successful_allocations
            / self.total_decisions
            * 100.0
            if self.total_decisions
            else 0.0
        )

        return {
            "algorithm": "ACTOR-CRITIC",
            "total_decisions": self.total_decisions,
            "decisions": self.total_decisions,
            "successful_allocations": self.successful_allocations,
            "failed_allocations": self.failed_allocations,
            "invalid_allocations": self.invalid_allocations,
            "wait_count": self.wait_count,
            "customers_served": self.successful_allocations,
            "current_reward": self.current_reward,
            "last_reward": self.last_reward,
            "best_reward": self.best_reward,
            "total_reward": self.total_reward,
            "average_reward": average_reward,
            "total_learning_reward": self.total_learning_reward,
            "total_penalties": self.total_penalties,
            "penalties": self.total_penalties,
            "waste_penalties": self.waste_penalty_count,
            "waste_penalty_count": self.waste_penalty_count,
            "q_updates": self.q_updates,
            "actor_updates": self.actor_updates,
            "critic_updates": self.critic_updates,
            "actor_loss": self.last_actor_loss,
            "critic_loss": self.last_critic_loss,
            "advantage": self.last_advantage,
            "last_advantage": self.last_advantage,
            "value_estimate": self.value_estimate,
            "value": self.value_estimate,
            "target": self.last_target,
            "td_error": self.last_td_error,
            "entropy": self.last_entropy,
            "allocation_accuracy": allocation_accuracy,
            "exact_fits": self.exact_fit_count,
            "one_unused": self.one_unused_count,
            "two_unused": self.two_unused_count,
            "large_waste": self.large_waste_count,
            "epsilon": 0.0,
            "learning_rate": self.actor_lr,
            "critic_learning_rate": self.critic_lr,
            "discount_factor": self.gamma,
            "entropy_coefficient": self.entropy_coefficient,
            "state_size": STATE_SIZE,
            "action_size": ACTION_SIZE,
            "device": str(DEVICE),
            "last_action": self.last_action,
            "last_group_size": self.last_group_size,
            "last_table_capacity": self.last_table_capacity,
            "last_unused_seats": self.last_unused_seats,
            "last_feasible_actions": list(
                self.last_feasible_actions
            ),
            "feasible_table_count": self.feasible_table_count
        }

    def get_rl_statistics(self):
        return self.get_statistics()

    def print_results(self):
        stats = self.get_statistics()

        print()
        print("========================================")
        print("ACTOR-CRITIC RESULTS")
        print("========================================")
        print(
            f"Decisions           : "
            f"{stats['total_decisions']}"
        )
        print(
            f"Successful          : "
            f"{stats['successful_allocations']}"
        )
        print(
            f"Failed              : "
            f"{stats['failed_allocations']}"
        )
        print(
            f"Invalid             : "
            f"{stats['invalid_allocations']}"
        )
        print(
            f"Total reward        : "
            f"{stats['total_reward']:+.2f}"
        )
        print(
            f"Average reward      : "
            f"{stats['average_reward']:+.2f}"
        )
        print(
            f"Total penalties     : "
            f"{stats['total_penalties']:.2f}"
        )
        print(
            f"Actor updates       : "
            f"{stats['actor_updates']}"
        )
        print(
            f"Critic updates      : "
            f"{stats['critic_updates']}"
        )
        print(
            f"Actor loss          : "
            f"{stats['actor_loss']:+.4f}"
        )
        print(
            f"Critic loss         : "
            f"{stats['critic_loss']:+.4f}"
        )
        print(
            f"Advantage           : "
            f"{stats['advantage']:+.4f}"
        )
        print(
            f"Value estimate      : "
            f"{stats['value_estimate']:+.4f}"
        )
        print(
            f"TD error            : "
            f"{stats['td_error']:+.4f}"
        )
        print(
            f"Entropy             : "
            f"{stats['entropy']:.4f}"
        )
        print(
            f"Allocation accuracy : "
            f"{stats['allocation_accuracy']:.2f}%"
        )
        print("========================================")
        print()

    def print_q_table(self):
        print(
            "Actor-Critic does not use a Q-table. "
            "The Actor policy and Critic value "
            "networks are learned directly."
        )


ActorCriticAgent = ActorCriticAlgorithm
ActorCritic = ActorCriticAlgorithm


if __name__ == "__main__":
    print("METRIUS EATS - ACTOR-CRITIC")
    print(f"Device     : {DEVICE}")
    print(f"State size : {STATE_SIZE}")
    print(f"Actions    : {ACTION_SIZE}")