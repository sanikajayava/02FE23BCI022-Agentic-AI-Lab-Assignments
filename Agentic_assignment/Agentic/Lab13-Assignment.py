
"""
Lab 13: Discipline-Specific Engineering Agents
Original Practical + Assignment 1 + Assignment 2

Original: Mechanical Engineering - Predictive Maintenance
Assignment 1: Electrical Engineering - Load Forecasting
Assignment 2: Trend-based escalation
"""

# ============================================================
# PART 1: ORIGINAL PRACTICAL - MECHANICAL ENGINEERING
# ============================================================

# Simulated motor sensor readings
SENSOR_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61},
    {"t": 1, "vibration_mm_s": 1.9, "temp_c": 62},
    {"t": 2, "vibration_mm_s": 2.4, "temp_c": 65},
    {"t": 3, "vibration_mm_s": 3.1, "temp_c": 70},
    {"t": 4, "vibration_mm_s": 4.6, "temp_c": 76},
    {"t": 5, "vibration_mm_s": 6.2, "temp_c": 84},
]

# Simplified teaching thresholds
THRESHOLDS = {
    "vibration_warn": 2.8,
    "vibration_alarm": 4.5,
    "temp_warn": 70,
    "temp_alarm": 80
}


def tool_read_sensor_log():
    return SENSOR_LOG


def classify_condition(reading):
    if (
        reading["vibration_mm_s"] >= THRESHOLDS["vibration_alarm"]
        or reading["temp_c"] >= THRESHOLDS["temp_alarm"]
    ):
        return "ALARM"

    if (
        reading["vibration_mm_s"] >= THRESHOLDS["vibration_warn"]
        or reading["temp_c"] >= THRESHOLDS["temp_warn"]
    ):
        return "WARNING"

    return "NORMAL"


def trend_direction(log):
    if len(log) < 2:
        return "insufficient_data"

    deltas = [
        log[i + 1]["vibration_mm_s"] - log[i]["vibration_mm_s"]
        for i in range(len(log) - 1)
    ]

    return "worsening" if all(d >= 0 for d in deltas) else "mixed"


def safety_check(condition):
    # ALARM-level shutdown must always require human approval.
    if condition == "ALARM":
        return {
            "action_allowed": "recommend_shutdown_for_human_review",
            "auto_execute": False
        }

    if condition == "WARNING":
        return {
            "action_allowed": "schedule_inspection",
            "auto_execute": False
        }

    return {
        "action_allowed": "continue_monitoring",
        "auto_execute": True
    }


def predictive_maintenance_agent():
    log = tool_read_sensor_log()

    latest = log[-1]
    condition = classify_condition(latest)
    trend = trend_direction(log)
    safety = safety_check(condition)

    return {
        "domain": "Mechanical Engineering -- Predictive Maintenance",
        "latest_reading": latest,
        "condition": condition,
        "trend": trend,
        "recommended_action": safety["action_allowed"],
        "auto_executed": safety["auto_execute"],
        "evaluation_method": (
            "Threshold classification against ISO-10816-style vibration "
            "bands, cross-checked with temperature trend over the log window."
        )
    }


# ============================================================
# PART 2: ASSIGNMENT 1 - ELECTRICAL LOAD FORECASTING
# ============================================================

# Simulated electrical load readings as percentage of rated capacity
ELECTRICAL_LOAD_LOG = [
    {"t": 0, "load_percent": 62},
    {"t": 1, "load_percent": 70},
    {"t": 2, "load_percent": 84},
    {"t": 3, "load_percent": 91},
    {"t": 4, "load_percent": 98}
]

ELECTRICAL_THRESHOLDS = {
    "load_warn": 80,
    "load_alarm": 95
}


def tool_read_electrical_load():
    return ELECTRICAL_LOAD_LOG


def classify_electrical_load(reading):
    load = reading["load_percent"]

    if load >= ELECTRICAL_THRESHOLDS["load_alarm"]:
        return "ALARM"

    if load >= ELECTRICAL_THRESHOLDS["load_warn"]:
        return "WARNING"

    return "NORMAL"


def electrical_safety_check(condition):
    # An ALARM-level electrical action must never be automatic.
    if condition == "ALARM":
        return {
            "recommended_action": "recommend_load_isolation_for_human_review",
            "auto_execute": False
        }

    if condition == "WARNING":
        return {
            "recommended_action": "inspect_electrical_load",
            "auto_execute": False
        }

    return {
        "recommended_action": "continue_load_monitoring",
        "auto_execute": True
    }


