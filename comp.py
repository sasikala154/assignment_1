import mysql.connector
import requests

# Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=0aRv55dviakXsgmkMGeQQvn67qnWxeUj3dHGPFwx"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
else:
    print(f"API request failed with status code {response.status_code}")
    exit()

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7094193019@milan",
    database="Sport"
)
cursor = conn.cursor()

# Create the Complexes table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Complexes (
        Complex_id CHAR(50) PRIMARY KEY,
        Complex_name VARCHAR(100) NOT NULL
    )
''')

# Create the Venues table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Venues (
        Venue_id CHAR(50) PRIMARY KEY,
        Venue_name VARCHAR(100) NOT NULL,
        City_name VARCHAR(100) NOT NULL,
        Country_name VARCHAR(100) NOT NULL,
        Country_code CHAR(3) NOT NULL,
        Timezone VARCHAR(100) NOT NULL,
        Complex_id CHAR(50),
        FOREIGN KEY (Complex_id) REFERENCES Complexes(Complex_id)
    )
''')

# Insert data into the tables
for complex_item in data.get("complexes", []):
    Complex_id = complex_item["id"]
    Complex_name = complex_item["name"]

    # Insert into the Complexes table
    cursor.execute('''
        INSERT IGNORE INTO Complexes (Complex_id, Complex_name)
        VALUES (%s, %s)
    ''', (Complex_id, Complex_name))

    # Insert venues related to the complex
    for venue in complex_item.get("venues", []):
        Venue_id = venue["id"]
        Venue_name = venue["name"]
        City_name = venue.get("city_name", "N/A")
        Country_name = venue.get("country_name", "N/A")
        Country_code = venue.get("country_code", "N/A")
        Timezone = venue.get("timezone", "N/A")

        # Insert into the Venues table
        cursor.execute('''
            INSERT IGNORE INTO Venues (Venue_id, Venue_name, City_name, Country_name, Country_code, Timezone, Complex_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (Venue_id, Venue_name, City_name, Country_name, Country_code, Timezone, Complex_id))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully into Complexes and Venues tables!")