"""Самопроверка артефакта недели 6: верификатор своей задачи с записанной методикой.

    python check_week6.py <путь к проекту>          проверка файлов и git
    python check_week6.py <путь к проекту> --run    и запуск верификатора

Скрипт читает файлы проекта и ничего в нём не меняет. Обязательные пункты соответствуют
минимуму для «зачтено»; рекомендации готовят проект к ДЗ 2. Код выхода 0, если все
обязательные пункты выполнены.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Разделы METHOD.md: ключевое слово в заголовке → что должно быть записано
SECTIONS = {
    "замысел": "вопрос и гипотеза",
    "постановка": "что меняется, что фиксируется, что измеряется",
    "данные": "источник, версия, договор о схеме",
    "верификатор": "что проверяет, команда, чего не проверяет",
    "правило принятия": "метрика, повторы, сравнение, порог",
    "пойманные ошибки": "что было не так, чем поймано, как исправлено",
}
HINT = re.compile(r"\*\([^*]*\)\*")          # подсказка шаблона: *(…)*
LABEL = re.compile(r"\*\*[^*]+\*\*:?")          # подпись поля: **Вопрос:**
TEMPLATE = Path(__file__).with_name("METHOD_TEMPLATE.md")


def normalize(line: str) -> str:
    return " ".join(line.split())


TEMPLATE_LINES = ({normalize(l) for l in TEMPLATE.read_text(encoding="utf-8").splitlines()}
                  if TEMPLATE.exists() else set())


def section_text(method: str, keyword: str) -> str:
    """Текст раздела, в заголовке которого есть ключевое слово (до следующего заголовка ##)."""
    parts = re.split(r"^##\s+", method, flags=re.M)
    for part in parts[1:]:
        title, _, body = part.partition("\n")
        if keyword in title.lower():
            return body
    return ""


def meaningful_lines(body: str, tables_only: bool = False) -> list[str]:
    """Строки раздела, которых нет в шаблоне и в которых есть что-то кроме подсказок и подписей."""
    found = []
    for line in body.splitlines():
        text = line.strip()
        if not text or normalize(text) in TEMPLATE_LINES or text.startswith(("#", ">")):
            continue
        is_row = text.startswith("|")
        if tables_only and not is_row:
            continue
        if is_row and set(text) <= set("|-: "):
            continue
        rest = LABEL.sub("", HINT.sub("", text))
        rest = re.sub(r"^[\s\-\d.]*", "", rest).replace("|", " ")
        if re.search(r"\w", rest):
            found.append(text)
    return found


def git(project: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    project = Path(args[0]).expanduser().resolve()
    run = "--run" in sys.argv
    required: list[tuple[bool, str]] = []
    advice: list[tuple[bool, str]] = []

    # 1. Методика
    method_path = project / "METHOD.md"
    method = method_path.read_text(encoding="utf-8") if method_path.exists() else ""
    required.append((bool(method), "METHOD.md в корне проекта"))
    for keyword, what in SECTIONS.items():
        body = section_text(method, keyword)
        required.append((bool(meaningful_lines(body)), f"METHOD.md, раздел «{keyword}» заполнен ({what})"))
    rule = section_text(method, "правило принятия")
    repeats = re.findall(r"(\d+)\s*(?:повтор|зер|запуск|значени[йя]\s+seed|seed)", rule.lower())
    advice.append((any(int(n) >= 3 for n in repeats), "в правиле принятия не меньше трёх повторов"))

    # 2. Верификатор и команда запуска
    checks = project / "checks"
    check_files = sorted(p for p in checks.rglob("*") if p.suffix in {".py", ".lean", ".jl", ".R", ".sh"}) if checks.is_dir() else []
    required.append((bool(check_files), "верификатор в checks/"))
    contract = next((project / n for n in ("AGENTS.md", "AGENT.md") if (project / n).exists()), None)
    contract_text = contract.read_text(encoding="utf-8") if contract else ""
    command_lines = [l for l in contract_text.splitlines() if "checks" in l and not l.lstrip().startswith("#")]
    required.append((bool(command_lines), "команда запуска верификатора в AGENTS.md (строка с checks)"))

    # 3. Пойманная ошибка: вывод «до» и «после» и запись в методике
    results = project / "results"
    before = sorted(results.glob("*before*")) if results.is_dir() else []
    after = sorted(results.glob("*after*")) if results.is_dir() else []
    required.append((bool(before) and bool(after), "вывод «до» и «после» пойманной ошибки в results/"))
    caught = section_text(method, "пойманные ошибки")
    required.append((bool(meaningful_lines(caught, tables_only=True)), "строка в таблице пойманных ошибок METHOD.md"))

    # 4. git
    code, _ = git(project, "rev-parse", "--is-inside-work-tree")
    in_git = code == 0
    required.append((in_git, "проект в git-репозитории"))
    if in_git:
        _, tracked = git(project, "ls-files", "METHOD.md")
        required.append((tracked == "METHOD.md", "METHOD.md в коммите"))
        _, tags = git(project, "tag", "-l", "exp-*")
        required.append((bool(tags), "метка эксперимента exp-*"))
        _, status = git(project, "status", "--short")
        advice.append((not status, "нет несохранённых изменений"))
        _, first_method = git(project, "log", "--reverse", "--format=%at", "--", "METHOD.md")
        _, first_results = git(project, "log", "--reverse", "--format=%at", "--", "results")
        if first_method and first_results:
            advice.append((int(first_method.split()[0]) <= int(first_results.split()[0]),
                           "методика закоммичена не позже первых результатов"))

    # 5. Запуск верификатора
    if run:
        test_like = [p for p in check_files if p.name.startswith("test_") or p.name.endswith("_test.py")]
        if test_like:
            command = [sys.executable, "-m", "pytest", "checks", "-q"]
            shown = "python -m pytest checks -q"
        else:
            script = next((p for p in check_files if p.suffix == ".py"), None)
            command = [sys.executable, str(script.relative_to(project))] if script else None
            shown = f"python {script.relative_to(project)}" if script else "—"
        if command:
            proc = subprocess.run(command, cwd=project, capture_output=True, text=True)
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-1:] or [""]
            required.append((proc.returncode == 0, f"верификатор проходит: {shown} → код {proc.returncode} ({tail[0][:70]})"))
        else:
            required.append((False, "верификатор запускается (в checks/ нет файла Python для запуска)"))

    print(f"Проект: {project}\n\nОбязательно:")
    for ok, text in required:
        print(f"  {'да ' if ok else 'НЕТ'}  {text}")
    print("\nРекомендации к ДЗ 2:")
    for ok, text in advice:
        print(f"  {'да ' if ok else 'нет'}  {text}")
    if not run:
        print("\nВерификатор не запускался: добавьте --run.")
    missing = sum(not ok for ok, _ in required)
    print(f"\nИтог: {'все обязательные пункты выполнены' if not missing else f'не выполнено обязательных пунктов: {missing}'}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
