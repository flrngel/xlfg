from __future__ import annotations

import datetime as _dt
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .runs import latest_run_id

_TYPED_KEYS = {"lex", "kind", "stage", "role", "scope", "path", "when"}
_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_QUOTED_RE = re.compile(r'(-?)"([^"]+)"')
_NEG_TERM_RE = re.compile(r"(?<!\S)-([a-z0-9_][a-z0-9_\-/]*)")
_ROLE_STAGE = {
    "query-refiner": "plan",
    "why-analyst": "plan",
    "root-cause-analyst": "plan",
    "test-strategist": "plan",
    "harness-profiler": "plan",
    "solution-architect": "plan",
    "env-doctor": "verify",
    "test-implementer": "implement",
    "task-implementer": "implement",
    "task-checker": "implement",
    "verify-reducer": "verify",
    "ux-reviewer": "review",
    "architecture-reviewer": "review",
    "security-reviewer": "review",
    "performance-reviewer": "review",
}
_RUN_STAGE_BY_NAME = {
    "query-contract": "plan",
    "why": "plan",
    "context": "plan",
    "repo-map": "plan",
    "brainstorm": "plan",
    "research": "plan",
    "risk": "plan",
    "harness-profile": "plan",
    "diagnosis": "plan",
    "solution-decision": "plan",
    "flow-spec": "plan",
    "spec": "plan",
    "plan": "plan",
    "test-contract": "plan",
    "workboard": "cross",
    "env-plan": "verify",
    "proof-map": "verify",
    "scorecard": "verify",
    "verification": "verify",
    "verify-fix-plan": "verify",
    "review-summary": "review",
    "compound-summary": "compound",
    "current-state-candidate": "compound",
    "run-summary": "compound",
    "task-brief": "implement",
    "implementer-report": "implement",
    "checker-report": "implement",
    "test-report": "implement",
}
_KNOWLEDGE_KIND = {
    "current-state": ("state-brief", "cross"),
    "patterns": ("pattern", "implement"),
    "decision-log": ("decision", "plan"),
    "testing": ("testing", "verify"),
    "ux-flows": ("ux-flow", "plan"),
    "failure-memory": ("failure", "verify"),
    "harness-rules": ("harness-rule", "verify"),
    "quality-bar": ("quality-bar", "cross"),
    "ledger": ("memory-event", "cross"),
    "queries": ("query-syntax", "cross"),
}


@dataclass(slots=True)
class LexQuery:
    raw: str = ""
    positive_terms: List[str] = field(default_factory=list)
    negative_terms: List[str] = field(default_factory=list)
    positive_phrases: List[str] = field(default_factory=list)
    negative_phrases: List[str] = field(default_factory=list)

    @property
    def has_terms(self) -> bool:
        return bool(self.positive_terms or self.positive_phrases)


@dataclass(slots=True)
class RecallQuery:
    mode: str = "search"  # search | temporal
    lex: LexQuery = field(default_factory=LexQuery)
    kinds: List[str] = field(default_factory=list)
    stages: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    path_filters: List[str] = field(default_factory=list)
    when_raw: Optional[str] = None
    time_range: Optional[Tuple[_dt.datetime, _dt.datetime]] = None
    raw: str = ""


@dataclass(slots=True)
class MemoryDoc:
    id: str
    scope: str
    path: str
    title: str
    body: str
    kind: str
    stage: str
    role: Optional[str]
    timestamp: Optional[_dt.datetime]
    source: str
    run_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunSummary:
    run_id: str
    timestamp: _dt.datetime
    request: str
    path: str
    phases_present: List[str]


class RecallParseError(ValueError):
    pass


DAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _now() -> _dt.datetime:
    return _dt.datetime.now().replace(microsecond=0)


