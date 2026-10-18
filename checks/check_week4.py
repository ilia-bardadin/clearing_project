#!/usr/bin/env python3
"""check_week4.py — проверка онтологии и графа проекта (неделя 4, AI4Science).

Самодельная реконструкция по practice.md: формат ontology.yaml, слои графа
(классы ontology/, объекты notes/ tasks/ reports/ review/, файлы проекта),
задачи со статусами и итогами, правила с полем check (закрытый мир).

Запуск из корня проекта:
    python3 check_week4.py               # онтология + согласованность связей
    python3 check_week4.py --strict      # + заметки классов, задачи, правила, ≥10 объектов
    python3 check_week4.py --mermaid graph_view.md   # схема графа в Mermaid

Код возврата 0 — обязательные пункты выполнены, 1 — есть [ОШИБКА]
(в режиме --strict ошибкой считается и [ПРАВИЛО]).
Нужен только PyYAML.
"""
import argparse
import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML: python3 -m pip install pyyaml")

ROOT = os.getcwd()
SKIP_DIRS = {".git", ".venv", "venv", ".obsidian", "__pycache__", "node_modules",
             ".ipynb_checkpoints", ".trash"}
OBJECT_DIRS = ("notes", "tasks", "reports", "review")
CHECK_KINDS = {"some", "some_inverse", "some_inverse_any", "all_inverse", "defined",
               "defined_inverse", "defined_value", "section", "disjoint_properties"}
DONE = {"выполнена", "принята"}
LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
REL_RE = re.compile(r"^\s*[-*]\s*([^:\[\]]+?)\s*:\s*(.*\[\[.*)$")
CODE_RE = re.compile(r"`[^`]*`")


class Report:
    def __init__(self, strict):
        self.strict = strict
        self.errors = 0
        self.rules = 0

    def block(self, title):
        print(f"\n== {title} ==")

    def ok(self, msg):
        print(f"[OK] {msg}")

    def err(self, msg, items=None):
        self.errors += 1
        print(f"[ОШИБКА] {msg}")
        self._items(items)

    def rule(self, msg, items=None):
        self.rules += 1
        print(f"[ПРАВИЛО] {msg}")
        self._items(items)

    def tip(self, msg, items=None):
        print(f"[СОВЕТ] {msg}")
        self._items(items)

    def info(self, msg):
        print(f"  {msg}")

    @staticmethod
    def _items(items, limit=12):
        if not items:
            return
        items = sorted(set(items))
        for x in items[:limit]:
            print(f"    - {x}")
        if len(items) > limit:
            print(f"    … ещё {len(items) - limit}")


def as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


# ---------------------------------------------------------------- онтология

