
"""
LAB 4: MEMORY AND RETRIEVAL — PROJECT MEMORY

ORIGINAL PRACTICAL:
1. Short-term session state
2. Long-term memory records
3. Source-tagged answers
4. Conflict detection
5. Role-based write permissions

ASSIGNMENT 1:
1. Add a second isolated topic: hosting
2. Demonstrate database and hosting retrieval separately
3. Verify that facts do not leak between topics

ASSIGNMENT 2:
1. Add retention_days control
2. Detect stale memory records
3. Warn before using outdated information
4. Test one fresh and one artificially old record

Run:
    python Lab4-Assignment.py
"""

from dataclasses import dataclass
from datetime import date


# ============================================================
# PART 1: MEMORY RECORD
# ============================================================

@dataclass
class MemoryRecord:

    topic: str
    fact: str
    date: str
    source: str = "memory"


# ============================================================
# PART 2: PROJECT MEMORY
# ============================================================

class ProjectMemory:

    def __init__(self, retention_days=90):

        # Long-term memory store
        self.records = []

        # Only team lead can write memory
        self.allowed_writers = {"team_lead"}

        # Assignment 2: retention policy
        self.retention_days = retention_days

    def retrieve(self, topic):

        # Return only records matching the requested topic
        return [
            record
            for record in self.records
            if record.topic == topic
        ]

    def write(self, record, user_role):

        # Check write permission
        if user_role not in self.allowed_writers:

            raise PermissionError(
                f"role '{user_role}' is not permitted to write memory"
            )

        self.records.append(record)

    def check_staleness(self, record):

        """
        Check whether a memory record is older
        than the configured retention period.
        """

        record_date = date.fromisoformat(record.date)

        age_days = (date.today() - record_date).days

        is_stale = age_days > self.retention_days

        return is_stale, age_days


# ============================================================
# PART 3: PROJECT ASSISTANT
# ============================================================

class ProjectAssistant:

    def __init__(self, memory):

        self.memory = memory

        # Short-term working memory
        self.session_facts = {}

    def set_session_fact(self, topic, fact):

        self.session_facts[topic] = fact

    def answer(self, topic, question):

        # First check current session state
        if topic in self.session_facts:

            return (
                f"[current session] {self.session_facts[topic]}"
            )

        # Retrieve only the requested topic
        hits = self.memory.retrieve(topic)

        if not hits:

            return (
                f"[session] No stored decision on '{topic}' yet. "
                f"{question}"
            )

        latest = hits[-1]

        # Assignment 2: check whether memory is stale
        is_stale, age_days = self.memory.check_staleness(latest)

        if is_stale:

            warning = (
                f"WARNING: This decision is from {age_days} days ago "
                f"and may be out of date. "
            )

        else:

            warning = ""

        return (
            f"{warning}"
            f"[memory, dated {latest.date}] "
            f"Per a decision on {latest.date}, {latest.fact}"
        )

    def receive_statement(self, topic, new_fact, user_role):

        """
        Check a new statement against the latest stored decision.
        If there is a conflict, flag it instead of silently overwriting.
        """

        hits = self.memory.retrieve(topic)

        if hits and hits[-1].fact.lower() != new_fact.lower():

            latest = hits[-1]

            return {
                "conflict": True,
                "stored": latest.fact,
                "stored_date": latest.date,
                "new": new_fact,
                "message": (
                    f"This conflicts with the stored decision from "
                    f"{latest.date} ('{latest.fact}'). "
                    f"Should I update memory to '{new_fact}'?"
                )
            }

        # No conflict: write through permission-controlled method
        record = MemoryRecord(
            topic=topic,
            fact=new_fact,
            date=str(date.today())
        )

        self.memory.write(record, user_role)

        return {
            "conflict": False,
            "message": f"Recorded: {new_fact}",
            "written": True
        }

    def confirm_update(self, topic, new_fact, user_role):

        """
        Update the memory after explicit confirmation.
        """

        record = MemoryRecord(
            topic=topic,
            fact=new_fact,
            date=str(date.today())
        )

        self.memory.write(record, user_role)

        return (
            f"Write permitted: memory updated by {user_role}."
        )


# ============================================================
# PART 4: ORIGINAL PRACTICAL
# ============================================================

def original_practical():

    print("\n" + "=" * 70)
    print("ORIGINAL PRACTICAL: PROJECT MEMORY")
    print("=" * 70)

    memory = ProjectMemory(retention_days=90)

    # Store initial database decision
    memory.write(
        MemoryRecord(
            topic="database",
            fact="we chose PostgreSQL",
            date="2026-07-03"
        ),
        user_role="team_lead"
    )

    assistant = ProjectAssistant(memory)

    # Retrieve stored decision
    print("\n--- Initial database decision ---")

    print(
        assistant.answer(
            "database",
            "What did we decide about the database?"
        )
    )

    # Member proposes a change
    print("\n--- A team member proposes a change ---")

    result = assistant.receive_statement(
        "database",
        "we're switching to SQLite",
        user_role="member"
    )

    print(result["message"])

    # Team lead confirms the change
    print("\n--- Team lead confirms the switch ---")

    if result["conflict"]:

        confirmation = assistant.confirm_update(
            "database",
            "we're switching to SQLite",
            user_role="team_lead"
        )

        print(confirmation)

    # Attempt unauthorized write
    print("\n--- Attempted write by an unpermitted role ---")

    try:

        memory.write(
            MemoryRecord(
                topic="database",
                fact="switch to MongoDB",
                date=str(date.today())
            ),
            user_role="member"
        )

    except PermissionError as error:

        print(f"Blocked as expected: {error}")

    # Final decision
    print("\n--- Final answer reflects the confirmed update ---")

    print(
        assistant.answer(
            "database",
            "What did we decide about the database?"
        )
    )

    return memory, assistant


