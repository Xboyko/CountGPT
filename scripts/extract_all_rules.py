import json
import os
import re
import sys

PARAM_PLACEHOLDER_RE = re.compile(
    r"\{\{\s*insert:\s*param\s*,\s*[^}]+\}\}",
    re.IGNORECASE,
)
MULTI_SPACE_RE = re.compile(r"[ \t]+")
MULTI_BLANK_RE = re.compile(r"\n{3,}")


def strip_oscal_placeholders(text):
    """Replace OSCAL {{ insert: param, ... }} tokens with a readable stub."""
    if not text:
        return ""
    cleaned = PARAM_PLACEHOLDER_RE.sub("[organization-defined]", text)
    cleaned = MULTI_SPACE_RE.sub(" ", cleaned)
    cleaned = MULTI_BLANK_RE.sub("\n\n", cleaned)
    return cleaned.strip()


def is_withdrawn(control):
    if not isinstance(control, dict):
        return False
    withdrawn = control.get("withdrawn")
    if withdrawn in (True, "true", "True", "yes", "withdrawn"):
        return True
    for prop in control.get("props") or []:
        if not isinstance(prop, dict):
            continue
        name = (prop.get("name") or "").strip().lower()
        value = (prop.get("value") or "").strip().lower()
        if name == "status" and value == "withdrawn":
            return True
        if name == "withdrawn" and value in ("true", "yes", "withdrawn", ""):
            return True
    return False


def get_all_prose(parts):
    text_pieces = []
    for part in parts or []:
        if not isinstance(part, dict):
            continue
        prose = part.get("prose")
        if prose:
            text_pieces.append(prose)
        nested = part.get("parts")
        if nested:
            nested_text = get_all_prose(nested)
            if nested_text:
                text_pieces.append(nested_text)
    return "\n".join(text_pieces)


def statement_text_from_control(control):
    pieces = []
    for part in control.get("parts") or []:
        if not isinstance(part, dict):
            continue
        if part.get("name") != "statement":
            continue
        if part.get("prose"):
            pieces.append(part["prose"])
        nested = part.get("parts")
        if nested:
            nested_text = get_all_prose(nested)
            if nested_text:
                pieces.append(nested_text)
        elif not part.get("prose"):
            # statement with no nested parts: still try this node as a list
            fallback = get_all_prose([part])
            if fallback:
                pieces.append(fallback)
    return "\n".join(p for p in pieces if p).strip()


def control_id(control):
    """Prefer OSCAL label (AC-2 / AC-2(1)); fall back to catalog id (ac-2)."""
    for prop in control.get("props") or []:
        if isinstance(prop, dict) and (prop.get("name") or "").lower() == "label":
            label = (prop.get("value") or "").strip()
            if label:
                return label
    return (control.get("id") or "").strip()


def extract_rules(data):
    """Flatten an OSCAL catalog dict into {id, title, text} rules.

    Returns (rules, stats) where stats counts withdrawn/empty drops.
    """
    all_rules = []
    stats = {
        "seen": 0,
        "kept": 0,
        "dropped_withdrawn": 0,
        "dropped_empty": 0,
    }

    def process_control(control):
        if not isinstance(control, dict):
            return
        stats["seen"] += 1

        withdrawn = is_withdrawn(control)
        if not withdrawn:
            rule_id = control_id(control)
            title = (control.get("title") or "").strip()
            raw_text = statement_text_from_control(control)
            text = strip_oscal_placeholders(raw_text)

            if not text:
                stats["dropped_empty"] += 1
            else:
                all_rules.append({
                    "id": rule_id or (control.get("id") or ""),
                    "title": title,
                    "text": text,
                })
                stats["kept"] += 1
        else:
            stats["dropped_withdrawn"] += 1

        for enhancement in control.get("controls") or []:
            process_control(enhancement)

    def process_group(group):
        if not isinstance(group, dict):
            return
        for control in group.get("controls") or []:
            process_control(control)
        for sub_group in group.get("groups") or []:
            process_group(sub_group)

    catalog = data.get("catalog") if isinstance(data, dict) else None
    if not catalog:
        raise ValueError("nist_data.json does not look like an OSCAL catalog (missing catalog key)")

    for group in catalog.get("groups") or []:
        process_group(group)

    # Some catalogs also list controls at the catalog root
    for control in catalog.get("controls") or []:
        process_control(control)

    stats["dropped"] = stats["dropped_withdrawn"] + stats["dropped_empty"]
    return all_rules, stats


def main():
    src = "nist_data.json"
    if not os.path.exists(src):
        print(
            f"ERROR: {src} not found in {os.getcwd()}. "
            "Place the NIST 800-53 OSCAL catalog JSON here, then re-run."
        )
        sys.exit(1)

    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_rules, stats = extract_rules(data)

    with open("clean_rules.json", "w", encoding="utf-8") as f:
        json.dump(all_rules, f, indent=2)

    print(
        f"Saved {stats['kept']} rules to clean_rules.json "
        f"(dropped {stats['dropped']}: "
        f"{stats['dropped_withdrawn']} withdrawn, "
        f"{stats['dropped_empty']} empty text; "
        f"scanned {stats['seen']} controls/enhancements)"
    )


if __name__ == "__main__":
    main()
