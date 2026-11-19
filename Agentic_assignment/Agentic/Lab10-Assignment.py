
"""
LAB 10: CLOUD OPERATIONS AGENT
Failed Deployment Diagnosis

Original Practical:
    - Inspect deployment logs and metrics
    - Classify incident severity
    - Identify likely root cause
    - Propose remediation
    - Require approval for high-risk actions

Assignment 1:
    - Add database connection-pool exhaustion incident
    - Use separate logs, deployment history and metrics
    - Produce a different diagnosis and severity

Assignment 2:
    - Add WARNING-level restart_single_pod scenario
    - Automatically execute permitted low-risk action
    - Always require approval for rollback-class actions

Workflow:
    Observe -> Reason -> Classify Risk -> Act Safely
"""

# ============================================================
# 1. ORIGINAL INCIDENT: PAYMENTS SERVICE
# ============================================================

LOGS = [

    {
        "ts": "14:00:00",
        "level": "INFO",
        "msg": "deploy started: payments-service v2.4.1"
    },

    {
        "ts": "14:00:45",
        "level": "INFO",
        "msg": "deploy completed: payments-service v2.4.1"
    },

    {
        "ts": "14:03:10",
        "level": "WARN",
        "msg": "refund endpoint latency elevated"
    },

    {
        "ts": "14:03:40",
        "level": "ERROR",
        "msg": "refund endpoint: NullPointerException in RefundHandler"
    },

    {
        "ts": "14:04:05",
        "level": "ERROR",
        "msg": "refund endpoint: NullPointerException in RefundHandler"
    },

    {
        "ts": "14:04:30",
        "level": "ERROR",
        "msg": "refund endpoint: NullPointerException in RefundHandler"
    }

]


DEPLOY_HISTORY = [

    {
        "ts": "14:00:00",
        "service": "payments-service",
        "version": "v2.4.1",
        "prev_version": "v2.4.0"
    }

]


METRICS = {

    "baseline_error_rate": 0.5,

    "current_error_rate": 1.6

}


# ============================================================
# 2. ASSIGNMENT 1: DATABASE CONNECTION-POOL INCIDENT
# ============================================================

DB_LOGS = [

    {
        "ts": "15:00:00",
        "level": "INFO",
        "msg": "deploy started: orders-service v1.8.0"
    },

    {
        "ts": "15:00:30",
        "level": "INFO",
        "msg": "deploy completed: orders-service v1.8.0"
    },

    {
        "ts": "15:02:00",
        "level": "WARN",
        "msg": "database connection pool usage reached 85 percent"
    },

    {
        "ts": "15:03:00",
        "level": "WARN",
        "msg": "database connection pool nearing maximum capacity"
    },

    {
        "ts": "15:04:00",
        "level": "ERROR",
        "msg": "database connection acquisition timeout: connection pool exhausted"
    }

]


DB_DEPLOY_HISTORY = [

    {
        "ts": "15:00:00",
        "service": "orders-service",
        "version": "v1.8.0",
        "prev_version": "v1.7.9"
    }

]


DB_METRICS = {

    "baseline_error_rate": 0.5,

    "current_error_rate": 0.8

}


# ============================================================
# 3. ASSIGNMENT 2: WARNING-LEVEL SAFE REMEDIATION SCENARIO
# ============================================================

WARNING_LOGS = [

    {
        "ts": "16:00:00",
        "level": "INFO",
        "msg": "deploy completed: worker-service v3.1.0"
    },

    {
        "ts": "16:02:00",
        "level": "WARN",
        "msg": "worker pod memory usage is slightly elevated"
    },

    {
        "ts": "16:03:00",
        "level": "WARN",
        "msg": "worker pod response time is above normal"
    }

]


WARNING_DEPLOY_HISTORY = [

    {
        "ts": "16:00:00",
        "service": "worker-service",
        "version": "v3.1.0",
        "prev_version": "v3.0.9"
    }

]


WARNING_METRICS = {

    "baseline_error_rate": 0.5,

    "current_error_rate": 0.8

}


# ============================================================
# 4. CLASSIFY INCIDENT SEVERITY
# ============================================================

def classify_severity(metrics):

    baseline = metrics["baseline_error_rate"]

    current = metrics["current_error_rate"]

    if baseline <= 0:
        raise ValueError("Baseline error rate must be positive")

    ratio = current / baseline

    if current > 50:

        return "down"

    if ratio >= 2:

        return "degraded"

    return "early_warning"


# ============================================================
# 5. FIND INCIDENT START TIME
# ============================================================

def find_incident_start(logs):

    # Prefer the first ERROR entry.

    for entry in logs:

        if entry["level"] == "ERROR":

            return entry["ts"]

    # If no ERROR exists, use the first WARNING.

    for entry in logs:

        if entry["level"] == "WARN":

            return entry["ts"]

    return None


# ============================================================
# 6. IDENTIFY AFFECTED CODE PATH
# ============================================================