# ============================================================
# PART 5: ASSIGNMENT 1 — SECOND ISOLATED TOPIC
# ============================================================

def assignment_1(memory, assistant):

    print("\n" + "=" * 70)
    print("ASSIGNMENT 1: SECOND, ISOLATED TOPIC")
    print("=" * 70)

    # Add a separate hosting decision
    memory.write(
        MemoryRecord(
            topic="hosting",
            fact="we chose AWS for application hosting",
            date=str(date.today())
        ),
        user_role="team_lead"
    )

    # Database retrieval
    print("\n--- Retrieve DATABASE topic ---")

    database_records = memory.retrieve("database")

    for record in database_records:

        print(
            f"Topic: {record.topic} | Fact: {record.fact}"
        )

    database_answer = assistant.answer(
        "database",
        "Which database did we choose?"
    )

    print("Database answer:")
    print(database_answer)

    # Hosting retrieval
    print("\n--- Retrieve HOSTING topic ---")

    hosting_records = memory.retrieve("hosting")

    for record in hosting_records:

        print(
            f"Topic: {record.topic} | Fact: {record.fact}"
        )

    hosting_answer = assistant.answer(
        "hosting",
        "Which hosting platform did we choose?"
    )

    print("Hosting answer:")
    print(hosting_answer)

    # Verify database isolation
    database_isolated = (
        len(database_records) > 0
        and all(r.topic == "database" for r in database_records)
        and "AWS" not in database_answer
    )

    # Verify hosting isolation
    hosting_isolated = (
        len(hosting_records) > 0
        and all(r.topic == "hosting" for r in hosting_records)
        and "PostgreSQL" not in hosting_answer
        and "SQLite" not in hosting_answer
    )

    print("\n--- Isolation validation ---")

    print(
        "Database retrieval is isolated:",
        database_isolated
    )

    print(
        "Hosting retrieval is isolated:",
        hosting_isolated
    )

    if database_isolated and hosting_isolated:

        print("\nASSIGNMENT 1: PASSED")

    else:

        print("\nASSIGNMENT 1: FAILED")


# ============================================================
# PART 6: ASSIGNMENT 2 — STALENESS / RETENTION POLICY
# ============================================================

def assignment_2():

    print("\n" + "=" * 70)
    print("ASSIGNMENT 2: STALENESS / RETENTION POLICY")
    print("=" * 70)

    # Configure retention policy
    RETENTION_DAYS = 90

    memory = ProjectMemory(
        retention_days=RETENTION_DAYS
    )

    assistant = ProjectAssistant(memory)

    print(
        "\nConfigured retention period:",
        memory.retention_days,
        "days"
    )

    # Fresh record
    fresh_record = MemoryRecord(
        topic="fresh_project",
        fact="the project uses Python for development",
        date=str(date.today())
    )

    # Artificially old record
    old_record = MemoryRecord(
        topic="old_project",
        fact="the project used an older hosting configuration",
        date="2025-01-01"
    )

    # Store both records
    memory.write(fresh_record, user_role="team_lead")

    memory.write(old_record, user_role="team_lead")

    # Test fresh record
    print("\n--- Test 1: Fresh memory record ---")

    fresh_answer = assistant.answer(
        "fresh_project",
        "What technology does the project use?"
    )

    print(fresh_answer)

    fresh_stale, fresh_age = memory.check_staleness(
        fresh_record
    )

    print("Record age:", fresh_age, "days")
    print("Is stale:", fresh_stale)

    # Test old record
    print("\n--- Test 2: Artificially old memory record ---")

    old_answer = assistant.answer(
        "old_project",
        "What was the old hosting configuration?"
    )

    print(old_answer)

    old_stale, old_age = memory.check_staleness(
        old_record
    )

    print("Record age:", old_age, "days")
    print("Is stale:", old_stale)

    # Validate both test cases
    fresh_passed = (
        not fresh_stale
        and "WARNING" not in fresh_answer
    )

    old_passed = (
        old_stale
        and "WARNING" in old_answer
        and "may be out of date" in old_answer
    )

    print("\n--- Staleness validation ---")

    print(
        "Fresh record correctly accepted:",
        fresh_passed
    )

    print(
        "Old record correctly flagged:",
        old_passed
    )

    if fresh_passed and old_passed:

        print("\nASSIGNMENT 2: PASSED")

    else:

        print("\nASSIGNMENT 2: FAILED")


# ============================================================
# PART 7: MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("*" * 70)
    print("LAB 4: MEMORY AND RETRIEVAL — PROJECT MEMORY")
    print("*" * 70)

    # Run original practical
    memory, assistant = original_practical()

    # Run Assignment 1
    assignment_1(memory, assistant)

    # Run Assignment 2
    assignment_2()

    print("\n" + "=" * 70)
    print("LAB 4 EXECUTION COMPLETED")
    print("=" * 70)
