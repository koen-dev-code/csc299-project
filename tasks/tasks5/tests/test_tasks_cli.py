import os
import json
import tempfile
from ..tasks_cli.storage import JSONStorage
from ..tasks_cli.models import Task


def test_create_and_persist(tmp_path: any):
    db = tmp_path / "tasks.json"
    storage = JSONStorage(path=str(db))

    t = Task.create("Buy milk", description="2 liters")
    storage.add_task(t)

    # reload storage and ensure task present
    storage2 = JSONStorage(path=str(db))
    tasks = storage2.load()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy milk"


def test_update_and_delete(tmp_path: any):
    db = tmp_path / "tasks.json"
    storage = JSONStorage(path=str(db))

    t = Task.create("Do laundry")
    storage.add_task(t)

    # update title
    storage.update_task(t.id, title="Do laundry now")
    t2 = storage.get(t.id)
    assert t2.title == "Do laundry now"

    # complete
    storage.update_task(t.id, status="completed")
    t3 = storage.get(t.id)
    assert t3.status == "completed"

    # delete
    storage.delete_task(t.id)
    tasks = storage.load()
    assert len(tasks) == 0


def test_list_and_search(tmp_path: any):
    db = tmp_path / "tasks.json"
    storage = JSONStorage(path=str(db))

    a = Task.create("Write report", description="monthly report")
    b = Task.create("Buy milk", description="for coffee")
    storage.add_task(a)
    storage.add_task(b)

    all_tasks = storage.list_tasks()
    assert len(all_tasks) == 2

    open_tasks = storage.list_tasks(status="open")
    assert len(open_tasks) == 2

    found = storage.list_tasks(q="report")
    assert len(found) == 1
    assert found[0].title == "Write report"
