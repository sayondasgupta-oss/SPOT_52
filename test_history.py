import requests

# AMFI historical NAV download URL
url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

# Test date range: 14 November to 20 November 2026
params = {
    "frmdt": "14-Nov-2026",
    "todt": "20-Nov-2026"
}

print("Connecting to AMFI historical NAV service...")

try:

    response = requests.get(
        url,
        params=params,
        timeout=120
    )

    response.raise_for_status()

    data = response.content.decode(
        "utf-8-sig",
        errors="replace"
    )

    print("\nHistorical data downloaded successfully!")

    print("Total characters downloaded:", len(data))

    print("\nFirst 10 lines of historical data:\n")

    for line in data.splitlines()[:10]:
        print(line)

except requests.exceptions.RequestException as error:

    print("\nUnable to download historical data.")

    print("Error:", error)