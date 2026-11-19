
import json

# ============================================================
# LAB 1: AGENT VS CHATBOT - STUDY PLANNER
#
# Original functionality:
#   Goal -> Plan -> Act -> Observe -> Revise
#
# Assignment 1:
#   Two independent rounds of feedback.
#   Both revisions mutate the SAME plan object.
#
# Assignment 2:
#   Detect conflicts involving multiple busy days.
#   Report conflicts before generating the final plan.
# ============================================================

# -------------------- SIMULATED INPUTS ----------------------

SIMULATED_ANSWERS = {
    "subjects": [
        "Data Structures",
        "Operating Systems",
        "AI Agents"
    ],
    "hours_per_day": 2,
    "unavailable_days": ["Sunday"]
}

# Existing schedule contains TWO busy days
SIMULATED_EXISTING_SCHEDULE = {
    "busy_days": ["Wednesday", "Thursday"]
}

# Simulated user response to the detected conflict
# The user agrees to make both busy days unavailable.
SIMULATED_CONFLICT_RESOLUTION = ["Wednesday", "Thursday"]

# Assignment 1: Two independent feedback rounds
SIMULATED_FEEDBACK_ROUNDS = [
    "Move Tuesday's session to the evening.",
    "Make Friday's session shorter, only one hour."
]

# -------------------- STUDY PLANNER AGENT -------------------

