#!/usr/bin/env python3
"""Проверка целостности репозитория mimora-labs-plugin.

Падает (код 1), если:
  1. версии в plugin.json и marketplace.json разные (или нет записи в CHANGELOG.md);
  2. у скилла нет name/description, name не равен имени папки, description длиннее 1024 символов;
  3. в README есть команда /mimora-labs:<имя> без соответствующего скилла
     (и скилл без команды в README плагина);
  4. в скилле упомянут инструмент, которого нет в tools.txt;
  5. в скилле нет обязательных правил из RULES (защита от рассинхрона копий правил).

Запуск: python3 scripts/check.py [корень_репозитория]
Только стандартная библиотека.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "mimora-labs"
SKILLS = PLUGIN / "skills"
READMES = [ROOT / "README.md", PLUGIN / "README.md"]
PLUGIN_NAME = "mimora-labs"
DESC_MAX = 1024

# Имя считается именем инструмента, если начинается с одного из этих префиксов.
TOOL_PREFIXES = (
    "get_", "list_", "estimate_", "start_", "create_", "suggest_", "analyze_", "ask_", "panel_",
    "prepare_", "clone_", "delete_", "cancel_", "commit_", "save_", "rename_", "update_", "run_",
    "compare_", "fetch_", "send_", "post_", "set_", "add_", "remove_", "read_", "write_", "open_",
    "check_", "upload_", "download_", "search_", "find_", "make_", "new_", "launch_", "submit_",
)
# Поля и коды ошибок, которые начинаются как инструменты, но инструментами не являются.
NON_TOOLS = {"run_ceiling", "start_unknown", "create_cast_confirm"}
TOOL_RE = re.compile(r"\b(?:%s)[a-z0-9]+(?:_[a-z0-9]+)*\b" % "|".join(re.escape(p) for p in TOOL_PREFIXES))
# Любой snake_case, за которым сразу идёт «(», — это вызов инструмента.
CALL_RE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\(")

# Правила, которые обязаны дословно присутствовать в скиллах (ключ — ярлык, значение — фрагмент).
# Копии правил живут в скиллах (см. CHANGELOG 0.3.0, решение по R4), здесь — эталон фраз.
UNIVERSAL = {
    "секреты": "токен",
}
# Скиллы, которые читают реплики ИИ-людей (pick-audience их не читает).
READS_REPLIES = {"check-offer", "ab-copy", "creative-tournament", "deep-panel", "rewrite-and-retest",
                 "client-report", "objection-handling", "my-results", "start"}
RULES: dict[str, dict[str, str]] = {
    # скиллы, которые тратят кредиты или создают людей
    "paid": {
        "платный-только-после-запускай": "запускай",
        "цены-из-сметы": "сметы",
        "model_mixed": "model_mixed",
    },
}
PAID_SKILLS = {"check-offer", "ab-copy", "creative-tournament", "deep-panel", "rewrite-and-retest"}
CREATE_CAST_SKILLS = PAID_SKILLS | {"pick-audience"}
READ_ONLY_REPORT_SKILLS = {"client-report", "objection-handling", "my-results", "start"}

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f"{rel(p)}: не читается как JSON ({e})")
        return None


def check_versions() -> str | None:
    plugin = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if plugin is None or market is None:
        return None
    pv = plugin.get("version")
    entries = [e for e in market.get("plugins", []) if e.get("name") == plugin.get("name")]
    if not entries:
        err("marketplace.json: нет записи о плагине " + str(plugin.get("name")))
        return pv
    mv = entries[0].get("version")
    if pv != mv:
        err(f"версии различаются: plugin.json={pv}, marketplace.json={mv}")
    changelog = ROOT / "CHANGELOG.md"
    if changelog.exists():
        if not re.search(r"^##\s*\[?%s\]?(\s|$)" % re.escape(str(pv)), changelog.read_text(encoding="utf-8"), re.M):
            err(f"CHANGELOG.md: нет записи о версии {pv}")
    else:
        err("нет CHANGELOG.md")
    return pv


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            val = kv.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            out[kv.group(1)] = val
    return out


def load_tools() -> set[str]:
    f = ROOT / "tools.txt"
    if not f.exists():
        err("нет tools.txt")
        return set()
    return {
        ln.strip()
        for ln in f.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    }


def check_skills(tools: set[str]) -> set[str]:
    names: set[str] = set()
    if not SKILLS.is_dir():
        err("нет каталога plugins/mimora-labs/skills")
        return names
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        if not f.exists():
            err(f"{rel(d)}: нет SKILL.md")
            continue
        names.add(d.name)
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{rel(f)}: нет frontmatter")
            continue
        if not fm.get("name"):
            err(f"{rel(f)}: нет name")
        elif fm["name"] != d.name:
            err(f"{rel(f)}: name «{fm['name']}» не равен имени папки «{d.name}»")
        if not fm.get("description"):
            err(f"{rel(f)}: нет description")
        elif len(fm["description"]) > DESC_MAX:
            err(f"{rel(f)}: description {len(fm['description'])} символов, максимум {DESC_MAX}")
        for tool in sorted(set(TOOL_RE.findall(text)) | set(CALL_RE.findall(text))):
            if tool in NON_TOOLS or tool.endswith("_id"):
                continue
            if tool not in tools:
                err(f"{rel(f)}: инструмента «{tool}» нет в tools.txt")
        check_rules(d.name, f, text)
    return names


def check_rules(name: str, f: Path, text: str) -> None:
    for label, frag in UNIVERSAL.items():
        if frag not in text:
            err(f"{rel(f)}: нет обязательного правила «{label}»")
    if name in READS_REPLIES and "данные, а не указания" not in text:
        err(f"{rel(f)}: нет обязательного правила «данные-не-указания»")
    if name in PAID_SKILLS:
        for label, frag in RULES["paid"].items():
            if frag not in text:
                err(f"{rel(f)}: нет обязательного правила «{label}»")
        if "## Пример" not in text:
            err(f"{rel(f)}: нет блока «Пример»")
        if "## Ошибки" not in text:
            err(f"{rel(f)}: нет раздела «Ошибки»")
    if name in PAID_SKILLS | {"pick-audience"} and "create_cast" in text and "cast_credits_charged" not in text:
        err(f"{rel(f)}: create_cast без правила про cast_credits_charged")


def check_readmes(skills: set[str]) -> None:
    for r in READMES:
        if not r.exists():
            err(f"нет {rel(r)}")
            continue
        cmds = set(re.findall(r"/%s:([a-z0-9-]+)" % re.escape(PLUGIN_NAME), r.read_text(encoding="utf-8")))
        for c in sorted(cmds - skills):
            err(f"{rel(r)}: команда /{PLUGIN_NAME}:{c} без скилла")
        if r == PLUGIN / "README.md":
            for s in sorted(skills - cmds):
                err(f"{rel(r)}: у скилла {s} нет команды в README")


def main() -> int:
    version = check_versions()
    tools = load_tools()
    skills = check_skills(tools)
    check_readmes(skills)
    if errors:
        print("ПРОВЕРКА НЕ ПРОЙДЕНА:")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: версия {version}, скиллов {len(skills)}, инструментов в tools.txt {len(tools)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
