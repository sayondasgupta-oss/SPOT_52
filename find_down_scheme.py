from analytics import load_nav_data
import pandas as pd

history, latest = load_nav_data()

# Keep valid NAV observations
history = history.dropna(subset=["NAV", "NAV Date"])
latest = latest.dropna(subset=["NAV", "NAV Date"])

# Combine historical and latest NAV data
combined = pd.concat([
    history[["Scheme Code", "Scheme Name", "NAV", "NAV Date"]],
    latest[["Scheme Code", "Scheme Name", "NAV", "NAV Date"]]
])

# Remove duplicate dates
combined = combined.drop_duplicates(
    subset=["Scheme Code", "NAV Date"],
    keep="last"
)

# Find the high and low dates for each scheme
results = []

for code, group in combined.groupby("Scheme Code"):

    group = group.sort_values("NAV Date")

    if len(group) < 100:
        continue

    high = group.loc[group["NAV"].idxmax()]
    low = group.loc[group["NAV"].idxmin()]

    if high["NAV Date"] < low["NAV Date"]:

        results.append({
            "Scheme Code": code,
            "Scheme Name": high["Scheme Name"],
            "High NAV": high["NAV"],
            "High Date": high["NAV Date"],
            "Low NAV": low["NAV"],
            "Low Date": low["NAV Date"]
        })

if results:
    output = pd.DataFrame(results)

    print("\nSCHEMES WHERE HIGH OCCURRED BEFORE LOW")
    print("---------------------------------------")

    print(output.head(10).to_string(index=False))

else:
    print("No suitable DOWN test scheme found.")