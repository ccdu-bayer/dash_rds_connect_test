import os
import dash
from dash import html, dcc, dash_table
import pandas as pd
import psycopg2
from datetime import datetime
import plotly.express as px

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "RDS PostgreSQL Connection Test"

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'ht-workflow.c9hukjucdlzt.us-east-1.rds.amazonaws.com'),
    'database': os.getenv('DB_NAME', 'htdb'),
    'user': os.getenv('DB_USER', 'ht6user'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'port': os.getenv('DB_PORT', '5432')
}

def test_db_connection():
    """Test database connection and return status"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Connected successfully! PostgreSQL version: {db_version}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_sample_data():
    """Get sample data from database or create dummy data if connection fails"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Create a simple test table if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM test_data;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO test_data (name, value) VALUES
                ('Sample A', 10),
                ('Sample B', 25),
                ('Sample C', 15),
                ('Sample D', 30),
                ('Sample E', 20);
            """)
            conn.commit()
        
        # Fetch data
        df = pd.read_sql_query("SELECT * FROM test_data ORDER BY created_at DESC LIMIT 10;", conn)
        
        cursor.close()
        conn.close()
        
        return df
    except Exception as e:
        # Return dummy data if database connection fails
        return pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Connection Error', 'Dummy Data', 'Check Logs'],
            'value': [0, 0, 0],
            'created_at': [datetime.now()] * 3
        })

# Test connection on startup
connection_status, connection_message = test_db_connection()

# Get sample data
df = get_sample_data()

# Create layout
app.layout = html.Div([
    html.H1("RDS PostgreSQL Connection Test", 
           style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Connection Status
    html.Div([
        html.H3("Connection Status:"),
        html.Div(
            connection_message,
            style={
                'padding': '10px',
                'backgroundColor': '#d4edda' if connection_status else '#f8d7da',
                'border': '1px solid #c3e6cb' if connection_status else '#f5c6cb',
                'borderRadius': '5px',
                'color': '#155724' if connection_status else '#721c24'
            }
        )
    ], style={'marginBottom': '30px'}),
    
    # Database Configuration (masked)
    html.Div([
        html.H3("Database Configuration:"),
        html.Ul([
            html.Li(f"Host: {DB_CONFIG['host']}"),
            html.Li(f"Database: {DB_CONFIG['database']}"),
            html.Li(f"User: {DB_CONFIG['user']}"),
            html.Li(f"Port: {DB_CONFIG['port']}"),
            html.Li("Password: ********")
        ])
    ], style={'marginBottom': '30px'}),
    
    # Sample Data Table
    html.Div([
        html.H3("Sample Data from Database:"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )
    ], style={'marginBottom': '30px'}),
    
    # Sample Chart
    html.Div([
        html.H3("Sample Chart:"),
        dcc.Graph(
            figure=px.bar(df, x='name', y='value', title='Sample Data Visualization')
        )
    ]),
    
    # Refresh Button
    html.Div([
        html.Button('Refresh Data', id='refresh-btn', n_clicks=0,
                   style={'marginTop': '20px', 'padding': '10px 20px'})
    ]),
    
    # Footer
    html.Hr(),
    html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
           style={'textAlign': 'center', 'color': 'gray'})
])

# Callback for refresh (optional - requires dash callbacks)
@app.callback(
    dash.dependencies.Output('refresh-btn', 'children'),
    [dash.dependencies.Input('refresh-btn', 'n_clicks')]
)
def refresh_data(n_clicks):
    if n_clicks > 0:
        return f'Refreshed ({n_clicks})'
    return 'Refresh Data'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)