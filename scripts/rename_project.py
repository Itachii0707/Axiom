"""
One-click project renamer for the sovereign RAG platform.
Usage:
    python scripts/rename_project.py <NewName>

Example:
    python scripts/rename_project.py AXIOM
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def rename(new_name: str):
    clean_name = new_name.strip()
    upper_name = clean_name.upper()
    title_name = clean_name.capitalize()
    lower_name = clean_name.lower()

    print(f"[*] Rebranding platform to: {title_name} ({upper_name})")

    targets = [
        ROOT / "core" / "config.py",
        ROOT / "static" / "index.html",
        ROOT / "static" / "admin.html",
        ROOT / "static" / "chatbot.js",
        ROOT / "static" / "theme.css",
        ROOT / "README.md",
        ROOT / "run_all.bat",
        ROOT / "run_all.ps1",
        ROOT / "LICENSE",
    ]

    for path in targets:
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            # Replace case variants of Kortex
            updated = re.sub(r'\bKORTEX\b', upper_name, content)
            updated = re.sub(r'\bKortex\b', title_name, updated)
            updated = re.sub(r'\bkortex\b', lower_name, updated)
            path.write_text(updated, encoding="utf-8")
            print(f"    [+] Updated {path.name}")
        except Exception as e:
            print(f"    [-] Error updating {path.name}: {e}")

    print(f"\n[✔] Project successfully rebranded to {title_name}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/rename_project.py <NewName>")
        sys.exit(1)
    rename(sys.argv[1])

