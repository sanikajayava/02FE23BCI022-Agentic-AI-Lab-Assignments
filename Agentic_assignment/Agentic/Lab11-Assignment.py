
"""
LAB 11: AGENTIC SDLC FACTORY
Original Practical + Assignment 1 + Assignment 2

Original:
CSV Export Feature

Assignment 1:
Add a second PDF Export story and process both stories
through independent SDLC pipeline branches.

Assignment 2:
Introduce a deliberate bug in coding_agent's CSV filter
logic and prove that testing_agent catches it.

Testing agent is independent of implementation.
"""

from concurrent.futures import ThreadPoolExecutor


FEATURE_REQUEST = (
    "Add CSV export to the reports page, preserving applied filters."
)


# ============================================================
# 1. REQUIREMENT AGENT
# ============================================================

def requirement_agent(request):

    stories = [

        {
            "id": "US-1",
            "format": "CSV",
            "text": (
                "As a user, I can export the current report view "
                "as a CSV file, preserving the applied filters."
            ),
            "acceptance_criteria": [
                "clicking Export produces a .csv file",
                "the CSV contains only rows matching the currently applied filters",
                "the CSV header row matches the visible column names"
            ]
        },

        {
            "id": "US-2",
            "format": "PDF",
            "text": (
                "As a user, I can export the current report view "
                "as a PDF file, preserving the applied filters."
            ),
            "acceptance_criteria": [
                "clicking Export PDF produces a .pdf file",
                "the PDF contains only rows matching the currently applied filters",
                "the PDF header row matches the visible column names"
            ]
        }

    ]

    return stories


# ============================================================
# 2. HUMAN CHECKPOINT
# ============================================================

def human_confirms_stories(stories):

    print("\n[HUMAN CHECKPOINT] Reviewing stories for real user intent...")

    for story in stories:
        print(f" Confirmed: {story['text']}")

    return True


# ============================================================
# 3. DESIGN AGENT
# ============================================================

def design_agent(story):

    if story["format"] == "CSV":

        components = [
            "export_endpoint",
            "csv_serializer",
            "export_button (UI)"
        ]

    else:

        components = [
            "pdf_export_endpoint",
            "pdf_generator",
            "export_pdf_button (UI)"
        ]

    return {
        "story_id": story["id"],
        "format": story["format"],
        "components": components
    }


# ============================================================
# 4. PDF GENERATOR
# ============================================================

def create_pdf(lines):
    """
    Creates a basic valid PDF using Python standard library.
    """

    def escape_pdf_text(text):
        return (
            str(text)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

    commands = [
        "BT",
        "/F1 12 Tf",
        "50 740 Td"
    ]

    for index, line in enumerate(lines):

        if index > 0:
            commands.append("0 -18 Td")

        commands.append(f"({escape_pdf_text(line)}) Tj")

    commands.append("ET")

    stream = "\n".join(commands).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",

        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",

        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> "
            b"/Contents 5 0 R >>"
        ),

        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",

        (
            b"<< /Length " + str(len(stream)).encode()
            + b" >>\nstream\n" + stream + b"\nendstream"
        )
    ]

    pdf = b"%PDF-1.4\n"
    offsets = [0]

    for number, obj in enumerate(objects, start=1):

        offsets.append(len(pdf))

        pdf += (
            f"{number} 0 obj\n".encode()
            + obj
            + b"\nendobj\n"
        )

    xref_offset = len(pdf)

    pdf += (
        f"xref\n0 {len(objects) + 1}\n".encode()
        + b"0000000000 65535 f \n"
    )

    for offset in offsets[1:]:

        pdf += f"{offset:010d} 00000 n \n".encode()

    pdf += (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
        + b"startxref\n"
        + str(xref_offset).encode()
        + b"\n%%EOF"
    )

    return pdf


# ============================================================
# 5. CODING AGENT
# ============================================================

def coding_agent(design, story, introduce_bug=False):
    """
    Coding agent implements the feature using only design
    and story information.

    introduce_bug=True deliberately inverts CSV filter logic
    for Assignment 2.
    """

    story_format = story["format"]

    if story_format == "CSV":

        def export_endpoint(rows, applied_filters, columns):

            if introduce_bug:

                # DELIBERATE BUG:
                # Inverted comparison includes nonmatching rows.
                filtered = [
                    row for row in rows
                    if not all(
                        row.get(key) == value
                        for key, value in applied_filters.items()
                    )
                ]

            else:

                filtered = [
                    row for row in rows
                    if all(
                        row.get(key) == value
                        for key, value in applied_filters.items()
                    )
                ]

            lines = [",".join(columns)]

            for row in filtered:

                lines.append(
                    ",".join(
                        str(row.get(column, ""))
                        for column in columns
                    )
                )

            return "\n".join(lines)

    else:

        def export_endpoint(rows, applied_filters, columns):

            filtered = [
                row for row in rows
                if all(
                    row.get(key) == value
                    for key, value in applied_filters.items()
                )
            ]

            lines = [
                " | ".join(columns)
            ]

            for row in filtered:

                lines.append(
                    " | ".join(
                        str(row.get(column, ""))
                        for column in columns
                    )
                )

            return create_pdf(lines)

    return {
        "story_id": story["id"],
        "format": story_format,
        "design_ref": design["components"],
        "export_endpoint": export_endpoint
    }


