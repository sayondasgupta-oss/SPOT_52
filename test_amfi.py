import requests

# AMFI latest NAV data source
url = "https://portal.amfiindia.com/spages/NAVAll.txt"

print("Connecting to AMFI...")

try:
    response = requests.get(url, timeout=60)

    # Check whether download was successful
    response.raise_for_status()

    # Read downloaded data
    data = response.text

    print("AMFI data downloaded successfully!")

    print("Total characters downloaded:", len(data))

    print("\nFirst 10 lines of AMFI data:\n")

    for line in data.splitlines()[:10]:
        print(line)

except requests.exceptions.RequestException as error:
    print("Unable to download AMFI data.")
    print("Error:", error)