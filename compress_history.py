import pandas as pd

print("SPOT 52 - Compressing historical NAV data")

df = pd.read_csv(
    "history_nav_52weeks.csv",
    dtype=str
)

print("Original records:", len(df))

df.to_csv(
    "history_nav_52weeks.csv.gz",
    index=False,
    compression="gzip"
)

print("Compression completed successfully.")