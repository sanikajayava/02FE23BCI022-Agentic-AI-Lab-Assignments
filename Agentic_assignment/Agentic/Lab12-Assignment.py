
"""
LAB 12: SAFETY, EVALUATION, AND GOVERNANCE

Original Practical:
Production-Change Agent with six governance controls.

Assignment 1:
Cost-category control, budget threshold, finance approval,
and rejection of missing cost estimates.

Assignment 2:
Mandatory re-evaluation after every five successful proposals.
The sixth proposal is blocked until evaluate() is called again.
"""

import math


# ============================================================
# CONFIGURATION
# ============================================================

REGRESSION_SUITE_RESULT = {
    "passed": 9,
    "total": 10
}

DEFAULT_BUDGET_THRESHOLD = 1000
MAX_PROPOSALS_PER_EVALUATION = 5


# ============================================================
# PRODUCTION CHANGE AGENT
# ============================================================

class ProdChangeAgent:

    def __init__(
        self,
        budget_threshold=DEFAULT_BUDGET_THRESHOLD,
        reevaluate_every=MAX_PROPOSALS_PER_EVALUATION
    ):

        # 1. Permissions: least privilege
        self.permissions = {
            "can_write": "staging_only"
        }

        self.audit_log = []
        self.evaluated = False

        # Assignment 1: budget control
        self.budget_threshold = budget_threshold

        # Assignment 2: proposal tracking
        self.reevaluate_every = reevaluate_every
        self.total_proposals = 0
        self.proposals_since_evaluation = 0
        self.evaluation_required = False

    # ========================================================
    # 2. EVALUATION CONTROL
    # ========================================================

    def evaluate(self):

        pass_rate = (
            REGRESSION_SUITE_RESULT["passed"]
            / REGRESSION_SUITE_RESULT["total"]
        )

        previous_count = self.proposals_since_evaluation

        self.evaluated = pass_rate >= 0.8

        # Reset counter after evaluation
        self.proposals_since_evaluation = 0

        self.evaluation_required = not self.evaluated

        self._log(
            "evaluation",
            {
                "pass_rate": pass_rate,
                "passed_gate": self.evaluated,
                "previous_proposals_since_evaluation": previous_count,
                "total_proposals": self.total_proposals
            }
        )

        return self.evaluated

    # ========================================================
    # 3. AUDIT LOGGING
    # ========================================================

    def _log(self, step, data):

        self.audit_log.append({
            "step": step,
            "data": data
        })

    # ========================================================
    # 4. REJECTION HELPER
    # ========================================================

    def _reject(self, reason, message):

        self._log(
            "propose_change",
            {
                "rejected": True,
                "reason": reason
            }
        )

        return {
            "rejected": True,
            "reason": message
        }

    # ========================================================
    # 5. PROPOSE CHANGE
    # ========================================================

    def propose_change(
        self,
        diagnosis,
        action,
        rollback_plan,
        privacy_scrubbed,
        cost_estimate=None,
        finance_approved=False
    ):

        # ASSIGNMENT 2: MANDATORY RE-EVALUATION

        if self.evaluation_required:

            return self._reject(
                "mandatory re-evaluation required",
                (
                    f"Blocked: {self.proposals_since_evaluation} proposals "
                    f"have been made. Call evaluate() again before making "
                    f"another proposal."
                )
            )

        # Evaluation gate
        if not self.evaluated:

            return self._reject(
                "agent not evaluated",
                "Evaluation gate not passed; cannot propose changes."
            )

        # 1. Permission check
        if self.permissions["can_write"] != "staging_only":

            raise PermissionError(
                "Agent must not hold direct production write access."
            )

        # 2. Privacy check
        if not privacy_scrubbed:

            return self._reject(
                "unscrubbed customer data in input",
                (
                    "Diagnostic input was not privacy-scrubbed; "
                    "rejecting."
                )
            )

        # 3. Rollback check
        if not rollback_plan:

            return self._reject(
                "no rollback plan supplied",
                "No rollback plan defined; rejecting proposal."
            )

        # ====================================================
        # ASSIGNMENT 1: COST-CATEGORY CONTROL
        # ====================================================

        # Reject missing cost estimate
        if cost_estimate is None:

            return self._reject(
                "missing cost estimate",
                "Cost estimate is required; rejecting proposal."
            )

        # Validate cost estimate
        if (
            isinstance(cost_estimate, bool)
            or not isinstance(cost_estimate, (int, float))
            or not math.isfinite(cost_estimate)
            or cost_estimate < 0
        ):

            return self._reject(
                "invalid cost estimate",
                (
                    "Cost estimate must be a valid "
                    "non-negative number."
                )
            )

        # Reject cost exceeding budget without finance approval
        if (
            cost_estimate > self.budget_threshold
            and finance_approved is not True
        ):

            return self._reject(
                "budget threshold exceeded without finance approval",
                (
                    f"Estimated cost {cost_estimate} exceeds budget "
                    f"threshold {self.budget_threshold}. "
                    f"Finance approval is required."
                )
            )

        # ====================================================
        # HUMAN APPROVAL REQUEST
        # ====================================================

        request = {
            "diagnosis": diagnosis,
            "proposed_action": action,
            "rollback_plan": rollback_plan,
            "category": "production",
            "requires_approval": True,
            "cost_estimate": cost_estimate,
            "budget_threshold": self.budget_threshold,
            "finance_approved": finance_approved
        }

        self._log(
            "approval_requested",
            request
        )

        # Count only valid proposals submitted for approval
        self.total_proposals += 1
        self.proposals_since_evaluation += 1

        # Require re-evaluation after five proposals
        if (
            self.proposals_since_evaluation
            >= self.reevaluate_every
        ):

            self.evaluation_required = True

            self._log(
                "reevaluation_required",
                {
                    "proposal_count": self.proposals_since_evaluation,
                    "message": (
                        "Five proposals completed. "
                        "Re-evaluation required."
                    )
                }
            )

        return request

    # ========================================================
    # 6. HUMAN APPROVAL AND PRIVILEGED DEPLOYMENT
    # ========================================================

    def apply_after_approval(self, request, human_decision):

        self._log(
            "human_decision",
            {
                "decision": human_decision
            }
        )

        if human_decision != "approved":

            return {
                "applied": False,
                "reason": "not approved by human"
            }

        # Agent never directly applies production changes
        return {
            "applied": False,
            "handed_off_to": "privileged_deploy_process",
            "note": (
                "This agent never holds production write access; "
                "a separate privileged process performs the "
                "actual apply step."
            )
        }


