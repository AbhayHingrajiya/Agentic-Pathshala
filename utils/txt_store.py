import json
from pathlib import Path
from threading import Lock


STORE_PATH = Path("data/storage")

# Thread-safe locks for files
file_locks = {}


def get_lock(filename: str):
    """
    Returns a thread lock for a specific file.
    """

    if filename not in file_locks:
        file_locks[filename] = Lock()

    return file_locks[filename]


def read_records(filename: str) -> list:
    """
    Read all JSON-line records from a TXT file.
    """

    path = STORE_PATH / filename

    if not path.exists():
        return []

    with open(path, "r") as f:
        lines = f.readlines()

    records = []

    for line in lines:

        line = line.strip()

        if line:
            records.append(json.loads(line))

    return records


def write_record(filename: str, record: dict):
    """
    Append a new record into a TXT file.
    """

    path = STORE_PATH / filename

    path.parent.mkdir(parents=True, exist_ok=True)

    lock = get_lock(filename)

    with lock:

        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")


def update_record(
    filename: str,
    match_key: str,
    match_value: str,
    updates: dict
):
    """
    Update records matching a condition.
    """

    path = STORE_PATH / filename

    lock = get_lock(filename)

    with lock:

        records = read_records(filename)

        updated = False

        for record in records:

            if record.get(match_key) == match_value:

                record.update(updates)
                updated = True

        with open(path, "w") as f:

            for record in records:
                f.write(json.dumps(record) + "\n")

    return updated