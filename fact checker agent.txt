FACT CHECKER FLOWS
------------------
1. Statement Verification Flow:
	1. Debate Statement → check_statement()
	2. → _extract_claims()
	   ├── Identify verifiable claims
	   └── Structure for verification
	3. For each claim:
	   ├── Check verified_facts dictionary
	   └── If not found → _verify_claim()
	4. → Claim Verification:
	   ├── Create verification prompt
	   ├── Get LLM response
	   └── _parse_verification_response()
	5. → Results Processing:
	   ├── _calculate_confidence()
	   ├── _calculate_evidence_likelihood()
	   └── _aggregate_verification_results()
	6. Final Results with:
	   ├── Verification status
	   ├── Confidence scores
	   └── Evidence analysis

2. Memory Update Flow:
	1. Verification Result → _store_verification_result()
	2. → Update Systems:
	   ├── Add to verified_facts
	   ├── Create memory entry
	   └── Update verification goals
	3. → Update Metrics:
	   ├── Accuracy tracking
	   ├── Confidence thresholds
	   └── Performance metrics

3. Batch Verification Flow:
	1. Multiple Claims → check_claims()
	2. → Parallel Processing:
	   ├── Group similar claims
	   └── Prioritize by importance
	3. → For each group:
	   ├── _verify_claim()
	   └── Track dependencies
	4. → Results Aggregation:
	   ├── _aggregate_verification_results()
	   ├── Cross-reference findings
	   └── Generate summary
	5. Final Report with:
	   ├── Individual results
	   ├── Group patterns
	   └── Overall assessment

------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------

FactCheckerAgent (Inherits from BaseAgent)
├── Core Fact-Checking Functions
│   ├── check_statement(statement)
│   │   ├── Input: statement to verify
│   │   ├── Output: verification results, confidence
│   │   └── Purpose: Main fact-checking entry point
│   │
│   └── check_claims(claims_list)
│       ├── Input: list of claims
│       ├── Output: verification results for each
│       └── Purpose: Batch claim verification

├── Layer 1: Claim Processing
│   ├── _extract_claims(statement)
│   │   ├── Input: statement text
│   │   ├── Output: list of verifiable claims
│   │   └── Purpose: Identifies checkable claims
│   │
│   ├── _verify_claim(claim)
│   │   ├── Input: single claim
│   │   ├── Output: verification result
│   │   └── Purpose: Verifies individual claim
│   │
│   └── _store_verification_result(claim, verification)
│       ├── Input: claim and result
│       ├── Output: storage confirmation
│       └── Purpose: Stores verification data

├── Layer 2: Analysis
│   ├── _calculate_evidence_likelihood(evidence)
│   │   ├── Input: supporting evidence
│   │   ├── Output: likelihood score
│   │   └── Purpose: Scores evidence strength
│   │
│   ├── _parse_verification_response(response)
│   │   ├── Input: LLM verification response
│   │   ├── Output: structured verification
│   │   └── Purpose: Processes verification
│   │
│   └── _aggregate_verification_results(results)
│       ├── Input: multiple results
│       ├── Output: combined analysis
│       └── Purpose: Combines verifications

└── Layer 3: Confidence & Results
    ├── _calculate_confidence(claim, evidence)
    │   ├── Input: claim and evidence
    │   ├── Output: confidence score
    │   └── Purpose: Determines verification confidence
    │
    ├── _get_accuracy_label(accuracy_score)
    │   ├── Input: accuracy score
    │   ├── Output: accuracy label
    │   └── Purpose: Converts score to label
    │
    └── _update_verification_goals(verification)
        ├── Input: verification result
        ├── Output: updated goals state
        └── Purpose: Updates checking goals