# ============================================================
# HELPER: DISPLAY AUDIT LOG
# ============================================================

def display_audit_log(agent):

    print("\n=== Full audit log ===")

    for entry in agent.audit_log:
        print(entry)


# ============================================================
# ORIGINAL LAB 12 PRACTICAL
# ============================================================

def run_original_practical():

    print("\n" + "=" * 65)
    print("ORIGINAL LAB 12 PRACTICAL")
    print("=" * 65)

    agent = ProdChangeAgent()

    print("\n=== Control 2: Evaluation gate ===")

    print(
        f"Evaluated and passed: {agent.evaluate()}"
    )

    # Attempt 1: Missing rollback plan
    print(
        "\n=== Attempt 1: missing rollback plan "
        "(should be rejected) ==="
    )

    result = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan=None,
        privacy_scrubbed=True,
        cost_estimate=500
    )

    print(result)

    # Attempt 2: Unscrubbed customer data
    print(
        "\n=== Attempt 2: unscrubbed customer data "
        "(should be rejected) ==="
    )

    result = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan="Revert config X to v3 if v4 also leaks.",
        privacy_scrubbed=False,
        cost_estimate=500
    )

    print(result)

    # Attempt 3: Valid proposal
    print("\n=== Attempt 3: complete, valid proposal ===")

    request = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan="Revert config X to v3 if v4 also leaks.",
        privacy_scrubbed=True,
        cost_estimate=500
    )

    print(request)

    # Human approval
    print(
        "\n=== Human approves; a SEPARATE privileged "
        "process applies it ==="
    )

    outcome = agent.apply_after_approval(
        request,
        human_decision="approved"
    )

    print(outcome)

    # Adversarial permission test
    print(
        "\n=== Adversarial test: agent attempts "
        "direct production write ==="
    )

    try:

        agent.permissions["can_write"] = "production"

        agent.propose_change(
            diagnosis="test",
            action="test",
            rollback_plan="test rollback",
            privacy_scrubbed=True,
            cost_estimate=100
        )

    except PermissionError as error:

        print(f"Blocked as expected: {error}")

    display_audit_log(agent)

    return True


