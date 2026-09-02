import requests
import json

url = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"
response = requests.get(url)

data = response.json()

with open("nist_data.json", "w") as f:
    json.dump(data, f)

print("Saved the full file as nist_data.json")