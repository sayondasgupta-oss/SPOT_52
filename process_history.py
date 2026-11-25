import requests
import pandas as pd

# Step 1: AMFI historical data URL
url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

params = {
    "frmdt": "14-Nov-2026",
    "todt": "20-Nov-2026"
}

print("Downloading historical NAV data...")

response = requests.get(
    url,
    params=params,
    timeout=120
)

response.raise_for_status()

# Step 2: Read downloaded data
lines = response.content.decode(
    "utf-8-sig",
    errors="replace"
).splitlines()

# Step 3: Extract historical records
records = []

for line in lines:

    parts = line.split(";")

    if len(parts) == 8 and parts[0].strip().isdigit():

        records.append([
            parts[0].strip(),
            parts[1].strip(),
            parts[2].strip(),
            parts[3].strip(),
            parts[4].strip(),
            parts[5].strip(),
            parts[6].strip(),
            parts[7].strip()
        ])

# Step 4: Create DataFrame
df = pd.DataFrame(
    records,
    columns=[
        "Scheme Code",
        "Scheme Name",
        "Plan",
        "Option",
        "ISIN Dividend Payout/Growth",
        "ISIN Dividend Reinvestment",
        "NAV",
        "NAV Date"
    ]
)

# Step 5: Convert NAV into numeric format
df["NAV"] = pd.to_numeric(
    df["NAV"],
    errors="coerce"
)

# Step 6: Convert dates
df["NAV Date"] = pd.to_datetime(
    df["NAV Date"],
    format="%d-%b-%Y",
    errors="coerce"
)

# Step 7: Remove invalid records
df = df.dropna(subset=["NAV", "NAV Date"])

# Step 8: Save historical data
df.to_csv(
    "history_nav.csv",
    index=False,
    encoding="utf-8-sig"
)

# Step 9: Display results
print("\nHistorical NAV data processed successfully!")

print("Total historical records:", len(df))

print("\nFirst 10 records:")

print(df.head(10).to_string(index=False))

print("\nFile saved as history_nav.csv")