# ============================================================
# ASSIGNMENT 1: COST-CATEGORY CONTROL
# ============================================================

def run_assignment_1():

    print("\n\n" + "=" * 65)
    print("ASSIGNMENT 1: COST-CATEGORY CONTROL")
    print("=" * 65)

    agent = ProdChangeAgent(
        budget_threshold=1000
    )

    print("\nBudget threshold:", agent.budget_threshold)

    print("\n=== Evaluation gate ===")

    print("Evaluated and passed:", agent.evaluate())

    # Test 1: Within budget
    print("\n=== Test 1: Cost within budget ===")

    result1 = agent.propose_change(
        diagnosis="Memory usage is high.",
        action="update memory configuration",
        rollback_plan="Restore previous memory configuration.",
        privacy_scrubbed=True,
        cost_estimate=500,
        finance_approved=False
    )

    print(result1)

    # Test 2: Above budget without approval
    print(
        "\n=== Test 2: Cost exceeds budget "
        "without finance approval ==="
    )

    result2 = agent.propose_change(
        diagnosis="Database performance issue.",
        action="upgrade database infrastructure",
        rollback_plan="Restore previous database configuration.",
        privacy_scrubbed=True,
        cost_estimate=1500,
        finance_approved=False
    )

    print(result2)

    # Test 3: Above budget with approval
    print(
        "\n=== Test 3: Cost exceeds budget "
        "with finance approval ==="
    )

    result3 = agent.propose_change(
        diagnosis="Database performance issue.",
        action="upgrade database infrastructure",
        rollback_plan="Restore previous database configuration.",
        privacy_scrubbed=True,
        cost_estimate=1500,
        finance_approved=True
    )

    print(result3)

    # Test 4: Missing cost estimate
    print(
        "\n=== Test 4: Adversarial test - "
        "missing cost estimate ==="
    )

    result4 = agent.propose_change(
        diagnosis="Unknown infrastructure issue.",
        action="change production configuration",
        rollback_plan="Restore the previous configuration.",
        privacy_scrubbed=True
        # Cost estimate intentionally omitted
    )

    print(result4)

    # Validation
    test1_passed = (
        isinstance(result1, dict)
        and result1.get("requires_approval") is True
    )

    test2_passed = (
        result2.get("rejected") is True
    )

    test3_passed = (
        isinstance(result3, dict)
        and result3.get("requires_approval") is True
        and result3.get("finance_approved") is True
    )

    test4_passed = (
        result4.get("rejected") is True
        and "Cost estimate is required"
        in result4.get("reason", "")
    )

    print("\n=== ASSIGNMENT 1 VALIDATION ===")

    print(
        "Within-budget proposal:",
        "PASS" if test1_passed else "FAIL"
    )

    print(
        "Over-budget proposal rejected without finance approval:",
        "PASS" if test2_passed else "FAIL"
    )

    print(
        "Over-budget proposal accepted with finance approval:",
        "PASS" if test3_passed else "FAIL"
    )

    print(
        "Missing cost estimate rejected:",
        "PASS" if test4_passed else "FAIL"
    )

    display_audit_log(agent)

    return all([
        test1_passed,
        test2_passed,
        test3_passed,
        test4_passed
    ])


# ============================================================
# ASSIGNMENT 2: MANDATORY RE-EVALUATION AFTER FIVE PROPOSALS
# ============================================================

