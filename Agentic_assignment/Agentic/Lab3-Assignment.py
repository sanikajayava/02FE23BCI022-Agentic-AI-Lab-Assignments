
"""
LAB 3: SKILL CREATION — RESEARCH SUMMARY SKILL

Includes:
1. Original practical: summarize two different articles.
2. Assignment 1: handle a multi-claim article and select the
   claim with the strongest supporting evidence.
3. Assignment 2: handle a low-evidence article without
   fabricating evidence or limitations.
4. Reusability and no-fabrication checks.

Run:
    python Lab3.py
"""

import re


# ============================================================
# PART 1: ORIGINAL TWO ARTICLES
# ============================================================

ARTICLE_A = {
    "title": "Retrieval-Augmented Generation Reduces Hallucination in Domain QA",
    "text": (
        "A recent benchmark study found that retrieval-augmented generation "
        "(RAG) reduced factual hallucination rates by 41% compared to a "
        "non-retrieval baseline on a domain-specific question-answering task. "
        "The evaluation used 200 held-out questions from a medical knowledge base. "
        "The authors note the evaluation set was small and drawn from a single "
        "domain, so results may not generalize to other domains without further testing."
    )
}

ARTICLE_B = {
    "title": "Campus Wi-Fi Upgrade Improves Peak-Hour Throughput",
    "text": (
        "Following a campus-wide Wi-Fi access point upgrade, average peak-hour "
        "throughput in the library increased by 60%. "
        "The measurement was taken over two weeks post-upgrade using the "
        "network monitoring dashboard. "
        "The report does not include measurements from other buildings on campus, "
        "so it is unclear whether the improvement is uniform across campus."
    )
}


# ============================================================
# PART 2: ASSIGNMENT 1 — MULTI-CLAIM ARTICLE
# ============================================================

ARTICLE_C = {
    "title": "Software Upgrade Improves Cost and Accuracy",
    "text": (
        "The new software reduced annual operating costs by 18%. "
        "An audit of 120 purchase invoices over six months confirmed the "
        "cost reduction compared with the previous system. "
        "The new software also improved prediction accuracy by 12%. "
        "An independent blinded test using 500 labelled records across "
        "two datasets measured the accuracy improvement. "
        "The evaluation was limited to two datasets and may not represent "
        "all real-world applications."
    )
}


# ============================================================
# PART 3: ASSIGNMENT 2 — LOW-EVIDENCE ARTICLE
# ============================================================

ARTICLE_D = {
    "title": "New Learning Application",
    "text": (
        "The new learning application improves student performance."
    )
}


# ============================================================
# PART 4: SKILL SPECIFICATION
# ============================================================

SKILL_SPEC = {
    "name": "research_summary",

    "instructions": [
        "Identify the main claim.",
        "List supporting evidence for the claim.",
        "Identify at least one limitation.",
        "Use 'not stated in source' when evidence or limitation is absent.",
        "Write a one-sentence undergraduate-level takeaway.",
        "When multiple claims exist, select the most evidence-supported claim."
    ],

    "constraints": [
        "Never present a hedged claim as an unhedged fact.",
        "Never fabricate evidence.",
        "Never fabricate limitations.",
        "Never omit the limitation field.",
        "Explicitly disclose selection between competing claims."
    ]
}


NOT_STATED = "not stated in source"


# ============================================================
# PART 5: HELPER FUNCTIONS
# ============================================================

def split_sentences(text):
    """Split article text into individual sentences."""

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def is_claim_sentence(sentence):
    """Identify sentences that make a research claim."""

    claim_words = [
        "reduced",
        "increased",
        "improved",
        "decreased",
        "enhanced",
        "caused",
        "achieved",
        "found that",
        "demonstrated",
        "shows that",
        "improves"
    ]

    sentence_lower = sentence.lower()

    return any(word in sentence_lower for word in claim_words)


