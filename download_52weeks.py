import requests
import csv
import time
from datetime import date, timedelta
from pathlib import Path

URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

OUTPUT_FILE = "history_nav_52weeks.csv"
PROGRESS_FILE = "download_progress.txt"

# Complete 52-week period
START_DATE = date.today() - timedelta(days=364)
END_DATE = date.today()

columns = [
    "Scheme Code",
    "Scheme Name",
    "Plan",
    "Option",
    "ISIN Dividend Payout/Growth",
    "ISIN Dividend Reinvestment",
    "NAV",
    "NAV Date"
]

session = requests.Session()

# Resume from saved progress
progress_path = Path(PROGRESS_FILE)

if progress_path.exists():

    current_date = date.fromisoformat(
        progress_path.read_text().strip()
    )

else:

    # First run: the first batch is already downloaded
    current_date = date(2025, 11, 30)

    progress_path.write_text(
        current_date.isoformat()
    )

total_records = 0
total_batches = 0

print("SPOT 52 - Resumable Historical Downloader")
print("-----------------------------------------")
print("Resuming from:", current_date)
print("Final date:", END_DATE)

while current_date <= END_DATE:

    batch_end = min(
        current_date + timedelta(days=6),
        END_DATE
    )

    params = {
        "frmdt": current_date.strftime("%d-%b-%Y"),
        "todt": batch_end.strftime("%d-%b-%Y")
    }

    print(
        f"\nDownloading {params['frmdt']} to {params['todt']}"
    )

    success = False

    for attempt in range(1, 4):

        try:

            response = session.get(
                URL,
                params=params,
                timeout=180
            )

            response.raise_for_status()

            data = response.content.decode(
                "utf-8-sig",
                errors="replace"
            )

            records = []

            for line in data.splitlines():

                parts = line.split(";")

                if (
                    len(parts) >= 8
                    and parts[0].strip().isdigit()
                ):

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

            # Validate actual records, not response size
            if not records:

                # Check whether the entire batch contains only weekends
                batch_days = (batch_end - current_date).days + 1

                weekend_only = all(
                    (current_date + timedelta(days=i)).weekday() >= 5
                    for i in range(batch_days)
                )

                if weekend_only:
                    print("Weekend detected. No NAV expected.")
                    print("Moving to the next date.")

                    current_date = batch_end + timedelta(days=1)

                    progress_path.write_text(
                        current_date.isoformat()
                    )

                    total_batches += 1
                    continue

                else:
                    raise ValueError(
                        "No NAV records found on working days. "
                        "Please investigate this batch."
                    )

                
                    
                
            # Append records to existing CSV
            with open(
                OUTPUT_FILE,
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)
                writer.writerows(records)

            total_records += len(records)
            total_batches += 1

            # Save next date after successful batch
            current_date = batch_end + timedelta(days=1)

            progress_path.write_text(
                current_date.isoformat()
            )

            print(
                "Successful:",
                len(records),
                "records"
            )

            success = True
            break

        except Exception as error:

            print(
                f"Attempt {attempt} failed: {error}"
            )

            if attempt < 3:
                time.sleep(10 * attempt)

    if not success:

        print("\nDownload paused.")
        print("Previously downloaded data is preserved.")
        print("Run this programme again to resume.")
        break

    time.sleep(2)

print("\n-----------------------------------------")
print("DOWNLOAD SUMMARY")
print("-----------------------------------------")
print("Successful batches:", total_batches)
print("New records downloaded:", total_records)
print("Output file:", OUTPUT_FILE)

if current_date > END_DATE:

    print("52-week download completed!")

else:

    print("Download remains incomplete.")
    print("Next date:", current_date)