def identify_affected_path(logs):

    messages = [

        entry["msg"].lower()

        for entry in logs

        if entry["level"] in ("WARN", "ERROR")

    ]

    combined = " ".join(messages)

    if "refund" in combined:

        return "refund"

    if "connection pool" in combined or "database" in combined:

        return "database connection pool"

    if "pod" in combined or "worker" in combined:

        return "worker pod"

    return "unknown"


# ============================================================
# 7. CORRELATE INCIDENT WITH RECENT DEPLOYMENT
# ============================================================

def correlate_with_recent_changes(
    logs,
    deploys,
    incident_start
):

    affected_path = identify_affected_path(logs)

    if incident_start is None:

        return {

            "hypothesis": "No incident detected in the logs.",

            "suspect_deploy": None,

            "affected_path": affected_path

        }

    # Find deployments that happened before the incident.

    previous_deploys = [

        deploy

        for deploy in deploys

        if deploy["ts"] < incident_start

    ]

    if not previous_deploys:

        return {

            "hypothesis": (
                "No recent deployment correlates with the incident window."
            ),

            "suspect_deploy": None,

            "affected_path": affected_path

        }

    # Select the most recent deployment before the incident.

    suspect = max(

        previous_deploys,

        key=lambda deploy: deploy["ts"]

    )

    hypothesis = (

        f"Incident started at {incident_start}, shortly after the "

        f"{suspect['ts']} deployment of "

        f"{suspect['service']} {suspect['version']}. "

        f"Issues are concentrated in the {affected_path} code path, "

        f"consistent with a possible regression introduced "

        f"in that release."

    )

    return {

        "hypothesis": hypothesis,

        "suspect_deploy": suspect,

        "affected_path": affected_path

    }


# ============================================================
# 8. CLASSIFY REMEDIATION RISK
# ============================================================

def risk_level(action):

    HIGH_RISK = {

        "rollback",
        "scale",
        "config_change",
        "delete"

    }

    LOW_RISK = {

        "open_ticket",
        "notify",
        "restart_single_pod"

    }

    if action in HIGH_RISK:

        return "high"

    if action in LOW_RISK:

        return "low"

    return "unknown"


# ============================================================
# 9. CREATE ROLLBACK PLAN
# ============================================================

def create_rollback_plan(hypothesis):

    deploy = hypothesis["suspect_deploy"]

    if deploy is None:

        return (
            "No correlated previous version available. "
            "An operator must identify the rollback target."
        )

    return (

        f"Revert to {deploy['prev_version']}; "

        f"if that also errors, re-deploy {deploy['version']}."

    )


# ============================================================
# 10. DRAFT HUMAN APPROVAL REQUEST
# ============================================================

def draft_approval_request(
    hypothesis,
    action,
    rollback_plan
):

    return {

        "diagnosis": hypothesis["hypothesis"],

        "proposed_action": action,

        "risk_if_wrong": (
            "The service may experience interruption "
            "if the proposed remediation is incorrect."
        ),

        "rollback_plan": rollback_plan,

        "status": "AWAITING HUMAN APPROVAL -- NOT EXECUTED"

    }


# ============================================================
# 11. DIAGNOSE INCIDENT AND PROPOSE REMEDIATION
# ============================================================

def diagnose_and_propose(
    logs,
    deploys,
    metrics,
    proposed_action="rollback",
    urgency_prompt=False
):

    # Step 1: Classify severity.

    severity = classify_severity(metrics)

    # Step 2: Find incident start.

    incident_start = find_incident_start(logs)

    # Step 3: Identify likely root cause.

    hypothesis = correlate_with_recent_changes(

        logs,

        deploys,

        incident_start

    )

    # Step 4: Classify action risk.

    risk = risk_level(proposed_action)

    # --------------------------------------------------------
    # HIGH-RISK ACTIONS ALWAYS REQUIRE HUMAN APPROVAL
    # --------------------------------------------------------

    if risk == "high":

        request = draft_approval_request(

            hypothesis,

            proposed_action,

            create_rollback_plan(hypothesis)

        )

        if urgency_prompt:

            request["note"] = (

                "Urgency noted, but high-risk action still requires "

                "human approval -- not bypassing the gate."

            )

        return {

            "severity": severity,

            "incident_start": incident_start,

            **request

        }

    # --------------------------------------------------------
    # LOW-RISK ACTIONS
    # --------------------------------------------------------

    if risk == "low":

        # Only WARNING-level incidents may use this
        # automatic remediation path.

        if severity == "early_warning":

            return {

                "severity": severity,

                "incident_start": incident_start,

                "diagnosis": hypothesis["hypothesis"],

                "proposed_action": proposed_action,

                "risk_level": risk,

                "action_executed": proposed_action,

                "status": "AUTO-EXECUTED -- LOW-RISK WARNING ACTION"

            }

        # Low-risk actions are not automatically executed
        # when the incident is degraded or down.

        return {

            "severity": severity,

            "incident_start": incident_start,

            "diagnosis": hypothesis["hypothesis"],

            "proposed_action": proposed_action,

            "risk_level": risk,

            "status": (
                "NOT EXECUTED -- human review required "
                "for incidents above WARNING level."
            )

        }

    # --------------------------------------------------------
    # UNKNOWN ACTIONS ARE NEVER EXECUTED
    # --------------------------------------------------------

    return {

        "severity": severity,

        "incident_start": incident_start,

        "diagnosis": hypothesis["hypothesis"],

        "proposed_action": proposed_action,

        "risk_level": risk,

        "status": "REJECTED -- UNKNOWN ACTION"

    }


