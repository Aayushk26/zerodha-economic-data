import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import streamlit as st
import pytz
from pycountry import countries

url = 'https://zerodha.com/markets/calendar/'

response = requests.get(url)
da = None

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')

    if table:
        headers = []
        for th in table.find('thead').find_all('th'):
            headers.append(th.text.strip())

        rows = []
        for tr in table.find('tbody').find_all('tr'):
            cells = []
            for td in tr.find_all('td'):
                cells.append(td.text.strip())
            rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)
        da = df
        print(df)

        df.to_csv('zerodha_calendar_data.csv', index=False)
    else:
        print('Table not found on the webpage.')
else:
    print(f'Failed to retrieve the webpage. Status code: {response.status_code}')


def extract_country(event):
    if isinstance(event, str):
        match = re.search(r'\((.*?)\)', event)
        if match:
            return match.group(1)
        else:
            return 'India'
    else:
        return 'India'


da['Country'] = da['Event'].apply(extract_country)
da['Date'] = da['Date'].astype(str)
da['Date'] = da['Date'].replace('', pd.NA).fillna(method='ffill')
da = da[da['Event'].notna()]

da.reset_index(drop=True, inplace=True)


def remove_country_from_event(event):
    return re.sub(r'\s*\(.*?\)', '', event)


da['Event'] = da['Event'].apply(remove_country_from_event)


def display_events(events):
    if events is None or events.empty:
        st.write("No upcoming events found.")
        return

    events['Day'] = pd.to_datetime(events['Date'], format='%a, %d %b %Y').dt.tz_localize('UTC').dt.tz_convert(
        'Asia/Kolkata').dt.strftime('%A')

    events['Days from Today'] = (pd.to_datetime(events['Date'], format='%a, %d %b %Y') - pd.Timestamp('today')).dt.days

    def highlight_importance(val):
        if val == 'High':
            color = 'lightcoral'
        elif val == 'Medium':
            color = 'lightblue'
        elif val == 'Low':
            color = 'lightgreen'
        else:
            color = ''
        return f'background-color: {color}'

    events_styled = events.style.applymap(highlight_importance, subset=['Importance'])

    legend_style = "background-color: rgba(240, 240, 240, 0.7); padding: 8px; margin-bottom: 8px;"
    st.markdown(
        "<div style='" + legend_style + "'>"
                                        "<div style='background-color:lightcoral;padding:8px;margin-bottom:4px;'>High Importance</div>"
                                        "<div style='background-color:lightblue;padding:8px;margin-bottom:4px;'>Medium Importance</div>"
                                        "<div style='background-color:lightgreen;padding:8px;margin-bottom:4px;'>Low Importance</div>"
                                        "</div>",
        unsafe_allow_html=True
    )

    st.dataframe(events_styled, width=1000, height=600)


def main():
    st.title("Economic Calendar")

    # List of valid country names from pycountry
    valid_country_names = {country.name for country in countries}

    # Include "Euro Area" in the list of valid names
    valid_country_names.add("Euro Area")

    available_countries = [country for country in da['Country'].unique().tolist() if country in valid_country_names]

    countries = st.multiselect("Select countries:", available_countries, default=["India"])

    date_ranges = {
        "7 days from today": 7,
        "14 days from today": 14,
        "1 month from today": 30,
    }
    selected_range = st.selectbox("Select date range:", list(date_ranges.keys()), index=1)
    max_days = date_ranges[selected_range]
    today = datetime.today().strftime('%a, %d %b %Y')
    to_date = (datetime.today() + timedelta(days=max_days)).strftime('%a, %d %b %Y')

    if countries:
        filtered_events = da[(da['Country'].isin(countries)) &
                             (pd.to_datetime(da['Date'], format='%a, %d %b %Y') >= pd.to_datetime(today)) &
                             (pd.to_datetime(da['Date'], format='%a, %d %b %Y') <= pd.to_datetime(to_date))]
        display_events(filtered_events)


main()
