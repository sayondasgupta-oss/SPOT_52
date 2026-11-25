import requests

url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

params = {
    "frmdt": "30-Nov-2025",
    "todt": "06-Dec-2025"
}

print("Checking AMFI response for the failed batch...")

response = requests.get(
    url,
    params=params,
    timeout=120
)

print("\nHTTP Status:", response.status_code)
print("Response size:", len(response.content), "bytes")

data = response.content.decode(
    "utf-8-sig",
    errors="replace"
)

print("\nFirst 2000 characters of response:\n")
print(data[:2000])

records = [
    line for line in data.splitlines()
    if len(line.split(";")) >= 8
    and line.split(";")[0].strip().isdigit()
]

print("\nNAV records detected:", len(records))