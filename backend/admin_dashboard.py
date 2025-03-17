import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import psycopg2

# Connect to Database
conn = psycopg2.connect(
    database="your_db",
    user="your_user",
    password="your_password",
    host="your_host",
    port="5432"
)

# Fetch Data
def fetch_data():
    query = "SELECT feature_used, COUNT(*) as count FROM user_data GROUP BY feature_used"
    df = pd.read_sql(query, conn)
    return df

app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    html.H1("AI Data Insights"),
    dcc.Graph(id="feature-usage-chart")
])

@app.callback(
    dash.dependencies.Output("feature-usage-chart", "figure"),
    [dash.dependencies.Input("feature-usage-chart", "id")]
)
def update_graph(_):
    df = fetch_data()
    fig = px.bar(df, x="feature_used", y="count", title="Feature Usage Trends")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

#python backend/admin_dashboard.py
