import os
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "RDS PostgreSQL Connection Test"
server = app.server

# Database connection parameters
# DB_CONFIG = {
#     'host': os.getenv('DB_HOST', 'ht-workflow.c9hukjucdlzt.us-east-1.rds.amazonaws.com'),
#     'database': os.getenv('DB_NAME', 'htdb'),
#     'user': os.getenv('DB_USER', 'ht6user'),
#     'password': os.getenv('DB_PASSWORD', ''),
#     'port': os.getenv('DB_PORT', '5432')
# }
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'htdb'),
    'user': os.getenv('DB_USER', 'ht6user'),
    'password': os.getenv('DB_PASSWORD', 'ht6workflowdbpass'),
    'port': os.getenv('DB_PORT', '9012')
}

def test_db_connection():
    """Test database connection and return status"""
    try:
        import psycopg2
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Connected successfully! PostgreSQL version: {db_version}"
    except ImportError:
        return False, "psycopg2 module not available"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_sample_data():
    """Get sample data from database or create dummy data if connection fails"""
    try:
        import psycopg2
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
        
        return df, None
    except Exception as e:
        # Return dummy data if database connection fails
        dummy_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Connection Error', 'Using Dummy Data', 'Check Database Config', 'Verify Network', 'Check Logs'],
            'value': [0, 0, 0, 0, 0],
            'created_at': [datetime.now()] * 5
        })
        return dummy_df, str(e)

# Test connection on startup
connection_status, connection_message = test_db_connection()
df, data_error = get_sample_data()

# Create layout
app.layout = html.Div([
    html.Div(id='page-content', children=[
        html.H1("RDS PostgreSQL Connection Test", 
               style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'}),
        
        # System Information
        html.Div([
            html.H3("System Information:", style={'color': '#34495e'}),
            html.Ul([
                html.Li(f"Python Version: {sys.version}"),
                html.Li(f"Pandas Version: {pd.__version__}"),
                html.Li(f"Dash Version: {dash.__version__}"),
                html.Li(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            ])
        ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        # Connection Status
        html.Div([
            html.H3("Database Connection Status:", style={'color': '#34495e'}),
            html.Div(
                connection_message,
                style={
                    'padding': '15px',
                    'backgroundColor': '#d4edda' if connection_status else '#f8d7da',
                    'border': f'2px solid {"#c3e6cb" if connection_status else "#f5c6cb"}',
                    'borderRadius': '10px',
                    'color': '#155724' if connection_status else '#721c24',
                    'fontWeight': 'bold'
                }
            )
        ], style={'marginBottom': '30px'}),
        
        # Database Configuration (masked)
        html.Div([
            html.H3("Database Configuration:", style={'color': '#34495e'}),
            html.Div([
                html.P(f"🖥️  Host: {DB_CONFIG['host']}"),
                html.P(f"🗄️  Database: {DB_CONFIG['database']}"),
                html.P(f"👤  User: {DB_CONFIG['user']}"),
                html.P(f"🔌  Port: {DB_CONFIG['port']}"),
                html.P("🔑  Password: " + "●" * len(DB_CONFIG.get('password', ''))),
            ])
        ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
        
        # Data Error (if any)
        html.Div([
            html.Div([
                html.H3("⚠️ Data Retrieval Warning:", style={'color': '#e74c3c'}),
                html.P(f"Error: {data_error}", style={'color': '#c0392b'})
            ])
        ] if data_error else [], style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#fadbd8', 'borderRadius': '10px'}),
        
        # Sample Data Table
        html.Div([
            html.H3("📊 Sample Data:", style={'color': '#34495e'}),
            dash_table.DataTable(
                id='data-table',
                data=df.to_dict('records'),
                columns=[{"name": i.title().replace('_', ' '), "id": i} for i in df.columns],
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Arial'
                },
                style_header={
                    'backgroundColor': '#3498db',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    }
                ]
            )
        ], style={'marginBottom': '30px'}),
        
        # Sample Chart
        html.Div([
            html.H3("📈 Data Visualization:", style={'color': '#34495e'}),
            dcc.Graph(
                id='sample-chart',
                figure=px.bar(
                    df, 
                    x='name', 
                    y='value', 
                    title='Sample Data Values',
                    color='value',
                    color_continuous_scale='viridis'
                ).update_layout(
                    title_font_size=20,
                    xaxis_title="Categories",
                    yaxis_title="Values"
                )
            )
        ], style={'marginBottom': '30px'}),
        
        # Refresh Section
        html.Div([
            html.Button(
                '🔄 Refresh Data', 
                id='refresh-btn', 
                n_clicks=0,
                style={
                    'padding': '12px 24px',
                    'fontSize': '16px',
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginRight': '10px'
                }
            ),
            html.Span(id='refresh-status', style={'marginLeft': '10px', 'fontStyle': 'italic'})
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Footer
        html.Hr(),
        html.Div([
            html.P(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '0'}),
            html.P("🚀 Deployed from GitHub to Posit Connect",
                   style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '12px', 'margin': '5px 0'})
        ])
    ])
])

# Callback for refresh button
@callback(
    [Output('refresh-status', 'children'),
     Output('data-table', 'data'),
     Output('sample-chart', 'figure')],
    [Input('refresh-btn', 'n_clicks')]
)
def refresh_data(n_clicks):
    if n_clicks > 0:
        # Get fresh data
        new_df, error = get_sample_data()
        
        # Create new chart
        new_figure = px.bar(
            new_df, 
            x='name', 
            y='value', 
            title='Sample Data Values (Refreshed)',
            color='value',
            color_continuous_scale='viridis'
        ).update_layout(
            title_font_size=20,
            xaxis_title="Categories",
            yaxis_title="Values"
        )
        
        status_msg = f"✅ Refreshed at {datetime.now().strftime('%H:%M:%S')}"
        if error:
            status_msg += f" (Warning: {error})"
        
        return status_msg, new_df.to_dict('records'), new_figure
    
    return "", df.to_dict('records'), px.bar(df, x='name', y='value', title='Sample Data Values')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=True,   port=port)