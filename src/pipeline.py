"""Top-level pipeline orchestrator.

Chains all phases in order:
  1. contacts  — fetch + filter from Notion
  2. enrich    — web search + summarize + writeback
  3. draft     — pick template + personalize + assemble
  4. review    — stage for human approval in Notion
  5. send      — gmail send (only after explicit Approved status)

Each phase is independently runnable via its own script in scripts/.
This file wires them together for a full end-to-end run.
"""
