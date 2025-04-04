# ================================
# Step 1: Importation of libraries
# ================================

# We import Dash to create our web application
import dash

# We import other necessary components of Dash such as dcc for graphics and interactive components
# html to create HTML content, and dash_table to display data table.
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# We import Plotly to generate interactive graphics
import plotly.graph_objs as go

# We import Pandas to analyse data
import pandas as pd

# We import other libraries
from datetime import datetime, timedelta  # used to manage datetime format
from jinja2 import Template  # used to generate dynamically HTML report


# ==========================================
# STEP 2: Initialization of the application
# ==========================================

# We create our Dash app with a dark theme (CYBORG => visually better)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# We define the title of our application, which will be displayed on the browser tab.
app.title = "Dashboard TSLA Marie and Nathan IF1"

server = app.server  # Allows Gunicorn to find Flask app

# ===========================
# STEP 3: Load and Clean Data
# ===========================

def load_data():
    df = pd.read_csv("prix_TSLA.csv", sep=";", parse_dates=["Date"], dayfirst=False)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    df = df.dropna()
    df['Price'] = df['Prix'].astype(str).str.replace(',', '.').astype(float)
    df['ESG Score'] = df['ESG Score'].astype(str).str.extract(r'(\d+,\d+)')[0].str.replace(',', '.').astype(float)
    df['Change'] = df['Variation'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
    df['Bid_Quantity'] = df['Quantite_Bid'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float).astype(int)
    df['Bid_Price'] = df['Prix_Bid'].astype(str).str.replace(',', '.').str.replace(' ', '').astype(float)
    df['Ask_Quantity'] = df['Quantite_Ask'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float).astype(int)
    df['Ask_Price'] = df['Prix_Ask'].astype(str).str.replace(',', '.').str.replace(' ', '').astype(float)
    df['Previous_Close'] = df['Cloture_Precedente'].astype(str).str.replace(',', '.').str.replace(' ', '').astype(float)
    df['High'] = df['Plus_Haut'].astype(str).str.replace(',', '.').str.replace(' ', '').astype(float)
    df['Low'] = df['Plus_Bas'].astype(str).str.replace(',', '.').str.replace(' ', '').astype(float)
    return df

# ==========================
# STEP 4: Graphs and Metrics
# ==========================

def graph_price(df):
    return go.Figure([
        go.Scatter(x=df['Date'], y=df['Price'], mode='lines', name='Price', line=dict(color='royalblue'))
    ]).update_layout(title="Price Evolution (TSLA)", template="plotly_dark")

def graph_recent_variation(df):
    last_hours = df[df['Date'] >= df['Date'].max() - timedelta(hours=3)]
    return go.Figure([
        go.Scatter(x=last_hours['Date'], y=last_hours['Change'], mode='lines+markers', name='Recent Change', line=dict(color='orange'))
    ]).update_layout(title="Change Over the Last 3 Hours (%)", template="plotly_dark")

def display_esg_score(df):
    current_esg = df['ESG Score'].dropna().iloc[-1] if not df['ESG Score'].dropna().empty else None
    score_display = f"{current_esg:.1f} / 100" if current_esg is not None and not pd.isna(current_esg) else "Data unavailable"

    return html.Div([
        html.H2("Current ESG Score", className="text-white text-center mb-2", style={"fontSize": "2.2rem", "fontFamily": "Segoe UI"}),
        html.H1(score_display, className="text-success text-center", style={"fontSize": "3.5rem", "fontWeight": "bold", "fontFamily": "Segoe UI"}),
        html.P("(Last available value in the dataset)", className="text-white text-center", style={"fontFamily": "Segoe UI"})
    ], style={"backgroundColor": "#1e1e1e", "padding": "2rem", "borderRadius": "10px", "height": "100%"})

def display_volume(df):
    today = df['Date'].dt.date == df['Date'].max().date()
    volume = df.loc[today, 'Bid_Quantity'].sum() + df.loc[today, 'Ask_Quantity'].sum()

    return html.Div([
        html.H2("Volume Traded (Today)", className="text-white text-center mb-2", style={"fontSize": "2.2rem", "fontFamily": "Segoe UI"}),
        html.H1(f"{int(volume):,} shares", className="text-center text-purple", style={"fontSize": "3.5rem", "fontWeight": "bold", "fontFamily": "Segoe UI"}),
        html.P("Reflects investor interest and liquidity for Tesla.", className="text-white text-center", style={"fontFamily": "Segoe UI"})
    ], style={"backgroundColor": "#1e1e1e", "padding": "2rem", "borderRadius": "10px", "height": "100%"})

def graph_bid_ask_pie(df):
    bid = df['Bid_Quantity'].sum()
    ask = df['Ask_Quantity'].sum()
    return go.Figure([
        go.Pie(labels=["Bid Quantity", "Ask Quantity"], values=[bid, ask], marker=dict(colors=['green', 'red']), hole=0.4)
    ]).update_layout(title="Bid/Ask Quantity Distribution", template="plotly_dark")

def graph_volume_smooth(df):
    df['Volume'] = df['Bid_Quantity'] + df['Ask_Quantity']
    df['Volume_MA'] = df['Volume'].rolling(window=3).mean()
    return go.Figure([
        go.Scatter(x=df['Date'], y=df['Volume_MA'], mode='lines', name='Average Volume', line=dict(color='violet'))
    ]).update_layout(title="Smoothed Volume (Bid + Ask)", template="plotly_dark")

def graph_spread_histogram(df):
    spread = df['Ask_Price'] - df['Bid_Price']
    return go.Figure([
        go.Histogram(x=spread, nbinsx=30, marker_color='#1f77b4')
    ]).update_layout(title="Bid-Ask Spread Distribution", template="plotly_dark")

def graph_high_low_area(df):
    return go.Figure([
        go.Scatter(x=df['Date'], y=df['High'], name='High', mode='lines', line=dict(color='darkorange')),
        go.Scatter(x=df['Date'], y=df['Low'], name='Low', mode='lines', fill='tonexty', line=dict(color='lightblue'))
    ]).update_layout(title="Daily High/Low Range", template="plotly_dark")

# =======================
# Table with Last 5 Rows
# =======================

def last_five_rows_table(df):
    last_five = df.tail(5)
    return dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in last_five.columns],
        data=last_five.to_dict('records'),
        style_table={'height': '250px', 'overflowY': 'auto', 'backgroundColor': '#2c2c2c'},
        style_cell={'color': 'white', 'backgroundColor': '#2c2c2c', 'textAlign': 'center'},
        style_header={'fontWeight': 'bold', 'textAlign': 'center', 'backgroundColor': '#343a40', 'color': 'white'}
    )

