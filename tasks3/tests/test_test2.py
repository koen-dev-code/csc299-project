import importlib.util
import json
from pathlib import Path
import uuid



def _load_module_unique(src_path: Path):
    """Load the test2.py module from the given path under a unique module name.

    Returns the loaded module object.
    """
    name = f"test2_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, str(src_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_add_and_load_tasks(tmp_path):
    src = Path(__file__).resolve().parents[2] / "tasks3" / "src" / "tasks3" / "test2.py"
    mod = _load_module_unique(src)

    data_file = tmp_path / "data.json"
    # point module DATA_FILE to our temp file
    mod.DATA_FILE = str(data_file)

    # start empty
    assert mod.load_tasks() == []
    assert mod.next_id([]) == 1

    # add a task
    mod.add_task("Buy milk", description="2 liters", tags=["groceries"], date="2025-12-01")
    tasks = mod.load_tasks()
    assert len(tasks) == 1
    t = tasks[0]
    assert t["id"] == 1
    assert t["title"] == "Buy milk"
    assert t["description"] == "2 liters"
    assert t["tags"] == ["groceries"]
    assert t["date"] == "2025-12-01"
    assert t["completed"] is False


def test_mark_complete_and_remove(tmp_path):
    src = Path(__file__).resolve().parents[2] / "tasks3" / "src" / "tasks3" / "test2.py"
    mod = _load_module_unique(src)
    mod.DATA_FILE = str(tmp_path / "data2.json")

    # add two tasks
    mod.add_task("A", description="a")
    mod.add_task("B", description="b")
    tasks = mod.load_tasks()
    assert len(tasks) == 2

    # mark first complete
    mod.mark_complete(1)
    tasks = mod.load_tasks()
    assert any(t for t in tasks if t.get("id") == 1 and t.get("completed") is True)

    # remove first
    mod.remove_task(1)
    tasks = mod.load_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] != 1

    # mark remaining completed and purge
    remaining_id = tasks[0]["id"]
    mod.mark_complete(remaining_id)
    mod.remove_completed_tasks()
    assert mod.load_tasks() == []


def test_search_and_list_output(tmp_path, capsys):
    src = Path(__file__).resolve().parents[2] / "tasks3" / "src" / "tasks3" / "test2.py"
    mod = _load_module_unique(src)
    mod.DATA_FILE = str(tmp_path / "data3.json")

    mod.add_task("Buy milk", description="from the store", tags=["errands", "groceries"]) 
    mod.add_task("Call mom", description="weekly call", tags=["personal"]) 
    mod.add_task("Milk the cow", description="farm task", tags=["farm"]) 

    # search by query
    mod.search_tasks(query="milk")
    out = capsys.readouterr().out
    assert "Buy milk" in out
    assert "Milk the cow" in out

    # search by tag
    mod.search_tasks(tag="groceries")
    out = capsys.readouterr().out
    assert "Buy milk" in out

    # list tasks output contains ids and titles
    mod.list_tasks(show_all=True, sort_by="title")
    out = capsys.readouterr().out
    assert "Call mom" in out
    assert "Buy milk" in out
