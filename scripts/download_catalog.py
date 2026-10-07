"""Download the official NIST SP 800-53 Rev 5 OSCAL catalog JSON."""

import json
import sys

import requests

NIST_OSCAL_URL = (
    "https://raw.githubusercontent.com/usnistgov/oscal-content/main/"
    "nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"
)
OUT_PATH = "nist_data.json"
TIMEOUT_SEC = 120


def download_catalog(url=NIST_OSCAL_URL, out_path=OUT_PATH):
    print(f"Downloading NIST 800-53 OSCAL catalog...\n  {url}")
    response = requests.get(url, timeout=TIMEOUT_SEC)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or "catalog" not in data:
        raise ValueError("Downloaded JSON is not an OSCAL catalog (missing 'catalog' key)")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"Saved {out_path}")
    return out_path


def main():
    try:
        download_catalog()
    except requests.RequestException as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid catalog JSON: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
