import pandas as pd
from datetime import date, datetime
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt

filename = 'https://raw.githubusercontent.com/jasonmlee/Big-Mac-Index/main/big-mac-full-index.csv'

def analyze(filename: str, date: str, base_ccy):
  """
  Takes a csv file and specified date and returns a bar plot
  """

  #step 1: reads the file
  raw_data = read(filename)

  #step 2: filters the data
  df_filtered_date = date_filter(raw_data, date)

  #step 3: find the base currency Big Mac Price
  base_bmp = find_base_bmp(df_filtered_date, base_ccy)

  #step 4: Calculate the BMER and add column to DF
  df_filtered_date['bmer'] = calculate_bmer(df_filtered_date, base_bmp)

  #step 5: Calculate the Percentage over/under-valued
  df_filtered_date['pct_over_under_valued'] = calculate_pct_over_under_valued(df_filtered_date)

  #step 6: Sort in Ascending Order
  df_filtered_date = df_filtered_date.sort_values(by=['pct_over_under_valued'])

  return df_filtered_date

def read(filename: str):
  """
  Reads the CSV and returns a DataFrame containing the:
  - date
  - currency code
  - local price of a big mac
  - dollar exchange rate
  - price of a big mac in USD
  """

  df=pd.read_csv(filename)
  df['date'] = pd.to_datetime(df['date'])
  raw_data = df[['date', 'currency_code', 'local_price', 'dollar_ex', 'dollar_price']]
  return raw_data

def date_filter(df, date: str):
  """
  Takes a DataFrame and filters by a specified date
  """
  df = read(filename).set_index("date").sort_index()
  df_filtered_date = df.loc[date]
  return df_filtered_date

def find_base_bmp(df, base_ccy: str):
  """
  Takes a df and returns the price of a Big Mac in USA
  """
  return df[df['currency_code'] == base_ccy]['local_price']

def calculate_bmer(df, base_bmp: float):
  """
  Calculates the Big Mac Exchange Rate
  """
  return df['local_price'] / base_bmp

def calculate_pct_over_under_valued(df):
  """
  Calculates the percentage over/under-valued relative to the USD Exchange Rate
  """
  return ((df['bmer'] / df['dollar_ex']) - 1)*100


st.write("""
  # Visualizing The Big Mac Index

""")

currency = st.selectbox(
    'Which base currency do you want to use?',
    ('USD', 'CAD', 'CNY', 'GBP', 'JPY'))

data = analyze(filename, '2022-07-01', currency)

c = alt.Chart(data).mark_bar().encode(
    alt.X('currency_code:N', sort='y', title='Currency Code'),
    alt.Y('pct_over_under_valued', title='Percentage over/under-valued')
)

st.altair_chart(c, use_container_width=True)