def check_ontology(rep):
    rep.block("Онтология")
    path = os.path.join(ROOT, "ontology.yaml")
    if not os.path.exists(path):
        rep.err("нет ontology.yaml в корне проекта")
        return None
    try:
        with open(path, encoding="utf-8") as f:
            onto = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        rep.err(f"ontology.yaml не читается как YAML: {e}")
        return None
    rep.ok("ontology.yaml читается")
    with open(path, encoding="utf-8") as f:
        placeholders = sorted(set(re.findall(r"<[^<>\n]{1,40}>", f.read())))
    if placeholders:
        rep.err("в ontology.yaml остались заготовки шаблона <…>", placeholders)

    if onto.get("ontology") and onto.get("goal"):
        rep.ok("есть ontology и goal")
    else:
        rep.err("нет поля ontology или goal")

    cq = as_list(onto.get("competency_questions"))
    if 3 <= len(cq) <= 5:
        rep.ok(f"компетентностных вопросов: {len(cq)}")
    else:
        rep.err(f"компетентностных вопросов {len(cq)}, нужно 3–5")

    classes = onto.get("classes") or {}
    if not isinstance(classes, dict):
        rep.err("classes — не словарь")
        return None
    bad_parent = [c for c, v in classes.items()
                  if (v or {}).get("parent") not in (None, *classes.keys())]
    no_def = [c for c, v in classes.items() if not (v or {}).get("definition")]
    spaces = [c for c in classes if " " in c]
    if len(classes) >= 3:
        rep.ok(f"классов: {len(classes)}")
    else:
        rep.err(f"классов {len(classes)}, нужно не меньше 3")
    for need in ("Задача", "Файл"):
        if need in classes:
            rep.ok(f"есть класс {need}")
        else:
            rep.err(f"нет класса {need}")
    if bad_parent:
        rep.err("parent указывает на необъявленный класс", bad_parent)
    else:
        rep.ok("у всех классов parent — null или объявленный класс")
    if no_def:
        rep.err("классы без definition", no_def)
    else:
        rep.ok("у всех классов есть definition")
    if spaces:
        rep.err("в имени класса пробел", spaces)
    # циклы наследования
    for c in classes:
        seen, cur = set(), c
        while cur is not None:
            if cur in seen:
                rep.err(f"цикл в иерархии классов через {c}")
                break
            seen.add(cur)
            cur = (classes.get(cur) or {}).get("parent")

    props = onto.get("properties") or {}
    bad_props = []
    for p, v in props.items():
        v = v or {}
        if "domain" not in v or "range" not in v:
            bad_props.append(f"{p}: нет domain или range")
            continue
        for k in ("domain", "range"):
            for c in as_list(v[k]):
                if c not in classes:
                    bad_props.append(f"{p}.{k}: {c} — не класс")
    if bad_props:
        rep.err("отношения с ошибками", bad_props)
    else:
        rep.ok(f"отношений: {len(props)}, у всех domain и range — объявленные классы")
    file_props = [p for p, v in props.items() if "Файл" in as_list((v or {}).get("range"))]
    if file_props:
        rep.ok(f"связи с файлами: {', '.join(file_props)}")
    else:
        rep.err("нет отношения с range: Файл (например, хранитсяВ)")
    if "подзадачаОт" in props:
        rep.ok("есть отношение подзадачаОт")
    else:
        rep.err("нет отношения подзадачаОт")

    attrs = onto.get("attributes") or {}
    st = attrs.get("status") or {}
    if st.get("domain") == "Задача" and as_list(st.get("values")):
        rep.ok(f"атрибут status: {', '.join(map(str, st['values']))}")
    else:
        rep.err("нет атрибута status с domain: Задача и списком values")
    bad_attr = [a for a, v in attrs.items() if (v or {}).get("domain") not in classes]
    if bad_attr:
        rep.err("атрибуты с необъявленным domain", bad_attr)

    rules = as_list(onto.get("rules"))
    defined_names = {(r.get("check") or {}).get("name") for r in rules if isinstance(r, dict)}
    defined_names.discard(None)
    known = set(classes) | defined_names
    bad_rules, checked = [], 0
    for r in rules:
        if not isinstance(r, dict):
            bad_rules.append(f"{r!r}: не словарь")
            continue
        rid = r.get("id", "?")
        if not r.get("text") or not r.get("dl"):
            bad_rules.append(f"{rid}: нет text или dl")
        ch = r.get("check")
        if not ch:
            continue
        checked += 1
        kind = ch.get("kind")
        if kind not in CHECK_KINDS:
            bad_rules.append(f"{rid}: неизвестный kind {kind}")
            continue
        for k in ("class", "target", "source"):
            if k in ch and ch[k] not in known:
                bad_rules.append(f"{rid}: {k} = {ch[k]} — не класс")
        for p in as_list(ch.get("property")) + as_list(ch.get("properties")):
            if p not in props and p not in attrs:
                bad_rules.append(f"{rid}: {p} — не отношение")
        if kind == "defined_value" and ch.get("attribute") not in attrs:
            bad_rules.append(f"{rid}: attribute {ch.get('attribute')} не объявлен")
    if len(rules) >= 2:
        rep.ok(f"правил: {len(rules)}, из них с check: {checked}")
    else:
        rep.err(f"правил {len(rules)}, нужно не меньше 2")
    if bad_rules:
        rep.err("правила с ошибками", bad_rules)
    elif rules:
        rep.ok("у правил есть text и dl, check ссылается на объявленные имена")
    return onto


# ---------------------------------------------------------------- граф

class Node:
    def __init__(self, rel, kind, ntype=None, meta=None, text=""):
        self.rel = rel          # путь от корня
        self.kind = kind        # класс | объект | файл
        self.type = ntype
        self.meta = meta or {}
        self.text = text
        self.edges = []         # (отношение, цель-строка, строка заметки)


