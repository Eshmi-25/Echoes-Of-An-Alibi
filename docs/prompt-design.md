# Prompt Design

LLM role: dialogue actor only.

## Inputs in Prompt Context
- Suspect identity, personality, alibi, true timeline.
- Allowed lies and forbidden knowledge.
- Discovered clues and unlocked topics for current player.
- Trust and pressure values.
- Recent conversation history.

## Output Contract
Model must return JSON:
- dialogue
- emotion
- revealed_fact_ids
- referenced_clue_ids
- suggested_topic_ids
- internal_flags

## Validation and Sanitization
- Pydantic model validation.
- Unauthorized fact IDs rejected.
- Contradictions computed by deterministic engine only.
- Safe fallback templates when Ollama fails or JSON is malformed.
