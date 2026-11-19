
"""
LAB 9: DEEP RESEARCH AGENT - AI TOPIC BRIEFING

Original Practical:
    1. Define research question
    2. Store multiple sources
    3. Build evidence table
    4. Compare sources
    5. Generate executive summary
    6. Recommend next questions

Assignment 1:
    1. Add fourth source S4
    2. Detect direct contradiction between S1 and S4
    3. Explain plausible reasons for disagreement
    4. Report genuine conflict, not merely a gap

Assignment 2:
    1. Add source-quality tiers
    2. Rank sources by quality
    3. Prefer higher-quality evidence in conflicts
    4. Disclose lower-tier claims that are down-weighted

Workflow:
    Question -> Search -> Extract -> Compare -> Synthesize
"""


# ============================================================
# 1. RESEARCH QUESTION
# ============================================================

QUESTION = (
    "What are the demonstrated benefits and limitations of "
    "retrieval-augmented generation (RAG) for domain-specific "
    "question answering, as of the last year?"
)

SUCCESS_CRITERIA = (
    "At least 3 independent sources; "
    "at least 1 limitation identified; "
    "1 executive summary."
)


# ============================================================
# 2. SOURCE QUALITY RANKING - ASSIGNMENT 2
# ============================================================

QUALITY_RANK = {

    "peer-reviewed": 3,

    "independent benchmark": 2,

    "vendor blog": 1

}


# ============================================================
# 3. RESEARCH SOURCES
# ============================================================

SOURCES = [

    # SOURCE 1 - PEER-REVIEWED PAPER

    {
        "id": "S1",

        "type": "peer-reviewed paper",

        "quality_tier": "peer-reviewed",

        "date": "2026-02",

        "claim": (
            "RAG reduces hallucination rate by 41% "
            "on domain QA vs a non-retrieval baseline."
        ),

        "evidence": (
            "200 held-out questions from a medical knowledge base."
        ),

        "limitation": (
            "Small, single-domain evaluation set; "
            "may not generalize."
        )
    },


    # SOURCE 2 - VENDOR ENGINEERING BLOG

    {
        "id": "S2",

        "type": "vendor engineering blog",

        "quality_tier": "vendor blog",

        "date": "2026-04",

        "claim": (
            "RAG improves answer accuracy by 35% "
            "in an internal support-ticket QA system."
        ),

        "evidence": (
            "Internal A/B test over 10,000 tickets."
        ),

        "limitation": (
            "Funded/internal evaluation; "
            "no independent replication reported."
        )
    },


    # SOURCE 3 - INDEPENDENT BENCHMARK REPORT

    {
        "id": "S3",

        "type": "independent benchmark report",

        "quality_tier": "independent benchmark",

        "date": "2026-05",

        "claim": (
            "RAG introduces a measurable latency overhead "
            "of 200-400ms per query."
        ),

        "evidence": (
            "Benchmarked across 5 open-source RAG pipelines."
        ),

        "limitation": (
            "Latency depends heavily on retrieval index size; "
            "not tested at scale."
        )
    },


    # SOURCE 4 - DIRECTLY CONTRADICTING SOURCE
    # ASSIGNMENT 1

    {
        "id": "S4",

        "type": "independent benchmark report",

        "quality_tier": "independent benchmark",

        "date": "2026-06",

        "claim": (
            "RAG showed no measurable reduction in "
            "hallucination rate compared with a "
            "non-retrieval baseline in a legal-domain QA evaluation."
        ),

        "evidence": (
            "Evaluation using 500 held-out legal question-answering "
            "samples."
        ),

        "limitation": (
            "Different domain and retrieval configuration from S1; "
            "cross-domain replication was not reported."
        )
    }

]


# ============================================================
# 4. BUILD EVIDENCE TABLE
# ============================================================

def build_evidence_table(sources):

    return sources


# ============================================================
# 5. COMPARE RESEARCH SOURCES
# ============================================================

