from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)

# Load AMFI data
df = pd.read_csv("amfi_nav.csv")

# Ensure scheme names are treated as text
df["Scheme Name"] = df["Scheme Name"].fillna("").astype(str)


@app.route("/", methods=["GET", "POST"])
def home():

    results = []
    search_name = ""

    if request.method == "POST":

        search_name = request.form.get("scheme", "").strip()

        if search_name:

            matching_schemes = df[
                df["Scheme Name"].str.contains(
                    search_name,
                    case=False,
                    na=False,
                    regex=False
                )
            ].head(30)

            results = matching_schemes.to_dict("records")

    return render_template_string("""

    <!DOCTYPE html>
    <html>

    <head>

        <title>SPOT 52 - Mutual Fund NAV Tracker</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f2f5f9;
                margin: 0;
                text-align: center;
            }

            header {
                background: #102a43;
                color: white;
                padding: 25px;
            }

            header h1 {
                font-size: 38px;
                margin: 5px;
            }

            header p {
                color: #55d6be;
            }

            .container {
                padding: 25px;
            }

            input {
                padding: 13px;
                width: 70%;
                max-width: 350px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }

            button {
                padding: 13px 20px;
                background: #008f83;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }

            .card {
                background: white;
                padding: 20px;
                margin: 15px auto;
                max-width: 450px;
                border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            }

            .card h3 {
                color: #102a43;
            }

            .value {
                color: #008f83;
                font-weight: bold;
                font-size: 20px;
            }

            footer {
                background: #102a43;
                color: white;
                padding: 15px;
                margin-top: 30px;
            }

        </style>

    </head>

    <body>

        <header>

            <h1>SPOT 52</h1>

            <p>MUTUAL FUND NAV TRACKER</p>

            <h3>Know where your fund stands.</h3>

        </header>

        <div class="container">

            <h2>Search Mutual Fund</h2>

            <form method="POST">

                <input
                    type="text"
                    name="scheme"
                    placeholder="Enter mutual fund name"
                    value="{{ search_name }}"
                    required
                >

                <button type="submit">Search</button>

            </form>

            {% if search_name %}

                <h3>Search Results</h3>

                {% if results %}

                    <p>{{ results|length }} matching schemes displayed</p>

                    {% for row in results %}

                        <div class="card">

                            <h3>{{ row['Scheme Name'] }}</h3>

                            <p>Scheme Code: {{ row['Scheme Code'] }}</p>

                            <p>Plan: {{ row['Plan'] }}</p>

                            <p>Option: {{ row['Option'] }}</p>

                            <p class="value">
                                NAV: ₹{{ "%.4f"|format(row['NAV']) }}
                            </p>

                            <p>NAV Date: {{ row['NAV Date'] }}</p>

                        </div>

                    {% endfor %}

                {% else %}

                    <p>No matching schemes found.</p>

                {% endif %}

            {% endif %}

        </div>

        <footer>

            <p>SPOT 52 | Mutual Fund Research Tool</p>

            <p>Data Source: AMFI</p>

        </footer>

    </body>

    </html>

    """, results=results, search_name=search_name)


if __name__ == "__main__":

    app.run(debug=True)