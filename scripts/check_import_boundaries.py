from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
EXAMPLES = ROOT / "examples"

FORBIDDEN_RUNTIME_DIRS = [
    SRC / "labvision_ai",
    SRC / ("labvision" + "_domains"),
    SRC / "labvision" / "publish",
]
FORBIDDEN_IMPORT_PREFIXES = (
    "labvision" + "_domains",
    "labvision" + ".publish",
    "pptx",
    "openpyxl",
)
FORBIDDEN_RUNTIME_PATTERNS = (
    "Spray" + "Pipeline",
    "Research" + "_Workbench",
    "2D" + "LIFMIE",
    "public_release" + "_blocked",
    "Private :: Do Not " + "Upload",
    "twine" + " upload",
    "license" + "_key",
    "api" + "_key",
    "--license",
    "stripe",
    "paypal",
)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def public_runtime_files() -> list[Path]:
    roots = [SRC, EXAMPLES]
    return [path for root in roots if root.exists() for path in root.rglob("*.py")]


violations: list[str] = []

for path in FORBIDDEN_RUNTIME_DIRS:
    if path.exists():
        violations.append(f"Forbidden public-runtime path exists: {path.relative_to(ROOT).as_posix()}")

for path in public_runtime_files():
    rel = path.relative_to(ROOT).as_posix()
    modules = imported_modules(path)
    for module in modules:
        if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
            violations.append(f"{rel} imports forbidden public-runtime module {module}")

runtime_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in public_runtime_files())
for pattern in FORBIDDEN_RUNTIME_PATTERNS:
    if pattern.lower() in runtime_text.lower():
        violations.append(f"Forbidden public-runtime pattern found: {pattern}")

if violations:
    for item in violations:
        print(f"VIOLATION: {item}", file=sys.stderr)
    raise SystemExit(1)

print("Import boundaries passed")