def evidence_score(sentence):
    """
    Calculate a simple evidence-strength score.

    This is a transparent rule-based heuristic, not a
    scientific assessment of evidence quality.
    """

    sentence_lower = sentence.lower()
    score = 0
    reasons = []

    # Quantitative information
    if re.search(r'\d+', sentence):
        score += 2
        reasons.append("contains numerical data")

    # Research or measurement methods
    method_words = [
        "audit",
        "study",
        "test",
        "benchmark",
        "measurement",
        "measured",
        "evaluation",
        "experiment",
        "monitoring",
        "analysis"
    ]

    for word in method_words:
        if word in sentence_lower:
            score += 1
            reasons.append("mentions " + word)
            break

    # Sample or dataset information
    sample_words = [
        "questions",
        "records",
        "participants",
        "samples",
        "invoices",
        "dataset",
        "datasets"
    ]

    for word in sample_words:
        if word in sentence_lower:
            score += 1
            reasons.append("contains sample or dataset information")
            break

    # Independent or controlled evaluation
    quality_words = [
        "independent",
        "blinded",
        "held-out",
        "compared",
        "control group"
    ]

    for word in quality_words:
        if word in sentence_lower:
            score += 2
            reasons.append("mentions " + word)
            break

    # Time period
    if re.search(r'\b(days?|weeks?|months?|years?)\b', sentence_lower):
        score += 1
        reasons.append("contains a time period")

    return score, reasons


def find_limitation(sentences):
    """Find an explicitly stated limitation."""

    limitation_words = [
        "small",
        "limited",
        "limitation",
        "does not include",
        "unclear",
        "may not generalize",
        "may not represent",
        "not representative",
        "further testing",
        "without further testing"
    ]

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(word in sentence_lower for word in limitation_words):
            return sentence

    return NOT_STATED


# ============================================================
# PART 6: MAIN RESEARCH SUMMARY SKILL
# ============================================================

def apply_research_summary_skill(article):

    sentences = split_sentences(article["text"])

    # Find all potential claim sentences.
    claim_candidates = []

    for index, sentence in enumerate(sentences):

        if is_claim_sentence(sentence):

            # The next sentence is treated as the possible
            # supporting evidence for this claim.
            possible_evidence = (
                sentences[index + 1]
                if index + 1 < len(sentences)
                else NOT_STATED
            )

            if possible_evidence != NOT_STATED:
                score, reasons = evidence_score(possible_evidence)
            else:
                score, reasons = 0, []

            # Avoid treating a limitation sentence as evidence.
            if find_limitation([possible_evidence]) != NOT_STATED:
                score = 0
                reasons = []

            if possible_evidence == NOT_STATED:
                score = 0

            claim_candidates.append({
                "claim": sentence,
                "evidence": (
                    possible_evidence if score > 0 else NOT_STATED
                ),
                "score": score,
                "reasons": reasons
            })

    # Fallback if no claim pattern is detected.
    if not claim_candidates:
        claim_candidates.append({
            "claim": sentences[0] if sentences else NOT_STATED,
            "evidence": NOT_STATED,
            "score": 0,
            "reasons": []
        })

    # Select the candidate with the strongest evidence score.
    selected = max(
        claim_candidates,
        key=lambda candidate: candidate["score"]
    )

    # Find limitation from the complete article.
    limitation = find_limitation(sentences)

    # Explicitly disclose multi-claim selection.
    if len(claim_candidates) > 1:

        selection_note = (
            f"Multiple claims detected ({len(claim_candidates)}). "
            f"Selected the claim with the highest evidence score "
            f"({selected['score']})."
        )

    else:

        selection_note = (
            "One main claim detected. No competing claim selection required."
        )

    # Create an undergraduate-level takeaway.
    if selected["claim"] != NOT_STATED:

        takeaway = (
            "Undergraduate takeaway: "
            + selected["claim"].rstrip(".")
            + " — interpret the result within the stated limitations."
        )

    else:

        takeaway = (
            "Undergraduate takeaway: The source does not provide "
            "enough information to identify a supported research claim."
        )

    return {
        "claim": selected["claim"],
        "evidence": selected["evidence"],
        "limitation": limitation,
        "takeaway": takeaway,
        "selection_note": selection_note,
        "evidence_score": selected["score"],
        "evidence_reasons": selected["reasons"],
        "number_of_claims": len(claim_candidates)
    }


# ============================================================
# PART 7: DISPLAY OUTPUT
# ============================================================

def print_skill_output(article, output):

    print("\n" + "=" * 75)
    print("ARTICLE:", article["title"])
    print("=" * 75)

    print("\nClaim:")
    print(output["claim"])

    print("\nSupporting Evidence:")
    print(output["evidence"])

    print("\nLimitation:")
    print(output["limitation"])

    print("\nUndergraduate Takeaway:")
    print(output["takeaway"])

    print("\nClaim Selection:")
    print(output["selection_note"])

    print("\nEvidence Score:")
    print(output["evidence_score"])

    if output["evidence_reasons"]:
        print("Evidence indicators:", ", ".join(output["evidence_reasons"]))


