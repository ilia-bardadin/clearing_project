#!/usr/bin/env python3
"""Check review table and draft consistency."""
import csv
import os
import re
import sys
from pathlib import Path

def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("review")
    table_path = base / "table.csv"
    draft_path = base / "draft.md"
    lib_path = Path("paper/library")

    errors = []

    # 1. Check table exists
    if not table_path.exists():
        print("ERROR: table.csv not found")
        sys.exit(1)

    # 2. Read table
    with open(table_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("ERROR: table.csv is empty")
        sys.exit(1)

    # Collect DOIs from table
    table_dois = set()
    for i, row in enumerate(rows):
        doi = row.get("doi", "").strip()
        if not doi:
            errors.append(f"Row {i+1}: missing DOI")
        else:
            table_dois.add(doi)

        # Check PDF exists
        pdf_file = row.get("файл", "").strip().strip('"')
        if not pdf_file:
            errors.append(f"Row {i+1}: missing файл")
        else:
            pdf_path = lib_path / pdf_file
            if not pdf_path.exists():
                errors.append(f"Row {i+1}: PDF not found: {pdf_file}")

    # 3. Check draft.md references
    if draft_path.exists():
        with open(draft_path, encoding="utf-8") as f:
            draft_text = f.read()

        doi_refs = re.findall(r"\[([0-9.]+/[A-Z0-9./-]+)\]", draft_text)
        for doi in doi_refs:
            if doi not in table_dois:
                errors.append(f"draft.md references [doi:{doi}] not in table")

        # Check no extra refs
        if not doi_refs:
            errors.append("draft.md has no [doi] references")
    else:
        errors.append("draft.md not found")

    # Report
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print(f"OK: {len(rows)} rows, {len(table_dois)} unique DOIs, all PDFs present, all [doi] refs in table")
        sys.exit(0)

if __name__ == "__main__":
    main()