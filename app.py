from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from models import Account



csv_file = st.file_uploader('Choose a CSV file', type='csv')

if csv_file:
    account = Account.from_chase_account_activity(csv_file.name, 'checking')
    df = account.to_df()
    st.title(str(account))


    today = datetime.now().date()

    date_ranges = {
        'Last 7 Days': today - timedelta(days=7),
        'Last 30 Days': today - timedelta(days=30),
        'Last Year': today.replace(year=today.year - 1),
        'Year to Date': today.replace(month=1, day=1),
        'All Time': df['Date'].min(),
    }

    option = st.selectbox('Select Date Range', list(date_ranges.keys()))

    start_date = date_ranges[option]

    df['Date'] = pd.to_datetime(df['Date'])

    filtered_df = df[df['Date'] >= pd.to_datetime(start_date)]
    filtered_df['Date'] = filtered_df['Date'].dt.date

    st.dataframe(filtered_df, hide_index=True, use_container_width=True)

    # Write total from filtered_df
    st.write(f'Total: {filtered_df["Amount"].sum()}')