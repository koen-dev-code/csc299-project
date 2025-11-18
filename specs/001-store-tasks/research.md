# Research: Store Tasks

Decision: Implement a small local CLI in Python that persists tasks to a single JSON document.

Rationale:
- The user explicitly requested Python and JSON storage; this aligns with the Simplicity principle.
- Using only the Python standard library keeps the dependency surface small and simplifies installation and review.
- A CLI-first implementation is the fastest path to deliver the P1 user story and test cases.

Alternatives considered:
- Use a lightweight embedded DB (SQLite) — offers robustness and querying but increases complexity compared to JSON for this scope.
- Use a web service (Flask/FastAPI) — enables multi-device sync but increases scope and infra requirements; out of scope for MVP.
- Use `typer`/`click` for CLI UX — improves UX and parsing but is optional; we can keep the core implementation dependency-free and add `typer` later as an opt-in enhancement.

Storage and durability:
- Store tasks in a JSON file located at a default OS-appropriate location (e.g., `%APPDATA%\tasks-cli\tasks.json` on Windows) or a configurable path via environment variable / CLI flag.
- Use atomic write: write to a temporary file and perform an atomic replace to avoid corruption on crashes.

Testing and automation:
- Use `pytest` for unit tests. Tests will run locally and be included in CI in future work.
- Tests will be written first for core operations (create, persist, update, delete, list).

Security/privacy:
- Data is stored locally in cleartext JSON. If encryption is needed later, it will be added behind a toggle/option.
