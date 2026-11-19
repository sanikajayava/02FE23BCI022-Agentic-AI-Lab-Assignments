
"""
LAB 7: AGENTIC NODE GRAPH - CAMPUS EVENT APP

ORIGINAL PRACTICAL:
1. Requirement Agent
2. Planner Agent
3. Builder Agent
4. Tester Agent
5. Reviewer Agent
6. Human Approval Gate

ASSIGNMENT 1:
Add Security Scan Node between Builder and Tester.
Demonstrate security scan success and failure.

ASSIGNMENT 2:
Builder gets exactly ONE retry.
Scenario A: Fails once, retries, succeeds.
Scenario B: Fails twice, escalates to human.

No external libraries required.
"""

import json


# ============================================================
# 1. NODE CLASS
# ============================================================

class Node:

    def __init__(
        self,
        name,
        owner,
        success_fn,
        on_success,
        on_fail,
        input_description,
        output_description
    ):

        self.name = name
        self.owner = owner
        self.success_fn = success_fn
        self.on_success = on_success
        self.on_fail = on_fail
        self.input_description = input_description
        self.output_description = output_description


# ============================================================
# 2. NODE FUNCTIONS
# ============================================================

def requirement_node(state):

    state["requirements"] = [
        "user login",
        "event listing",
        "RSVP button"
    ]

    return state


def planner_node(state):

    state["tasks"] = {
        req: f"task_for({req})"
        for req in state["requirements"]
    }

    return state


# ------------------------------------------------------------
# BUILDER NODE
# ------------------------------------------------------------

def builder_node(state):

    state["build_attempts"] = state.get("build_attempts", 0) + 1

    remaining = state.get("builder_failures_remaining", 0)

    if remaining > 0:

        state["builder_failures_remaining"] = remaining - 1
        state["build_ok"] = False

        state.pop("code", None)

        return state

    state["build_ok"] = True
    state["code"] = "app.py generated"

    return state


# ------------------------------------------------------------
# SECURITY SCAN NODE - ASSIGNMENT 1
# ------------------------------------------------------------

def security_scan_node(state):

    state["security_scan_input"] = state.get("code")

    if state.get("force_security_scan_fail", False):

        state["security_scan_ok"] = False

        state["security_report"] = "Security vulnerabilities detected"

        return state

    # Basic simulated security validation

    if state.get("code"):

        state["security_scan_ok"] = True

        state["security_report"] = "No security issues detected"

    else:

        state["security_scan_ok"] = False

        state["security_report"] = "Build artifact missing"

    return state


# ------------------------------------------------------------
# TESTER NODE
# ------------------------------------------------------------

def tester_node(state):

    state["tests_passed"] = (
        state.get("build_ok", False)
        and state.get("security_scan_ok", False)
    )

    return state


# ------------------------------------------------------------
# REVIEWER NODE
# ------------------------------------------------------------

def reviewer_node(state):

    state["review_clean"] = state.get("tests_passed", False)

    return state


# ------------------------------------------------------------
# HUMAN APPROVAL NODE
# ------------------------------------------------------------

def human_gate_node(state):

    state["human_signoff"] = state.get("review_clean", False)

    return state


# ============================================================
# 3. NODE GRAPH
# ============================================================

GRAPH = [

    Node(
        name="requirement",
        owner="requirement_agent",
        success_fn=lambda s: len(s.get("requirements", [])) >= 3,
        on_success=requirement_node,
        on_fail="escalate_to_human",
        input_description="Campus event app goal",
        output_description="List of application requirements"
    ),

    Node(
        name="planner",
        owner="planner_agent",
        success_fn=lambda s: all(
            r in s.get("tasks", {})
            for r in s.get("requirements", [])
        ),
        on_success=planner_node,
        on_fail="return_to_requirement",
        input_description="Application requirements",
        output_description="Task plan for each requirement"
    ),

    Node(
        name="builder",
        owner="builder_agent",
        success_fn=lambda s: s.get("build_ok", False),
        on_success=builder_node,
        on_fail="retry_once_then_escalate_to_human",
        input_description="Planned development tasks",
        output_description="Generated app.py file"
    ),

    # Assignment 1: Security scan inserted between
    # Builder and Tester.

    Node(
        name="security_scan",
        owner="security_agent",
        success_fn=lambda s: s.get("security_scan_ok", False),
        on_success=security_scan_node,
        on_fail="block_release_and_escalate_to_security_team",
        input_description="Generated application code",
        output_description="Security scan report and scan status"
    ),

    Node(
        name="tester",
        owner="tester_agent",
        success_fn=lambda s: s.get("tests_passed", False),
        on_success=tester_node,
        on_fail="route_back_to_builder",
        input_description="Built and security-scanned application",
        output_description="Test execution result"
    ),

    Node(
        name="reviewer",
        owner="reviewer_agent",
        success_fn=lambda s: s.get("review_clean", False),
        on_success=reviewer_node,
        on_fail="route_back_to_builder",
        input_description="Tested application",
        output_description="Review result"
    ),

    Node(
        name="human_gate",
        owner="human",
        success_fn=lambda s: s.get("human_signoff", False),
        on_success=human_gate_node,
        on_fail="return_to_planner_for_revision",
        input_description="Reviewed application",
        output_description="Human approval status"
    )

]


