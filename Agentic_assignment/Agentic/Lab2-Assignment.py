
"""
============================================================
LAB 2: TOOL-USING AGENT - CAMPUS DATA ASSISTANT
============================================================

ORIGINAL FUNCTIONALITY:
1. Calculator
2. CSV Reader
3. Mock Events API

ASSIGNMENT 1:
4. Notification Drafting Tool
   - Checks average sign-ups against a threshold.
   - Drafts a notification when average is below threshold.
   - Does NOT actually send notifications.

ASSIGNMENT 2:
5. Category Filtering Tool
   - Reads CSV data.
   - Filters technical events.
   - Validates filtered results.
   - Calculates average for technical events.

All tools use structured inputs and outputs.
All tool calls are recorded in a trace.
============================================================
"""

import csv
import io
import json


# ============================================================
# CONFIGURATION
# ============================================================

# Average below this threshold triggers a notification draft.
# The original dataset average is 12.33, so threshold 13
# demonstrates the notification functionality.

LOW_TURNOUT_THRESHOLD = 13


# ============================================================
# CSV DATA WITH CATEGORY FIELD
# ============================================================

SIGNUPS_CSV = """event,signups,category
AI Club Talk,12,technical
Hackathon Kickoff,9,technical
Robotics Demo,15,technical
GenAI Workshop,7,technical
Capstone Expo,20,technical
Career Panel,11,social
"""


# ============================================================
# MOCK EVENTS API DATABASE
# ============================================================

MOCK_EVENTS_API_DB = {

    "AI Club Talk": {
        "date": "2026-07-02",
        "location": "CS Block Auditorium"
    },

    "Hackathon Kickoff": {
        "date": "2026-07-05",
        "location": "Innovation Lab"
    }

}


# ============================================================
# TOOL 1: CALCULATOR
# ============================================================

def calculator(operation, values):

    if operation == "average":

        if not values:
            return {
                "error": "no values supplied"
            }

        return {
            "result": sum(values) / len(values)
        }

    elif operation == "sum":

        return {
            "result": sum(values)
        }

    else:

        return {
            "error": f"unsupported operation: {operation}"
        }


# ============================================================
# TOOL 2: CSV READER
# ============================================================

def read_csv(source_text=SIGNUPS_CSV):

    reader = csv.DictReader(
        io.StringIO(source_text)
    )

    rows = list(reader)

    if not rows:

        return {
            "error": "empty file",
            "rows": [],
            "row_count": 0
        }

    return {
        "rows": rows,
        "row_count": len(rows)
    }


# ============================================================
# TOOL 3: MOCK EVENTS API
# ============================================================

def mock_events_api(event_name):

    record = MOCK_EVENTS_API_DB.get(event_name)

    if record is None:

        return {
            "error": (
                f"no event metadata found for '{event_name}'"
            )
        }

    return record


# ============================================================
# ASSIGNMENT 1: TOOL 4 - NOTIFICATION DRAFTING
# ============================================================

def send_notification(message):

    # This tool ONLY creates a draft.
    # It does not send an email, SMS, or any notification.

    return {
        "draft_message": message,
        "status": "DRAFTED",
        "sent": False
    }


# ============================================================
# ASSIGNMENT 2: TOOL 5 - CATEGORY FILTERING
# ============================================================

def filter_by_category(rows, category):

    filtered_rows = [
        row for row in rows
        if row.get("category", "").lower() == category.lower()
    ]

    return {
        "filtered_rows": filtered_rows,
        "row_count": len(filtered_rows),
        "category": category
    }


# ============================================================
# REGISTER ALL AVAILABLE TOOLS
# ============================================================

TOOLS = {

    "calculator": calculator,

    "read_csv": read_csv,

    "events_api": mock_events_api,

    "send_notification": send_notification,

    "filter_by_category": filter_by_category

}


# ============================================================
# CAMPUS DATA ASSISTANT
# ============================================================

