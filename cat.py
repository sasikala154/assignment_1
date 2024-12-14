import mysql.connector
import requests

# Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=0aRv55dviakXsgmkMGeQQvn67qnWxeUj3dHGPFwx"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)
data = response.json()

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7094193019@milan",
    database="Sport"
)

cursor = conn.cursor()

# Create the Categories table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        Category_id VARCHAR(250) PRIMARY KEY,
        Category_name VARCHAR(250) NOT NULL
    )
''')

# Create the Competitions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Competitions (
        Competition_id VARCHAR(250) PRIMARY KEY,
        Competition_name VARCHAR(250) NOT NULL,
        Parent_id VARCHAR(250),
        Type VARCHAR(100),
        Gender VARCHAR(50),
        Category_id VARCHAR(250),
        FOREIGN KEY (Category_id) REFERENCES Categories(Category_id)
    )
''')

# Insert data into the tables
for competition in data["competitions"]:
    # Extract data for the Categories table
    category_id = competition["category"]["id"]
    category_name = competition["category"]["name"]

    # Insert into Categories table (avoid duplicates using INSERT IGNORE)
    cursor.execute('''
        INSERT IGNORE INTO Categories (Category_id, Category_name)
        VALUES (%s, %s)
    ''', (category_id, category_name))

    # Extract data for the Competitions table
    competition_id = competition["id"]
    competition_name = competition["name"]
    parent_id = competition.get("parent_id", None)  # Use None if not present
    competition_type = competition["type"]
    gender = competition.get("gender", None)  # Use None if not present

    # Insert into Competitions table (avoid duplicates using INSERT IGNORE or update on conflict)
    cursor.execute('''
        INSERT INTO Competitions (Competition_id, Competition_name, Parent_id, Type, Gender, Category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Competition_name = VALUES(Competition_name),
            Parent_id = VALUES(Parent_id),
            Type = VALUES(Type),
            Gender = VALUES(Gender),
            Category_id = VALUES(Category_id)
    ''', (competition_id, competition_name, parent_id, competition_type, gender, category_id))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully into Categories and Competitions tables!") 