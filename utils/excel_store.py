from pathlib import Path
from threading import Lock
from openpyxl import Workbook, load_workbook
from datetime import datetime

STORE_PATH = Path("data/storage")

HEADER_BG   = "1B4F72"   # dark navy
HEADER_FONT = "FFFFFF"   # white
ALT_ROW_BG  = "D6EAF8"   # pale blue
BORDER_COLOR = "AAAAAA"

file_locks: dict[str, Lock] = {}

def _get_lock(filename: str):
    if filename not in file_locks:
        file_locks[filename] = Lock()
    return file_locks[filename]

def _xlsx_path(filename: str) -> Path:
    stem = Path(filename).stem
    return STORE_PATH / f"{stem}.xlsx"

def _sheet_to_records(ws) -> tuple[list[str], list[dict]]:
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    
    headers = [str(h) for h in rows[0] if h is not None]
    records = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
        record = {headers[i]: row[i] for i in range(len(headers)) if i < len(row) and row[i] is not None}
        records.append(record)
    return headers, records

def get_lock(filename: str) -> Lock:
    return _get_lock(filename)

def read_records(filename: str) -> list[dict]:
    path = _xlsx_path(filename)
    if not path.exists():
        return []
    
    with _get_lock(filename):
        wb = load_workbook(str(path), read_only=True, data_only=True)
        ws = wb.active
        _, records = _sheet_to_records(ws)
        wb.close()
    return records

def write_record(filename: str, record: dict):
    """
    Append a new row to the existing Excel file.
    Uses whatever columns are already in the file — no reformatting.
    Creates the file with headers only if it doesn't exist yet.
    """
    path = _xlsx_path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
 
    with _get_lock(filename):
        if not path.exists():
            # First time only — create file with headers from the record
            wb = Workbook()
            ws = wb.active
            ws.append(list(record.keys()))    # header row
            ws.append(list(record.values()))  # first data row
            wb.save(str(path))
            return
 
        # File exists — just append a new row using existing column order
        wb = load_workbook(str(path))
        ws = wb.active
 
        headers, _ = _sheet_to_records(ws)
 
        # Any new key not in existing headers gets added to the end
        extra_keys = [k for k in record.keys() if k not in headers]
        if extra_keys:
            headers = headers + extra_keys
            for col_idx, h in enumerate(headers, start=1):
                ws.cell(row=1, column=col_idx, value=h)
 
        row_values = [record.get(h) for h in headers]
        ws.append(row_values)
 
        wb.save(str(path))
 
 
def update_record(
    filename: str,
    match_key: str,
    match_value,
    updates: dict,
) -> bool:
    """
    Update rows where match_key == match_value.
    Edits cells directly in place — no row deletion or recreation.
    Returns True if at least one record was updated.
    """
    path = _xlsx_path(filename)
    if not path.exists():
        return False
 
    with _get_lock(filename):
        wb = load_workbook(str(path))
        ws = wb.active
 
        headers = [str(ws.cell(row=1, column=c).value) for c in range(1, ws.max_column + 1)]
        col_map = {h: idx + 1 for idx, h in enumerate(headers)}
 
        updated = False
 
        for row in ws.iter_rows(min_row=2):
            match_col_idx = col_map.get(match_key)
            if match_col_idx is None:
                continue
 
            cell_value = ws.cell(row=row[0].row, column=match_col_idx).value
            if str(cell_value) != str(match_value):
                continue
 
            # Update only the specific cells that need changing
            for key, value in updates.items():
                if key in col_map:
                    ws.cell(row=row[0].row, column=col_map[key], value=value)
                else:
                    # New column — add header and value
                    new_col = ws.max_column + 1
                    ws.cell(row=1, column=new_col, value=key)
                    col_map[key] = new_col
                    ws.cell(row=row[0].row, column=new_col, value=value)
 
            updated = True
 
        if updated:
            wb.save(str(path))
 
    return updated
 
 
def delete_record(filename: str, match_key: str, match_value) -> bool:
    """
    Delete rows where match_key == match_value.
    Returns True if at least one row was deleted.
    """
    path = _xlsx_path(filename)
    if not path.exists():
        return False
 
    with _get_lock(filename):
        wb = load_workbook(str(path))
        ws = wb.active
 
        headers = [str(ws.cell(row=1, column=c).value) for c in range(1, ws.max_column + 1)]
        col_map = {h: idx + 1 for idx, h in enumerate(headers)}
 
        match_col = col_map.get(match_key)
        if match_col is None:
            return False
 
        rows_to_delete = [
            row[0].row for row in ws.iter_rows(min_row=2)
            if str(ws.cell(row=row[0].row, column=match_col).value) == str(match_value)
        ]
 
        for row_num in reversed(rows_to_delete):  # reverse so indices stay valid
            ws.delete_rows(row_num)
 
        if rows_to_delete:
            wb.save(str(path))
            return True
 
    return False
 
 
def get_record(filename: str, match_key: str, match_value) -> dict | None:
    """Return the first record where match_key == match_value, or None."""
    for record in read_records(filename):
        if str(record.get(match_key)) == str(match_value):
            return record
    return None
 