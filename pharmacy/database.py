import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('pharmacy_inventory.db')
cursor = conn.cursor()


# Function to create the table if it doesn't exist
def create_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dosage TEXT,
        form TEXT,
        manufacturer TEXT,
        stock INTEGER,
        expiry_date TEXT,
        reorder_point INTEGER,
        price REAL
    )""")
    conn.commit()


create_table()  # Call the function to create the table


# create patients table


def create_patients_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone_number TEXT,
        allergies TEXT
    )""")
    conn.commit()


create_patients_table()  # Call the function to create the table


# create prescriptions table
def create_prescriptions_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        medicine_id INTEGER,
        dosage TEXT,
        frequency TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )""")
    conn.commit()


create_prescriptions_table()  # Call the function to create the table