def read_note(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            try:
                meta = yaml.safe_load(text[3:end]) or {}
            except yaml.YAMLError:
                meta = {"__bad__": True}
            text_body = text[end + 4:]
            return meta, text_body
    return meta, text


def scan_project():
    files = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if f.startswith("."):
                continue
            files.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    return files


def build_graph(onto, rep):
    files = scan_project()
    nodes = {}
    for rel in files:
        top = rel.split("/")[0]
        if rel.endswith(".md") and top == "ontology":
            meta, body = read_note(os.path.join(ROOT, rel))
            nodes[rel] = Node(rel, "класс", os.path.basename(rel)[:-3], meta, body)
        elif rel.endswith(".md") and top in OBJECT_DIRS:
            meta, body = read_note(os.path.join(ROOT, rel))
            if meta.get("type"):
                nodes[rel] = Node(rel, "объект", str(meta["type"]).strip(), meta, body)
            else:
                nodes[rel] = Node(rel, "файл", "Файл", meta, body)
        else:
            nodes[rel] = Node(rel, "файл", "Файл")
    # индекс разрешения ссылок, как в Obsidian: путь от корня или имя файла
    index = {}
    for rel in nodes:
        keys = {rel}
        if rel.endswith(".md"):
            keys |= {rel[:-3], os.path.basename(rel)[:-3]}
        keys.add(os.path.basename(rel))
        for k in keys:
            index.setdefault(k.lower(), []).append(rel)
    # связи из раздела «Связи»
    for n in nodes.values():
        if n.kind == "файл" or not n.text:
            continue
        in_links = False
        for line in n.text.splitlines():
            if line.startswith("## "):
                in_links = line[3:].strip().lower() == "связи"
                continue
            if not in_links:
                continue
            m = REL_RE.match(line)
            if not m:
                continue
            relname = m.group(1).strip()
            for tgt in LINK_RE.findall(CODE_RE.sub("", m.group(2))):
                n.edges.append((relname, tgt.strip(), line.strip()))
    return nodes, index


def resolve(target, index):
    t = target.strip().lower()
    hits = index.get(t) or index.get(t + ".md") or []
    return sorted(set(hits))


def is_a(t, c, classes):
    seen = set()
    while t is not None and t not in seen:
        if t == c:
            return True
        seen.add(t)
        t = (classes.get(t) or {}).get("parent")
    return False


def check_graph(onto, rep):
    rep.block("Граф проекта")
    classes = onto.get("classes") or {}
    props = onto.get("properties") or {}
    attrs = onto.get("attributes") or {}
    nodes, index = build_graph(onto, rep)

    # хранилище
    for f, key in ((".obsidian/app.json", "showUnsupportedFiles"),
                   (".obsidian/graph.json", "showAttachments")):
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            (rep.err if rep.strict else rep.tip)(f"нет {f}")
            continue
        try:
            import json
            with open(p, encoding="utf-8") as fh:
                val = json.load(fh).get(key)
        except Exception:
            val = None
        if val is True:
            rep.ok(f"{f}: {key} = true")
        else:
            rep.tip(f"{f}: {key} не true — файлы проекта не видны в графе")

    # заметки классов
    class_notes = {n.type for n in nodes.values() if n.kind == "класс"}
    missing = [c for c in classes if c not in class_notes]
    extra = [c for c in class_notes if c not in classes]
    if missing:
        (rep.err if rep.strict else rep.tip)("классы без заметки в ontology/", missing)
    elif classes:
        rep.ok(f"заметки классов: {len(class_notes)} (по числу классов)")
    if extra:
        rep.tip("заметки в ontology/ без класса в ontology.yaml", extra)

    objects = [n for n in nodes.values() if n.kind == "объект"]
    rep.info(f"объектов: {len(objects)}, файлов проекта: "
             f"{sum(1 for n in nodes.values() if n.kind == 'файл')}")

    unknown_types = [f"{n.rel}: {n.type}" for n in objects if n.type not in classes]
    if unknown_types:
        rep.tip("типы, которых нет в онтологии", unknown_types)

    named_as_class = [n.rel for n in objects
                      if os.path.basename(n.rel)[:-3] in classes]
    if named_as_class:
        rep.err("заметка названа как класс", named_as_class)

    bad_chars = [n.rel for n in objects if re.search(r"[\\:#|\[\]]", os.path.basename(n.rel))]
    if bad_chars:
        rep.err("в названии заметки символы \\ : # | [ ]", bad_chars)

    # строка «- тип: [[Класс]]»
    no_type_link, wrong_type_link = [], []
    for n in objects:
        tl = [tgt for rel, tgt, _ in n.edges if rel == "тип"]
        if not tl:
            no_type_link.append(n.rel)
        elif all(tgt.split("/")[-1] != n.type for tgt in tl):
            wrong_type_link.append(f"{n.rel}: type {n.type}, тип: [[{tl[0]}]]")
    if no_type_link:
        rep.err("нет строки «- тип: [[Класс]]» в разделе «Связи»", no_type_link)
    elif objects:
        rep.ok("у всех объектов есть «- тип: [[Класс]]»")
    if wrong_type_link:
        rep.err("тип в поле type и в строке «- тип:» расходятся", wrong_type_link)

    # связи по онтологии
    edges = []          # (src_rel, prop, dst_rel)
    unknown_rel, bad_dom, bad_rng, unresolved, ambiguous, to_class, bare_file = ([] for _ in range(7))
    for n in objects:
        for relname, tgt, line in n.edges:
            if relname == "тип":
                continue
            if relname not in props:
                unknown_rel.append(f"{n.rel}: {relname}")
                continue
            hits = resolve(tgt, index)
            if not hits:
                unresolved.append(f"{n.rel}: {relname} → [[{tgt}]]")
                continue
            if len(hits) > 1:
                ambiguous.append(f"{n.rel}: [[{tgt}]] → {', '.join(hits)}")
                continue
            dst = nodes[hits[0]]
            if dst.kind == "класс":
                to_class.append(f"{n.rel}: {relname} → [[{tgt}]]")
                continue
            if dst.kind == "файл" and "/" in dst.rel and "/" not in tgt:
                bare_file.append(f"{n.rel}: [[{tgt}]] → [[{dst.rel}]]")
            dom, rng = as_list(props[relname].get("domain")), as_list(props[relname].get("range"))
            if not any(is_a(n.type, c, classes) for c in dom):
                bad_dom.append(f"{n.rel} ({n.type}): {relname}, domain {dom}")
            if not any(is_a(dst.type, c, classes) for c in rng):
                bad_rng.append(f"{n.rel}: {relname} → {dst.rel} ({dst.type}), range {rng}")
            edges.append((n.rel, relname, dst.rel))
    for msg, items in (("отношения, которых нет в онтологии", unknown_rel),
                       ("связь против области определения (domain)", bad_dom),
                       ("цель связи не из области значений (range)", bad_rng),
                       ("ссылка на класс отношением — к классу ведёт только «тип»", to_class),
                       ("ссылка не разрешается: заметки или файла нет", unresolved),
                       ("ссылка неоднозначна — укажите путь от корня", ambiguous)):
        if items:
            rep.err(msg, items)
    if bare_file:
        rep.tip("ссылка на файл по имени, а не по пути от корня", bare_file)
    if objects and not any((unknown_rel, bad_dom, bad_rng, to_class, unresolved, ambiguous)):
        rep.ok(f"связей по онтологии: {len(edges)}, все согласованы с domain и range")

    linked_files = {d for _, _, d in edges if nodes[d].kind == "файл"}
    if objects:
        if linked_files:
            rep.ok(f"файлов проекта, связанных с объектами: {len(linked_files)}")
        else:
            (rep.err if rep.strict else rep.tip)("ни один файл проекта не связан с объектами")

    # атрибуты
    bad_attr = []
    for n in objects:
        for a, spec in attrs.items():
            if a in n.meta and is_a(n.type, spec.get("domain"), classes):
                if str(n.meta[a]) not in map(str, as_list(spec.get("values"))):
                    bad_attr.append(f"{n.rel}: {a} = {n.meta[a]}")
    if bad_attr:
        rep.err("значение атрибута не из списка values", bad_attr)

    if rep.strict:
        typed = [n for n in objects if n.rel not in no_type_link]
        if len(typed) >= 10:
            rep.ok(f"объектов со связью «тип»: {len(typed)} (≥ 10)")
        else:
            rep.err(f"объектов со связью «тип»: {len(typed)}, нужно не меньше 10")
    return nodes, edges, objects


# ---------------------------------------------------------------- задачи

def check_tasks(onto, nodes, rep):
    rep.block("Задачи")
    tasks = [n for n in nodes.values() if n.kind == "объект" and n.type == "Задача"]
    if not tasks:
        (rep.err if rep.strict else rep.tip)("в tasks/ нет заметок задач")
        return
    values = list(map(str, as_list(((onto.get("attributes") or {}).get("status") or {}).get("values"))))
    counts, bad_status, no_done, no_summary = {}, [], [], []
    for t in tasks:
        st = str(t.meta.get("status", "")).strip()
        counts[st] = counts.get(st, 0) + 1
        if st not in values:
            bad_status.append(f"{t.rel}: status = {st or '—'}")
        if "Готово, когда" not in t.text:
            no_done.append(t.rel)
        if st in DONE and not re.search(r"^##\s+Итог\s*$", t.text, re.M):
            no_summary.append(t.rel)
    print("  задачи по статусам:")
    for st in values + [s for s in counts if s not in values]:
        if counts.get(st):
            print(f"    {st}: {counts[st]}")
    if bad_status:
        rep.err("статус не из списка attributes.status", bad_status)
    else:
        rep.ok(f"задач: {len(tasks)}, статусы допустимые")
    if no_done:
        (rep.err if rep.strict else rep.tip)("нет строки «Готово, когда»", no_done)
    if no_summary:
        rep.err("статус «выполнена»/«принята» без раздела «## Итог»", no_summary)
    elif any(counts.get(s) for s in DONE):
        rep.ok("у выполненных и принятых задач есть раздел «Итог»")


# ---------------------------------------------------------------- правила

def check_rules(onto, nodes, edges, objects, rep):
    rep.block("Правила (закрытый мир: «не найдено» значит «не записано»)")
    classes = onto.get("classes") or {}
    rules = [r for r in as_list(onto.get("rules")) if isinstance(r, dict)]
    files = {n.rel for n in nodes.values() if n.kind == "файл"}

    def members(c):
        if c in defined:
            return defined[c]
        if c == "Файл":
            return files | {n.rel for n in objects if is_a(n.type, "Файл", classes)}
        return {n.rel for n in objects if is_a(n.type, c, classes)}

    out_e, in_e = {}, {}
    for s, p, d in edges:
        out_e.setdefault((s, p), set()).add(d)
        in_e.setdefault((d, p), set()).add(s)

    defined = {}
    for r in rules:   # сначала выводимые классы
        ch = r.get("check") or {}
        k, name = ch.get("kind"), ch.get("name")
        if not name:
            continue
        base = members(ch.get("class"))
        if k == "defined":
            tgt = members(ch.get("target"))
            defined[name] = {x for x in base if out_e.get((x, ch.get("property")), set()) & tgt}
        elif k == "defined_inverse":
            defined[name] = {x for x in base
                             if any(in_e.get((x, p)) for p in as_list(ch.get("properties")))}
        elif k == "defined_value":
            vals = set(map(str, as_list(ch.get("values"))))
            defined[name] = {x for x in base
                             if str(nodes[x].meta.get(ch.get("attribute"), "")).strip() in vals}

    for r in rules:
        rid, ch = r.get("id", "?"), r.get("check") or {}
        k = ch.get("kind")
        if not k:
            rep.info(f"{rid}: без check — скрипт не проверяет")
            continue
        if k in ("defined", "defined_inverse", "defined_value"):
            m = sorted(defined.get(ch.get("name"), set()))
            rep.ok(f"{rid}: {ch.get('name')} — {len(m)}"
                   + (": " + ", ".join(os.path.basename(x)[:-3] for x in m[:6]) if m else ""))
            continue
        cls = members(ch.get("class")) if ch.get("class") else set()
        if k == "some":
            tgt = members(ch["target"])
            bad = [x for x in cls if not (out_e.get((x, ch["property"]), set()) & tgt)]
            desc = f"нет связи {ch['property']} к {ch['target']}"
        elif k == "some_inverse":
            src = members(ch["source"])
            bad = [x for x in cls if not (in_e.get((x, ch["property"]), set()) & src)]
            desc = f"нет входящей связи {ch['property']} от {ch['source']}"
        elif k == "some_inverse_any":
            ps = as_list(ch.get("properties"))
            bad = [x for x in cls if not any(in_e.get((x, p)) for p in ps)]
            desc = f"нет входящей связи {' или '.join(ps)}"
        elif k == "all_inverse":
            src = members(ch["source"])
            bad = [f"{x} ← {s}" for x in cls for s in in_e.get((x, ch["property"]), set())
                   if s not in src]
            desc = f"связь {ch['property']} идёт не от {ch['source']}"
        elif k == "section":
            sec = ch.get("section", "")
            bad = [x for x in cls if x in nodes and not re.search(
                rf"^##\s+{re.escape(sec)}\s*$", nodes[x].text, re.M)]
            desc = f"нет раздела «## {sec}»"
        elif k == "disjoint_properties":
            p1, p2 = as_list(ch.get("properties"))[:2]
            pairs1 = {(s, d) for s, p, d in edges if p == p1}
            bad = [f"{s} → {d}" for s, p, d in edges if p == p2 and (s, d) in pairs1]
            desc = f"{p1} и {p2} соединяют одну пару"
        else:
            continue
        if bad:
            rep.rule(f"{rid}: {r.get('text', '').strip()} — {desc}", bad)
        else:
            rep.ok(f"{rid}: выполнено ({len(cls)} проверено)" if k != "disjoint_properties"
                   else f"{rid}: выполнено")


# ---------------------------------------------------------------- mermaid, git

def write_mermaid(path, nodes, edges, objects):
    ids, lines = {}, ["```mermaid", "graph LR"]

    def nid(rel):
        if rel not in ids:
            ids[rel] = f"n{len(ids)}"
            n = nodes[rel]
            label = os.path.basename(rel)[:-3] if n.kind != "файл" else rel
            label = label.replace('"', "'")
            shape = (f'(["{label}"])' if n.kind == "класс"
                     else f'["{label}"]' if n.kind == "объект" else f'[/"{label}"/]')
            lines.append(f"  {ids[rel]}{shape}")
        return ids[rel]

    class_by_name = {n.type: n.rel for n in nodes.values() if n.kind == "класс"}
    for n in objects:
        a = nid(n.rel)
        if n.type in class_by_name:
            lines.append(f"  {a} -.->|тип| {nid(class_by_name[n.type])}")
    for s, p, d in edges:
        lines.append(f"  {nid(s)} -->|{p}| {nid(d)}")
    lines.append("```")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Граф проекта\n\n" + "\n".join(lines) + "\n")
    print(f"\nСхема записана: {path}")


def check_git(rep):
    rep.block("Git")
    try:
        out = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True,
                             text=True, timeout=10)
    except Exception:
        rep.tip("git недоступен")
        return
    if out.returncode != 0:
        rep.tip("проект не в git-репозитории")
    elif out.stdout.strip():
        rep.tip("есть незакоммиченные изменения", out.stdout.strip().splitlines())
    else:
        rep.ok("рабочее дерево чистое")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true",
                    help="заметки классов, задачи, ≥10 объектов и правила — обязательны")
    ap.add_argument("--mermaid", metavar="FILE", help="записать схему графа в Mermaid")
    args = ap.parse_args()
    rep = Report(args.strict)
    print(f"Проект: {ROOT}" + ("   [режим --strict]" if args.strict else ""))
    onto = check_ontology(rep)
    if onto is None:
        print("\nОнтология не прочитана — граф не проверяется.")
        sys.exit(1)
    nodes, edges, objects = check_graph(onto, rep)
    check_tasks(onto, nodes, rep)
    check_rules(onto, nodes, edges, objects, rep)
    check_git(rep)
    if args.mermaid:
        write_mermaid(args.mermaid, nodes, edges, objects)
    failed = rep.errors + (rep.rules if args.strict else 0)
    print(f"\nОшибок: {rep.errors}, нарушений правил: {rep.rules}")
    if failed:
        print("Есть обязательные пункты, которые не выполнены.")
        sys.exit(1)
    print("Все обязательные пункты выполнены")


if __name__ == "__main__":
    main()
