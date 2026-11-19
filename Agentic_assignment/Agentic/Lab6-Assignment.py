
"""
LAB 6: OpenCLA/OpenClaw-Style Runtime
Personal Agent Runtime

ORIGINAL PRACTICAL:
1. Interface
2. Runtime loop
3. Skill registry
4. Tools
5. Scoped memory
6. Audit log

ASSIGNMENT 1:
Per-user rate limiting - maximum 3 tasks per session.

ASSIGNMENT 2:
After two failures of the same skill for the same user
in the same session, escalate the third attempt to a human.
"""

from datetime import datetime


# ============================================================
# 1. TOOLS
# ============================================================

def tool_word_count(text):
    return {"count": len(text.split())}


def tool_lookup_contact(name, contacts_db):
    return contacts_db.get(
        name,
        {"error": f"no contact found for {name}"}
    )


TOOLS = {
    "word_count": tool_word_count,
    "lookup_contact": tool_lookup_contact
}


# ============================================================
# 2. MEMORY - SCOPED PER USER
# ============================================================

class Memory:

    def __init__(self):
        self._store = {}

    def scope(self, user):
        return self._store.setdefault(user, {})


# ============================================================
# 3. AUDIT LOG
# ============================================================

class Audit:

    def __init__(self):
        self.entries = []

    def log(
        self,
        task,
        skill_name,
        tool_calls,
        user,
        result=None,
        error=None,
        escalated=False
    ):

        self.entries.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user,
            "session_id": task.get("session_id"),
            "task": task.copy(),
            "skill": skill_name,
            "tool_calls": tool_calls.copy(),
            "result": result,
            "error": error,
            "escalated": escalated
        })

    # Count previous actual skill failures.
    # Escalation records are not counted as skill failures.

    def count_failures(self, user, session_id, skill_name):

        count = 0

        for entry in self.entries:

            if (
                entry["user"] == user
                and entry["session_id"] == session_id
                and entry["skill"] == skill_name
                and entry["error"] is not None
                and entry["escalated"] is False
            ):
                count += 1

        return count


# ============================================================
# 4. SKILLS
# ============================================================

class SummarizeNotesSkill:

    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):

        text = task.get("text", "")

        wc = TOOLS["word_count"](text)

        self.tool_calls.append({
            "tool": "word_count",
            "output": wc
        })

        self.memory_scope["last_note_length"] = wc["count"]

        return f"Summary stub: note has {wc['count']} words."


class DraftEmailSkill:

    CONTACTS = {
        "Dr. Meena": {
            "email": "meena@example.edu"
        }
    }

    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):

        contact = TOOLS["lookup_contact"](
            task["to"],
            self.CONTACTS
        )

        self.tool_calls.append({
            "tool": "lookup_contact",
            "output": contact
        })

        if "error" in contact:
            raise RuntimeError(contact["error"])

        return (
            f"Draft email to {contact['email']}: "
            f"'{task['subject']}'"
        )


# ============================================================
# 5. THIRD SKILL - TRANSLATE TEXT
# ============================================================

class TranslateTextSkill:

    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):

        return (
            f"[translated to {task['target_lang']}] "
            f"{task['text']}"
        )


# ============================================================
# 6. SKILL REGISTRY
# ============================================================

SKILL_REGISTRY = {
    "summarize_notes": SummarizeNotesSkill,
    "draft_email": DraftEmailSkill
}


# ============================================================
# 7. SKILL SELECTION
# ============================================================

def select_skill(task):
    return task["skill"]


# ============================================================
# 8. ORIGINAL RUNTIME CORE LOOP
# ============================================================

def run_task(task, user, memory, audit):

    skill_name = select_skill(task)

    skill_cls = SKILL_REGISTRY[skill_name]

    skill = skill_cls(memory.scope(user))

    try:

        result = skill.execute(task)

        audit.log(
            task=task,
            skill_name=skill_name,
            tool_calls=skill.tool_calls,
            user=user,
            result=result
        )

        return result

    except Exception as e:

        audit.log(
            task=task,
            skill_name=skill_name,
            tool_calls=skill.tool_calls,
            user=user,
            error=str(e)
        )

        raise


# ============================================================
# 9. ASSIGNMENT 1 - PER-USER RATE LIMITING
# ============================================================

class SessionLimiter:

    def __init__(self, max_tasks=3):
        self.max_tasks = max_tasks
        self.task_counts = {}

    def allow_task(self, user, session_id):

        key = (user, session_id)

        current_count = self.task_counts.get(key, 0)

        if current_count >= self.max_tasks:
            return False

        self.task_counts[key] = current_count + 1

        return True

    def get_count(self, user, session_id):

        return self.task_counts.get((user, session_id), 0)


# ============================================================
# 10. INTERFACE - RECEIVE TASK
# ============================================================

def receive_task(task, user, memory, audit, limiter):

    session_id = task["session_id"]
    skill_name = task["skill"]

    # Assignment 1: Rate limit check.

    if not limiter.allow_task(user, session_id):

        return (
            f"REJECTED: User '{user}' has reached the "
            f"maximum of {limiter.max_tasks} tasks "
            f"in session '{session_id}'."
        )

    # Check whether the requested skill exists.

    if skill_name not in SKILL_REGISTRY:

        error_message = f"Unknown skill: {skill_name}"

        audit.log(
            task=task,
            skill_name=skill_name,
            tool_calls=[],
            user=user,
            error=error_message
        )

        return f"ERROR: {error_message}"

    # Assignment 2: Count previous failures
    # using the existing audit log.

    previous_failures = audit.count_failures(
        user,
        session_id,
        skill_name
    )

    if previous_failures >= 2:

        message = (
            f"HUMAN ESCALATION: Skill '{skill_name}' "
            f"failed twice for user '{user}'. "
            f"Third attempt will not be executed."
        )

        audit.log(
            task=task,
            skill_name=skill_name,
            tool_calls=[],
            user=user,
            error=message,
            escalated=True
        )

        return message

    # Execute the original runtime core loop.

    return run_task(task, user, memory, audit)