def run_assignment_2():

    print("\n\n" + "=" * 65)
    print("ASSIGNMENT 2: MANDATORY RE-EVALUATION")
    print("=" * 65)

    agent = ProdChangeAgent(
        budget_threshold=1000,
        reevaluate_every=5
    )

    # Initial evaluation
    print("\n=== Initial evaluation ===")

    print(
        "Evaluated and passed:",
        agent.evaluate()
    )

    # Submit five valid proposals
    print("\n=== Submitting five valid proposals ===")

    first_five_passed = True

    for number in range(1, 6):

        print(f"\n--- Proposal {number} ---")

        result = agent.propose_change(
            diagnosis=f"System issue detected for proposal {number}.",
            action=f"Apply safe configuration change {number}.",
            rollback_plan=(
                f"Restore configuration before change {number}."
            ),
            privacy_scrubbed=True,
            cost_estimate=200,
            finance_approved=False
        )

        print(result)

        if (
            not isinstance(result, dict)
            or result.get("requires_approval") is not True
        ):

            first_five_passed = False

    print("\nTotal proposals:", agent.total_proposals)

    print(
        "Proposals since evaluation:",
        agent.proposals_since_evaluation
    )

    print(
        "Re-evaluation required:",
        agent.evaluation_required
    )

    # Sixth proposal before re-evaluation
    print(
        "\n=== Sixth proposal: should be blocked "
        "until re-evaluation ==="
    )

    sixth_attempt_before_evaluation = agent.propose_change(
        diagnosis="Another system issue detected.",
        action="Apply configuration change number 6.",
        rollback_plan="Restore the previous configuration.",
        privacy_scrubbed=True,
        cost_estimate=200,
        finance_approved=False
    )

    print(sixth_attempt_before_evaluation)

    # Corrected validation: case-insensitive message comparison
    sixth_reason = sixth_attempt_before_evaluation.get(
        "reason", ""
    )

    sixth_blocked = (
        sixth_attempt_before_evaluation.get("rejected") is True
        and "call evaluate()" in sixth_reason.lower()
    )

    # Re-evaluate after five proposals
    print("\n=== Re-evaluation after five proposals ===")

    reevaluation_passed = agent.evaluate()

    print(
        "Re-evaluated and passed:",
        reevaluation_passed
    )

    print(
        "Proposals since evaluation:",
        agent.proposals_since_evaluation
    )

    # Sixth proposal after re-evaluation
    print(
        "\n=== Sixth proposal after re-evaluation "
        "(should be accepted for approval) ==="
    )

    sixth_attempt_after_evaluation = agent.propose_change(
        diagnosis="Another system issue detected.",
        action="Apply configuration change number 6.",
        rollback_plan="Restore the previous configuration.",
        privacy_scrubbed=True,
        cost_estimate=200,
        finance_approved=False
    )

    print(sixth_attempt_after_evaluation)

    sixth_allowed = (
        isinstance(sixth_attempt_after_evaluation, dict)
        and sixth_attempt_after_evaluation.get(
            "requires_approval"
        ) is True
    )

    # Assignment 2 validation
    print("\n=== ASSIGNMENT 2 VALIDATION ===")

    print(
        "First five proposals accepted:",
        "PASS" if first_five_passed else "FAIL"
    )

    print(
        "Sixth proposal blocked before re-evaluation:",
        "PASS" if sixth_blocked else "FAIL"
    )

    print(
        "Re-evaluation passed:",
        "PASS" if reevaluation_passed else "FAIL"
    )

    print(
        "Sixth proposal allowed after re-evaluation:",
        "PASS" if sixth_allowed else "FAIL"
    )

    print(
        "Total successful proposals:",
        agent.total_proposals
    )

    display_audit_log(agent)

    return all([
        first_five_passed,
        sixth_blocked,
        reevaluation_passed,
        sixth_allowed
    ])


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    original_passed = run_original_practical()

    assignment1_passed = run_assignment_1()

    assignment2_passed = run_assignment_2()

    print("\n\n" + "=" * 65)
    print("FINAL LAB 12 VALIDATION")
    print("=" * 65)

    print(
        "Original Practical:",
        "PASS" if original_passed else "FAIL"
    )

    print(
        "Assignment 1 - Cost-Category Control:",
        "PASS" if assignment1_passed else "FAIL"
    )

    print(
        "Assignment 2 - Mandatory Re-Evaluation:",
        "PASS" if assignment2_passed else "FAIL"
    )

    if (
        original_passed
        and assignment1_passed
        and assignment2_passed
    ):

        print("\nALL LAB 12 REQUIREMENTS PASSED")

    else:

        print("\nSOME LAB 12 REQUIREMENTS FAILED")
