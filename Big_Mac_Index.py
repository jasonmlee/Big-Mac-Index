import pandas as pd
from datetime import date, datetime
import streamlit as st
import altair as alt
import requests
from bs4 import BeautifulSoup

filename = 'https://raw.githubusercontent.com/jasonmlee/Big-Mac-Index/main/big-mac-full-index.csv'
CurrencyUrl = 'https://www.iban.com/currency-codes'

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
  - price of a big mac in CCY
  """

  df=pd.read_csv(filename)
  df['date'] = pd.to_datetime(df['date'])
  df['date2'] = df['date'].dt.strftime('%b %Y')
  raw_data = df[['date','date2','currency_code', 'local_price', 'dollar_ex', 'dollar_price']]
  return raw_data

def merged_data(filename: str):
  """
  Merges IBAN currency code table with raw data
  """
  raw_data = read(filename)
  merged_data = raw_data.merge(get_currency_codes(CurrencyUrl), on='currency_code', how='left')
  return merged_data

def date_filter(df, date: str):
  """
  Takes a DataFrame and filters by a specified date
  """
  df = read(filename).set_index("date2").sort_index()
  df_filtered_date = df.loc[date]
  return df_filtered_date

def date_list(filename):
  """
  Takes a DataFrame and returns the full list of dates
  """

  df=read(filename)
  date_data = df['date2'].unique()
  return date_data

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

def get_currency_codes(url: str):
  """
  Uses the Beautiful Soup Library to Webscrape IBAN Currency Code Data. Returns a DataFrame.
  """

  with requests.Session() as session:
    info = session.get(url)
    soup = BeautifulSoup(info.text, 'html.parser')

  html_table = soup.find_all('table')[0]
  data = pd.read_html(html_table.prettify())
  CurrencyData = data[0]

  CurrencyData["currency_code"] = CurrencyData["Code"]
  CurrencyData["currency_name"] = CurrencyData["Currency"]
  CurrencyData = CurrencyData[["currency_code", "currency_name", "Country"]]

  return CurrencyData


st.write("""
  # Visualizing The Big Mac Index
  The Big Mac Index was invented in 1986 by The Economist as a lighthearted guide to whether currencies are at their "correct" level. It is based on the theory of purchasing-power parity (PPP), the notion that in the long run exchange rates should move towards the rate that would equalise the prices of an identical basket of goods and services (in this case, a burger) in any two countries.

""")

currency = st.selectbox(
    'Base Currency',
    ('USD', 'CAD', 'CNY', 'GBP', 'JPY'))

datelist =  date_list(filename)

date = st.selectbox(
    'Select Date',
    datelist)

data = analyze(filename, date, currency)

c = alt.Chart(data).mark_bar().encode(
    alt.X('currency_code:N', sort='y', title='Currency Code'),
    alt.Y('pct_over_under_valued', title='Percentage over/under-valued')
)



st.altair_chart(c, use_container_width=True)