# ============================================================
# 6. TESTING AGENT
# ============================================================

def testing_agent(story):
    """
    Tests are generated from acceptance criteria ONLY.

    The testing agent does not receive or inspect code.
    This function is unchanged between the correct and
    deliberately buggy coding runs.
    """

    acceptance_criteria = story["acceptance_criteria"]

    def test_suite(export_fn):

        rows = [
            {"region": "North", "sales": 100},
            {"region": "South", "sales": 200},
            {"region": "North", "sales": 150}
        ]

        columns = ["region", "sales"]

        output = export_fn(
            rows,
            {"region": "North"},
            columns
        )

        results = []

        if story["format"] == "CSV":

            results.append((
                "produces output",
                len(output) > 0
            ))

            results.append((
                "header matches columns",
                output.splitlines()[0] == "region,sales"
            ))

            results.append((
                "only filtered rows present",
                all(
                    "South" not in line
                    for line in output.splitlines()[1:]
                )
            ))

        else:

            pdf_text = output.decode("latin-1")

            results.append((
                "produces valid PDF output",
                pdf_text.startswith("%PDF-1.4")
            ))

            results.append((
                "PDF header matches columns",
                "region | sales" in pdf_text
            ))

            results.append((
                "only filtered rows present",
                "North" in pdf_text and "South" not in pdf_text
            ))

        return results, acceptance_criteria

    return test_suite


# ============================================================
# 7. REVIEW AGENT
# ============================================================

def review_agent(design, code, test_results):

    issues = []

    if design["story_id"] != code["story_id"]:

        issues.append(
            "design and code story IDs do not match"
        )

    if len(code["design_ref"]) < 2:

        issues.append(
            "design under-specified: fewer than 2 components"
        )

    if not all(passed for _, passed in test_results):

        issues.append(
            "one or more independent tests failed"
        )

    return {
        "story_id": code["story_id"],
        "issues": issues,
        "clean": len(issues) == 0
    }


# ============================================================
# 8. HUMAN FINAL DECISION
# ============================================================

def human_final_decision(review):

    print(
        "\n[HUMAN CHECKPOINT] "
        "Final accept/reject based on review + tests..."
    )

    decision = "accept" if review["clean"] else "reject"

    print(f" Decision: {decision}")

    return decision


# ============================================================
# 9. DOCUMENTATION AGENT
# ============================================================

def docs_agent(story):

    if story["format"] == "CSV":

        return (
            f"Usage: click 'Export' on the reports page "
            f"to download the filtered view as CSV. "
            f"({story['id']})"
        )

    return (
        f"Usage: click 'Export PDF' on the reports page "
        f"to download the filtered view as PDF. "
        f"({story['id']})"
    )


# ============================================================
# 10. RELEASE AGENT
# ============================================================

def release_agent(decision, story):

    if decision != "accept":

        return {
            "story_id": story["id"],
            "released": False,
            "reason": "review did not pass"
        }

    return {
        "story_id": story["id"],
        "released": True,
        "release_note": (
            f"Added {story['format']} export ({story['id']})."
        ),
        "rollback_plan": (
            "Revert to previous reports-page build "
            "if export errors spike post-release."
        )
    }


# ============================================================
# 11. PROCESS ONE STORY THROUGH THE SDLC PIPELINE
# ============================================================

def process_story(story, introduce_bug=False):

    # Design
    design = design_agent(story)

    # Coding
    code = coding_agent(
        design,
        story,
        introduce_bug=introduce_bug
    )

    # Testing is created from story only.
    test_suite = testing_agent(story)

    # Implementation is passed to the test suite externally.
    test_results, acceptance_criteria = test_suite(
        code["export_endpoint"]
    )

    # Review
    review = review_agent(
        design,
        code,
        test_results
    )

    # Human decision
    decision = human_final_decision(review)

    # Documentation
    docs = docs_agent(story)

    # Release
    release = release_agent(
        decision,
        story
    )

    return {
        "story": story,
        "design": design,
        "code": code,
        "acceptance_criteria": acceptance_criteria,
        "test_results": test_results,
        "review": review,
        "decision": decision,
        "docs": docs,
        "release": release
    }


# ============================================================
# 12. DISPLAY PIPELINE RESULTS AND LINEAGE
# ============================================================

