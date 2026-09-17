# ============================================================
# MESSAGES.PY
# ============================================================
#
# METRIUS EATS
#
# Handles all agent communication messages.
#
# IMPORTANT:
#
# This file ONLY creates text messages.
# It does NOT make allocation decisions.
#
# ============================================================


# ============================================================
# DEFAULT MESSAGE
# ============================================================

DEFAULT_WAITING_MESSAGE = (
    "Waiting for the next allocation..."
)


# ============================================================
# GROUP DETECTED
# ============================================================

def group_detected_message(group_size):

    if group_size == 1:

        return (
            "Okay, I have 1 person waiting."
        )

    return (
        f"Okay, I have {group_size} people waiting."
    )


# ============================================================
# CHECKING TABLES
# ============================================================

def checking_tables_message():

    return (
        "Checking available tables..."
    )


# ============================================================
# CLEANING TABLE
# ============================================================

def cleaning_table_message(
    table_name,
    remaining_seconds=None
):

    if remaining_seconds is None:

        return (
            f"Cleaning {table_name}..."
        )

    remaining_seconds = max(
        1,
        int(round(remaining_seconds))
    )

    if remaining_seconds == 1:

        return (
            f"Cleaning {table_name}... "
            f"1 second remaining."
        )

    return (
        f"Cleaning {table_name}... "
        f"{remaining_seconds} seconds remaining."
    )


# ============================================================
# TABLE CLEAN
# ============================================================

def table_clean_message(
    table_name
):

    return (
        f"{table_name} is clean and ready."
    )


# ============================================================
# ALGORITHM SWITCHED
# ============================================================
#
# Used when the user selects a different allocation
# algorithm from the sidebar.
#
# Example:
#
#     Switched to Expected SARSA.
#
# ============================================================

def algorithm_switched_message(
    algorithm_name
):

    return (
        f"Switched to {algorithm_name}."
    )


# ============================================================
# EXPECTED SARSA SWITCHED
# ============================================================
#
# Dedicated message for Expected SARSA.
#
# This keeps the message simple and can be called directly
# from the agent/sidebar when Expected SARSA is selected.
#
# ============================================================

def expected_sarsa_switched_message():

    return (
        "Switched to Expected SARSA."
    )


# ============================================================
# DEFAULT ALGORITHM SWITCHED
# ============================================================

def default_algorithm_switched_message():

    return (
        "Switched to Default."
    )


# ============================================================
# ASSIGN TABLE
# ============================================================

def assign_table_message(
    group_size,
    table_name
):

    if group_size == 1:

        return (
            f"Okay, I will assign "
            f"1 person to {table_name}."
        )

    return (
        f"Okay, I will assign "
        f"{group_size} people to {table_name}."
    )


# ============================================================
# TABLE OCCUPIED
# ============================================================

def table_occupied_message(
    table_name
):

    return (
        f"{table_name} is currently occupied."
    )


# ============================================================
# NO SUITABLE TABLE
# ============================================================

def no_table_message(
    group_size
):

    if group_size == 1:

        return (
            "No suitable table is available "
            "for 1 person."
        )

    return (
        f"No suitable table is available "
        f"for {group_size} people."
    )


# ============================================================
# GROUP TOO LARGE
# ============================================================

def group_too_large_message(
    group_size
):

    return (
        f"I cannot seat a group of "
        f"{group_size} people right now."
    )


# ============================================================
# SUCCESS MESSAGE
# ============================================================

def allocation_complete_message(
    group_size,
    table_name
):

    if group_size == 1:

        return (
            f"1 person assigned to {table_name}."
        )

    return (
        f"{group_size} people assigned to {table_name}."
    )


# ============================================================
# RESET MESSAGE
# ============================================================

def waiting_message():

    return DEFAULT_WAITING_MESSAGE


# ============================================================
# END OF MESSAGES.PY
# ============================================================