class StudyPlannerAgent:

    def __init__(self, existing_schedule):

        # Goal represented as structured data
        self.goal = {
            "subjects": None,
            "hours_per_day": None,
            "unavailable_days": None,
            "schedule_generated": False
        }

        self.existing_schedule = existing_schedule
        self.plan = None
        self.log = []

        # Store detected conflicts
        self.conflicts = []

    # --------------------------------------------------------
    # GOAL CHECK
    # --------------------------------------------------------

    def satisfied(self):
        return self.goal["schedule_generated"] is True

    # --------------------------------------------------------
    # PLANNER: DECIDE THE NEXT STEP
    # --------------------------------------------------------

    def next_step(self):

        for field in (
            "subjects",
            "hours_per_day",
            "unavailable_days"
        ):

            if self.goal[field] is None:
                return ("ask", field)

        return ("generate_plan", None)

    # --------------------------------------------------------
    # TOOL: READ EXISTING SCHEDULE
    # --------------------------------------------------------

    def read_existing_schedule(self):

        result = self.existing_schedule

        if "error" in result:
            raise RuntimeError(
                f"Tool error: {result['error']}"
            )

        return result

    # --------------------------------------------------------
    # ASSIGNMENT 2: DETECT SCHEDULING CONFLICTS
    # --------------------------------------------------------

    def detect_conflicts(self, busy_schedule):

        busy_days = busy_schedule.get("busy_days", [])

        unavailable_days = self.goal["unavailable_days"]

        # A conflict exists when a busy day has not been
        # included in the student's unavailable days.
        self.conflicts = [
            day for day in busy_days
            if day not in unavailable_days
        ]

        if self.conflicts:

            message = (
                "SCHEDULING CONFLICT DETECTED!\n"
                "The following days are already busy: "
                + ", ".join(self.conflicts)
                + "\nThese days are not included in your "
                  "unavailable days."
            )

            print("\n" + "=" * 55)
            print(message)
            print("The plan will NOT be finalized until "
                  "these conflicts are resolved.")
            print("=" * 55)

            self.log.append({
                "iteration": len(self.log) + 1,
                "planned": "check existing schedule for conflicts",
                "action": "detected scheduling conflicts",
                "observed": {
                    "busy_days": busy_days,
                    "unavailable_days": unavailable_days,
                    "conflicting_days": self.conflicts
                },
                "stopped": False,
                "status": "conflict_detected"
            })

            return False

        print("\nNo scheduling conflicts detected.")

        return True

    # --------------------------------------------------------
    # ASSIGNMENT 2: RESOLVE SCHEDULING CONFLICTS
    # --------------------------------------------------------

    def resolve_conflicts(self):

        if not self.conflicts:
            return

        print("\nResolving conflicts...")

        # Simulated user confirmation.
        # In an interactive version, these days can be
        # collected using input().

        approved_days = SIMULATED_CONFLICT_RESOLUTION

        for day in self.conflicts:

            if day in approved_days:

                if day not in self.goal["unavailable_days"]:

                    self.goal["unavailable_days"].append(day)

                    print(
                        f"Resolved: {day} added to "
                        "unavailable days."
                    )

            else:

                raise RuntimeError(
                    f"Conflict on {day} was not resolved. "
                    "The study plan cannot be finalized."
                )

        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "resolve detected scheduling conflicts",
            "action": "updated unavailable days after user confirmation",
            "observed": {
                "resolved_days": self.conflicts,
                "updated_unavailable_days":
                    self.goal["unavailable_days"]
            },
            "stopped": False,
            "status": "conflicts_resolved"
        })

        # Verify that all busy days are now unavailable.
        unresolved = [
            day for day in self.existing_schedule.get("busy_days", [])
            if day not in self.goal["unavailable_days"]
        ]

        if unresolved:

            raise RuntimeError(
                "Unresolved scheduling conflicts: "
                + ", ".join(unresolved)
            )

        print("All scheduling conflicts resolved.")

    # --------------------------------------------------------
    # CORE AGENT LOOP
    # --------------------------------------------------------

    def run(self):

        while not self.satisfied():

            step, arg = self.next_step()

            # Ask only for missing information
            if step == "ask":

                answer = SIMULATED_ANSWERS[arg]

                self.goal[arg] = answer

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": f"ask for {arg}",
                    "action": f"asked user for {arg}",
                    "observed": answer,
                    "stopped": False
                })

            # Generate the plan after gathering requirements
            elif step == "generate_plan":

                # Read existing schedule using the tool
                busy = self.read_existing_schedule()

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read existing schedule before generating plan",
                    "action": "tool call: read_existing_schedule()",
                    "observed": busy,
                    "stopped": False
                })

                # Assignment 2: detect conflicts
                conflict_free = self.detect_conflicts(busy)

                if not conflict_free:

                    # Explicitly resolve conflicts before proceeding
                    self.resolve_conflicts()

                    # Check again after resolution
                    conflict_free = self.detect_conflicts(busy)

                    if not conflict_free:
                        raise RuntimeError(
                            "Cannot generate plan due to unresolved conflicts."
                        )

                # Build the plan only after conflict checking
                self.plan = self._build_plan(busy)

                self.goal["schedule_generated"] = True

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate schedule from gathered requirements",
                    "action": "built weekly plan",
                    "observed": self.plan,
                    "stopped": True,
                    "stop_reason":
                        "goal.schedule_generated is now True"
                })

        return self.plan

    # --------------------------------------------------------
    # BUILD THE ACTUAL STUDY PLAN
    # --------------------------------------------------------

    def _build_plan(self, busy_slots):

        days = [
            day for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]
            if day not in self.goal["unavailable_days"]
        ]

        subjects = self.goal["subjects"]

        plan = {}

        for i, day in enumerate(days):

            subject = subjects[i % len(subjects)]

            # Default duration is based on requested hours/day
            hours = self.goal["hours_per_day"]

            start_hour = 17
            end_hour = start_hour + hours

            time_slot = (
                f"{start_hour:02d}:00-{end_hour:02d}:00"
            )

            plan[day] = {
                "subject": subject,
                "time": time_slot
            }

        return plan

    # --------------------------------------------------------
    # ASSIGNMENT 1: APPLY USER FEEDBACK
    # --------------------------------------------------------

    def revise(self, feedback):

        print("\nApplying feedback:", feedback)

        # Keep a reference to the existing plan object.
        # We modify it directly instead of generating a new plan.
        original_plan_id = id(self.plan)

        if self.plan is None:
            raise RuntimeError(
                "Generate a study plan before applying feedback."
            )

        # Record feedback action
        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "apply user feedback to existing plan",
            "action": f"feedback received: '{feedback}'",
            "observed": None,
            "stopped": False
        })

        feedback_lower = feedback.lower()

        # Feedback round 1:
        # Move Tuesday's session to the evening.
        if "tuesday" in feedback_lower and "evening" in feedback_lower:

            if "Tuesday" in self.plan:

                self.plan["Tuesday"]["time"] = "20:00-22:00"

                print(
                    "Tuesday session moved to 20:00-22:00."
                )

            else:
                print(
                    "Tuesday is not available in the current plan."
                )

        # Feedback round 2:
        # Make Friday's session one hour long.
        elif (
            "friday" in feedback_lower
            and "one hour" in feedback_lower
        ):

            if "Friday" in self.plan:

                self.plan["Friday"]["time"] = "17:00-18:00"

                print(
                    "Friday session shortened to one hour."
                )

            else:
                print(
                    "Friday is not available in the current plan."
                )

        else:

            print(
                "Feedback was received but no matching "
                "revision rule was found."
            )

        # Verify the same plan object is being modified
        if id(self.plan) != original_plan_id:
            raise RuntimeError(
                "Error: A new plan object was created!"
            )

        # Record the completed revision
        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "confirm revised plan",
            "action": "mutated the existing plan object",
            "observed": self.plan,
            "stopped": True,
            "stop_reason":
                "revision applied without regenerating the plan"
        })

        return self.plan

    # --------------------------------------------------------
    # DISPLAY COMPLETE ITERATION LOG
    # --------------------------------------------------------

    def display_log(self):

        print("\n" + "=" * 60)
        print("COMPLETE AGENT ITERATION LOG")
        print("=" * 60)

        for entry in self.log:

            print("\n" + json.dumps(entry, indent=2))

# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("LAB 1: AGENT VS CHATBOT - STUDY PLANNER")
    print("=" * 60)

    print("\nStopping condition:")
    print("goal['schedule_generated'] is True")

    # Create agent with existing schedule data
    agent = StudyPlannerAgent(
        SIMULATED_EXISTING_SCHEDULE
    )

    # ---------------- ORIGINAL LAB FUNCTIONALITY ------------

    initial_plan = agent.run()

    print("\n" + "=" * 60)
    print("INITIAL STUDY PLAN")
    print("=" * 60)

    print(json.dumps(initial_plan, indent=2))

    # Keep the original plan object's identity
    original_plan_reference = id(agent.plan)

    # ---------------- ASSIGNMENT 1 ---------------------------

    print("\n" + "=" * 60)
    print("ASSIGNMENT 1: TWO ROUNDS OF FEEDBACK")
    print("=" * 60)

    # Feedback round 1
    print("\n--- Feedback Round 1 ---")

    revised_plan_1 = agent.revise(
        SIMULATED_FEEDBACK_ROUNDS[0]
    )

    print("\nPlan after feedback round 1:")
    print(json.dumps(revised_plan_1, indent=2))

    # Feedback round 2
    print("\n--- Feedback Round 2 ---")

    revised_plan_2 = agent.revise(
        SIMULATED_FEEDBACK_ROUNDS[1]
    )

    print("\nPlan after feedback round 2:")
    print(json.dumps(revised_plan_2, indent=2))

    # Verify that both revisions used the same plan object
    print("\n--- Plan Object Verification ---")

    if (
        id(agent.plan) == original_plan_reference
        and revised_plan_1 is revised_plan_2
    ):

        print(
            "SUCCESS: Both feedback rounds modified "
            "the same plan object."
        )

    else:

        print(
            "ERROR: Plan object was regenerated."
        )

    # ---------------- FINAL PLAN -----------------------------

    print("\n" + "=" * 60)
    print("FINAL STUDY PLAN")
    print("=" * 60)

    print(json.dumps(agent.plan, indent=2))

    # ---------------- ITERATION LOG --------------------------

    agent.display_log()

    # ---------------- FINAL SUMMARY --------------------------

    print("\n" + "=" * 60)
    print("LAB 1 EXECUTION SUMMARY")
    print("=" * 60)

    print("Original agent loop: COMPLETED")
    print("Missing information collection: COMPLETED")
    print("Existing schedule tool: COMPLETED")
    print("Busy-day conflict detection: COMPLETED")
    print("Conflict resolution: COMPLETED")
    print("Feedback round 1: COMPLETED")
    print("Feedback round 2: COMPLETED")
    print("Same plan object verification: COMPLETED")

    print("\nTotal iteration log entries:", len(agent.log))

    print("\nLAB 1 COMPLETED SUCCESSFULLY!")