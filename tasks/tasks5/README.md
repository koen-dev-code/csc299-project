# CLI JSON DB

Small Python CLI application that stores simple key/value pairs in a JSON file.

Usage

```
python cli_db.py add mykey "my value"
python cli_db.py get mykey
python cli_db.py list
python cli_db.py delete mykey
```

Options

- `--db PATH` — path to JSON file (default: `.cli_db.json` next to `cli_db.py`).

Notes

- No external dependencies required — Python 3.8+ recommended.
- Data is written atomically to avoid corruption.