def compare(sources):

    agreements = []

    conflicts = []

    gaps = []


    # --------------------------------------------------------
    # ORIGINAL PRACTICAL: AGREEMENTS BETWEEN S1 AND S2
    # --------------------------------------------------------

    source_ids = {

        source["id"]: source

        for source in sources

    }

    if "S1" in source_ids and "S2" in source_ids:

        agreements.append({

            "source_ids": ["S1", "S2"],

            "finding": (
                "S1 and S2 agree that RAG improves "
                "factual or answer accuracy over a "
                "non-retrieval baseline, in different domains."
            )

        })


    # --------------------------------------------------------
    # ASSIGNMENT 1: DIRECT CONTRADICTION BETWEEN S1 AND S4
    # --------------------------------------------------------

    if "S1" in source_ids and "S4" in source_ids:

        conflicts.append({

            "source_ids": ["S1", "S4"],

            "type": "direct contradiction",

            "claim_1": source_ids["S1"]["claim"],

            "claim_4": source_ids["S4"]["claim"],

            "explanation": (
                "S1 reports a 41% reduction in hallucination, "
                "whereas S4 reports no measurable reduction."
            ),

            "possible_reason": (
                "The disagreement may result from different "
                "evaluation methodologies, different domains "
                "(medical versus legal QA), different datasets, "
                "or different retrieval configurations."
            )

        })


    # --------------------------------------------------------
    # ORIGINAL PRACTICAL: LATENCY FINDING FROM S3
    # --------------------------------------------------------

    if "S3" in source_ids:

        gaps.append({

            "source_ids": ["S3"],

            "finding": (
                "S3 reports a latency overhead of 200-400ms "
                "per query. S1 and S2 do not report latency, "
                "so this is a coverage gap rather than "
                "a direct contradiction."
            )

        })


    # --------------------------------------------------------
    # ORIGINAL PRACTICAL: NON-ENGLISH LANGUAGE GAP
    # --------------------------------------------------------

    gaps.append({

        "source_ids": [],

        "finding": (
            "No source in this set reports on RAG performance "
            "for non-English languages."
        )

    })


    return {

        "agreements": agreements,

        "conflicts": conflicts,

        "gaps": gaps

    }


# ============================================================
# 6. SOURCE QUALITY COMPARISON - ASSIGNMENT 2
# ============================================================

def evaluate_source_quality(source_1, source_2):

    rank_1 = QUALITY_RANK[
        source_1["quality_tier"]
    ]

    rank_2 = QUALITY_RANK[
        source_2["quality_tier"]
    ]

    if rank_1 > rank_2:

        preferred = source_1

        down_weighted = source_2

    elif rank_2 > rank_1:

        preferred = source_2

        down_weighted = source_1

    else:

        return {

            "preferred_source": None,

            "down_weighted_source": None,

            "decision": (
                "Both sources have equal quality tiers. "
                "No quality-based preference is assigned."
            )

        }

    return {

        "preferred_source": preferred,

        "down_weighted_source": down_weighted,

        "decision": (
            f"Lean toward {preferred['id']} because its "
            f"quality tier ({preferred['quality_tier']}) "
            f"ranks higher than {down_weighted['id']} "
            f"({down_weighted['quality_tier']})."
        )

    }


# ============================================================
# 7. SYNTHESIZE RESEARCH FINDINGS
# ============================================================

def synthesize(evidence_table, comparison):

    lines = []


    # --------------------------------------------------------
    # INDIVIDUAL SOURCE CLAIMS
    # --------------------------------------------------------

    for source in evidence_table:

        lines.append(

            f"[{source['id']}] {source['claim']}"

        )


    # --------------------------------------------------------
    # AGREEMENTS
    # --------------------------------------------------------

    for agreement in comparison["agreements"]:

        source_tag = ",".join(
            agreement["source_ids"]
        )

        lines.append(

            f"[{source_tag}] {agreement['finding']}"

        )


    # --------------------------------------------------------
    # CONFLICTS
    # --------------------------------------------------------

    for conflict in comparison["conflicts"]:

        source_tag = ",".join(
            conflict["source_ids"]
        )

        lines.append(

            f"[{source_tag}] Genuine conflict: "
            f"{conflict['explanation']}"

        )

        lines.append(

            f"[{source_tag}] Possible reason: "
            f"{conflict['possible_reason']}"

        )


    # --------------------------------------------------------
    # GAPS
    # --------------------------------------------------------

    for gap in comparison["gaps"]:

        source_tag = ",".join(
            gap["source_ids"]
        )

        if source_tag:

            lines.append(

                f"[{source_tag}] Gap: {gap['finding']}"

            )

        else:

            lines.append(

                f"[gap] {gap['finding']}"

            )


    # --------------------------------------------------------
    # ASSIGNMENT 2: QUALITY-WEIGHTED SYNTHESIS
    # --------------------------------------------------------

    source_map = {

        source["id"]: source

        for source in evidence_table

    }

    if "S1" in source_map and "S4" in source_map:

        quality_result = evaluate_source_quality(

            source_map["S1"],

            source_map["S4"]

        )

        preferred = quality_result["preferred_source"]

        down_weighted = quality_result["down_weighted_source"]


        if preferred is not None:

            lines.append(

                f"[{preferred['id']}] QUALITY-WEIGHTED CONCLUSION: "
                f"The synthesis leans toward this claim because "
                f"it has the higher source-quality tier."
            )

            lines.append(

                f"[{down_weighted['id']}] DISCLOSURE: "
                f"This lower-tier source's claim is down-weighted, "
                f"not discarded. Its contradictory finding "
                f"remains included in the evidence."
            )

        else:

            lines.append(

                "[S1,S4] No source is preferred based on "
                "quality tier because both tiers are equal."

            )


    return lines


