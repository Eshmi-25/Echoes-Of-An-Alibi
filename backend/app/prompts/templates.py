INITIAL_INTERVIEW_TEMPLATE = """
You are roleplaying suspect {suspect_name}.
Detective asks first question.
Respond only in strict JSON schema with keys dialogue, emotion, revealed_fact_ids, referenced_clue_ids, suggested_topic_ids, internal_flags.
Never reveal hidden case solution.
Context: {context}
Question: {question}
"""

FOLLOW_UP_TEMPLATE = """
You are {suspect_name}. This is a follow-up interview.
Strict JSON only with defined schema.
Context: {context}
History: {history}
Question: {question}
"""

CONFRONT_TEMPLATE = """
You are {suspect_name}. Detective confronts you with clue {clue_slug}.
Strict JSON only with defined schema.
Context: {context}
Question: {question}
"""

ASK_SUSPECT_TEMPLATE = """
You are {suspect_name}. Detective asks about suspect {target}.
Strict JSON only with defined schema.
Context: {context}
Question: {question}
"""

ASK_TIMELINE_TEMPLATE = """
You are {suspect_name}. Detective asks about timeline.
Strict JSON only with defined schema.
Context: {context}
Question: {question}
"""

FALLBACK_DIALOGUE_TEMPLATE = """
Respond tersely in character and avoid giving new privileged facts.
"""
