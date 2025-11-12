<!--
Sync Impact Report

Version change: unknown → 0.1.0

Modified principles:
- [PRINCIPLE_1_NAME] -> I. Academic Integrity & Attribution
- [PRINCIPLE_2_NAME] -> II. Test-First Development
- [PRINCIPLE_3_NAME] -> III. Clear Interfaces & Reproducibility
- [PRINCIPLE_4_NAME] -> IV. Documentation & Observability
- [PRINCIPLE_5_NAME] -> V. Simplicity, Versioning & Breaking Changes

Added sections:
- Constraints & Security
- Development Workflow & Quality Gates

Removed sections: none

Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending (verify "Constitution Check" maps to new principles)
- .specify/templates/spec-template.md: ⚠ pending (ensure mandatory sections align with governance requirements)
- .specify/templates/tasks-template.md: ⚠ pending (task categorization aligns with principle-driven types)
- .specify/templates/agent-file-template.md: ⚠ pending (ensure generated guidelines include new principles)
- .specify/templates/checklist-template.md: ⚠ pending (ensure checklist generation considers constitution constraints)

Follow-up TODOs:
- TODO(RATIFICATION_DATE): original ratification date is unknown and must be provided.
-->

# CSC299 Project Constitution

## Core Principles

### I. Academic Integrity & Attribution
All contributors MUST follow institutional and academic integrity rules. Work submitted
to this repository MUST be original, or explicitly attributed and licensed. Any external
code, large excerpts, or datasets integrated into the project MUST include a clear
attribution line, license reference, and a short rationale recorded in the feature
spec (spec.md). Plagiarism or undisclosed reuse is not permitted and is grounds for
removal of the contribution.

Rationale: This repository is used for academic work; protecting intellectual honesty
and respecting licenses preserves the project's integrity and avoids legal issues.

### II. Test-First Development
Tests are a primary artifact. For all non-trivial features, at least one failing test
MUST exist before implementation (unit/contract/integration as appropriate). The
project REQUIRES the red–green–refactor cycle: write tests → verify they fail →
implement code to make tests pass → refactor with tests passing. Continuous
Integration (CI) MUST run the test suite on every pull request and block merges on
failures.

Rationale: Test-first development reduces regressions, clarifies requirements, and
ensures features are independently verifiable.

### III. Clear Interfaces & Reproducibility
All public interfaces (APIs, CLI, file formats, contracts) MUST be explicitly
documented in the corresponding spec and quickstart. Feature plans MUST declare
reproducibility steps (build, run, test) so another contributor can reproduce the
result from a clean environment. Outputs used for grading or evaluation MUST be
reproducible with the provided instructions.

Rationale: Clear contracts and reproducible instructions reduce integration friction
and make verification (grading, code review) straightforward.

### IV. Documentation & Observability
Documentation (README/quickstart/spec.md) MUST explain how to build, test, and run
the project. Features MUST include a short quickstart with example inputs and
expected outputs. Runtime observability (structured logs, testable error messages)
SHOULD be implemented at a level appropriate to the project scope to aid debugging.

Rationale: Well-documented projects are easier to use, review, and grade. Observability
shortens feedback loops when diagnosing failures.

### V. Simplicity, Versioning & Breaking Changes
Prefer the simplest design that satisfies requirements (YAGNI). When changes break
public contracts, the change MUST be documented in the feature spec and follow the
project's semantic versioning policy (see Governance). Deprecation MUST include a
migration note and a timeline for removal. Non-essential complexity that increases
risk or maintenance burden MUST be avoided.

Rationale: Simplicity reduces bugs and review time; explicit versioning and
deprecation policies make cross-feature coordination predictable.

## Constraints & Security

Technology choices are declared per-feature in plan.md. When a plan uses a language
or platform not previously adopted by the project, the plan MUST include a short
justification and an integration/migration strategy. Secrets (API keys, passwords)
MUST never be stored in the repository. All runtime credentials MUST be managed via
environment variables or secure secret storage and documented in quickstart.md.

Security expectations: follow least-privilege for any external services, sanitize
inputs from untrusted sources, and follow institution policies for data handling.
If personal data is used, document data sources, retention, and consent requirements
in the spec.

## Development Workflow & Quality Gates

- Pull requests MUST include a descriptive title, link to the feature spec, and the
	related tasks. PRs MUST be reviewed and approved by at least one other contributor
	(or a course maintainer) before merging.
- CI MUST pass for unit and any declared integration tests on feature branches.
- Commit messages SHOULD follow conventional style (type(scope): short description)
	to aid changelog generation, but the priority is clarity.
- Major changes that affect grading or public contracts MUST include a migration plan
	and be communicated to maintainers and evaluators in advance.

Quality gates: failing tests, missing documentation, or undisclosed external code
are blocking issues and must be resolved before merge.

## Governance

Amendments: changes to this constitution are proposed by opening a pull request
against `.specify/memory/constitution.md` that documents the proposed change,
the rationale, and any migration steps. Amendments MUST include a version bump and
an explicit rationale for the bump type (MAJOR/MINOR/PATCH) as defined below.

Approval: for this project, approval consists of either (a) merge by a designated
project maintainer or instructor, or (b) a PR with at least one approving review
from a teammate and explicit maintainer acknowledgment. For curricular/graded
artifacts, instructors retain final approval.

Versioning policy:
- MAJOR version when principles or governance language are removed or redefined in a
	backward-incompatible way.
- MINOR version when a new principle or section is added or when guidance is
	materially expanded.
- PATCH version for clarifications, wording fixes, typos, or non-semantic refinements.

Compliance review: PRs altering behavior that could affect evaluation MUST include
tests and a migration or compatibility note. The constitution supersedes local
practice; any process that conflicts with the constitution MUST be changed or the
conflict documented as a temporary exception with a sunset.

**Version**: 0.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-11-12