# ============================================================
# 8. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":


    # --------------------------------------------------------
    # STEP 1: DISPLAY RESEARCH QUESTION
    # --------------------------------------------------------

    print("=== Question ===")

    print(QUESTION)

    print(
        f"Success criteria: {SUCCESS_CRITERIA}\n"
    )


    # --------------------------------------------------------
    # STEP 2: BUILD EVIDENCE TABLE
    # --------------------------------------------------------

    table = build_evidence_table(SOURCES)

    print("=== Evidence table ===")

    for row in table:

        print(row)


    # --------------------------------------------------------
    # STEP 3: COMPARE SOURCES
    # --------------------------------------------------------

    comparison = compare(table)

    print("\n=== Comparison ===")

    print(comparison)


    # --------------------------------------------------------
    # STEP 4: GENERATE EXECUTIVE SUMMARY
    # --------------------------------------------------------

    synthesis = synthesize(

        table,

        comparison

    )

    print(
        "\n=== Executive summary "
        "(every line traceable to a source) ==="
    )

    for line in synthesis:

        print(line)


    # --------------------------------------------------------
    # STEP 5: DISPLAY QUALITY RANKING
    # --------------------------------------------------------

    print("\n=== Source quality ranking ===")

    for source in table:

        print(

            f"{source['id']}: "
            f"{source['quality_tier']} "
            f"(rank {QUALITY_RANK[source['quality_tier']]})"

        )


    # --------------------------------------------------------
    # STEP 6: DISPLAY FINAL QUALITY DECISION
    # --------------------------------------------------------

    source_map = {

        source["id"]: source

        for source in table

    }

    quality_result = evaluate_source_quality(

        source_map["S1"],

        source_map["S4"]

    )

    print("\n=== Quality-weighted conflict decision ===")

    print(quality_result["decision"])


    if quality_result["down_weighted_source"]:

        print(

            "Down-weighted but not discarded:",

            quality_result["down_weighted_source"]["id"]

        )


    # --------------------------------------------------------
    # STEP 7: RECOMMENDED NEXT QUESTIONS
    # --------------------------------------------------------

    print("\n=== Recommended next questions ===")

    print(
        "- How does RAG latency scale with retrieval "
        "index size beyond the tested range?"
    )

    print(
        "- Do RAG accuracy gains hold for "
        "non-English domain QA?"
    )

    print(
        "- Why do medical and legal QA evaluations "
        "report different hallucination-reduction results?"
    )


    # --------------------------------------------------------
    # STEP 8: VALIDATION
    # --------------------------------------------------------

    print("\n=== Validation Results ===")


    # Original practical validation

    original_pass = (

        len(table) >= 3

        and len(comparison["agreements"]) > 0

        and len(synthesis) > 0

        and all(

            source["evidence"] and source["limitation"]

            for source in table

        )

    )


    # Assignment 1 validation

    assignment_1_pass = (

        "S4" in source_map

        and len(comparison["conflicts"]) > 0

        and comparison["conflicts"][0]["type"]
        == "direct contradiction"

        and len(
            comparison["conflicts"][0]["possible_reason"]
        ) > 0

    )


    # Assignment 2 validation

    assignment_2_pass = (

        all(

            source["quality_tier"] in QUALITY_RANK

            for source in table

        )

        and quality_result["preferred_source"] is not None

        and quality_result["down_weighted_source"] is not None

        and any(

            "down-weighted, not discarded" in line

            for line in synthesis

        )

    )


    print(

        "Original Practical:",

        "PASS" if original_pass else "FAIL"

    )

    print(

        "Assignment 1 - Direct Contradiction:",

        "PASS" if assignment_1_pass else "FAIL"

    )

    print(

        "Assignment 2 - Source Quality Weighting:",

        "PASS" if assignment_2_pass else "FAIL"

    )


    if (

        original_pass

        and assignment_1_pass

        and assignment_2_pass

    ):

        print("\nALL LAB 9 ASSIGNMENTS PASSED")

    else:

        print("\nPLEASE CHECK THE FAILED REQUIREMENT")
