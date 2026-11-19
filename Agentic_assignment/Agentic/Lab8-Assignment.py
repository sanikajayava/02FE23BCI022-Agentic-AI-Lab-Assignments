
"""
LAB 8: PARALLEL SWARM - HACKATHON PLANNER

Original Practical:
    1. Research Agent
    2. Logistics Agent
    3. Budget Agent
    4. Judging Agent

Assignment 1:
    5. Add Marketing Agent
    6. Detect marketing budget conflict
    7. Resolve using budget_over_preference

Assignment 2:
    8. Each role independently critiques merged draft
    9. Record which role raised each objection
    10. Generate distributed critique transcript

Execution:
    Parallel Agents -> Merge -> Distributed Critique
    -> Conflict Resolution -> Final Swarm Report
"""

from concurrent.futures import ThreadPoolExecutor


# ============================================================
# 1. RESEARCH AGENT
# ============================================================

def research_agent(goal):

    return {
        "role": "research",
        "output": {
            "format": "24-hour hackathon",
            "tracks": ["AI", "Machine Learning", "Web Development"],
            "research_notes": (
                "Past events favored a 24-hour format "
                "with themed tracks."
            )
        }
    }


# ============================================================
# 2. LOGISTICS AGENT
# ============================================================

def logistics_agent(goal):

    return {
        "role": "logistics",
        "output": {
            "venue": "Grand Hall",
            "venue_cost": 45000,
            "date": "Saturday"
        }
    }


# ============================================================
# 3. BUDGET AGENT
# ============================================================

def budget_agent(goal):

    return {
        "role": "budget",
        "output": {
            "total_cap": 30000,
            "currency": "INR"
        }
    }


# ============================================================
# 4. JUDGING AGENT
# ============================================================

def judging_agent(goal):

    return {
        "role": "judging",
        "output": {
            "criteria": [
                "Innovation",
                "Technical depth",
                "Demo quality"
            ]
        }
    }


# ============================================================
# 5. MARKETING AGENT - ASSIGNMENT 1
# ============================================================

def marketing_agent(goal):

    return {
        "role": "marketing",
        "output": {
            "publicity_plan": (
                "Social media campaigns, posters, "
                "email promotions and campus announcements"
            ),
            "marketing_cost": 35000,
            "channels": [
                "Instagram",
                "Email",
                "College Posters"
            ]
        }
    }


# ============================================================
# 6. ROLE REGISTRY
# ============================================================

ROLES = {
    "research": research_agent,
    "logistics": logistics_agent,
    "budget": budget_agent,
    "judging": judging_agent,
    "marketing": marketing_agent
}


# ============================================================
# 7. RUN ALL AGENTS IN PARALLEL
# ============================================================

def run_swarm(goal):

    print("\nStarting parallel swarm execution...")

    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:

        futures = {
            name: pool.submit(agent, goal)
            for name, agent in ROLES.items()
        }

        outputs = {
            name: future.result()
            for name, future in futures.items()
        }

    return outputs


# ============================================================
# 8. MERGE ALL AGENT OUTPUTS
# ============================================================

def merge(outputs):

    research = outputs["research"]["output"]
    logistics = outputs["logistics"]["output"]
    budget = outputs["budget"]["output"]
    judging = outputs["judging"]["output"]
    marketing = outputs["marketing"]["output"]

    draft = {

        "format": research["format"],

        "tracks": research["tracks"],

        "format_notes": research["research_notes"],

        "venue": logistics["venue"],

        "venue_cost": logistics["venue_cost"],

        "date": logistics["date"],

        "budget_cap": budget["total_cap"],

        "judging_criteria": judging["criteria"],

        "publicity_plan": marketing["publicity_plan"],

        "marketing_cost": marketing["marketing_cost"],

        "marketing_channels": marketing["channels"]

    }

    return draft


# ============================================================
# 9. ASSIGNMENT 2 - INDEPENDENT ROLE CRITIQUES
# ============================================================

# Each role has its own critique function.
# Every function independently checks the merged draft
# against that role's constraints.


# ---------------- RESEARCH AGENT CRITIQUE ----------------