def display_results(results):

    for result in results:

        story = result["story"]
        story_id = story["id"]

        print("\n" + "=" * 65)
        print(f"STORY: {story_id} - {story['format']} EXPORT")
        print("=" * 65)

        print("\nDesign:")
        print(result["design"])

        print("\n=== Test results ===")
        print(
            "Acceptance criteria tested:",
            result["acceptance_criteria"]
        )

        for name, passed in result["test_results"]:

            print(
                f" [{'PASS' if passed else 'FAIL'}] {name}"
            )

        print("\nReview:")
        print(result["review"])

        print("\nDecision:")
        print(result["decision"])

        print("\nDocs:")
        print(result["docs"])

        print("\nRelease:")
        print(result["release"])

    print("\n=== LINEAGE ===")

    for result in results:

        story_id = result["story"]["id"]

        print(
            f"stories[{story_id}] <- "
            "requirement_agent(feature_request)"
        )

        print(
            f"design[{story_id}] <- "
            f"design_agent(story[{story_id}])"
        )

        print(
            f"code[{story_id}] <- "
            f"coding_agent(design[{story_id}], story[{story_id}])"
        )

        print(
            f"tests[{story_id}] <- "
            f"testing_agent(story[{story_id}]) "
            "[independent of code]"
        )

        print(
            f"review[{story_id}] <- "
            f"review_agent(design[{story_id}], "
            f"code[{story_id}], tests[{story_id}])"
        )

        print(
            f"release[{story_id}] <- "
            f"release_agent(decision, story[{story_id}])"
        )


# ============================================================
# 13. RUN PIPELINE
# ============================================================

def run_pipeline(stories, bug_story_ids=None):

    if bug_story_ids is None:
        bug_story_ids = set()

    # First human checkpoint
    human_confirms_stories(stories)

    print("\n[SDLC] Processing independent story branches...")

    # Process independent stories concurrently.
    with ThreadPoolExecutor(
        max_workers=len(stories)
    ) as executor:

        futures = [
            executor.submit(
                process_story,
                story,
                story["id"] in bug_story_ids
            )
            for story in stories
        ]

        results = [
            future.result()
            for future in futures
        ]

    display_results(results)

    return results


# ============================================================
# 14. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n" + "#" * 65)
    print("LAB 11: AGENTIC SDLC FACTORY")
    print("#" * 65)

    # Generate stories
    all_stories = requirement_agent(FEATURE_REQUEST)

    csv_story = all_stories[0]
    pdf_story = all_stories[1]

    # --------------------------------------------------------
    # ORIGINAL PRACTICAL + ASSIGNMENT 1
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 65)
    print("ASSIGNMENT 1: SECOND CONCURRENT STORY")
    print("=" * 65)

    print("\nProcessing CSV and PDF stories with correct code.")

    assignment1_results = run_pipeline(
        [csv_story, pdf_story]
    )

    assignment1_passed = all(
        result["review"]["clean"]
        and result["release"]["released"]
        for result in assignment1_results
    )

    csv_attributed = (
        assignment1_results[0]["design"]["story_id"] == "US-1"
        and assignment1_results[0]["code"]["story_id"] == "US-1"
    )

    pdf_attributed = (
        assignment1_results[1]["design"]["story_id"] == "US-2"
        and assignment1_results[1]["code"]["story_id"] == "US-2"
    )

    print("\n=== ASSIGNMENT 1 VALIDATION ===")

    print(
        "CSV story pipeline:",
        "PASS" if csv_attributed else "FAIL"
    )

    print(
        "PDF story pipeline:",
        "PASS" if pdf_attributed else "FAIL"
    )

    print(
        "Both stories released:",
        "PASS" if assignment1_passed else "FAIL"
    )

    # --------------------------------------------------------
    # ASSIGNMENT 2
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 65)
    print("ASSIGNMENT 2: DELIBERATE BUG DETECTION")
    print("=" * 65)

    print(
        "\nIntroducing an inverted filter bug "
        "inside coding_agent."
    )

    print(
        "testing_agent remains unchanged and independent."
    )

    assignment2_results = run_pipeline(
        [csv_story],
        bug_story_ids={"US-1"}
    )

    bug_result = assignment2_results[0]

    failed_tests = [
        name
        for name, passed in bug_result["test_results"]
        if not passed
    ]

    assignment2_passed = (
        len(failed_tests) > 0
        and not bug_result["review"]["clean"]
        and bug_result["decision"] == "reject"
        and not bug_result["release"]["released"]
    )

    print("\n=== ASSIGNMENT 2 VALIDATION ===")

    print(
        "Deliberate bug introduced:",
        "PASS"
    )

    print(
        "Independent tests detected failure:",
        "PASS" if failed_tests else "FAIL"
    )

    print("Failed tests:", failed_tests)

    print(
        "Review rejected buggy implementation:",
        "PASS" if not bug_result["review"]["clean"] else "FAIL"
    )

    print(
        "Buggy implementation blocked from release:",
        "PASS" if not bug_result["release"]["released"] else "FAIL"
    )

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 65)
    print("FINAL LAB 11 VALIDATION")
    print("=" * 65)

    print(
        "Original Practical:",
        "PASS" if assignment1_results[0]["release"]["released"] else "FAIL"
    )

    print(
        "Assignment 1 - Second Story:",
        "PASS" if assignment1_passed else "FAIL"
    )

    print(
        "Assignment 2 - Independent Bug Detection:",
        "PASS" if assignment2_passed else "FAIL"
    )

    if assignment1_passed and assignment2_passed:

        print("\nALL LAB 11 REQUIREMENTS PASSED")

    else:

        print("\nSOME LAB 11 REQUIREMENTS FAILED")