# =========================
# STEP 5: Daily HTML Report
# =========================

def generate_html_report(df):
    today = df[df['Date'].dt.date == df['Date'].max().date()]
    if today.empty:
        return "<p>No data available for today.</p>"

    template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>TESLA Daily Report - {{ date }}</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background-color: #121212;
                color: #f0f0f0;
                padding: 2rem;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: #1e1e1e;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 0 10px #000;
            }
            h1, h2 {
                text-align: center;
                color: #ffffff;
            }
            table {
                width: 100%;
                margin-top: 2rem;
                border-collapse: collapse;
                font-size: 1.1rem;
            }
            th, td {
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #444;
            }
            th {
                color: #00bfff;
                font-weight: bold;
            }
            .footer {
                text-align: center;
                font-size: 0.9rem;
                color: #aaa;
                margin-top: 3rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TESLA Daily Report</h1>
            <h2>{{ date.strftime('%B %d, %Y') }}</h2>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr><td>Average Price</td><td>{{ avg_price }} €</td></tr>
                <tr><td>High Price</td><td>{{ high }} €</td></tr>
                <tr><td>Low Price</td><td>{{ low }} €</td></tr>
                <tr><td>Volatility (Std Dev)</td><td>{{ volatility }}</td></tr>
                <tr><td>ESG Score</td><td>{{ esg }} / 100</td></tr>
                <tr><td>Total Volume</td><td>{{ "{:,}".format(volume) }} shares</td></tr>
            </table>

            <div class="footer">
                Report generated by Marie Aracil & Nathan Arpin - IF1<br>
                {{ date.strftime('%Y-%m-%d') }}
            </div>
        </div>
    </body>
    </html>
    """)

    return template.render(
        date=today['Date'].max().date(),
        avg_price=round(today['Price'].mean(), 2),
        high=round(today['High'].max(), 2),
        low=round(today['Low'].min(), 2),
        volatility=round(today['Price'].std(), 4),
        esg=round(today['ESG Score'].mean(), 1),
        volume=int(today['Bid_Quantity'].sum() + today['Ask_Quantity'].sum())
    )


# ==============
# STEP 6: Layout
# ==============

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png",
                style={"height": "150px", "marginBottom": "10px"}
            ),
            width="auto"
        ),
        dbc.Col(
            html.H2(
                "Our Project: TESLA Dashboard",
                className="text-white mb-4 text-center",
                style={"fontFamily": "'Segoe UI', sans-serif", "paddingTop": "60px"}
            ),
            align="center"
        )
    ]),

    dbc.Card(
        dbc.CardBody([
            html.H5(
                "Why TESLA?",
                className="card-title text-white",
                style={"fontFamily": "sans-serif", "fontWeight": "bold"}
            ),
            html.P(
                "We chose Tesla because it is frequently in the financial spotlight!",
                className="card-text text-white"
            ),
            html.A(
                "We decided to scrap data from Boursorama:",
                href="https://www.boursorama.com/cours/TSLA/",
                target="_blank",
                className="card-text text-white"
            ),
            html.P(
                "But, to do this project, we realized several different steps:",
                className="card-text text-white"
            ),
            html.Ul([
                html.Li("Step 1: We created a scrapper using a Bash script."),
                html.Li("Step 2: We stored the collected data in an Excel file."),
                html.Li("Step 3: We coded this dashboard which updates every 5 minutes — a daily report is downloadable at 8 PM."),
            ], className="text-white")
        ]),
        style={"backgroundColor": "#2c2c2c", "borderRadius": "10px", "padding": "20px"}
    ),

    html.Hr(),

    dbc.Row([
        dbc.Col([display_esg_score(load_data())], md=6),
        dbc.Col([display_volume(load_data())], md=6)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=graph_price(load_data())),
            html.P("Shows the long-term price evolution — useful for trend analysis and historical comparisons.", className="text-white text-center mt-2")
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=graph_recent_variation(load_data())),
            html.P("Highlights recent fluctuations — essential to detect short-term volatility and momentum.", className="text-white text-center mt-2")
        ], md=6)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=graph_bid_ask_pie(load_data())),
            html.P("Compares the number of buyers and sellers — gives an idea of who is most active in the market.", className="text-white text-center mt-2")
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=graph_volume_smooth(load_data())),
            html.P("Shows how much Tesla stock is being traded over time — easier to spot busy or quiet periods.", className="text-white text-center mt-2")
        ], md=6)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=graph_spread_histogram(load_data())),
            html.P("Displays how different the buying and selling prices are — helpful to understand how easy it is to trade.", className="text-white text-center mt-2")
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=graph_high_low_area(load_data())),
            html.P("Shows the highest and lowest prices during each day — useful to spot strong movements or stability.", className="text-white text-center mt-2")
        ], md=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H4(
                "Last 5 Rows Summary",
                className="text-white text-center mb-4",
                style={"fontFamily": "sans-serif"}
            ),
            last_five_rows_table(load_data())
        ], className="mt-4 mb-4")
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H4("Download Daily HTML Report", className="text-white mt-4 mb-3"),
            html.A(
                dbc.Button(
                    "Download HTML Report",
                    id="btn-download",
                    color="secondary",
                    className="mt-2",
                    style={'width': '100%'}
                ),
                id="download-link",
                href=None,
                target="_blank",
                hidden=datetime.now().hour < 20
            ),
            dcc.Download(id="download-html-report")
        ])
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.P(
                "Python Git Linux Project - Group Marie Aracil & Nathan Arpin IF1",
                className="text-muted text-center"
            ),
            html.Div([
                html.A(
                    "Source Code on GitHub",
                    href="https://github.com/Ma-moi/Projet_Python_Git_Linux",
                    target="_blank"
                )
            ], className="text-center")
        ])
    ])
], fluid=True)


# =================================
# STEP 7: Callback to Download HTML
# =================================

@app.callback(
    Output("download-html-report", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True
)
def download_html(n):
    df = load_data()
    html_content = generate_html_report(df)
    return dcc.send_string(html_content, filename=f"report_{datetime.now().strftime('%Y%m%d')}.html")

# ===========
# RUN THE APP
# ===========

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
