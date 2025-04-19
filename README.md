# Budget Reporting

This is a Streamlit app that allows me to view my budget and actuals in a single dashboard.

It uses a PostgreSQL database I have running locally. I have a separate dbt code project to manage the data, which is called `dbt_money`.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Streamlit secrets:
```bash
streamlit secrets
```

3. Run the app:
```bash
streamlit run streamlit_app.py
```

## Notes