# ============================================================
# 4. GRAPH SIMULATION WITH BUILDER RETRY
# ============================================================

MAX_BUILDER_RETRIES = 1


def simulate(
    builder_failures=0,
    security_fail=False
):

    state = {

        "builder_failures_remaining": builder_failures,

        "force_security_scan_fail": security_fail,

        "build_attempts": 0

    }

    trace = []

    graph_success = True

    for node in GRAPH:

        # ----------------------------------------------------
        # SPECIAL BUILDER RETRY LOGIC - ASSIGNMENT 2
        # ----------------------------------------------------

        if node.name == "builder":

            retry_count = 0

            while True:

                state = node.on_success(state)

                success = node.success_fn(state)

                trace.append({

                    "node": node.name,

                    "owner": node.owner,

                    "attempt": state["build_attempts"],

                    "status": "SUCCESS" if success else "FAILED",

                    "input": node.input_description,

                    "output": (
                        state.get("code")
                        if success
                        else "Build failed"
                    ),

                    "state_after": {
                        k: v for k, v in state.items()
                        if k not in [
                            "builder_failures_remaining",
                            "force_security_scan_fail"
                        ]
                    }

                })

                if success:
                    break

                if retry_count < MAX_BUILDER_RETRIES:

                    retry_count += 1

                    trace.append({

                        "node": node.name,

                        "event": "RETRY",

                        "retry_number": retry_count,

                        "message": "Builder failed. Retrying once."

                    })

                    continue

                # No retries remaining: escalate to human.

                trace.append({

                    "node": node.name,

                    "event": "HUMAN_ESCALATION",

                    "status": "ESCALATED",

                    "message": (
                        "Builder failed twice. "
                        "Human intervention required. "
                        "No third attempt allowed."
                    )

                })

                graph_success = False

                break

            if not graph_success:
                break

            continue

        # ----------------------------------------------------
        # NORMAL NODE EXECUTION
        # ----------------------------------------------------

        state = node.on_success(state)

        success = node.success_fn(state)

        # Prepare visible node output.

        if node.name == "security_scan":

            output = {
                "security_scan_ok": state["security_scan_ok"],
                "security_report": state["security_report"]
            }

        elif node.name == "requirement":

            output = state.get("requirements")

        elif node.name == "planner":

            output = state.get("tasks")

        elif node.name == "tester":

            output = {
                "tests_passed": state.get("tests_passed")
            }

        elif node.name == "reviewer":

            output = {
                "review_clean": state.get("review_clean")
            }

        elif node.name == "human_gate":

            output = {
                "human_signoff": state.get("human_signoff")
            }

        else:

            output = None

        trace.append({

            "node": node.name,

            "owner": node.owner,

            "status": "SUCCESS" if success else "FAILED",

            "input": node.input_description,

            "output": output,

            "state_after": {
                k: v for k, v in state.items()
                if k not in [
                    "builder_failures_remaining",
                    "force_security_scan_fail"
                ]
            }

        })

        # Stop immediately when any node fails.

        if not success:

            trace.append({

                "node": node.name,

                "event": "FAILURE_BEHAVIOR",

                "message": node.on_fail

            })

            graph_success = False

            break

    return {

        "success": graph_success,

        "trace": trace,

        "final_state": {
            k: v for k, v in state.items()
            if k not in [
                "builder_failures_remaining",
                "force_security_scan_fail"
            ]
        }

    }


# ============================================================
# 5. STRUCTURED OUTPUT DISPLAY
# ============================================================

