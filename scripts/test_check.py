#!/usr/bin/env python3
"""Тесты для scripts/check.py: на чистой копии проверка проходит, на каждой поломке — падает.

Запуск: python3 scripts/test_check.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check.py"
COPY = ["README.md", "CHANGELOG.md", "tools.txt", ".claude-plugin", "plugins"]
SK = "plugins/mimora-labs/skills"


def run(root: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-I", str(CHECK), str(root)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def sub(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert old in t, f"{path}: нет фрагмента {old!r}"
    path.write_text(t.replace(old, new, 1), encoding="utf-8")


# (название, функция поломки, ожидаемая подстрока в выводе)
BREAKS = [
    ("разные версии", lambda r: sub(r / ".claude-plugin/marketplace.json", '"version": "', '"version": "9.'), "версии различаются"),
    ("скилл без name", lambda r: sub(r / SK / "ab-copy/SKILL.md", 'name: "ab-copy"\n', ""), "нет name"),
    ("name не равен папке", lambda r: sub(r / SK / "ab-copy/SKILL.md", 'name: "ab-copy"', 'name: "other"'), "не равен имени папки"),
    ("скилл без description", lambda r: sub(r / SK / "pick-audience/SKILL.md", "description:", "descr:"), "нет description"),
    ("description длиннее 1024", lambda r: sub(r / SK / "pick-audience/SKILL.md", 'description: "', 'description: "' + "я" * 1100), "максимум 1024"),
    ("неизвестный инструмент", lambda r: sub(r / SK / "check-offer/SKILL.md", "get_limits", "get_limits, fetch_secret_data(x)"), "fetch_secret_data"),
    ("команда README без скилла", lambda r: sub(r / "plugins/mimora-labs/README.md", "/mimora-labs:start", "/mimora-labs:ghost"), "без скилла"),
    ("нет раздела «Ошибки»", lambda r: sub(r / SK / "ab-copy/SKILL.md", "## Ошибки", "## Прочее"), "Ошибки"),
    ("нет записи в CHANGELOG", lambda r: sub(r / "CHANGELOG.md", "## 0.3.0", "## 0.0.1"), "CHANGELOG"),
    ("нет правила про запуск", lambda r: sub(r / SK / "check-offer/SKILL.md", "только после явного «запускай»", "без согласия"), "запускай"),
]


def main() -> int:
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "base"
        base.mkdir()
        for n in COPY:
            src = ROOT / n
            (shutil.copytree if src.is_dir() else shutil.copy)(src, base / n)
        code, out = run(base)
        if code != 0:
            print("FAIL чистая копия не проходит:\n" + out)
            return 1
        print("ok   чистая копия проходит")
        for i, (name, brk, expect) in enumerate(BREAKS):
            case = Path(tmp) / f"case{i}"
            shutil.copytree(base, case)
            brk(case)
            code, out = run(case)
            if code == 1 and expect in out:
                print(f"ok   падает: {name}")
            else:
                failed += 1
                print(f"FAIL не поймано: {name} (код {code})\n{out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
