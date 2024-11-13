MODERATOR
-----------
Input → Analysis → Decision → Action → Update State
└── Continuous Monitoring Loop


MODERATOR FLOWS:

1. Introduction Flow:
	1. Topic & Parameters → moderate("introduction")
	2. → _generate_introduction()
	   ├── Set debate expectations
	   ├── Introduce topic importance
	   └── Establish rules
	3. → Initial State Setup
	   ├── Initialize time tracking
	   ├── Set speaker order
	   └── Reset intervention counts
	4. Final Introduction with:
	   ├── Opening statement
	   ├── Debate guidelines
	   └── Stage metadata

2. Monitoring Flow (Continuous):
	1. Debate Content → _check_intervention_needed()
	2. → Parallel Checks:
	   ├── _check_time_violation()
	   ├── _check_off_topic()
	   ├── _check_interruption()
	   └── _check_inappropriate_content()
	3. → If Issues Detected:
	   ├── _generate_intervention()
	   └── record_intervention()
	4. → State Updates:
	   ├── update_speaker_time()
	   ├── update_topic_adherence()
	   └── record_inappropriate_content()

3. Transition Flow:
	1. Current State → _determine_next_speaker()
	2. → _generate_transition()
	3. → Update Tracking:
	   ├── Update last speaker
	   └── Reset timers
4. Final Transition with:
	   ├── Acknowledgment
	   ├── Handoff
	   └── Time markers

4. Closing Flow:
	1. Debate History → _summarize_debate()
	2. → _parse_summary()
	3. → Analytics Generation:
	   ├── _calculate_speaker_balance()
	   ├── _calculate_debate_duration()
	   └── _analyze_debate_flow()
	4. → _generate_closing()
	5. Final Closing with:
	   ├── Summary
	   ├── Analytics
	   └── Conclusion


--------------------------------------------------------------------
--------------------------------------------------------------------

ModeratorAgent (Inherits from BaseAgent)
├── Core Moderation Functions
│   ├── moderate(topic, stage) 
│   │   ├── Input: topic, debate stage (intro/transition/intervention/closing)
│   │   ├── Output: moderation message, metadata, stage info
│   │   └── Purpose: Main moderation control for each stage
│   │
│   ├── get_debate_analytics()
│   │   ├── Input: debate state, metrics
│   │   ├── Output: duration, interventions, speaker balance, topic adherence
│   │   └── Purpose: Provides comprehensive debate analysis
│   │
│   └── record_intervention()
│       ├── Input: intervention type, reason
│       ├── Output: updated intervention count, state
│       └── Purpose: Tracks moderator interventions

├── Layer 1: Stage Management
│   ├── _generate_introduction(topic)
│   │   ├── Input: debate topic, parameters
│   │   ├── Output: introduction statement, expectations
│   │   └── Purpose: Opens debate session
│   │
│   ├── _generate_transition()
│   │   ├── Input: last speaker, next speaker
│   │   ├── Output: transition statement
│   │   └── Purpose: Manages speaker transitions
│   │
│   ├── _generate_intervention()
│   │   ├── Input: intervention reason, context
│   │   ├── Output: intervention statement
│   │   └── Purpose: Creates intervention messages
│   │
│   └── _generate_closing()
│       ├── Input: debate summary, metrics
│       ├── Output: closing statement, final summary
│       └── Purpose: Concludes debate session

├── Layer 2: Monitoring & Control
│   ├── _check_intervention_needed()
│   │   ├── Input: current debate state
│   │   ├── Output: need intervention (bool), reason
│   │   └── Purpose: Determines if intervention needed
│   │
│   ├── _check_time_violation()
│   │   ├── Input: current speaking time
│   │   ├── Output: violation status
│   │   └── Purpose: Monitors time limits
│   │
│   ├── _check_off_topic()
│   │   ├── Input: current content
│   │   ├── Output: topic adherence status
│   │   └── Purpose: Monitors topic relevance
│   │
│   ├── _check_interruption()
│   │   ├── Input: debate flow state
│   │   ├── Output: interruption detected
│   │   └── Purpose: Monitors speaker interruptions
│   │
│   └── _check_inappropriate_content()
│       ├── Input: speaker content
│       ├── Output: appropriateness status
│       └── Purpose: Monitors content appropriateness

├── Layer 3: Analysis & Metrics
│   ├── _calculate_speaker_balance()
│   │   ├── Input: speaker times
│   │   ├── Output: balance score
│   │   └── Purpose: Assesses speaking time fairness
│   │
│   ├── _calculate_debate_duration()
│   │   ├── Input: start/end times
│   │   ├── Output: duration metrics
│   │   └── Purpose: Tracks debate timing
│   │
│   ├── _analyze_debate_flow()
│   │   ├── Input: debate history
│   │   ├── Output: flow metrics, issues
│   │   └── Purpose: Analyzes debate progression
│   │
│   └── _summarize_debate()
│       ├── Input: debate content
│       ├── Output: key points, summary
│       └── Purpose: Creates debate summary

└── Layer 4: State Management
    ├── update_speaker_time(speaker, duration)
    │   ├── Input: speaker, time used
    │   ├── Output: updated times
    │   └── Purpose: Tracks speaker times
    │
    ├── update_topic_adherence(score)
    │   ├── Input: adherence score
    │   ├── Output: updated adherence metric
    │   └── Purpose: Updates topic tracking
    │
    ├── record_inappropriate_content()
    │   ├── Input: content incident
    │   ├── Output: updated content flags
    │   └── Purpose: Tracks content issues
    │
    └── _parse_summary(response)
        ├── Input: raw summary
        ├── Output: structured summary
        └── Purpose: Processes summary content

