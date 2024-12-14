import streamlit as st
import mysql.connector
import pandas as pd
import altair as alt

# Set up the MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sai@12345",
        database="Sport"
    )

# Function to fetch data from the database
def fetch_data(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return pd.DataFrame(result)

# Streamlit app
st.set_page_config(page_title="Tennis Data Analytics", layout="wide")
st.title("Game Analytics: Unlocking Tennis Data with SportRadar API")
st.sidebar.title("Navigation")
options = ["Homepage", "Search Competitors", "Country-Wise Analysis", "Leaderboards"]
page = st.sidebar.radio("Go to", options)

if page == "Homepage":
    st.header("Homepage Dashboard")

    # Summary statistics
    total_competitors = fetch_data("SELECT COUNT(*) AS total FROM Competitors").iloc[0]['total']
    total_countries = fetch_data("SELECT COUNT(DISTINCT country) AS total FROM Competitors").iloc[0]['total']
    highest_points = fetch_data("SELECT MAX(points) AS max_points FROM Competitor_Rankings").iloc[0]['max_points']

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Competitors", total_competitors)
    col2.metric("Countries Represented", total_countries)
    col3.metric("Highest Points", highest_points)

    # Chart for points distribution
    points_data = fetch_data("SELECT points, name FROM Competitor_Rankings JOIN Competitors ON Competitor_Rankings.competitor_id = Competitors.competitor_id")
    chart = alt.Chart(points_data).mark_bar().encode(
        x=alt.X("points", bin=True),
        y="count()",
        tooltip=["count()"]
    ).properties(title="Points Distribution")
    st.altair_chart(chart, use_container_width=True)

elif page == "Search Competitors":
    st.header("Search and Filter Competitors")

    # Filters
    name = st.text_input("Search by Name")
    country = st.text_input("Filter by Country")
    min_rank, max_rank = st.slider("Rank Range", 1, 500, (1, 100))

    # Query with filters
    query = """
    SELECT c.name, c.country, cr.rank, cr.points, cr.competitions_played
    FROM Competitors c
    JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    WHERE cr.rank BETWEEN %s AND %s
    """
    params = [min_rank, max_rank]

    if name:
        query += " AND c.name LIKE %s"
        params.append(f"%{name}%")

    if country:
        query += " AND c.country = %s"
        params.append(country)

    competitors = fetch_data(query % tuple(params))
    st.dataframe(competitors)

elif page == "Country-Wise Analysis":
    st.header("Country-Wise Analysis")

    # Query for country-wise data
    country_data = fetch_data("""
        SELECT country, COUNT(*) AS num_competitors, AVG(points) AS avg_points
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        GROUP BY country
    """)

    st.dataframe(country_data)

    # Bar chart for average points by country
    chart = alt.Chart(country_data).mark_bar().encode(
        x="country",
        y="avg_points",
        tooltip=["avg_points"]
    ).properties(title="Average Points by Country")
    st.altair_chart(chart, use_container_width=True)

elif page == "Leaderboards":
    st.header("Leaderboards")

    # Top-ranked competitors
    top_competitors = fetch_data("""
        SELECT c.name, c.country, cr.rank, cr.points
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.rank ASC
        LIMIT 10
    """)
    st.subheader("Top 10 Competitors")
    st.dataframe(top_competitors)

    # Competitors with highest points
    highest_points_competitors = fetch_data("""
        SELECT c.name, c.country, cr.points, cr.week
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE cr.week = (SELECT MAX(week) FROM Competitor_Rankings)
        ORDER BY cr.points DESC
        LIMIT 10
    """)
    st.subheader("Competitors with Highest Points")
    st.dataframe(highest_points_competitors)

st.sidebar.info("Developed as part of 'Game Analytics: Unlocking Tennis Data with SportRadar API' project.")