class CampusDataAssistant:

    def __init__(self):

        self.trace = []


    # --------------------------------------------------------
    # COMMON TOOL CALL METHOD
    # --------------------------------------------------------

    def _call(self, tool_name, reason, **kwargs):

        print(f"\n[TOOL CALL] {tool_name}")
        print(f"[REASON] {reason}")
        print(f"[INPUT] {kwargs}")

        # Execute the selected tool
        result = TOOLS[tool_name](**kwargs)

        # Record tool execution
        entry = {

            "tool": tool_name,

            "reason": reason,

            "input": kwargs,

            "output": result

        }

        self.trace.append(entry)

        print(f"[OUTPUT] {result}")

        # Validate tool output
        if "error" in result:

            raise RuntimeError(
                f"{tool_name} failed: {result['error']}"
            )

        return result


    # --------------------------------------------------------
    # QUESTION 1: TOTAL AND AVERAGE SIGN-UPS
    # --------------------------------------------------------

    def get_signup_statistics(self):

        # Step 1: Read CSV
        csv_result = self._call(

            "read_csv",

            "Sign-up counts are stored in the CSV file."
        )

        # Extract numerical sign-up values
        values = [
            int(row["signups"])
            for row in csv_result["rows"]
        ]

        # Step 2: Calculate total
        total = self._call(

            "calculator",

            "Calculate the total number of sign-ups.",

            operation="sum",

            values=values
        )

        # Step 3: Calculate average
        avg = self._call(

            "calculator",

            "Calculate average sign-ups across all events.",

            operation="average",

            values=values
        )

        average_value = avg["result"]

        # Assignment 1: Check low-turnout threshold
        notification_draft = None

        if average_value < LOW_TURNOUT_THRESHOLD:

            message = (
                "LOW EVENT TURNOUT NOTICE: "
                f"The average event sign-up is "
                f"{average_value:.2f}, which is below "
                f"the threshold of "
                f"{LOW_TURNOUT_THRESHOLD}. "
                "Consider promoting upcoming campus events."
            )

            # Draft notification using fourth tool
            notification_draft = self._call(

                "send_notification",

                "The computed average is below the low-turnout "
                "threshold, so a notification draft is required.",

                message=message
            )

        else:

            print(
                "\nAverage sign-ups are above the threshold. "
                "No notification draft is required."
            )

        answer = (
            f"Total sign-ups: {total['result']}. "
            f"Average per event: {average_value:.2f} "
            f"(across {csv_result['row_count']} events)."
        )

        if notification_draft:

            answer += (
                "\nLow-turnout notification has been drafted "
                "(not sent)."
            )

        return answer


    # --------------------------------------------------------
    # QUESTION 2: HACKATHON EVENT DETAILS
    # --------------------------------------------------------

    def get_hackathon_details(self):

        meta = self._call(

            "events_api",

            "Location and date information is available "
            "in the events API.",

            event_name="Hackathon Kickoff"
        )

        return (
            f"Hackathon Kickoff is at "
            f"{meta['location']} on {meta['date']}."
        )


    # --------------------------------------------------------
    # QUESTION 3: CAPSTONE EXPO EVENT DETAILS
    # --------------------------------------------------------

    def get_capstone_details(self):

        try:

            meta = self._call(

                "events_api",

                "Checking the events API for Capstone Expo metadata.",

                event_name="Capstone Expo"
            )

            return (
                f"Capstone Expo is at "
                f"{meta['location']} on {meta['date']}."
            )

        except RuntimeError:

            return (
                "I don't have location/date metadata "
                "for Capstone Expo in the events API."
            )


    # --------------------------------------------------------
    # ASSIGNMENT 2:
    # TECHNICAL EVENTS AVERAGE
    # --------------------------------------------------------

    def get_technical_average(self):

        print("\n--- TECHNICAL EVENT ANALYSIS ---")

        # STEP 1: Read CSV
        csv_result = self._call(

            "read_csv",

            "Read the CSV because event sign-up counts "
            "and categories are stored in the file."
        )

        rows = csv_result["rows"]

        # STEP 2: Filter technical events
        filtered_result = self._call(

            "filter_by_category",

            "Filter the CSV rows to include only technical events.",

            rows=rows,

            category="technical"
        )

        filtered_rows = filtered_result["filtered_rows"]

        print("\nFiltered technical events:")

        print(
            json.dumps(filtered_rows, indent=2)
        )

        # VALIDATION: Check that filtered data is not empty
        if not filtered_rows:

            message = (
                "No technical events found. "
                "Average cannot be calculated."
            )

            print("\nVALIDATION FAILED:", message)

            self.trace.append({

                "tool": "filter_validation",

                "reason": (
                    "Check that the category filter returned "
                    "at least one matching event."
                ),

                "input": {
                    "category": "technical"
                },

                "output": {
                    "valid": False,
                    "error": "empty filtered result"
                }

            })

            return message

        # Record successful validation
        self.trace.append({

            "tool": "filter_validation",

            "reason": (
                "Verify that the filtered technical event "
                "list is non-empty before calculating average."
            ),

            "input": {
                "category": "technical",
                "filtered_count": len(filtered_rows)
            },

            "output": {
                "valid": True,
                "filtered_count": len(filtered_rows)
            }

        })

        print(
            "\nVALIDATION PASSED: "
            "Filtered result is not empty."
        )

        # STEP 3: Extract sign-up values
        technical_values = [
            int(row["signups"])
            for row in filtered_rows
        ]

        # Calculate average only after validation
        avg_result = self._call(

            "calculator",

            "Calculate the average sign-ups using only "
            "the validated technical event records.",

            operation="average",

            values=technical_values
        )

        return (

            f"Average sign-ups for technical events: "
            f"{avg_result['result']:.2f} "
            f"(across {len(filtered_rows)} technical events)."

        )


    # --------------------------------------------------------
    # PLANNER: ANSWER USER QUESTIONS
    # --------------------------------------------------------

    def answer(self, question):

        q = question.lower()

        # Assignment 2 question must be checked first
        if (
            "technical" in q
            and ("average" in q or "sign" in q)
        ):

            return self.get_technical_average()

        # Original question: Total and average sign-ups
        if "average" in q and "sign" in q:

            return self.get_signup_statistics()

        # Original question: Hackathon details
        if "where" in q and "hackathon" in q:

            return self.get_hackathon_details()

        # Original question: Capstone Expo details
        if "where" in q and "capstone" in q:

            return self.get_capstone_details()

        return (
            "I don't have a tool path configured "
            "for that question."
        )


    # --------------------------------------------------------
    # DISPLAY COMPLETE TOOL TRACE
    # --------------------------------------------------------

    def display_trace(self):

        print("\n" + "=" * 65)

        print("COMPLETE TOOL EXECUTION TRACE")

        print("=" * 65)

        for i, entry in enumerate(self.trace, 1):

            print(f"\n--- TOOL TRACE {i} ---")

            print(
                "Tool:",
                entry["tool"]
            )

            print(
                "Reason:",
                entry["reason"]
            )

            print(
                "Input:",
                json.dumps(entry["input"], indent=2)
            )

            print(
                "Output:",
                json.dumps(entry["output"], indent=2)
            )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    assistant = CampusDataAssistant()

    print("=" * 65)

    print("LAB 2: TOOL-USING AGENT - CAMPUS DATA ASSISTANT")

    print("=" * 65)

    print("\nAvailable tools:")

    for tool_name in TOOLS:

        print("-", tool_name)


    # --------------------------------------------------------
    # ORIGINAL QUESTION 1
    # --------------------------------------------------------

    q1 = (
        "How many students signed up for events this month, "
        "and what's the average per event?"
    )

    print("\n" + "=" * 65)

    print("ORIGINAL QUESTION 1")

    print("=" * 65)

    print("\nQ:", q1)

    print("\nA:", assistant.answer(q1))


    # --------------------------------------------------------
    # ORIGINAL QUESTION 2
    # --------------------------------------------------------

    q2 = "Where and when is the Hackathon Kickoff?"

    print("\n" + "=" * 65)

    print("ORIGINAL QUESTION 2")

    print("=" * 65)

    print("\nQ:", q2)

    print("\nA:", assistant.answer(q2))


    # --------------------------------------------------------
    # ORIGINAL QUESTION 3
    # --------------------------------------------------------

    q3 = "Where and when is the Capstone Expo?"

    print("\n" + "=" * 65)

    print("ORIGINAL QUESTION 3")

    print("=" * 65)

    print("\nQ:", q3)

    print("\nA:", assistant.answer(q3))


    # --------------------------------------------------------
    # ASSIGNMENT 2 QUESTION
    # --------------------------------------------------------

    q4 = (
        "What's the average sign-up for technical events only?"
    )

    print("\n" + "=" * 65)

    print("ASSIGNMENT 2: TECHNICAL EVENTS AVERAGE")

    print("=" * 65)

    print("\nQ:", q4)

    print("\nA:", assistant.answer(q4))


    # --------------------------------------------------------
    # DISPLAY COMPLETE TOOL TRACE
    # --------------------------------------------------------

    assistant.display_trace()


    # --------------------------------------------------------
    # FINAL EXECUTION SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 65)

    print("LAB 2 EXECUTION SUMMARY")

    print("=" * 65)

    print("Original calculator tool: COMPLETED")

    print("Original CSV reader tool: COMPLETED")

    print("Original Mock Events API: COMPLETED")

    print("Assignment 1 notification drafting: COMPLETED")

    print("Assignment 2 category filtering: COMPLETED")

    print("Filtered data validation: COMPLETED")

    print("Tool execution trace: COMPLETED")

    print("\nLAB 2 COMPLETED SUCCESSFULLY!")
