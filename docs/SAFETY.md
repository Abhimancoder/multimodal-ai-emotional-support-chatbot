# Safety & Guardrail Specification

## 1. Safety Principles
1. **Human Safety First:** When acute self-harm, suicidal ideation, or violence is detected, safety overrides conversation.
2. **Transparent Boundaries:** The AI makes it clear it is not a human, licensed therapist, or doctor.
3. **No Medical Advice:** The AI does not diagnose conditions or recommend/alter prescription drugs.

## 2. Crisis Intervention Protocol
When input matches crisis keywords or semantic patterns:
1. Short-circuit the LLM call.
2. Return a pre-configured compassionate message:
   - Empathize without romanticizing or interrogating.
   - Provide the 988 Suicide & Crisis Lifeline (call/text 988).
   - Provide the Crisis Text Line (text HOME to 741741).
   - Direct to international emergency services (911, 112).
3. Log event to `safety_events` table (metadata only, no raw PII).

## 3. Input & Output Guardrails
- **Prompt Injection Defense:** Wrap user queries and retrieved context in explicit XML tags; instruct the system prompt to ignore instructions attempting to override safety rules.
- **Output Validation:** Post-process assistant response to ensure it does not generate clinical diagnoses.
