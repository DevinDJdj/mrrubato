from pathlib import Path

base_path = Path("books/")

for path in base_path.rglob("*.txt"):
    print(path)