# ============================================================
# PART 8: REUSABILITY CHECK
# ============================================================

def reusability_check(outputs):

    required_keys = {
        "claim",
        "evidence",
        "limitation",
        "takeaway",
        "selection_note",
        "evidence_score",
        "evidence_reasons",
        "number_of_claims"
    }

    same_structure = all(
        set(output.keys()) == required_keys
        for output in outputs
    )

    all_have_limitation = all(
        output["limitation"].strip() != ""
        for output in outputs
    )

    print("\n" + "=" * 75)
    print("REUSABILITY CHECK")
    print("=" * 75)

    print("Same output structure:", same_structure)
    print("Limitation field populated in every output:", all_have_limitation)

    if same_structure and all_have_limitation:
        print("\nRESULT: SKILL IS REUSABLE")
    else:
        print("\nRESULT: SKILL NEEDS IMPROVEMENT")

    return same_structure and all_have_limitation


# ============================================================
# PART 9: ASSIGNMENT 1 CHECK
# ============================================================

def assignment_1_check(output):

    print("\n" + "=" * 75)
    print("ASSIGNMENT 1: MULTI-CLAIM VALIDATION")
    print("=" * 75)

    detected_multiple = output["number_of_claims"] >= 2

    disclosed_selection = (
        "Multiple claims detected" in output["selection_note"]
    )

    selected_evidence = output["evidence"] != NOT_STATED

    print("Multiple claims detected:", detected_multiple)
    print("Selection explicitly disclosed:", disclosed_selection)
    print("Selected claim has supporting evidence:", selected_evidence)

    if detected_multiple and disclosed_selection and selected_evidence:
        print("\nASSIGNMENT 1: PASSED")
    else:
        print("\nASSIGNMENT 1: NEEDS REVIEW")


# ============================================================
# PART 10: ASSIGNMENT 2 CHECK
# ============================================================

def assignment_2_check(output):

    print("\n" + "=" * 75)
    print("ASSIGNMENT 2: LOW-EVIDENCE VALIDATION")
    print("=" * 75)

    evidence_not_fabricated = output["evidence"] == NOT_STATED

    limitation_not_fabricated = output["limitation"] == NOT_STATED

    print("Evidence correctly marked as not stated:",
          evidence_not_fabricated)

    print("Limitation correctly marked as not stated:",
          limitation_not_fabricated)

    if evidence_not_fabricated and limitation_not_fabricated:
        print("\nASSIGNMENT 2: PASSED")
        print("No fabrication occurred.")
    else:
        print("\nASSIGNMENT 2: NEEDS REVIEW")


# ============================================================
# PART 11: MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("*" * 75)
    print("LAB 3: SKILL CREATION — RESEARCH SUMMARY SKILL")
    print("*" * 75)

    print("\nSkill Name:", SKILL_SPEC["name"])

    # Original practical: two different articles.
    output_a = apply_research_summary_skill(ARTICLE_A)
    output_b = apply_research_summary_skill(ARTICLE_B)

    print("\n\n********** ORIGINAL PRACTICAL **********")

    print_skill_output(ARTICLE_A, output_a)
    print_skill_output(ARTICLE_B, output_b)

    # Assignment 1: multi-claim article.
    output_c = apply_research_summary_skill(ARTICLE_C)

    print("\n\n********** ASSIGNMENT 1 **********")

    print_skill_output(ARTICLE_C, output_c)
    assignment_1_check(output_c)

    # Assignment 2: low-evidence article.
    output_d = apply_research_summary_skill(ARTICLE_D)

    print("\n\n********** ASSIGNMENT 2 **********")

    print("Article Text:")
    print(ARTICLE_D["text"])

    print_skill_output(ARTICLE_D, output_d)
    assignment_2_check(output_d)

    # Reusability across all four articles.
    print("\n\n********** FINAL REUSABILITY TEST **********")

    reusability_check([
        output_a,
        output_b,
        output_c,
        output_d
    ])

    print("\n" + "*" * 75)
    print("LAB 3 EXECUTION COMPLETED")
    print("*" * 75)
