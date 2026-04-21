# Dash RDS PostgreSQL Test App

A simple Dash application to test connectivity with AWS RDS PostgreSQL database.

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and update with your database credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python app.py`

## Environment Variables

Set these environment variables in your deployment platform:

- `DB_HOST`: RDS endpoint
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_PORT`: Database port (default: 5432)

## Deployment

This app can be deployed to various platforms that support Python applications:

- Posit Connect
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run

## Features

- Database connection testing
- Sample data creation and retrieval
- Data visualization with Plotly
- Responsive web interface