def parse_date_expr(expr: str, now: Optional[_dt.datetime] = None) -> Tuple[_dt.datetime, _dt.datetime]:
    expr = " ".join(expr.strip().lower().split())
    now = now or _now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if expr == "today":
        return today, today + _dt.timedelta(days=1)
    if expr == "yesterday":
        start = today - _dt.timedelta(days=1)
        return start, today
    if expr == "this week":
        monday = today - _dt.timedelta(days=today.weekday())
        return monday, today + _dt.timedelta(days=1)
    if expr == "last week":
        this_monday = today - _dt.timedelta(days=today.weekday())
        last_monday = this_monday - _dt.timedelta(days=7)
        return last_monday, this_monday

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", expr)
    if m:
        start = _dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return start, start + _dt.timedelta(days=1)

    m = re.fullmatch(r"(\d+)\s+days?\s+ago", expr)
    if m:
        start = today - _dt.timedelta(days=int(m.group(1)))
        return start, start + _dt.timedelta(days=1)

    m = re.fullmatch(r"last\s+(\d+)\s+days?", expr)
    if m:
        days = int(m.group(1))
        start = today - _dt.timedelta(days=days)
        return start, today + _dt.timedelta(days=1)

    m = re.fullmatch(r"last\s+(\d+)\s+weeks?", expr)
    if m:
        weeks = int(m.group(1))
        start = today - _dt.timedelta(days=7 * weeks)
        return start, today + _dt.timedelta(days=1)

    m = re.fullmatch(r"last\s+([a-z]+)", expr)
    if m and m.group(1) in DAY_NAMES:
        target = DAY_NAMES[m.group(1)]
        delta = (today.weekday() - target) % 7
        if delta == 0:
            delta = 7
        start = today - _dt.timedelta(days=delta)
        return start, start + _dt.timedelta(days=1)

    raise RecallParseError(f"Unsupported date expression: {expr}")


def _split_values(raw: str) -> List[str]:
    parts: List[str] = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece:
            continue
        parts.extend([x.strip().lower() for x in piece.split() if x.strip()])
    return parts


def parse_lex_query(text: str) -> LexQuery:
    raw = text.strip()
    if not raw:
        return LexQuery(raw="")

    positive_phrases: List[str] = []
    negative_phrases: List[str] = []
    consumed_spans: List[Tuple[int, int]] = []
    for m in _QUOTED_RE.finditer(raw):
        sign, phrase = m.group(1), m.group(2).strip().lower()
        if not phrase:
            continue
        if sign == "-":
            negative_phrases.append(phrase)
        else:
            positive_phrases.append(phrase)
        consumed_spans.append((m.start(), m.end()))

    masked = list(raw)
    for start, end in consumed_spans:
        for i in range(start, end):
            masked[i] = " "
    masked_text = "".join(masked).lower()

    negative_terms = [m.group(1).lower() for m in _NEG_TERM_RE.finditer(masked_text)]
    masked_text = _NEG_TERM_RE.sub(" ", masked_text)
    positive_terms = [t for t in _TOKEN_RE.findall(masked_text) if t]

    return LexQuery(
        raw=raw,
        positive_terms=positive_terms,
        negative_terms=negative_terms,
        positive_phrases=positive_phrases,
        negative_phrases=negative_phrases,
    )


def parse_query(query: str, now: Optional[_dt.datetime] = None) -> RecallQuery:
    raw = query.strip()
    if not raw:
        return RecallQuery(raw="")

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    typed = all(":" in line and line.split(":", 1)[0].strip().lower() in _TYPED_KEYS for line in lines)

    rq = RecallQuery(raw=raw)

    if typed and lines:
        for line in lines:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "lex":
                rq.lex = parse_lex_query(value)
            elif key == "kind":
                rq.kinds.extend(_split_values(value))
            elif key == "stage":
                rq.stages.extend(_split_values(value))
            elif key == "role":
                rq.roles.extend(_split_values(value))
            elif key == "scope":
                rq.scopes.extend(_split_values(value))
            elif key == "path":
                rq.path_filters.extend([x.strip().lower() for x in value.split(",") if x.strip()])
            elif key == "when":
                rq.when_raw = value
        if rq.when_raw:
            try:
                rq.time_range = parse_date_expr(rq.when_raw, now=now)
            except RecallParseError:
                rq.time_range = None
        if rq.when_raw and not rq.lex.has_terms and not rq.kinds and not rq.roles and not rq.path_filters:
            rq.mode = "temporal"
        return rq

    try:
        rq.time_range = parse_date_expr(raw, now=now)
        rq.when_raw = raw
        rq.mode = "temporal"
        return rq
    except RecallParseError:
        pass

    rq.lex = parse_lex_query(raw)
    return rq


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _first_heading(text: str) -> Optional[str]:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
        if line:
            return line[:120]
    return None


