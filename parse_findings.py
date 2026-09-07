"""Best-effort ACAS / Nessus / CSV finding parser for Workbench POA&M rows.

Learning aid only. Maps plugin/name, severity, host, and synopsis when they
are present. Never invents plugin IDs or dates that were not in the paste.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Any

PARSER_DISCLAIMER = (
    "Best-effort / learning aid. This parser maps columns it recognizes and "
    "leaves the rest blank. It does not invent plugin IDs or dates. Review "
    "every row before generating a draft. Drafts remain not assessor-validated."
)

# Flexible header aliases → canonical field
HEADER_ALIASES = {
    "plugin": "plugin_id",
    "plugin id": "plugin_id",
    "plugin_id": "plugin_id",
    "pluginid": "plugin_id",
    "nessus id": "plugin_id",
    "nessus_id": "plugin_id",
    "plugin #": "plugin_id",
    "name": "plugin_name",
    "plugin name": "plugin_name",
    "plugin_name": "plugin_name",
    "title": "plugin_name",
    "vulnerability": "plugin_name",
    "severity": "severity",
    "risk": "severity",
    "risk factor": "severity",
    "cvss": "severity",
    "host": "host",
    "hostname": "host",
    "ip": "host",
    "ip address": "host",
    "dns name": "host",
    "fqdn": "host",
    "asset": "host",
    "synopsis": "synopsis",
    "description": "synopsis",
    "summary": "synopsis",
    "finding": "synopsis",
    "weakness": "synopsis",
    "plugin output": "synopsis",
    "system": "system_name",
    "system name": "system_name",
    "system_name": "system_name",
    "control": "control_id",
    "control id": "control_id",
    "control_id": "control_id",
    "date": "discovery_date",
    "first discovered": "discovery_date",
    "discovery": "discovery_date",
    "discovery date": "discovery_date",
    "discovery_date": "discovery_date",
    "plugin publication date": "discovery_date",
}

SEVERITY_MAP = {
    "critical": "High",
    "crit": "High",
    "high": "High",
    "hi": "High",
    "medium": "Moderate",
    "med": "Moderate",
    "moderate": "Moderate",
    "mod": "Moderate",
    "low": "Low",
    "lo": "Low",
    "info": "Low",
    "informational": "Low",
}

PLUGIN_ID_RE = re.compile(
    r"(?:plugin(?:\s+id)?|nessus(?:\s+id)?)\s*[:=#]?\s*(\d{3,7})\b",
    re.IGNORECASE,
)
BARE_PLUGIN_RE = re.compile(r"\b(\d{4,7})\b")
SEVERITY_TOKEN_RE = re.compile(
    r"\b(critical|high|medium|moderate|low|informational|info)\b",
    re.IGNORECASE,
)
HOST_RE = re.compile(
    r"\b(?:host|hostname|ip|asset)\s*[:=]\s*([A-Za-z0-9._:-]+)",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/20\d{2})\b")
KV_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9 /#_*-]{1,40})\s*[:=]\s*(.+?)\s*$"
)
PIPE_SPLIT_RE = re.compile(r"\s*\|\s*")
DASH_SPLIT_RE = re.compile(r"\s+[-–—]\s+")

NIST_CONTROL_RE = re.compile(
    r"\b([A-Za-z]{2,3})-(\d+)(?:\((\d+)\)|\.(\d+))?"
)


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_header(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip().lower())


def map_severity(value: Any) -> str:
    raw = _clean(value).lower()
    if not raw:
        return ""
    if raw in SEVERITY_MAP:
        return SEVERITY_MAP[raw]
    token = SEVERITY_TOKEN_RE.search(raw)
    if token:
        return SEVERITY_MAP.get(token.group(1).lower(), "")
    return ""


def extract_plugin_id(text: str) -> str:
    """Return a plugin ID only when the paste clearly labels one."""
    labeled = PLUGIN_ID_RE.search(text or "")
    if labeled:
        return labeled.group(1)
    return ""


def extract_date(text: str) -> str:
    match = DATE_RE.search(text or "")
    return match.group(1) if match else ""


def looks_like_csv(text: str) -> bool:
    sample = (text or "").lstrip("\ufeff")
    if not sample.strip():
        return False
    first = sample.splitlines()[0]
    if first.count(",") < 1 and first.count("\t") < 1:
        return False
    headers = [_normalize_header(h) for h in re.split(r"[,\t]", first)]
    known = sum(1 for h in headers if h in HEADER_ALIASES)
    return known >= 2


def empty_row() -> dict[str, str]:
    return {
        "plugin_id": "",
        "plugin_name": "",
        "severity": "",
        "host": "",
        "synopsis": "",
        "finding": "",
        "system_name": "",
        "detector_source": "",
        "discovery_date": "",
        "control_id": "",
        "notes": "",
    }


def _apply_mapped(row: dict[str, str], field: str, value: str) -> None:
    value = _clean(value)
    if not value:
        return
    if field == "severity":
        mapped = map_severity(value)
        if mapped:
            row["severity"] = mapped
        return
    if field == "plugin_id":
        digits = re.sub(r"\D", "", value)
        if 3 <= len(digits) <= 7:
            row["plugin_id"] = digits
        return
    if field == "discovery_date":
        found = extract_date(value)
        if found:
            row["discovery_date"] = found
        return
    if field == "control_id":
        match = NIST_CONTROL_RE.search(value)
        if match:
            fam, num = match.group(1), match.group(2)
            enh = match.group(3) or match.group(4)
            row["control_id"] = f"{fam.upper()}-{int(num)}" + (
                f"({int(enh)})" if enh else ""
            )
        return
    row[field] = value


def finish_row(row: dict[str, str], *, detector_hint: str = "") -> dict[str, str]:
    name = row.get("plugin_name") or ""
    synopsis = row.get("synopsis") or ""
    host = row.get("host") or ""
    plugin = row.get("plugin_id") or ""
    parts = []
    if name:
        parts.append(name)
    if synopsis and synopsis.lower() != name.lower():
        parts.append(synopsis)
    if host:
        parts.append(f"Host: {host}")
    if plugin:
        parts.append(f"Plugin {plugin}")
    finding = ". ".join(p.rstrip(".") for p in parts if p)
    row["finding"] = finding or synopsis or name
    if not row.get("system_name") and host:
        row["system_name"] = host
    if not row.get("detector_source"):
        row["detector_source"] = detector_hint or "ACAS/Nessus"
    row["notes"] = PARSER_DISCLAIMER
    return row


def parse_csv(text: str) -> list[dict[str, str]]:
    sample = (text or "").lstrip("\ufeff")
    dialect = csv.Sniffer().sniff(sample.splitlines()[0], delimiters=",\t;")
    reader = csv.DictReader(io.StringIO(sample), dialect=dialect)
    rows = []
    for raw in reader:
        if not raw:
            continue
        row = empty_row()
        mapped_any = False
        leftovers = []
        for key, value in raw.items():
            field = HEADER_ALIASES.get(_normalize_header(key or ""))
            if field:
                _apply_mapped(row, field, value)
                mapped_any = True
            elif _clean(value):
                leftovers.append(f"{key}: {value}")
        if not mapped_any and not any(_clean(v) for v in (raw.values() if raw else [])):
            continue
        if leftovers and not row.get("synopsis"):
            row["synopsis"] = "; ".join(leftovers[:3])
        if row["finding"] or row["plugin_name"] or row["synopsis"] or row["plugin_id"]:
            rows.append(finish_row(row))
    return rows


def parse_kv_block(block: str) -> dict[str, str] | None:
    row = empty_row()
    mapped = False
    unlabeled = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        kv = KV_RE.match(line)
        if kv:
            field = HEADER_ALIASES.get(_normalize_header(kv.group(1)))
            if field:
                _apply_mapped(row, field, kv.group(2))
                mapped = True
                continue
        unlabeled.append(line)
        plugin = extract_plugin_id(line)
        if plugin and not row["plugin_id"]:
            row["plugin_id"] = plugin
            mapped = True
        sev = map_severity(line)
        if sev and not row["severity"] and SEVERITY_TOKEN_RE.search(line):
            # Only accept severity from a short label-ish line
            if len(line) < 40:
                row["severity"] = sev
                mapped = True
        host = HOST_RE.search(line)
        if host and not row["host"]:
            row["host"] = host.group(1)
            mapped = True
        date = extract_date(line)
        if date and not row["discovery_date"]:
            row["discovery_date"] = date
    if unlabeled and not row["synopsis"]:
        # Prefer a longer descriptive leftover as synopsis
        descriptive = [u for u in unlabeled if len(u) > 20 and not KV_RE.match(u)]
        row["synopsis"] = " ".join(descriptive or unlabeled)
        mapped = True
    if not mapped:
        return None
    if not (row["plugin_id"] or row["plugin_name"] or row["synopsis"] or row["finding"]):
        return None
    return finish_row(row)


def parse_single_line(line: str) -> dict[str, str] | None:
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    row = empty_row()

    if "|" in text:
        parts = [p.strip() for p in PIPE_SPLIT_RE.split(text) if p.strip()]
    elif DASH_SPLIT_RE.search(text):
        parts = [p.strip() for p in DASH_SPLIT_RE.split(text) if p.strip()]
    else:
        parts = [text]

    labeled_plugin = extract_plugin_id(text)
    if labeled_plugin:
        row["plugin_id"] = labeled_plugin

    # First short numeric token is a plugin only when labeled or when the
    # line also has a severity token (typical ACAS one-liner).
    if not row["plugin_id"]:
        first_num = BARE_PLUGIN_RE.search(text)
        if first_num and (labeled_plugin or SEVERITY_TOKEN_RE.search(text)):
            # Require a labeled plugin OR (number + severity + another field)
            if labeled_plugin or (len(parts) >= 3):
                row["plugin_id"] = first_num.group(1)

    for part in parts:
        sev = map_severity(part)
        if sev and not row["severity"] and len(part) < 24:
            row["severity"] = sev
            continue
        if HOST_RE.search(part):
            row["host"] = HOST_RE.search(part).group(1)
            continue
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{1,80}", part) and (
            "." in part or "-" in part
        ):
            if not row["host"] and not map_severity(part):
                row["host"] = part
                continue
        if extract_date(part) and not row["discovery_date"]:
            row["discovery_date"] = extract_date(part)
            continue
        if not row["plugin_name"] and not extract_plugin_id(part) and not (
            row["plugin_id"] and part == row["plugin_id"]
        ):
            if not map_severity(part) or len(part) > 20:
                row["plugin_name"] = part
        elif not row["synopsis"] and part not in {row["plugin_name"], row["plugin_id"]}:
            if not map_severity(part) or len(part) > 20:
                row["synopsis"] = part

    if not row["plugin_name"] and not row["synopsis"] and not row["plugin_id"]:
        row["synopsis"] = text
    if not (row["plugin_id"] or row["plugin_name"] or row["synopsis"]):
        return None
    return finish_row(row)


def parse_findings(text: str, *, filename: str = "") -> dict[str, Any]:
    """Parse pasted scan text or CSV into draft POA&M row dicts."""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return {
            "rows": [],
            "parser": "best-effort",
            "disclaimer": PARSER_DISCLAIMER,
            "warning": "Nothing to parse. Paste scan lines or a CSV with a header row.",
        }

    name = (filename or "").lower()
    rows: list[dict[str, str]] = []
    if name.endswith(".csv") or looks_like_csv(raw):
        try:
            rows = parse_csv(raw)
        except csv.Error:
            rows = []

    if not rows:
        blocks = re.split(r"\n\s*\n", raw)
        if len(blocks) > 1:
            for block in blocks:
                parsed = parse_kv_block(block) or parse_single_line(block.replace("\n", " | "))
                if parsed:
                    rows.append(parsed)
        if not rows:
            kv = parse_kv_block(raw)
            if kv:
                rows.append(kv)
        if not rows:
            for line in raw.splitlines():
                parsed = parse_single_line(line)
                if parsed:
                    rows.append(parsed)

    # Drop rows that are only a header echo
    cleaned = []
    for row in rows:
        finding = (row.get("finding") or "").lower()
        if finding.startswith("plugin") and "severity" in finding and "host" in finding:
            continue
        cleaned.append(row)

    return {
        "rows": cleaned,
        "parser": "best-effort",
        "disclaimer": PARSER_DISCLAIMER,
        "warning": ""
        if cleaned
        else "Could not map any rows. Try a CSV header such as plugin,name,severity,host,synopsis.",
    }
