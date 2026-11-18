import pymysql
import csv

from tools import get_mysql, already_seeded

conn = get_mysql()
cursor = conn.cursor()

def run(input, params = None):
    for statement in input.strip().split(";"):
        if statement.strip():
            cursor.execute(statement)
    conn.commit()
    print("Statement has been executed")

def insert_csv(table, path):
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    statement = f"""INSERT INTO {table} ({', '.join(rows[0].keys())})
    VALUES ({', '.join(['%s'] * len(rows[0]))});"""

    for row in rows:
        cursor.execute(statement, tuple(row.values()))

    conn.commit()

    print(f"Loaded {len(rows)} into {table}.")

#Table strings
ct_parks = """
CREATE TABLE parks (
    park_code CHAR(4) PRIMARY KEY,
    park_name VARCHAR(100),
    state_id CHAR(2)
);
"""

ct_visitor_use_stats = """
CREATE TABLE visitor_use_stats (
    park_code CHAR(4) PRIMARY KEY,
    month INT PRIMARY KEY,
    BC INT,
    CCG INT,
    CL INT,
    MISC INT,
    NROS INT,
    TH INT,
    TNRV INT,
    TNRVH INT,
    TOS INT,
    TRV INT,
    TRVH INT,
    TRVS INT,
    TT INT,
    TTRV INT,
    TV INT,
    FOREIGN KEY (park_code) REFERENCES parks (park_code)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);
"""

ct_segment_shares_monthly = """
CREATE TABLE segment_shares_monthly (
    park_code CHAR(4) PRIMARY KEY,
    month INT PRIMARY KEY,
    segment VARCHAR(20) PRIMARY KEY,
    segment_split DECIMAL(5,4),
    FOREIGN KEY (park_code) REFERENCES parks (park_code)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);
"""

ct_spending_profiles = """
CREATE TABLE spending_profiles (
    park_code CHAR(4) PRIMARY KEY,
    segment VARCHAR(20) PRIMARY KEY,
    spending_category VARCHAR(100) PRIMARY KEY,
    spending_group VARCHAR(100),
    reporting_group VARCHAR(100),
    spending_pppdn DECIMAL(10,2),
    FOREIGN KEY (park_code) REFERENCES parks (park_code)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);
"""

ct_trip_characteristics = """
CREATE TABLE trip_characteristics (
    park_code CHAR(4) PRIMARY KEY,
    segment VARCHAR(20) PRIMARY KEY,
    entry_rate DECIMAL(5,2),
    length_of_stay_attributable DECIMAL(5,2),
    length_of_stay_local_area DECIMAL(5,2),
    party_size DECIMAL(12,11),
    percent_nonlocal DECIMAL(12,11),
    trip_purpose_equal DECIMAL(12,11),
    trip_purpose_incidental DECIMAL(12,11),
    trip_purpose_primary DECIMAL(12,11),
    FOREIGN KEY (park_code) REFERENCES parks (park_code)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);
"""

#Seed the database if it hasn't been seeded yet
#UPDATE THE CSV FILE PATHS BELOW TO MATCH THEIR REAL LOCATIONS
if not already_seeded():
    run(ct_parks)
    run(ct_visitor_use_stats)
    run(ct_segment_shares_monthly)
    run(ct_spending_profiles)
    run(ct_trip_characteristics)

    insert_csv("parks", "parks.csv")
    insert_csv("visitor_use_stats", "visitor_use_stats.csv")
    insert_csv("segment_shares_monthly", "segment_shares_monthly.csv")
    insert_csv("spending_profiles", "spending_profiles.csv")
    insert_csv("trip_characteristics", "trip_characteristics.csv")

cursor.close()
conn.close() 