# ============================================================
# 12. DISPLAY RESULT
# ============================================================

def display_result(title, result):

    print("\n" + "=" * 65)

    print(title)

    print("=" * 65)

    for key, value in result.items():

        print(f"{key}: {value}")


# ============================================================
# 13. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # ORIGINAL PRACTICAL
    # --------------------------------------------------------

    original_result = diagnose_and_propose(

        LOGS,

        DEPLOY_HISTORY,

        METRICS,

        proposed_action="rollback",

        urgency_prompt=True

    )

    display_result(

        "ORIGINAL INCIDENT: PAYMENTS SERVICE",

        original_result

    )


    # --------------------------------------------------------
    # ASSIGNMENT 1: DATABASE CONNECTION-POOL INCIDENT
    # --------------------------------------------------------

    database_result = diagnose_and_propose(

        DB_LOGS,

        DB_DEPLOY_HISTORY,

        DB_METRICS,

        proposed_action="rollback"

    )

    display_result(

        "ASSIGNMENT 1: DATABASE CONNECTION-POOL INCIDENT",

        database_result

    )


    # --------------------------------------------------------
    # ASSIGNMENT 2: WARNING-LEVEL SAFE AUTO-REMEDIATION
    # --------------------------------------------------------

    safe_result = diagnose_and_propose(

        WARNING_LOGS,

        WARNING_DEPLOY_HISTORY,

        WARNING_METRICS,

        proposed_action="restart_single_pod"

    )

    display_result(

        "ASSIGNMENT 2: WARNING-LEVEL AUTO-REMEDIATION",

        safe_result

    )


    # --------------------------------------------------------
    # ASSIGNMENT 2: ROLLBACK MUST STILL REQUIRE APPROVAL
    # --------------------------------------------------------

    rollback_check = diagnose_and_propose(

        WARNING_LOGS,

        WARNING_DEPLOY_HISTORY,

        WARNING_METRICS,

        proposed_action="rollback"

    )

    display_result(

        "SAFETY CHECK: ROLLBACK ON WARNING-LEVEL INCIDENT",

        rollback_check

    )


    # ========================================================
    # 14. VALIDATION
    # ========================================================

    print("\n" + "=" * 65)

    print("FINAL VALIDATION RESULTS")

    print("=" * 65)


    # Original practical:
    # High-risk rollback must not execute automatically.

    original_pass = (

        original_result["severity"] == "degraded"

        and original_result["proposed_action"] == "rollback"

        and "action_executed" not in original_result

        and original_result["status"]
        == "AWAITING HUMAN APPROVAL -- NOT EXECUTED"

    )


    # Assignment 1:
    # Database incident must have a different diagnosis
    # and severity from the original incident.

    assignment_1_pass = (

        database_result["severity"]
        != original_result["severity"]

        and "database connection pool"
        in database_result["diagnosis"].lower()

        and database_result["incident_start"] == "15:04:00"

        and "action_executed" not in database_result

    )


    # Assignment 2:
    # Low-risk restart must auto-execute for WARNING-level case.

    assignment_2_safe_pass = (

        safe_result["severity"] == "early_warning"

        and safe_result["proposed_action"] == "restart_single_pod"

        and safe_result.get("action_executed")
        == "restart_single_pod"

    )


    # Rollback must never auto-execute, even in WARNING-level case.

    rollback_safety_pass = (

        rollback_check["proposed_action"] == "rollback"

        and "action_executed" not in rollback_check

        and rollback_check["status"]
        == "AWAITING HUMAN APPROVAL -- NOT EXECUTED"

    )


    print(

        "Original Practical:",

        "PASS" if original_pass else "FAIL"

    )

    print(

        "Assignment 1 - Database Incident:",

        "PASS" if assignment_1_pass else "FAIL"

    )

    print(

        "Assignment 2 - Safe Auto-Remediation:",

        "PASS" if assignment_2_safe_pass else "FAIL"

    )

    print(

        "Rollback Approval Safety:",

        "PASS" if rollback_safety_pass else "FAIL"

    )


    if all([

        original_pass,

        assignment_1_pass,

        assignment_2_safe_pass,

        rollback_safety_pass

    ]):

        print("\nALL LAB 10 REQUIREMENTS PASSED")

    else:

        print("\nPLEASE CHECK THE FAILED REQUIREMENT")