def electrical_load_agent():
    log = tool_read_electrical_load()

    latest = log[-1]
    condition = classify_electrical_load(latest)

    safety = electrical_safety_check(condition)

    return {
        "domain": "Electrical Engineering -- Load Forecasting",
        "latest_reading": latest,
        "condition": condition,
        "recommended_action": safety["recommended_action"],
        "auto_executed": safety["auto_execute"],
        "evaluation_method": (
            "Threshold-based classification using electrical load "
            "percentage of rated capacity."
        )
    }


# ============================================================
# PART 3: ASSIGNMENT 2 - TREND-BASED ESCALATION
# ============================================================

# Three consecutive WARNING readings.
# All readings remain below the ALARM thresholds.
TREND_SENSOR_LOG = [
    {"t": 0, "vibration_mm_s": 2.9, "temp_c": 65},
    {"t": 1, "vibration_mm_s": 3.2, "temp_c": 67},
    {"t": 2, "vibration_mm_s": 3.5, "temp_c": 69}
]


def count_consecutive_warnings(log):
    count = 0

    # Count WARNING readings backwards from the latest reading.
    for reading in reversed(log):
        if classify_condition(reading) == "WARNING":
            count += 1
        else:
            break

    return count


def trend_based_maintenance_agent():
    log = TREND_SENSOR_LOG

    latest = log[-1]
    condition = classify_condition(latest)
    trend = trend_direction(log)

    consecutive_warnings = count_consecutive_warnings(log)

    # Start with the normal threshold-based safety decision.
    safety = safety_check(condition)

    # Assignment 2: escalate after three consecutive warnings.
    if consecutive_warnings >= 3 and trend == "worsening":
        recommended_action = "schedule_inspection"
        auto_executed = False
        escalation_reason = (
            "Three consecutive WARNING readings with an upward "
            "vibration trend. Inspection is required."
        )
    else:
        recommended_action = safety["action_allowed"]
        auto_executed = safety["auto_execute"]
        escalation_reason = "No trend-based escalation required."

    return {
        "domain": "Mechanical Engineering -- Trend-based Maintenance",
        "latest_reading": latest,
        "condition": condition,
        "trend": trend,
        "consecutive_warning_readings": consecutive_warnings,
        "recommended_action": recommended_action,
        "auto_executed": auto_executed,
        "escalation_reason": escalation_reason
    }


# ============================================================
# PART 4: DISPLAY AND VALIDATION
# ============================================================

def display_result(title, result):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":

    # Original Practical
    original_result = predictive_maintenance_agent()
    display_result(
        "ORIGINAL PRACTICAL: MECHANICAL PREDICTIVE MAINTENANCE",
        original_result
    )

    # Assignment 1
    electrical_result = electrical_load_agent()
    display_result(
        "ASSIGNMENT 1: ELECTRICAL LOAD FORECASTING",
        electrical_result
    )

    # Assignment 2
    trend_result = trend_based_maintenance_agent()
    display_result(
        "ASSIGNMENT 2: TREND-BASED ESCALATION",
        trend_result
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("LAB 13 VALIDATION")
    print("=" * 65)

    # Original practical validation
    original_pass = (
        original_result["condition"] == "ALARM"
        and original_result["auto_executed"] is False
        and original_result["recommended_action"]
        == "recommend_shutdown_for_human_review"
    )

    # Assignment 1 validation
    electrical_pass = (
        electrical_result["condition"] == "ALARM"
        and electrical_result["auto_executed"] is False
        and electrical_result["recommended_action"]
        == "recommend_load_isolation_for_human_review"
    )

    # Assignment 2 validation
    trend_pass = (
        trend_result["consecutive_warning_readings"] >= 3
        and trend_result["condition"] == "WARNING"
        and trend_result["trend"] == "worsening"
        and trend_result["recommended_action"] == "schedule_inspection"
        and trend_result["auto_executed"] is False
        and all(
            reading["vibration_mm_s"] < THRESHOLDS["vibration_alarm"]
            and reading["temp_c"] < THRESHOLDS["temp_alarm"]
            for reading in TREND_SENSOR_LOG
        )
    )

    print(
        "Original Practical:",
        "PASS" if original_pass else "FAIL"
    )

    print(
        "Assignment 1 - Electrical Load Forecasting:",
        "PASS" if electrical_pass else "FAIL"
    )

    print(
        "Assignment 2 - Trend-based Escalation:",
        "PASS" if trend_pass else "FAIL"
    )

    all_passed = original_pass and electrical_pass and trend_pass

    print("\n" + "=" * 65)

    if all_passed:
        print("ALL LAB 13 REQUIREMENTS PASSED")
    else:
        print("SOME LAB 13 REQUIREMENTS FAILED")

    print("=" * 65)
