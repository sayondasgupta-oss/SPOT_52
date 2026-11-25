from flask import Flask, request, jsonify, render_template_string
import pandas as pd
from analytics import analyze_scheme

app = Flask(__name__)

LATEST_FILE = "amfi_nav.csv"


# Load scheme names for autocomplete
def load_schemes():

    df = pd.read_csv(
        LATEST_FILE,
        encoding="utf-8-sig",
        dtype=str
    )

    df["Scheme Code"] = df["Scheme Code"].astype(str).str.strip()

    df = df.dropna(subset=["Scheme Name"])

    return df


schemes = load_schemes()


HTML = """
<!DOCTYPE html>
<html>
<head>

    <title>SPOT 52</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>

        body {
            background-color: #101C2C;
            color: #EAF0F6;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 850px;
            margin: auto;
        }

        .header {
            text-align: center;
            padding: 25px 10px;
        }

        .header h1 {
            color: #39C6B4;
            font-size: 38px;
            margin-bottom: 8px;
        }

        .tagline {
            color: #B8C7D9;
            font-size: 16px;
        }

        .card {
            background: #1B2B40;
            border: 1px solid #30465F;
            border-radius: 14px;
            padding: 22px;
            margin-top: 20px;
        }

        input {
            width: 100%;
            padding: 14px;
            box-sizing: border-box;
            border-radius: 8px;
            border: 1px solid #52677E;
            background: #F4F7FA;
            font-size: 16px;
        }

        .suggestions {
            background: #263B52;
            border-radius: 8px;
            margin-top: 5px;
            overflow: hidden;
        }

        .suggestion {
            padding: 12px;
            cursor: pointer;
            border-bottom: 1px solid #40566D;
        }

        .suggestion:hover {
            background: #36516D;
        }

        button {
            background: #20B7A5;
            color: #071B28;
            border: none;
            padding: 13px 22px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
        }

        .nav-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            text-align: center;
        }

        .nav-label {
            color: #AFC1D3;
            font-size: 14px;
        }

        .nav-value {
            font-size: 25px;
            font-weight: bold;
            margin: 12px 0;
        }

        .nav-date {
            color: #B8C7D9;
            font-size: 13px;
        }

        .summary {
            text-align: center;
            padding: 35px 10px;
            border-top: 1px solid #40566D;
            margin-top: 25px;
        }

        .percentage {
            font-size: 48px;
            font-weight: bold;
        }

        .up {
            color: #24D17E;
        }

        .down {
            color: #FF6262;
        }

        .summary-title {
            font-size: 25px;
            font-weight: bold;
            margin-top: 20px;
        }

        .reference-date {
            color: #B8C7D9;
            margin-top: 15px;
        }

        .range {
            text-align: center;
            font-size: 18px;
            color: #39C6B4;
            margin-top: 25px;
        }

        .error {
            color: #FF7777;
            margin-top: 15px;
        }

        @media(max-width: 600px) {

            .nav-grid {
                grid-template-columns: 1fr;
            }

            .percentage {
                font-size: 38px;
            }

            .summary-title {
                font-size: 20px;
            }

        }

    </style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>SPOT 52</h1>

        <div class="tagline">
            Know where your fund stands.
        </div>

    </div>


    <div class="card">

        <h2>Search Mutual Fund</h2>

        <input
            type="text"
            id="schemeSearch"
            placeholder="Start typing a scheme name..."
            autocomplete="off"
        >

        <div id="suggestions" class="suggestions"></div>

        <form method="POST" action="/analyse">

            <input
                type="hidden"
                name="scheme_code"
                id="schemeCode"
            >

            <div id="selectedScheme"></div>

            <button type="submit">
                Analyse Fund
            </button>

        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

    </div>


    {% if result %}

    <div class="card">

        <h2>{{ result.scheme_name }}</h2>

        <div class="nav-grid">

            <div>

                <div class="nav-label">52-week Low</div>

                <div class="nav-value">
                    ₹{{ "%.2f"|format(result.low_nav) }}
                </div>

                <div class="nav-date">
                    {{ result.low_date.strftime("%d-%b-%Y") }}
                </div>

            </div>


            <div>

                <div class="nav-label">Current NAV</div>

                <div class="nav-value">
                    ₹{{ "%.2f"|format(result.current_nav) }}
                </div>

                <div class="nav-date">
                    {{ result.current_date.strftime("%d-%b-%Y") }}
                </div>

            </div>


            <div>

                <div class="nav-label">52-week High</div>

                <div class="nav-value">
                    ₹{{ "%.2f"|format(result.high_nav) }}
                </div>

                <div class="nav-date">
                    {{ result.high_date.strftime("%d-%b-%Y") }}
                </div>

            </div>

        </div>


        <div class="summary">

            {% if result.direction == "UP" %}

                <div class="percentage up">
                    ↑ {{ "%.2f"|format(result.change_percent) }}%
                </div>

                <div class="summary-title">
                    UP FROM 52-WEEK LOW
                </div>

                <div class="reference-date">
                    Since {{ result.reference_date.strftime("%d-%b-%Y") }}
                </div>


            {% elif result.direction == "DOWN" %}

                <div class="percentage down">
                    ↓ {{ "%.2f"|format(abs(result.change_percent)) }}%
                </div>

                <div class="summary-title">
                    DOWN FROM 52-WEEK HIGH
                </div>

                <div class="reference-date">
                    Since {{ result.reference_date.strftime("%d-%b-%Y") }}
                </div>


            {% else %}

                <div class="summary-title">
                    NEUTRAL
                </div>

                <div class="reference-date">
                    Both extremes occurred on the same date.
                </div>

            {% endif %}

        </div>


        <div class="range">

            NAV Range Position:
            <strong>{{ "%.2f"|format(result.range_position) }}%</strong>

        </div>

    </div>

    {% endif %}

</div>


<script>

const searchBox = document.getElementById("schemeSearch");
const suggestionsBox = document.getElementById("suggestions");
const schemeCode = document.getElementById("schemeCode");
const selectedScheme = document.getElementById("selectedScheme");

let timer;


searchBox.addEventListener("input", function() {

    clearTimeout(timer);

    const query = this.value.trim();

    schemeCode.value = "";
    selectedScheme.innerHTML = "";

    if (query.length < 2) {
        suggestionsBox.innerHTML = "";
        return;
    }

    timer = setTimeout(async function() {

        const response = await fetch(
            "/suggest?q=" + encodeURIComponent(query)
        );

        const results = await response.json();

        suggestionsBox.innerHTML = "";

        results.forEach(function(item) {

            const div = document.createElement("div");

            div.className = "suggestion";
            div.textContent = item.name;

            div.addEventListener("click", function() {

                searchBox.value = item.name;
                schemeCode.value = item.code;

                selectedScheme.textContent =
                    "Selected: " + item.name;

                suggestionsBox.innerHTML = "";

            });

            suggestionsBox.appendChild(div);

        });

    }, 300);

});

</script>

</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():

    return render_template_string(
        HTML,
        result=None,
        error=None
    )


@app.route("/suggest")
def suggest():

    query = request.args.get("q", "").strip().lower()

    if len(query) < 2:
        return jsonify([])

    matches = schemes[
        schemes["Scheme Name"].str.lower().str.contains(
            query,
            regex=False,
            na=False
        )
    ].head(20)

    results = []

    for _, row in matches.iterrows():

        scheme_name = str(row["Scheme Name"]).strip()

        plan = str(row["Plan"]).strip()
        option = str(row["Option"]).strip()

        display_name = scheme_name

        if plan and plan.lower() != "nan":
            display_name += " - " + plan

        if option and option.lower() != "nan":
            display_name += " - " + option

        results.append({
            "code": str(row["Scheme Code"]).strip(),
            "name": display_name
        })

    return jsonify(results)

   


@app.route("/analyse", methods=["POST"])
def analyse():

    code = request.form.get("scheme_code", "").strip()

    if not code:
        return render_template_string(
            HTML,
            result=None,
            error="Please select a scheme from the suggestions."
        )

    try:

        result = analyze_scheme(code)

        selected = schemes[
            schemes["Scheme Code"].astype(str).str.strip() == code
        ].iloc[0]

        full_name = str(selected["Scheme Name"]).strip()

        plan = str(selected["Plan"]).strip()
        option = str(selected["Option"]).strip()

        if plan.lower() != "nan":
            full_name += " - " + plan

        if option.lower() != "nan":
            full_name += " - " + option

        result["scheme_name"] = full_name

        return render_template_string(
            HTML,
            result=result,
            error=None,
            abs=abs
        )

    except Exception as e:

        return render_template_string(
            HTML,
            result=None,
            error=str(e)
        )


if __name__ == "__main__":

    app.run(debug=True)