def research_critique(draft):

    objections = []

    if not draft["format"] or not draft["tracks"]:

        objections.append({

            "conflict_id": "research_requirements_missing",

            "conflict": "Hackathon format or tracks are missing",

            "role_raised": "research",

            "details": "Research requirements are incomplete"

        })

    return objections


# ---------------- LOGISTICS AGENT CRITIQUE ----------------

def logistics_critique(draft):

    objections = []

    if not draft["venue"]:

        objections.append({

            "conflict_id": "venue_missing",

            "conflict": "Venue has not been selected",

            "role_raised": "logistics",

            "details": "A venue must be selected"

        })

    if draft["venue_cost"] > draft["budget_cap"]:

        objections.append({

            "conflict_id": "venue_cost_exceeds_budget_cap",

            "conflict": "Venue cost exceeds the overall budget cap",

            "role_raised": "logistics",

            "logistics_value": draft["venue_cost"],

            "budget_value": draft["budget_cap"]

        })

    return objections


# ---------------- BUDGET AGENT CRITIQUE ----------------

def budget_critique(draft):

    objections = []

    if draft["budget_cap"] <= 0:

        objections.append({

            "conflict_id": "invalid_budget",

            "conflict": "Budget cap must be greater than zero",

            "role_raised": "budget"

        })

    if draft["venue_cost"] > draft["budget_cap"]:

        objections.append({

            "conflict_id": "venue_cost_exceeds_budget_cap",

            "conflict": "Venue cost exceeds the approved budget",

            "role_raised": "budget",

            "logistics_value": draft["venue_cost"],

            "budget_value": draft["budget_cap"]

        })

    if draft["marketing_cost"] > draft["budget_cap"]:

        objections.append({

            "conflict_id": "marketing_cost_exceeds_budget_cap",

            "conflict": "Marketing cost exceeds the approved budget",

            "role_raised": "budget",

            "marketing_value": draft["marketing_cost"],

            "budget_value": draft["budget_cap"]

        })

    return objections


# ---------------- JUDGING AGENT CRITIQUE ----------------

def judging_critique(draft):

    objections = []

    if not draft["judging_criteria"]:

        objections.append({

            "conflict_id": "judging_criteria_missing",

            "conflict": "Judging criteria are missing",

            "role_raised": "judging"

        })

    return objections


# ---------------- MARKETING AGENT CRITIQUE ----------------

def marketing_critique(draft):

    objections = []

    if not draft["publicity_plan"]:

        objections.append({

            "conflict_id": "publicity_plan_missing",

            "conflict": "Marketing publicity plan is missing",

            "role_raised": "marketing"

        })

    if draft["marketing_cost"] > draft["budget_cap"]:

        objections.append({

            "conflict_id": "marketing_cost_exceeds_budget_cap",

            "conflict": "Marketing publicity cost exceeds the budget cap",

            "role_raised": "marketing",

            "marketing_value": draft["marketing_cost"],

            "budget_value": draft["budget_cap"]

        })

    return objections


# ============================================================
# 10. DISTRIBUTED CRITIQUE REGISTRY
# ============================================================

ROLE_CRITIQUES = {

    "research": research_critique,

    "logistics": logistics_critique,

    "budget": budget_critique,

    "judging": judging_critique,

    "marketing": marketing_critique

}


# ============================================================
# 11. RUN INDEPENDENT CRITIQUES IN PARALLEL
# ============================================================

def run_distributed_critiques(draft):

    all_objections = []

    with ThreadPoolExecutor(
        max_workers=len(ROLE_CRITIQUES)
    ) as pool:

        futures = {

            role: pool.submit(critique_function, draft)

            for role, critique_function in ROLE_CRITIQUES.items()

        }

        for role, future in futures.items():

            objections = future.result()

            all_objections.extend(objections)

    return all_objections


# ============================================================
# 12. CONFLICT RESOLUTION
# ============================================================

