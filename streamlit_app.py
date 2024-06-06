import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape data from Zerodha Economic Calendar
def scrape_zerodha_calendar():
    url = "https://zerodha.com/markets/calendar/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extracting data from the table
    table = soup.find("table")
    tbody = table.find("tbody")

    # Lists to hold the data
    dates = []
    events = []
    importance = []
    previous = []
    actual = []
    units = []
    countries = []

    # Temporary variable to hold the current date while iterating
    current_date = ""

    for row in tbody.find_all("tr"):
        # Check if the row is a date row or an event row
        if "date" in row.get("class", []):
            current_date = row.find("td", class_="date").text.strip()
        else:
            event = row.find("td", class_=None).text.strip()
            imp = row.find("span", class_="importance").text.strip()
            prev = row.find("td", class_="prev").text.strip()
            actl = row.find("td", class_="actual").text.strip()
            unit = row.find("td", class_="unit").text.strip()
            
            # Extract country from event description (assuming it’s within parentheses)
            country = event.split('(')[-1].replace(')', '').strip() if '(' in event else "Unknown"
            
            dates.append(current_date)
            events.append(event)
            importance.append(imp)
            previous.append(prev)
            actual.append(actl)
            units.append(unit)
            countries.append(country)
    
    # Creating a DataFrame
    data = {
        "Date": dates,
        "Event": events,
        "Importance": importance,
        "Previous": previous,
        "Actual": actual,
        "Units": units,
        "Country": countries
    }
    df = pd.DataFrame(data)
    return df

# Main function to run the Streamlit app
def main():
    st.title("Zerodha Economic Calendar")
    st.subheader("Filter events by country")

    # Scrape the data
    df = scrape_zerodha_calendar()

    # Extract unique countries for the filter
    countries = df["Country"].unique()
    
    # Multi-select widget for country filter
    selected_countries = st.multiselect("Select countries", options=countries, default=countries)

    # Filter data based on selected countries
    filtered_df = df[df["Country"].isin(selected_countries)]
    
    # Display the filtered DataFrame
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
