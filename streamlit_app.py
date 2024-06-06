import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape data
def scrape_data():
    url = "https://zerodha.com/markets/calendar/"
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    events = []
    dates = []
    previous = []
    actual = []
    importance = []

    table = soup.find("table")
    tbody = table.find("tbody")

    for row in tbody.find_all("tr"):
        date_row = row.get("class")
        if date_row and "date" in date_row:
            current_date = row.find("td", class_="date").text.strip()
            continue
        event = row.find("td", class_=None).text.strip()
        prev = row.find("td", class_="prev").text.strip()
        actl = row.find("td", class_="actual").text.strip()
        imp = row.find("span", class_="importance").text.strip()
        
        events.append(event)
        dates.append(current_date)
        previous.append(prev)
        actual.append(actl)
        importance.append(imp)

    data = {
        "Event": events,
        "Date": dates,
        "Previous": previous,
        "Actual": actual,
        "Importance": importance
    }

    df = pd.DataFrame(data)
    return df

# Main function
def main():
    st.title("Zerodha Economic Calendar")
    st.subheader("Displaying scraped data")

    # Scrape data and display DataFrame
    df = scrape_data()
    st.write(df)

if __name__ == "__main__":
    main()
