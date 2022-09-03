import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASEURL = os.getenv("BASEURL")
DOMAIN = os.getenv("DOMAIN")
SUBDOMAIN = os.getenv("SUBDOMAIN")
HEADERS = {
  "User-Agent": os.getenv("USERAGENT"),
  "Authorization": "Bearer " + os.getenv("PERSONAL_ACCESS_TOKEN")
}

current_ip = requests.get("https://ifconfig.me").text

# print(current_ip.text)

dns_zones_response = requests.get(BASEURL + "/dns_zones", headers=HEADERS)
dns_zones_arr = dns_zones_response.json()

# print(dns_zones_arr)

zone = [ dns_zone for dns_zone in dns_zones_arr if dns_zone["name"] == DOMAIN ][0]
# print(zone)

zone_id = zone["id"]

dns_records_response = requests.get(BASEURL + f"/dns_zones/{zone_id}/dns_records", headers=HEADERS)
dns_records_arr = dns_records_response.json()

record = [ dns_record for dns_record in dns_records_arr if dns_record["hostname"] == SUBDOMAIN + "." + DOMAIN ]
# print(record)

if not len(record) == 0:
  record = record[0]
  print("Found existing record.")
  previous_ip = record["value"]

  if not current_ip == previous_ip:
    print("Deleting existing record.")
    record_id = record["id"]
    delete_response = requests.delete(BASEURL + f"/dns_zones/{zone_id}/dns_records/{record_id}", headers=HEADERS)
  else:
    print("Record is up to date.")
    exit(0)

new_record = {
    "type": "A",
    "hostname": SUBDOMAIN,
    "value": current_ip,
    "ttl": 3600,
    "priority": None,
    "weight": None,
    "port": None,
    "flag": None,
    "tag": None
}

print("Creating new record.")
new_record_response = requests.post(BASEURL + f"/dns_zones/{zone_id}/dns_records", json=new_record, headers=HEADERS)
