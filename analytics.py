import pandas as pd

HISTORY_FILE = "history_nav_52weeks.csv.gz"
LATEST_FILE = "amfi_nav.csv"


def load_nav_data():

    history = pd.read_csv(
        HISTORY_FILE,
        encoding="utf-8-sig",
        dtype=str,
        compression="gzip"
    )

    latest = pd.read_csv(
        LATEST_FILE,
        encoding="utf-8-sig",
        dtype=str
    )

    # Clean scheme codes
    history["Scheme Code"] = history["Scheme Code"].str.strip()
    latest["Scheme Code"] = latest["Scheme Code"].str.strip()

    # Convert NAV into numbers
    history["NAV"] = pd.to_numeric(
        history["NAV"], errors="coerce"
    )

    latest["NAV"] = pd.to_numeric(
        latest["NAV"], errors="coerce"
    )

    # Convert NAV dates
    history["NAV Date"] = pd.to_datetime(
        history["NAV Date"],
        format="%d-%b-%Y",
        errors="coerce"
    )

    latest["NAV Date"] = pd.to_datetime(
        latest["NAV Date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    return history, latest


def analyze_scheme(scheme_code):

    history, latest = load_nav_data()

    scheme_code = str(scheme_code).strip()

    # Find the selected scheme in latest AMFI data
    latest_scheme = latest[
        latest["Scheme Code"] == scheme_code
    ].copy()

    if latest_scheme.empty:
        raise ValueError("Scheme not found in latest AMFI data.")

    latest_scheme = latest_scheme.dropna(
        subset=["NAV", "NAV Date"]
    )

    if latest_scheme.empty:
        raise ValueError("Latest NAV is unavailable.")

    latest_row = latest_scheme.sort_values(
        "NAV Date"
    ).iloc[-1]

    current_nav = float(latest_row["NAV"])
    current_date = latest_row["NAV Date"]

    scheme_name = latest_row["Scheme Name"]

    # Select historical records for this scheme
    scheme_history = history[
        history["Scheme Code"] == scheme_code
    ].copy()

    scheme_history = scheme_history.dropna(
        subset=["NAV", "NAV Date"]
    )

    # Include the latest NAV observation as well
    latest_record = pd.DataFrame([{
        "Scheme Code": scheme_code,
        "NAV": current_nav,
        "NAV Date": current_date
    }])

    observations = pd.concat(
        [
            scheme_history[["Scheme Code", "NAV", "NAV Date"]],
            latest_record
        ],
        ignore_index=True
    )

    # Remove duplicate scheme-date observations
    observations = observations.drop_duplicates(
        subset=["Scheme Code", "NAV Date"],
        keep="last"
    )

    # Define the trailing 52-week period
    start_date = current_date - pd.Timedelta(days=364)

    observations = observations[
        (observations["NAV Date"] >= start_date) &
        (observations["NAV Date"] <= current_date)
    ].sort_values("NAV Date")

    if observations.empty:
        raise ValueError("No historical NAV observations available.")

    # Check historical coverage
    coverage_start = observations["NAV Date"].min()

    coverage_days = (
        current_date - coverage_start
    ).days + 1

    # Allow a 7-day tolerance for weekends and holidays
    full_coverage = (
        coverage_start <= start_date + pd.Timedelta(days=7)
    )

    if full_coverage:
        coverage_status = "FULL 52-WEEK COVERAGE"
    else:
        coverage_status = "LIMITED HISTORICAL DATA"

        print("\nWARNING:", coverage_status)
        print(
            "Available history starts:",
            coverage_start.strftime("%d-%b-%Y")
        )

    print("Historical coverage:", coverage_days, "days")

    # Calculate 52-week high and low
    high_row = observations.loc[
        observations["NAV"].idxmax()
    ]

    low_row = observations.loc[
        observations["NAV"].idxmin()
    ]

    high_nav = float(high_row["NAV"])
    high_date = high_row["NAV Date"]

    low_nav = float(low_row["NAV"])
    low_date = low_row["NAV Date"]

    # Calculate NAV range position
    if high_nav == low_nav:
        range_position = 0.0
    else:
        range_position = (
            (current_nav - low_nav) /
            (high_nav - low_nav)
        ) * 100

    # Identify which extreme occurred later
    if low_date > high_date:
        reference_nav = low_nav
        reference_date = low_date

        change_percent = (
            (current_nav - reference_nav) /
            reference_nav
        ) * 100

    elif high_date > low_date:
        reference_nav = high_nav
        reference_date = high_date

        change_percent = (
            (current_nav - reference_nav) /
            reference_nav
        ) * 100

    else:
        reference_nav = None
        reference_date = high_date
        change_percent = None

    if change_percent is None:
        direction = "NEUTRAL"
        colour = "grey"
    elif change_percent > 0:
        direction = "UP"
        colour = "green"
    elif change_percent < 0:
        direction = "DOWN"
        colour = "red"
    else:
        direction = "UNCHANGED"
        colour = "grey"

    return {
        "scheme_name": scheme_name,
        "scheme_code": scheme_code,

        "current_nav": current_nav,
        "current_date": current_date,

        "high_nav": high_nav,
        "high_date": high_date,

        "low_nav": low_nav,
        "low_date": low_date,

        "range_position": range_position,

        "reference_nav": reference_nav,
        "reference_date": reference_date,

        "change_percent": change_percent,
        "direction": direction,
        "colour": colour,
        "coverage_start": coverage_start,
        "coverage_days": coverage_days,
        "full_coverage": full_coverage,
        "coverage_status": coverage_status,

        "observations": len(observations)
    }


if __name__ == "__main__":

    history, latest = load_nav_data()

    # Keep only schemes with valid latest NAV and date
    valid_latest = latest.dropna(
        subset=["NAV", "NAV Date"]
    )

    valid_latest = valid_latest[
        valid_latest["NAV"] > 0
    ]

    # Find schemes available in both datasets
    matched_codes = (
        set(history["Scheme Code"]) &
        set(valid_latest["Scheme Code"])
    )

    if not matched_codes:
        raise ValueError(
            "No schemes with valid latest NAV found."
        )

    # Select a scheme with valid latest NAV
    test_code = "100034"

    print("Testing Scheme Code:", test_code)

    result = analyze_scheme(test_code)

    print("\nSPOT 52 - 52 WEEK NAV ANALYSIS")
    print("--------------------------------")

    print("Scheme:", result["scheme_name"])
    print("Scheme Code:", result["scheme_code"])

    print("\nLATEST NAV")
    print("NAV:", result["current_nav"])
    print("Date:", result["current_date"].strftime("%d-%b-%Y"))

    print("\n52-WEEK HIGH")
    print("NAV:", result["high_nav"])
    print("Date:", result["high_date"].strftime("%d-%b-%Y"))

    print("\n52-WEEK LOW")
    print("NAV:", result["low_nav"])
    print("Date:", result["low_date"].strftime("%d-%b-%Y"))

    print("\nSUMMARY")
    print("Direction:", result["direction"])
    if result["direction"] == "UP":
        print(
            f"\n↑ {result['change_percent']:.2f}% "
            "UP FROM 52-WEEK LOW"
        )
        print(
            "Since:",
            result["reference_date"].strftime("%d-%b-%Y")
        )

    elif result["direction"] == "DOWN":
        print(
            f"\n↓ {abs(result['change_percent']):.2f}% "
            "DOWN FROM 52-WEEK HIGH"
        )
        print(
            "Since:",
            result["reference_date"].strftime("%d-%b-%Y")
        )

    else:
        print("\nNEUTRAL")

    print("\nNAV RANGE POSITION")
    print(round(result["range_position"], 2), "%")

    print("\nHistorical observations:", result["observations"])
    print("\nCOVERAGE STATUS")
    print(result["coverage_status"])
    print(
    "Available from:",
    result["coverage_start"].strftime("%d-%b-%Y")
    )
    print("Coverage days:", result["coverage_days"])