def _parse_run_timestamp(run_id: str) -> Optional[_dt.datetime]:
    m = re.match(r"(\d{8})-(\d{6})-", run_id)
    if not m:
        return None
    try:
        return _dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except Exception:
        return None


def _infer_run_stage(filename: str) -> str:
    return _RUN_STAGE_BY_NAME.get(filename, "cross")


def _infer_knowledge_kind(stem: str) -> Tuple[str, str]:
    return _KNOWLEDGE_KIND.get(stem, (stem, "cross"))


def _extract_request_from_context(context_text: str) -> str:
    lines = context_text.splitlines()
    capture = False
    chunks: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## request":
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped:
            chunks.append(stripped)
    return " ".join(chunks)[:200].strip()


def _iter_markdown_docs(root: Path) -> Iterable[MemoryDoc]:
    knowledge_dir = root / "docs" / "xlfg" / "knowledge"
    if knowledge_dir.exists():
        for path in sorted(knowledge_dir.rglob("*.md")):
            rel = str(path.relative_to(root))
            text = _read_text(path)
            if not text:
                continue
            if "agent-memory" in path.parts:
                role = path.stem.lower()
                yield MemoryDoc(
                    id=rel,
                    scope="agent-memory",
                    path=rel,
                    title=_first_heading(text) or role,
                    body=text,
                    kind="agent-memory",
                    stage=_ROLE_STAGE.get(role, "cross"),
                    role=role,
                    timestamp=_dt.datetime.fromtimestamp(path.stat().st_mtime),
                    source="markdown",
                )
                continue
            kind, stage = _infer_knowledge_kind(path.stem)
            yield MemoryDoc(
                id=rel,
                scope="knowledge",
                path=rel,
                title=_first_heading(text) or path.stem,
                body=text,
                kind=kind,
                stage=stage,
                role=None,
                timestamp=_dt.datetime.fromtimestamp(path.stat().st_mtime),
                source="markdown",
            )

    runs_dir = root / "docs" / "xlfg" / "runs"
    if runs_dir.exists():
        for run_dir in sorted([p for p in runs_dir.iterdir() if p.is_dir()]):
            run_id = run_dir.name
            ts = _parse_run_timestamp(run_id)
            for path in sorted(run_dir.rglob("*.md")):
                rel = str(path.relative_to(root))
                text = _read_text(path)
                if not text:
                    continue
                stem = path.stem.lower()
                yield MemoryDoc(
                    id=rel,
                    scope="runs",
                    path=rel,
                    title=_first_heading(text) or stem,
                    body=text,
                    kind=stem,
                    stage=_infer_run_stage(stem),
                    role=None,
                    timestamp=ts or _dt.datetime.fromtimestamp(path.stat().st_mtime),
                    source="markdown",
                    run_id=run_id,
                )

    migrations_dir = root / "docs" / "xlfg" / "migrations"
    if migrations_dir.exists():
        for path in sorted(migrations_dir.glob("*.md")):
            rel = str(path.relative_to(root))
            text = _read_text(path)
            if not text:
                continue
            yield MemoryDoc(
                id=rel,
                scope="migrations",
                path=rel,
                title=_first_heading(text) or path.stem,
                body=text,
                kind="migration",
                stage="cross",
                role=None,
                timestamp=_dt.datetime.fromtimestamp(path.stat().st_mtime),
                source="markdown",
            )


