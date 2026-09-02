import json

with open("nist_data.json", "r") as f:
    data = json.load(f)

groups = data["catalog"]["groups"]

def print_all_prose(parts, indent=0):
    for part in parts:
        if "prose" in part:
            print("  " * indent + "- " + part["prose"])
        if "parts" in part:
            print_all_prose(part["parts"], indent + 1)

for group in groups:
    for control in group.get("controls", []):
        if control.get("id") == "ac-2":
            print("ID:", control["id"])
            print("Title:", control["title"])
            print()
            for part in control.get("parts", []):
                if part.get("name") == "statement":
                    print("Rule text:")
                    print_all_prose(part.get("parts", []) or [part])