# ============================================================
# RESULT_TRACKER.PY
# ============================================================
#
# METRIUS EATS
#
# Handles:
#
#   - Tracking results for every algorithm used
#   - Keeping Default and Expected SARSA results separately
#   - Preserving results when switching algorithms
#   - Recording RL statistics
#   - Recording restaurant performance
#   - Comparing algorithms
#   - Finding the best-performing algorithm
#   - Preparing clean data for PDF report generation
#
# This file DOES NOT:
#   - Draw anything
#   - Depend on pygame
#   - Generate the PDF itself
#   - Control the RL agent
#
# The future PDF generator can simply call:
#
#       tracker.get_report_data()
#
# ============================================================


import time
from copy import deepcopy


# ============================================================
# ALGORITHM NAMES
# ============================================================

DEFAULT_ALGORITHM = "Default"
EXPECTED_SARSA_ALGORITHM = "Expected SARSA"


# ============================================================
# RESULT TRACKER
# ============================================================

class ResultTracker:

    def __init__(self):
        """
        Create a fresh result tracker.

        The tracker keeps one result record for every algorithm
        that has actually been used during the simulation.
        """

        self.results = {}

        # Current algorithm being tracked
        self.current_algorithm = None

        # Simulation information
        self.simulation_start_time = time.time()
        self.simulation_end_time = None

        self.day = 1

        # Number of algorithm switches
        self.algorithm_switches = 0

        # Overall number of decisions recorded
        self.total_decisions = 0

        # Prevent duplicate initialization issues
        self.initialized = False

    # ========================================================
    # INTERNAL HELPERS
    # ========================================================

    def _create_algorithm_record(self, algorithm_name):
        """
        Create a fresh record for an algorithm.
        """

        return {
            # ----------------------------------------------
            # Basic information
            # ----------------------------------------------

            "algorithm": algorithm_name,
            "used": True,

            # ----------------------------------------------
            # Restaurant performance
            # ----------------------------------------------

            "customers_served": 0,

            "successful_allocations": 0,
            "failed_allocations": 0,
            "invalid_allocations": 0,

            # ----------------------------------------------
            # Waiting time
            # ----------------------------------------------

            "total_wait_time": 0.0,
            "average_wait_time": 0.0,

            # ----------------------------------------------
            # Reward information
            # ----------------------------------------------

            "total_reward": 0.0,
            "average_reward": 0.0,

            # ----------------------------------------------
            # Penalties
            # ----------------------------------------------

            "penalties": 0,
            "waste_penalties": 0,

            # ----------------------------------------------
            # RL information
            # ----------------------------------------------

            "q_updates": 0,
            "q_value_updates": 0,

            "policy": "Unknown",
            "learning_method": algorithm_name,

            # ----------------------------------------------
            # Decisions
            # ----------------------------------------------

            "decisions": 0,

            # ----------------------------------------------
            # Table allocation
            # ----------------------------------------------

            "exact_fits": 0,
            "one_unused": 0,
            "two_unused": 0,
            "large_waste": 0,

            # ----------------------------------------------
            # Timing
            # ----------------------------------------------

            "tracking_start_time": time.time(),
            "tracking_end_time": None,
            "duration_seconds": 0.0,

            # ----------------------------------------------
            # Raw statistics
            #
            # Useful if future versions of agent.py provide
            # additional statistics.
            # ----------------------------------------------

            "raw_statistics": {},

            # ----------------------------------------------
            # Last known values
            # ----------------------------------------------

            "last_reward": 0.0,
            "last_penalty": 0.0,
            "last_decision": None,
        }

    def _ensure_algorithm(self, algorithm_name):
        """
        Make sure an algorithm has a result record.
        """

        if not algorithm_name:
            algorithm_name = DEFAULT_ALGORITHM

        if algorithm_name not in self.results:
            self.results[algorithm_name] = self._create_algorithm_record(
                algorithm_name
            )

        return self.results[algorithm_name]

    @staticmethod
    def _safe_float(value, default=0.0):
        """
        Safely convert a value to float.
        """

        try:
            if value is None:
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value, default=0):
        """
        Safely convert a value to int.
        """

        try:
            if value is None:
                return default

            return int(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _first_value(data, keys, default=None):
        """
        Return the first available value from a list of possible
        dictionary keys.

        This makes the tracker tolerant if agent.py uses slightly
        different statistic names.
        """

        if not isinstance(data, dict):
            return default

        for key in keys:
            if key in data:
                return data[key]

        return default

    # ========================================================
    # ALGORITHM MANAGEMENT
    # ========================================================

    def start_algorithm(self, algorithm_name):
        """
        Start tracking an algorithm.

        Example:

            tracker.start_algorithm("Default")

        Then later:

            tracker.start_algorithm("Expected SARSA")

        The previous algorithm's results remain stored.
        """

        if not algorithm_name:
            algorithm_name = DEFAULT_ALGORITHM

        algorithm_name = str(algorithm_name)

        # Count switch only if we were already tracking
        # another algorithm.
        if (
            self.current_algorithm is not None
            and self.current_algorithm != algorithm_name
        ):
            self.algorithm_switches += 1

            # Stop timing the previous algorithm.
            previous = self.results.get(self.current_algorithm)

            if previous is not None:
                previous["tracking_end_time"] = time.time()
                previous["duration_seconds"] = (
                    previous["tracking_end_time"]
                    - previous["tracking_start_time"]
                )

        self.current_algorithm = algorithm_name

        self._ensure_algorithm(algorithm_name)

        self.initialized = True

        return self.current_algorithm

    def set_current_algorithm(self, algorithm_name):
        """
        Alias for start_algorithm().

        Useful from main.py if you prefer the name
        set_current_algorithm().
        """

        return self.start_algorithm(algorithm_name)

    def get_current_algorithm(self):
        """
        Return the currently active algorithm.
        """

        return self.current_algorithm

    def has_algorithm(self, algorithm_name):
        """
        Return True if this algorithm has been used.
        """

        return algorithm_name in self.results

    def get_used_algorithms(self):
        """
        Return a list of algorithms actually used.

        Example:

            ["Default", "Expected SARSA"]
        """

        return list(self.results.keys())

    # ========================================================
    # STATISTICS UPDATE
    # ========================================================

    def update_from_statistics(
        self,
        statistics,
        algorithm_name=None
    ):
        """
        Update an algorithm's result record using statistics
        returned by agent.py.

        Typical usage:

            tracker.update_from_statistics(
                agent.get_rl_statistics()
            )

        """

        if algorithm_name is None:
            algorithm_name = self.current_algorithm

        if algorithm_name is None:
            algorithm_name = DEFAULT_ALGORITHM

        record = self._ensure_algorithm(algorithm_name)

        if not isinstance(statistics, dict):
            return record

        # Keep a copy of the complete original statistics.
        record["raw_statistics"] = deepcopy(statistics)

        # ====================================================
        # CUSTOMERS SERVED
        # ====================================================

        customers_served = self._first_value(
            statistics,
            [
                "customers_served",
                "customers",
                "served",
                "total_customers_served",
            ],
            None,
        )

        if customers_served is not None:
            record["customers_served"] = self._safe_int(
                customers_served
            )

        # ====================================================
        # SUCCESSFUL ALLOCATIONS
        # ====================================================

        successful = self._first_value(
            statistics,
            [
                "successful_allocations",
                "successful",
                "successes",
                "successful_decisions",
            ],
            None,
        )

        if successful is not None:
            record["successful_allocations"] = self._safe_int(
                successful
            )

        # ====================================================
        # FAILED ALLOCATIONS
        # ====================================================

        failed = self._first_value(
            statistics,
            [
                "failed_allocations",
                "failed",
                "failures",
            ],
            None,
        )

        if failed is not None:
            record["failed_allocations"] = self._safe_int(
                failed
            )

        # ====================================================
        # INVALID ALLOCATIONS
        # ====================================================

        invalid = self._first_value(
            statistics,
            [
                "invalid_allocations",
                "invalid_actions",
                "invalid",
            ],
            None,
        )

        if invalid is not None:
            record["invalid_allocations"] = self._safe_int(
                invalid
            )

        # ====================================================
        # WAITING TIME
        # ====================================================

        total_wait = self._first_value(
            statistics,
            [
                "total_wait_time",
                "total_wait",
                "wait_time_total",
            ],
            None,
        )

        if total_wait is not None:
            record["total_wait_time"] = self._safe_float(
                total_wait
            )

        average_wait = self._first_value(
            statistics,
            [
                "average_wait_time",
                "avg_wait_time",
                "average_wait",
                "avg_wait",
            ],
            None,
        )

        if average_wait is not None:
            record["average_wait_time"] = self._safe_float(
                average_wait
            )

        # ====================================================
        # TOTAL REWARD
        # ====================================================

        total_reward = self._first_value(
            statistics,
            [
                "total_reward",
                "cumulative_reward",
                "reward",
                "total_rewards",
            ],
            None,
        )

        if total_reward is not None:
            record["total_reward"] = self._safe_float(
                total_reward
            )

        # ====================================================
        # AVERAGE REWARD
        # ====================================================

        average_reward = self._first_value(
            statistics,
            [
                "average_reward",
                "avg_reward",
            ],
            None,
        )

        if average_reward is not None:
            record["average_reward"] = self._safe_float(
                average_reward
            )

        # ====================================================
        # PENALTIES
        # ====================================================

        penalties = self._first_value(
            statistics,
            [
                "penalties",
                "total_penalties",
                "penalty_count",
            ],
            None,
        )

        if penalties is not None:
            record["penalties"] = self._safe_int(
                penalties
            )

        # ====================================================
        # WASTE PENALTIES
        # ====================================================

        waste_penalties = self._first_value(
            statistics,
            [
                "waste_penalties",
                "waste_penalty_count",
                "large_waste_penalties",
            ],
            None,
        )

        if waste_penalties is not None:
            record["waste_penalties"] = self._safe_int(
                waste_penalties
            )

        # ====================================================
        # Q-VALUE UPDATES
        # ====================================================

        q_updates = self._first_value(
            statistics,
            [
                "q_updates",
                "q_value_updates",
                "updates",
                "total_q_updates",
            ],
            None,
        )

        if q_updates is not None:
            q_value = self._safe_int(q_updates)

            record["q_updates"] = q_value
            record["q_value_updates"] = q_value

        # ====================================================
        # POLICY
        # ====================================================

        policy = self._first_value(
            statistics,
            [
                "policy",
                "policy_name",
            ],
            None,
        )

        if policy is not None:
            record["policy"] = str(policy)

        # ====================================================
        # LEARNING METHOD
        # ====================================================

        learning = self._first_value(
            statistics,
            [
                "learning_method",
                "learning",
                "method",
            ],
            None,
        )

        if learning is not None:
            record["learning_method"] = str(learning)

        # ====================================================
        # DECISIONS
        # ====================================================

        decisions = self._first_value(
            statistics,
            [
                "decisions",
                "decision_count",
                "total_decisions",
                "steps",
            ],
            None,
        )

        if decisions is not None:
            record["decisions"] = self._safe_int(
                decisions
            )

        # ====================================================
        # ALLOCATION QUALITY
        # ====================================================

        exact_fits = self._first_value(
            statistics,
            [
                "exact_fits",
                "exact_fit_count",
            ],
            None,
        )

        if exact_fits is not None:
            record["exact_fits"] = self._safe_int(
                exact_fits
            )

        one_unused = self._first_value(
            statistics,
            [
                "one_unused",
                "one_unused_count",
            ],
            None,
        )

        if one_unused is not None:
            record["one_unused"] = self._safe_int(
                one_unused
            )

        two_unused = self._first_value(
            statistics,
            [
                "two_unused",
                "two_unused_count",
            ],
            None,
        )

        if two_unused is not None:
            record["two_unused"] = self._safe_int(
                two_unused
            )

        large_waste = self._first_value(
            statistics,
            [
                "large_waste",
                "large_waste_count",
                "waste_count",
            ],
            None,
        )

        if large_waste is not None:
            record["large_waste"] = self._safe_int(
                large_waste
            )

        # Update global decision count.
        self.total_decisions = sum(
            result.get("decisions", 0)
            for result in self.results.values()
        )

        return record

    # ========================================================
    # INDIVIDUAL DECISION TRACKING
    # ========================================================

    def record_decision(
        self,
        algorithm_name=None,
        group_size=None,
        table_name=None,
        reward=None,
        penalty=None,
        result="SUCCESS",
        unused_seats=None,
    ):
        """
        Record one allocation decision.

        This is optional because agent.get_rl_statistics()
        already contains most of the important information.

        It is useful when we want a more detailed experiment
        history.
        """

        if algorithm_name is None:
            algorithm_name = self.current_algorithm

        if algorithm_name is None:
            algorithm_name = DEFAULT_ALGORITHM

        record = self._ensure_algorithm(algorithm_name)

        record["decisions"] += 1

        self.total_decisions += 1

        # ----------------------------------------------
        # Reward
        # ----------------------------------------------

        if reward is not None:
            reward_value = self._safe_float(reward)

            record["last_reward"] = reward_value

        else:
            reward_value = 0.0

        # ----------------------------------------------
        # Penalty
        # ----------------------------------------------

        if penalty is not None:
            penalty_value = self._safe_float(penalty)

            record["last_penalty"] = penalty_value

        else:
            penalty_value = 0.0

        # ----------------------------------------------
        # Decision result
        # ----------------------------------------------

        decision = {
            "group_size": group_size,
            "table": table_name,
            "reward": reward_value,
            "penalty": penalty_value,
            "result": result,
            "unused_seats": unused_seats,
        }

        record["last_decision"] = decision

        # ----------------------------------------------
        # Result counters
        # ----------------------------------------------

        result_upper = str(result).upper()

        if result_upper == "SUCCESS":
            record["successful_allocations"] += 1
        else:
            record["failed_allocations"] += 1

        # ----------------------------------------------
        # Allocation quality
        # ----------------------------------------------

        if unused_seats is not None:
            unused = self._safe_int(unused_seats)

            if unused == 0:
                record["exact_fits"] += 1

            elif unused == 1:
                record["one_unused"] += 1

            elif unused == 2:
                record["two_unused"] += 1

            elif unused >= 3:
                record["large_waste"] += 1

        return decision

    # ========================================================
    # MANUAL CUSTOMER UPDATE
    # ========================================================

    def record_customer_served(
        self,
        wait_time=0.0,
        algorithm_name=None
    ):
        """
        Record a customer/group being successfully served.

        Useful if main.py wants to explicitly report a
        completed customer group.
        """

        if algorithm_name is None:
            algorithm_name = self.current_algorithm

        if algorithm_name is None:
            algorithm_name = DEFAULT_ALGORITHM

        record = self._ensure_algorithm(algorithm_name)

        record["customers_served"] += 1

        wait = self._safe_float(wait_time)

        record["total_wait_time"] += wait

        if record["customers_served"] > 0:
            record["average_wait_time"] = (
                record["total_wait_time"]
                / record["customers_served"]
            )

        return record["customers_served"]

    # ========================================================
    # MANUAL REWARD UPDATE
    # ========================================================

    def record_reward(
        self,
        reward,
        algorithm_name=None
    ):
        """
        Add a reward to an algorithm.
        """

        if algorithm_name is None:
            algorithm_name = self.current_algorithm

        if algorithm_name is None:
            algorithm_name = DEFAULT_ALGORITHM

        record = self._ensure_algorithm(algorithm_name)

        reward_value = self._safe_float(reward)

        record["total_reward"] += reward_value

        record["last_reward"] = reward_value

        if record["decisions"] > 0:
            record["average_reward"] = (
                record["total_reward"]
                / record["decisions"]
            )

        return record["total_reward"]

    # ========================================================
    # MANUAL PENALTY UPDATE
    # ========================================================

    def record_penalty(
        self,
        penalty=1,
        algorithm_name=None,
        waste=False
    ):
        """
        Record a penalty.

        Example:

            tracker.record_penalty()

        For a waste penalty:

            tracker.record_penalty(
                penalty=1,
                waste=True
            )
        """

        if algorithm_name is None:
            algorithm_name = self.current_algorithm

        if algorithm_name is None:
            algorithm_name = DEFAULT_ALGORITHM

        record = self._ensure_algorithm(algorithm_name)

        penalty_value = self._safe_int(penalty)

        record["penalties"] += penalty_value

        if waste:
            record["waste_penalties"] += penalty_value

        return record["penalties"]

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def get_algorithm_result(self, algorithm_name):
        """
        Return a copy of one algorithm's results.
        """

        if algorithm_name not in self.results:
            return None

        return deepcopy(
            self.results[algorithm_name]
        )

    def get_all_results(self):
        """
        Return all algorithm results.
        """

        return deepcopy(self.results)

    # ========================================================
    # COMPARISON
    # ========================================================

    def compare_algorithms(self):
        """
        Compare every algorithm that has been used.

        Returns a dictionary containing the metrics and
        percentage improvements.

        If fewer than two algorithms were used, the comparison
        still returns useful information but does not claim
        there is a winner.
        """

        algorithms = self.get_used_algorithms()

        comparison = {
            "algorithms": algorithms,
            "can_compare": len(algorithms) >= 2,
            "metrics": {},
            "winner": None,
            "winner_reason": None,
        }

        if not algorithms:
            return comparison

        # ----------------------------------------------------
        # If only one algorithm has been used
        # ----------------------------------------------------

        if len(algorithms) == 1:
            comparison["winner"] = algorithms[0]
            comparison["winner_reason"] = (
                "Only one algorithm was used."
            )

            return comparison

        # ----------------------------------------------------
        # Build metric comparison
        # ----------------------------------------------------

        metric_definitions = {
            "customers_served": {
                "label": "Customers Served",
                "higher_is_better": True,
            },

            "average_wait_time": {
                "label": "Average Wait Time",
                "higher_is_better": False,
            },

            "total_reward": {
                "label": "Total Reward",
                "higher_is_better": True,
            },

            "penalties": {
                "label": "Penalties",
                "higher_is_better": False,
            },

            "waste_penalties": {
                "label": "Waste Penalties",
                "higher_is_better": False,
            },

            "q_updates": {
                "label": "Q-Value Updates",
                "higher_is_better": True,
            },

            "successful_allocations": {
                "label": "Successful Allocations",
                "higher_is_better": True,
            },

            "invalid_allocations": {
                "label": "Invalid Allocations",
                "higher_is_better": False,
            },
        }

        for metric, definition in metric_definitions.items():

            values = {}

            for algorithm in algorithms:
                record = self.results[algorithm]

                values[algorithm] = record.get(
                    metric,
                    0
                )

            best_algorithm = None

            if definition["higher_is_better"]:
                best_algorithm = max(
                    values,
                    key=values.get
                )
            else:
                best_algorithm = min(
                    values,
                    key=values.get
                )

            comparison["metrics"][metric] = {
                "label": definition["label"],
                "values": values,
                "best": best_algorithm,
                "higher_is_better": definition[
                    "higher_is_better"
                ],
            }

        # ----------------------------------------------------
        # Overall winner
        #
        # We use several meaningful restaurant metrics rather
        # than Q-updates alone.
        # ----------------------------------------------------

        scores = {
            algorithm: 0.0
            for algorithm in algorithms
        }

        # Customers served
        self._score_metric(
            scores,
            "customers_served",
            higher_is_better=True
        )

        # Average waiting time
        self._score_metric(
            scores,
            "average_wait_time",
            higher_is_better=False
        )

        # Total reward
        self._score_metric(
            scores,
            "total_reward",
            higher_is_better=True
        )

        # Penalties
        self._score_metric(
            scores,
            "penalties",
            higher_is_better=False
        )

        # Waste penalties
        self._score_metric(
            scores,
            "waste_penalties",
            higher_is_better=False
        )

        winner = max(
            scores,
            key=scores.get
        )

        comparison["winner"] = winner

        comparison["winner_reason"] = (
            "Best overall performance across "
            "customers served, waiting time, reward, "
            "and penalty metrics."
        )

        comparison["overall_scores"] = scores

        return comparison

    def _score_metric(
        self,
        scores,
        metric,
        higher_is_better=True
    ):
        """
        Internal helper used by compare_algorithms().
        """

        algorithms = list(scores.keys())

        if not algorithms:
            return

        values = {}

        for algorithm in algorithms:
            values[algorithm] = self._safe_float(
                self.results[algorithm].get(
                    metric,
                    0
                )
            )

        highest = max(values.values())
        lowest = min(values.values())

        # All equal.
        if highest == lowest:
            for algorithm in algorithms:
                scores[algorithm] += 1.0

            return

        for algorithm in algorithms:

            value = values[algorithm]

            if higher_is_better:
                normalized = (
                    value - lowest
                ) / (
                    highest - lowest
                )

            else:
                normalized = (
                    highest - value
                ) / (
                    highest - lowest
                )

            scores[algorithm] += normalized

    # ========================================================
    # PERCENTAGE IMPROVEMENT
    # ========================================================

    @staticmethod
    def percentage_change(old_value, new_value):
        """
        Calculate percentage change from old -> new.

        Returns 0 when the old value is zero.
        """

        old = float(old_value)
        new = float(new_value)

        if old == 0:
            return 0.0

        return (
            (new - old)
            / abs(old)
        ) * 100.0

    def get_pairwise_comparison(
        self,
        algorithm_a,
        algorithm_b
    ):
        """
        Compare two specific algorithms.

        Example:

            tracker.get_pairwise_comparison(
                "Default",
                "Expected SARSA"
            )
        """

        result_a = self.results.get(algorithm_a)
        result_b = self.results.get(algorithm_b)

        if result_a is None or result_b is None:
            return None

        metrics = [
            "customers_served",
            "average_wait_time",
            "total_reward",
            "penalties",
            "waste_penalties",
            "q_updates",
            "successful_allocations",
            "invalid_allocations",
        ]

        comparison = {
            "algorithm_a": algorithm_a,
            "algorithm_b": algorithm_b,
            "metrics": {},
        }

        for metric in metrics:

            value_a = self._safe_float(
                result_a.get(metric, 0)
            )

            value_b = self._safe_float(
                result_b.get(metric, 0)
            )

            comparison["metrics"][metric] = {
                algorithm_a: value_a,
                algorithm_b: value_b,
                "change_a_to_b": self.percentage_change(
                    value_a,
                    value_b
                ),
            }

        return comparison

    # ========================================================
    # REPORT DATA
    # ========================================================

    def get_report_data(self):
        """
        Return all information required by the future PDF
        generator.

        This is the main method the PDF generator should use.
        """

        self._finish_current_timing()

        algorithms = self.get_used_algorithms()

        report = {
            # ------------------------------------------------
            # Report information
            # ------------------------------------------------

            "title": "METRIUS EATS",
            "subtitle": "Reinforcement Learning Algorithm Evaluation",
            "day": self.day,

            # ------------------------------------------------
            # Simulation
            # ------------------------------------------------

            "simulation": {
                "start_time": self.simulation_start_time,
                "end_time": self.simulation_end_time,
                "duration_seconds": self.get_simulation_duration(),
                "algorithm_switches": self.algorithm_switches,
                "total_decisions": self.total_decisions,
            },

            # ------------------------------------------------
            # Algorithms
            # ------------------------------------------------

            "algorithms_used": algorithms,
            "algorithm_count": len(algorithms),

            # ------------------------------------------------
            # Individual results
            # ------------------------------------------------

            "results": self.get_all_results(),

            # ------------------------------------------------
            # Comparison
            # ------------------------------------------------

            "comparison": self.compare_algorithms(),

            # ------------------------------------------------
            # Best algorithm
            # ------------------------------------------------

            "best_algorithm": (
                self.compare_algorithms().get("winner")
            ),
        }

        return report

    # ========================================================
    # SIMULATION TIMING
    # ========================================================

    def set_day(self, day):
        """
        Set simulation day.
        """

        self.day = self._safe_int(day, 1)

    def finish_simulation(self):
        """
        Mark the simulation as finished.
        """

        self.simulation_end_time = time.time()

        self._finish_current_timing()

    def _finish_current_timing(self):
        """
        Update the current algorithm's tracking duration.
        """

        now = time.time()

        if self.current_algorithm is not None:

            record = self.results.get(
                self.current_algorithm
            )

            if record is not None:

                if record["tracking_end_time"] is None:
                    record["tracking_end_time"] = now

                record["duration_seconds"] = (
                    record["tracking_end_time"]
                    - record["tracking_start_time"]
                )

    def get_simulation_duration(self):
        """
        Return total simulation duration in seconds.
        """

        if self.simulation_end_time is not None:

            return (
                self.simulation_end_time
                - self.simulation_start_time
            )

        return (
            time.time()
            - self.simulation_start_time
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Completely reset the tracker.

        Useful when starting a new simulation experiment.
        """

        self.results = {}

        self.current_algorithm = None

        self.simulation_start_time = time.time()

        self.simulation_end_time = None

        self.day = 1

        self.algorithm_switches = 0

        self.total_decisions = 0

        self.initialized = False

    # ========================================================
    # DEBUG / CONSOLE
    # ========================================================

    def print_results(self):
        """
        Print a readable summary to the console.
        """

        print()
        print("=" * 65)
        print("METRIUS EATS - RESULT TRACKER")
        print("=" * 65)

        print(
            f"Algorithms Used: "
            f"{len(self.results)}"
        )

        print(
            f"Total Decisions: "
            f"{self.total_decisions}"
        )

        print(
            f"Algorithm Switches: "
            f"{self.algorithm_switches}"
        )

        print("-" * 65)

        for algorithm, record in self.results.items():

            print()
            print(f"[{algorithm}]")

            print(
                f"  Customers Served : "
                f"{record['customers_served']}"
            )

            print(
                f"  Average Wait     : "
                f"{record['average_wait_time']:.2f}"
            )

            print(
                f"  Total Reward     : "
                f"{record['total_reward']:.2f}"
            )

            print(
                f"  Penalties        : "
                f"{record['penalties']}"
            )

            print(
                f"  Waste Penalties  : "
                f"{record['waste_penalties']}"
            )

            print(
                f"  Q Updates        : "
                f"{record['q_updates']}"
            )

            print(
                f"  Decisions        : "
                f"{record['decisions']}"
            )

        print()
        print("-" * 65)

        comparison = self.compare_algorithms()

        if comparison["can_compare"]:

            print(
                f"Best Algorithm: "
                f"{comparison['winner']}"
            )

            print(
                f"Reason: "
                f"{comparison['winner_reason']}"
            )

        elif comparison["winner"]:

            print(
                f"Algorithm: "
                f"{comparison['winner']}"
            )

        print("=" * 65)
        print()

    # ========================================================
    # EXPORT-FRIENDLY FLAT DATA
    # ========================================================

    def get_comparison_table(self):
        """
        Return a simple list of dictionaries.

        This will be particularly useful when creating
        the PDF comparison table.
        """

        algorithms = self.get_used_algorithms()

        rows = []

        for algorithm in algorithms:

            record = self.results[algorithm]

            rows.append({
                "Algorithm": algorithm,

                "Customers Served":
                    record.get(
                        "customers_served",
                        0
                    ),

                "Average Wait Time":
                    record.get(
                        "average_wait_time",
                        0.0
                    ),

                "Total Reward":
                    record.get(
                        "total_reward",
                        0.0
                    ),

                "Penalties":
                    record.get(
                        "penalties",
                        0
                    ),

                "Waste Penalties":
                    record.get(
                        "waste_penalties",
                        0
                    ),

                "Q-Value Updates":
                    record.get(
                        "q_updates",
                        0
                    ),

                "Successful Allocations":
                    record.get(
                        "successful_allocations",
                        0
                    ),

                "Invalid Allocations":
                    record.get(
                        "invalid_allocations",
                        0
                    ),
            })

        return rows


# ============================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================

ResultsTracker = ResultTracker


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Testing ResultTracker...")

    tracker = ResultTracker()

    # --------------------------------------------------------
    # Default algorithm
    # --------------------------------------------------------

    tracker.start_algorithm("Default")

    tracker.update_from_statistics({
        "customers_served": 42,
        "average_wait_time": 1.8,
        "total_reward": 320,
        "penalties": 8,
        "waste_penalties": 5,
        "successful_allocations": 42,
        "invalid_allocations": 0,
        "q_updates": 0,
        "policy": "Rule-Based",
    })

    # --------------------------------------------------------
    # Expected SARSA
    # --------------------------------------------------------

    tracker.start_algorithm("Expected SARSA")

    tracker.update_from_statistics({
        "customers_served": 51,
        "average_wait_time": 1.2,
        "total_reward": 487,
        "penalties": 3,
        "waste_penalties": 1,
        "successful_allocations": 51,
        "invalid_allocations": 0,
        "q_updates": 184,
        "policy": "Epsilon Greedy",
        "learning_method": "Expected Q-value",
    })

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    tracker.print_results()

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    comparison = tracker.compare_algorithms()

    print("Comparison:")
    print(comparison)

    print()

    print("Comparison Table:")

    for row in tracker.get_comparison_table():
        print(row)

    print()

    print("Report Data:")
    print(tracker.get_report_data())

    print()
    print("ResultTracker test completed.")