def _iter_ledger_docs(root: Path) -> Iterable[MemoryDoc]:
    ledger_path = root / "docs" / "xlfg" / "knowledge" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    docs: List[MemoryDoc] = []
    for idx, line in enumerate(ledger_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        body_parts: List[str] = []
        for key in ("title", "summary", "symptom", "root_cause", "action", "prevention", "lex"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                body_parts.append(value.strip())
        tags = data.get("tags") or []
        if isinstance(tags, list):
            body_parts.append(" ".join(str(t) for t in tags))
        evidence = data.get("evidence") or []
        if isinstance(evidence, list):
            body_parts.append(" ".join(str(e) for e in evidence))
        created_at = data.get("created_at")
        ts = None
        if isinstance(created_at, str):
            try:
                ts = _dt.datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                ts = None
        docs.append(
            MemoryDoc(
                id=str(data.get("id") or f"ledger-{idx}"),
                scope="ledger",
                path=f"docs/xlfg/knowledge/ledger.jsonl#{data.get('id') or idx}",
                title=str(data.get("title") or data.get("id") or f"ledger-{idx}"),
                body="\n".join(body_parts).strip(),
                kind=str(data.get("kind") or "memory-event").lower(),
                stage=str(data.get("stage") or _ROLE_STAGE.get(str(data.get("role") or "").lower(), "cross")).lower(),
                role=str(data.get("role")).lower() if data.get("role") else None,
                timestamp=ts,
                source="ledger",
                run_id=str(data.get("run_id")) if data.get("run_id") else None,
                extra=data,
            )
        )
    return docs


def _normalize_scope(scope: str) -> List[str]:
    scope = scope.strip().lower()
    if scope == "all" or not scope:
        return ["knowledge", "agent-memory", "ledger", "runs", "migrations"]
    if scope == "memory":
        return ["knowledge", "agent-memory", "ledger"]
    return [scope]


def _query_scopes(query: RecallQuery) -> List[str]:
    if not query.scopes:
        return ["knowledge", "agent-memory", "ledger", "runs", "migrations"]
    scopes: List[str] = []
    for scope in query.scopes:
        for expanded in _normalize_scope(scope):
            if expanded not in scopes:
                scopes.append(expanded)
    return scopes


def _matches_filters(doc: MemoryDoc, query: RecallQuery) -> bool:
    scopes = _query_scopes(query)
    if doc.scope not in scopes:
        return False
    if query.kinds and doc.kind.lower() not in query.kinds:
        return False
    if query.stages and doc.stage.lower() not in query.stages:
        return False
    if query.roles and (doc.role or "").lower() not in query.roles:
        return False
    if query.path_filters and not all(pf in doc.path.lower() for pf in query.path_filters):
        return False
    if query.time_range and doc.timestamp is not None:
        start, end = query.time_range
        if doc.timestamp < start or doc.timestamp >= end:
            return False
    return True


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _bm25_scores(docs: Sequence[MemoryDoc], query: RecallQuery) -> Dict[str, float]:
    lex = query.lex
    if not lex.has_terms:
        return {doc.id: 1.0 for doc in docs}

    tokenized: Dict[str, List[str]] = {doc.id: _tokenize(doc.title + "\n" + doc.body) for doc in docs}
    lengths = {doc_id: len(tokens) or 1 for doc_id, tokens in tokenized.items()}
    avgdl = sum(lengths.values()) / max(len(lengths), 1)

    positive_terms = list(dict.fromkeys(lex.positive_terms))
    dfs: Dict[str, int] = {}
    for term in positive_terms:
        dfs[term] = sum(1 for tokens in tokenized.values() if term in tokens)

    scores: Dict[str, float] = {}
    lower_cache = {doc.id: (doc.title + "\n" + doc.body).lower() for doc in docs}

    for doc in docs:
        text_lower = lower_cache[doc.id]
        title_lower = doc.title.lower()
        path_lower = doc.path.lower()

        if any(phrase in text_lower for phrase in lex.negative_phrases):
            continue
        if any(term in tokenized[doc.id] for term in lex.negative_terms):
            continue

        score = 0.0
        matched_any = False
        tokens = tokenized[doc.id]
        tf_counts: Dict[str, int] = {}
        for token in tokens:
            tf_counts[token] = tf_counts.get(token, 0) + 1

        for term in positive_terms:
            tf = tf_counts.get(term, 0)
            if tf <= 0:
                continue
            matched_any = True
            df = dfs.get(term, 0)
            idf = math.log(1.0 + (len(docs) - df + 0.5) / (df + 0.5)) if df else 1.0
            k1 = 1.5
            b = 0.75
            denom = tf + k1 * (1 - b + b * lengths[doc.id] / max(avgdl, 1e-9))
            score += idf * (tf * (k1 + 1) / max(denom, 1e-9))
            if term in title_lower:
                score += 1.25
            if term in path_lower:
                score += 0.75

        for phrase in lex.positive_phrases:
            count = text_lower.count(phrase)
            if count <= 0:
                continue
            matched_any = True
            score += 3.5 * count
            if phrase in title_lower:
                score += 1.5
            if phrase in path_lower:
                score += 1.0

        if not matched_any:
            continue

        if doc.source == "ledger":
            score += 0.5
        if doc.scope == "agent-memory":
            score += 0.4
        if doc.path.endswith("current-state.md"):
            score += 0.75
        if doc.path.endswith("current-state-candidate.md"):
            score += 0.9
        scores[doc.id] = score

    return scores


def _extract_snippet(doc: MemoryDoc, query: RecallQuery, max_lines: int = 5, max_chars: int = 320) -> str:
    lex = query.lex
    text = doc.body
    lines = text.splitlines()
    needles = [*lex.positive_phrases, *lex.positive_terms]
    needles = [n.lower() for n in needles if n]
    if not lines:
        return ""
    if not needles:
        snippet = " ".join(line.strip() for line in lines[:max_lines] if line.strip())
        return snippet[:max_chars]
    for idx, line in enumerate(lines):
        lower = line.lower()
        if any(n in lower for n in needles):
            start = max(0, idx - 1)
            end = min(len(lines), idx + max_lines - 1)
            snippet = "\n".join(l.rstrip() for l in lines[start:end] if l.strip())
            return snippet[:max_chars]
    snippet = " ".join(line.strip() for line in lines[:max_lines] if line.strip())
    return snippet[:max_chars]


def _run_summaries(root: Path) -> List[RunSummary]:
    runs_dir = root / "docs" / "xlfg" / "runs"
    if not runs_dir.exists():
        return []
    summaries: List[RunSummary] = []
    for run_dir in sorted([p for p in runs_dir.iterdir() if p.is_dir()]):
        ts = _parse_run_timestamp(run_dir.name)
        if ts is None:
            try:
                ts = _dt.datetime.fromtimestamp(run_dir.stat().st_mtime)
            except Exception:
                continue
        context = _read_text(run_dir / "context.md")
        request = _extract_request_from_context(context) or run_dir.name
        phases_present: List[str] = []
        for stem in ("diagnosis", "plan", "verification", "review-summary", "compound-summary"):
            if (run_dir / f"{stem}.md").exists():
                phases_present.append(stem)
        summaries.append(
            RunSummary(
                run_id=run_dir.name,
                timestamp=ts,
                request=request,
                path=str(run_dir.relative_to(root)),
                phases_present=phases_present,
            )
        )
    summaries.sort(key=lambda r: (r.timestamp, r.run_id), reverse=True)
    return summaries


def recall(root: Path, query_text: str, limit: int = 10) -> Dict[str, Any]:
    query = parse_query(query_text)
    scopes = _query_scopes(query)

    if query.mode == "temporal":
        runs = _run_summaries(root)
        if query.time_range:
            start, end = query.time_range
            runs = [run for run in runs if start <= run.timestamp < end]
        return {
            "mode": "temporal",
            "query": query_text,
            "scopes": scopes,
            "results": [
                {
                    "run_id": run.run_id,
                    "timestamp": run.timestamp.isoformat(),
                    "request": run.request,
                    "path": run.path,
                    "phases_present": run.phases_present,
                }
                for run in runs[:limit]
            ],
        }

    docs = [doc for doc in list(_iter_markdown_docs(root)) + list(_iter_ledger_docs(root)) if _matches_filters(doc, query)]
    scores = _bm25_scores(docs, query)

    ranked: List[Tuple[MemoryDoc, float]] = []
    for doc in docs:
        score = scores.get(doc.id)
        if score is None:
            continue
        ranked.append((doc, score))

    ranked.sort(
        key=lambda item: (
            item[1],
            item[0].timestamp.isoformat() if item[0].timestamp else "",
            item[0].path,
        ),
        reverse=True,
    )

    results: List[Dict[str, Any]] = []
    for rank, (doc, score) in enumerate(ranked[:limit], start=1):
        results.append(
            {
                "rank": rank,
                "score": round(score, 4),
                "scope": doc.scope,
                "kind": doc.kind,
                "stage": doc.stage,
                "role": doc.role,
                "path": doc.path,
                "title": doc.title,
                "timestamp": doc.timestamp.isoformat() if doc.timestamp else None,
                "run_id": doc.run_id,
                "snippet": _extract_snippet(doc, query),
                "source": doc.source,
            }
        )

    return {
        "mode": "search",
        "query": query_text,
        "scopes": scopes,
        "filters": {
            "kind": query.kinds,
            "stage": query.stages,
            "role": query.roles,
            "path": query.path_filters,
            "when": query.when_raw,
        },
        "results": results,
    }
