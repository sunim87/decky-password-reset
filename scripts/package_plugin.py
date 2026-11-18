"""Create a Decky ZIP from an explicit allowlist."""
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
version = json.loads((root / "package.json").read_text(encoding="utf-8"))["version"]
files = ["main.py", "plugin.json", "package.json", "README.md", "LICENSE", "dist/index.js", "dist/index.js.map"]
output = root / f"PasswordReset-{version}.zip"
for name in files:
    if not (root / name).is_file():
        raise SystemExit(f"Missing {name}; run npm run build first")
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(root / name, "PasswordReset/" + name)
with ZipFile(output) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {"PasswordReset/" + name for name in files}
print(output.name)
