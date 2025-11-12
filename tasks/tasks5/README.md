# CLI Task Manager (specs/001-cli-task-manager)

[![CI](https://github.com/koen-dev-code/csc299-project/actions/workflows/ci.yml/badge.svg)](https://github.com/koen-dev-code/csc299-project/actions/workflows/ci.yml)

[![Coverage Status](https://codecov.io/gh/koen-dev-code/csc299-project/branch/001-cli-task-manager/graph/badge.svg)](https://codecov.io/gh/koen-dev-code/csc299-project)

This folder contains the specification and implementation for a small Python-based
CLI task manager that supports adding, listing, and deleting tasks persisted to a
local JSON document.

Notes
- The coverage badge above will show actual coverage once the project is configured
  with Codecov and a CODECOV_TOKEN is provided to the CI job. The CI workflow already
  generates `coverage.xml` and uploads it as an artifact so you can manually inspect
  it from the Actions run.

Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m taskcli add "Buy milk"
python -m taskcli list
```