def resolve(conflict, priority_rule="budget_over_preference"):

    conflict_id = conflict["conflict_id"]

    # Venue budget conflict

    if conflict_id == "venue_cost_exceeds_budget_cap":

        resolution = (
            f"Reject venue costing "
            f"{conflict['logistics_value']}; "
            f"request logistics to propose an alternative "
            f"under {conflict['budget_value']}."
        )

    # Marketing budget conflict

    elif conflict_id == "marketing_cost_exceeds_budget_cap":

        resolution = (
            f"Reject publicity proposal costing "
            f"{conflict['marketing_value']}; "
            f"request marketing to prepare an alternative "
            f"under {conflict['budget_value']}."
        )

    # Other conflicts

    else:

        resolution = (
            "Send the issue back to the responsible role "
            "for correction."
        )

    return {

        "rule_applied": priority_rule,

        "resolution": resolution

    }


# ============================================================
# 13. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    goal = "Plan a college AI hackathon"

    # --------------------------------------------------------
    # STEP 1: RUN PARALLEL SWARM
    # --------------------------------------------------------

    outputs = run_swarm(goal)

    print("\n========== PARALLEL ROLE OUTPUTS ==========")

    for role, result in outputs.items():

        print(f"\n{role.upper()} AGENT:")

        print(result["output"])


    # --------------------------------------------------------
    # STEP 2: MERGE OUTPUTS
    # --------------------------------------------------------

    draft = merge(outputs)

    print("\n========== MERGED DRAFT PLAN ==========")

    print(draft)


    # --------------------------------------------------------
    # STEP 3: DISTRIBUTED CRITIQUE
    # --------------------------------------------------------

    print("\n========== DISTRIBUTED CRITIQUE TRANSCRIPT ==========")

    objections = run_distributed_critiques(draft)

    if objections:

        for objection in objections:

            print(
                f"\nRole raising objection: "
                f"{objection['role_raised'].upper()}"
            )

            print(
                f"Conflict: {objection['conflict']}"
            )

    else:

        print("No conflicts found.")


    # --------------------------------------------------------
    # STEP 4: RESOLVE ALL CONFLICTS
    # --------------------------------------------------------

    print("\n========== CONFLICT RESOLUTION ==========")

    conflict_log = []

    for objection in objections:

        resolution = resolve(objection)

        log_entry = {

            **objection,

            **resolution

        }

        conflict_log.append(log_entry)

        print("\nRole:", objection["role_raised"])

        print("Conflict:", objection["conflict"])

        print("Rule:", resolution["rule_applied"])

        print("Resolution:", resolution["resolution"])


    # --------------------------------------------------------
    # STEP 5: FINAL SWARM REPORT
    # --------------------------------------------------------

    print("\n========== FINAL CONFLICT LOG ==========")

    for index, entry in enumerate(conflict_log, start=1):

        print(f"\nConflict {index}:")

        print("Raised by:", entry["role_raised"])

        print("Conflict:", entry["conflict"])

        print("Rule applied:", entry["rule_applied"])

        print("Resolution:", entry["resolution"])


    # --------------------------------------------------------
    # STEP 6: VALIDATION
    # --------------------------------------------------------

    print("\n========== VALIDATION RESULTS ==========")

    assignment_1_pass = (

        "marketing" in outputs

        and draft["marketing_cost"] > draft["budget_cap"]

        and any(
            item["conflict_id"] ==
            "marketing_cost_exceeds_budget_cap"
            for item in objections
        )

    )

    roles_that_objected = {

        item["role_raised"]

        for item in objections

    }

    assignment_2_pass = (

        len(ROLE_CRITIQUES) == 5

        and len(roles_that_objected) >= 2

        and all(
            item["role_raised"] in ROLE_CRITIQUES
            for item in objections
        )

    )

    print(
        "Original Parallel Swarm:",
        "PASS" if len(outputs) == 5 else "FAIL"
    )

    print(
        "Assignment 1 - Marketing Agent:",
        "PASS" if assignment_1_pass else "FAIL"
    )

    print(
        "Assignment 2 - Distributed Critique:",
        "PASS" if assignment_2_pass else "FAIL"
    )

    if assignment_1_pass and assignment_2_pass:

        print("\nALL LAB 8 ASSIGNMENTS PASSED")

    else:

        print("\nPLEASE CHECK THE FAILED REQUIREMENT")