# ============================================================
# 11. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    memory = Memory()
    audit = Audit()
    limiter = SessionLimiter(max_tasks=3)

    # ========================================================
    # ORIGINAL PRACTICAL
    # ========================================================

    print("\n========== ORIGINAL PRACTICAL ==========")

    original_user = "uday"
    original_session = "original_session_1"

    print("\n=== Successful run: summarize_notes ===")

    result = receive_task(
        {
            "skill": "summarize_notes",
            "text": "Agentic AI systems combine goals tools skills memory",
            "session_id": original_session
        },
        user=original_user,
        memory=memory,
        audit=audit,
        limiter=limiter
    )

    print(result)

    print("\n=== Successful run: draft_email ===")

    result = receive_task(
        {
            "skill": "draft_email",
            "to": "Dr. Meena",
            "subject": "Lab guide review",
            "session_id": original_session
        },
        user=original_user,
        memory=memory,
        audit=audit,
        limiter=limiter
    )

    print(result)

    print("\n=== Failing run: draft_email to unknown contact ===")

    try:

        receive_task(
            {
                "skill": "draft_email",
                "to": "Unknown Person",
                "subject": "Hello",
                "session_id": original_session
            },
            user=original_user,
            memory=memory,
            audit=audit,
            limiter=limiter
        )

    except RuntimeError as e:

        print(f"Run failed as expected: {e}")

    print("\n=== Register a THIRD skill ===")

    # Register without modifying run_task or select_skill.

    SKILL_REGISTRY["translate_text"] = TranslateTextSkill

    result = receive_task(
        {
            "skill": "translate_text",
            "text": "Hello, team",
            "target_lang": "Kannada",
            "session_id": "original_session_2"
        },
        user=original_user,
        memory=memory,
        audit=audit,
        limiter=limiter
    )

    print(result)

    # ========================================================
    # ASSIGNMENT 1 - RATE LIMITING
    # ========================================================

    print("\n========== ASSIGNMENT 1 ==========")

    print("\n=== Maximum 3 tasks per user per session ===")

    rate_user = "student1"
    rate_session = "rate_session_1"

    for i in range(1, 5):

        task = {
            "skill": "summarize_notes",
            "text": f"This is rate limit test task number {i}",
            "session_id": rate_session
        }

        print(f"\nTask {i}:")

        result = receive_task(
            task,
            user=rate_user,
            memory=memory,
            audit=audit,
            limiter=limiter
        )

        print(result)

    accepted_tasks = limiter.get_count(
        rate_user,
        rate_session
    )

    print("\nTotal accepted tasks:", accepted_tasks)

    print("\nAssignment 1 validation:")

    if accepted_tasks == 3:
        print("PASS: Fourth task was rejected.")
    else:
        print("FAIL: Rate limiting did not work correctly.")

    # ========================================================
    # ASSIGNMENT 2 - ESCALATION AFTER TWO FAILURES
    # ========================================================

    print("\n========== ASSIGNMENT 2 ==========")

    print("\n=== Two failures followed by human escalation ===")

    escalation_user = "student2"
    escalation_session = "escalation_session_1"

    for attempt in range(1, 4):

        print(f"\nAttempt {attempt}:")

        task = {
            "skill": "draft_email",
            "to": "Unknown Person",
            "subject": f"Test attempt {attempt}",
            "session_id": escalation_session
        }

        try:

            result = receive_task(
                task,
                user=escalation_user,
                memory=memory,
                audit=audit,
                limiter=limiter
            )

            print(result)

        except RuntimeError as e:

            # Catch the expected skill failure.
            # Continue to the next attempt.

            print(f"Run failed as expected: {e}")

    # ========================================================
    # ASSIGNMENT 2 - VALIDATION
    # ========================================================

    failure_count = audit.count_failures(
        escalation_user,
        escalation_session,
        "draft_email"
    )

    escalation_entries = [
        entry for entry in audit.entries
        if (
            entry["user"] == escalation_user
            and entry["session_id"] == escalation_session
            and entry["skill"] == "draft_email"
            and entry["escalated"] is True
        )
    ]

    print("\nAssignment 2 validation:")

    print("Actual skill failures:", failure_count)

    print("Human escalations:", len(escalation_entries))

    if failure_count == 2 and len(escalation_entries) == 1:

        print(
            "PASS: Two failures detected. "
            "Third attempt escalated to human."
        )

    else:

        print("FAIL: Escalation validation failed.")

    # ========================================================
    # FULL AUDIT LOG
    # ========================================================

    print("\n========== FULL AUDIT LOG ==========")

    for entry in audit.entries:
        print(entry)

    # ========================================================
    # USER-SCOPED MEMORY
    # ========================================================

    print("\n========== SCOPED MEMORY ==========")

    print("\nMemory for uday:")
    print(memory.scope("uday"))

    print("\nMemory for student1:")
    print(memory.scope("student1"))

    print("\nMemory for student2:")
    print(memory.scope("student2"))

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print("\n========== FINAL LAB 6 STATUS ==========")

    if accepted_tasks == 3:
        print("Original Practical: Completed")
        print("Assignment 1: PASSED")
    else:
        print("Assignment 1: FAILED")

    if failure_count == 2 and len(escalation_entries) == 1:
        print("Assignment 2: PASSED")
    else:
        print("Assignment 2: FAILED")

    print("\nLAB 6 EXECUTION COMPLETED")