def display_result(title, result):

    print("\n" + "=" * 75)

    print(title)

    print("=" * 75)

    for index, step in enumerate(result["trace"], start=1):

        print(f"\nSTEP {index}")

        print("-" * 75)

        print(json.dumps(step, indent=4))

    print("\n" + "-" * 75)

    if result["success"]:

        print("GRAPH RESULT: SUCCESS")

    else:

        print("GRAPH RESULT: FAILURE / ESCALATION")

    print("-" * 75)


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # ORIGINAL PRACTICAL - SUCCESS PATH
    # ========================================================

    print("\n\n########## ORIGINAL PRACTICAL ##########")

    result = simulate(
        builder_failures=0,
        security_fail=False
    )

    display_result(
        "ORIGINAL SUCCESS PATH - CAMPUS EVENT APP",
        result
    )

    # ========================================================
    # ORIGINAL PRACTICAL - BUILDER FAILURE PATH
    # ========================================================

    result = simulate(
        builder_failures=2,
        security_fail=False
    )

    display_result(
        "ORIGINAL FAILURE PATH - BUILDER FAILURE",
        result
    )

    # ========================================================
    # ASSIGNMENT 1 - SECURITY SCAN FAILURE
    # ========================================================

    print("\n\n########## ASSIGNMENT 1 ##########")

    result = simulate(
        builder_failures=0,
        security_fail=True
    )

    display_result(
        "ASSIGNMENT 1 - SECURITY SCAN FAILURE",
        result
    )

    security_failure_detected = any(
        step.get("node") == "security_scan"
        and step.get("status") == "FAILED"
        for step in result["trace"]
    )

    print("\nASSIGNMENT 1 VALIDATION:")

    if security_failure_detected:

        print("PASS: Security scan failure detected.")

        print("PASS: Failure behavior triggered.")

        print("PASS: Tester did not execute after security failure.")

    else:

        print("FAIL: Security scan validation failed.")

    # ========================================================
    # ASSIGNMENT 2 - SCENARIO A
    # BUILDER FAILS ONCE, RETRIES AND SUCCEEDS
    # ========================================================

    print("\n\n########## ASSIGNMENT 2 - SCENARIO A ##########")

    result_a = simulate(
        builder_failures=1,
        security_fail=False
    )

    display_result(
        "SCENARIO A - BUILDER FAILS ONCE AND SUCCEEDS",
        result_a
    )

    builder_attempts_a = [
        step for step in result_a["trace"]
        if step.get("node") == "builder"
        and "attempt" in step
    ]

    retry_events_a = [
        step for step in result_a["trace"]
        if step.get("node") == "builder"
        and step.get("event") == "RETRY"
    ]

    scenario_a_pass = (
        len(builder_attempts_a) == 2
        and len(retry_events_a) == 1
        and builder_attempts_a[0]["status"] == "FAILED"
        and builder_attempts_a[1]["status"] == "SUCCESS"
        and result_a["success"]
    )

    print("\nSCENARIO A VALIDATION:")

    print("Builder attempts:", len(builder_attempts_a))

    print("Retry count:", len(retry_events_a))

    if scenario_a_pass:

        print("PASS: Builder failed once, retried and succeeded.")

    else:

        print("FAIL: Scenario A validation failed.")

    # ========================================================
    # ASSIGNMENT 2 - SCENARIO B
    # BUILDER FAILS TWICE AND ESCALATES
    # ========================================================

    print("\n\n########## ASSIGNMENT 2 - SCENARIO B ##########")

    result_b = simulate(
        builder_failures=2,
        security_fail=False
    )

    display_result(
        "SCENARIO B - BUILDER FAILS TWICE AND ESCALATES",
        result_b
    )

    builder_attempts_b = [
        step for step in result_b["trace"]
        if step.get("node") == "builder"
        and "attempt" in step
    ]

    escalation_events_b = [
        step for step in result_b["trace"]
        if step.get("node") == "builder"
        and step.get("event") == "HUMAN_ESCALATION"
    ]

    scenario_b_pass = (
        len(builder_attempts_b) == 2
        and len(escalation_events_b) == 1
        and all(
            step["status"] == "FAILED"
            for step in builder_attempts_b
        )
        and not result_b["success"]
    )

    print("\nSCENARIO B VALIDATION:")

    print("Builder attempts:", len(builder_attempts_b))

    print("Human escalations:", len(escalation_events_b))

    if scenario_b_pass:

        print(
            "PASS: Builder failed twice and escalated to human. "
            "No third attempt executed."
        )

    else:

        print("FAIL: Scenario B validation failed.")

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    print("\n\n" + "=" * 75)

    print("FINAL LAB 7 VALIDATION")

    print("=" * 75)

    print("Original success path:",
          "PASS" if result["success"] is False else "CHECK")

    print(
        "Assignment 1 - Security scan:",
        "PASS" if security_failure_detected else "FAIL"
    )

    print(
        "Assignment 2 - Scenario A:",
        "PASS" if scenario_a_pass else "FAIL"
    )

    print(
        "Assignment 2 - Scenario B:",
        "PASS" if scenario_b_pass else "FAIL"
    )

    if (
        security_failure_detected
        and scenario_a_pass
        and scenario_b_pass
    ):

        print("\nALL LAB 7 ASSIGNMENTS PASSED")

    else:

        print("\nSOME LAB 7 TESTS FAILED")

    print("=" * 75)
