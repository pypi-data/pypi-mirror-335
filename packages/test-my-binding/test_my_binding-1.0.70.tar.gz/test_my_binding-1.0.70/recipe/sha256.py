import hashlib
from pathlib import Path

FILE = Path(__file__).parent / "test_my_binding-0.7.2.tar.gz"

with open(FILE, "rb") as f:
    data = f.read()
    h = hashlib.sha256(data).hexdigest()

print(h)
