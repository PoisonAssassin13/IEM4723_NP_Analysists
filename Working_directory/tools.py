import streamlit as st
import pymysql

import csv
import time

#This file contains the functions needed for seed and querying the database, imported into seed.py and app.py

#Might need to change the port number after testing.
MYSQL = dict(host="mysql", port=3306, user="root",
             password="CR&LK", database="NP_Analysis")


def get_mysql():
    return pymysql.connect(host="mysql", port=3306, user="root",
                           password="CR&LK", database="NP_Analysis",
                           connect_timeout=5, read_timeout=10)

def wait_for_mysql(timeout=90):
    """Block until MySQL accepts a connection, or give up after timeout seconds."""
    started = time.time()
    while True:
        try:
            pymysql.connect(**MYSQL).close()
            return
        except pymysql.err.OperationalError:
            if time.time() - started > timeout:
                raise
            time.sleep(1)

def already_seeded():
    conn = pymysql.connect(**MYSQL)
    cur = conn.cursor()
    cur.execute("SHOW TABLES LIKE 'parks'")
    if cur.fetchone() is None:
        conn.close()
        return False
    cur.execute("SELECT COUNT(*) FROM parks")
    rows = cur.fetchone()[0]
    conn.close()
    if rows > 0:
        return True
    else:
        return False

#Queries
#-------
#Grab all park codes and their corresponding names and state IDs
def park_desc_query():
    conn = get_mysql()
    cursor = conn.cursor()
    cursor.execute("""SELECT park_code, park_name, state_id
                      FROM parks""")
    
    parks = []
    for row in cursor.fetchall():
        parks.append({
            "park_code": row[0],
            "park_name": row[1],
            "state_id": row[2]
        })
    
    cursor.close()
    conn.close()
    return parks

#Doesn't query the database, just returns a hardcoded dictionary of statistic descriptions
def statistic_desc():
    return {
        "BC":"Backcountry Overnight Stays",
        "CCG":"Concessionaire Operated Campground Overnight Stays",
        "CL":"Concessionaire Operated Lodging Overnight Stays",
        "MISC":"Miscellaneous Overnight Stays",
        "NROS":"Non-Recreation Overnight Stays",
        "TH":"Visitor Hours (Recreational AND Non-Recreational)",
        "TNRV":"Nonrecreational visits",
        "TNRVH":"Nonrecreational visitor hours",
        "TOS":"Total Overnight Stays",
        "TRV":"Recreational Visits",
        "TRVH":"Recreational Visitor Hours",
        "TRVS":"NPS Operated Campground Overnight Stays",
        "TT":"NPS Operated Campground Tent Overnight Stays",
        "TTRV":"NPS Operated Campground Overnight Stays (Tent + RV)",
        "TV":"Total Visits (Recreational AND Non-Recreational)"
    }

#Doesn't query the database, just returns a hardcoded dictionary of segment descriptions
def segments_desc():
    return {
        "Backcountry":"local or non-local visitors who camp in the backcountry in the park",
        "Boat":"local or non-local visitors who visit the park on a small cruise ship or adventure tour boat",
        "BoatIN":"local or non-local visitors who stay overnight on a boat (at anchor or at dock) within the park",
        "CampIN":"local or non-local visitors who stay at campgrounds or at backcountry camping sites within the park.",
        "CampOut":"local or non-local visitors who camp outside of the park, including developed campsites and dispersed camping on public land.",
        "Cruise":"local or non-local visitors who visit the park on a large cruise ship",
        "HouseBoat":"local or non-local visitors who stay overnight in a houseboat in the park",
        "LocalDay":"local visitors who visit the park for a single day and return home.",
        "LodgeIN":"local or non-local visitors who stay at a lodge or motel within the park.",
        "LodgeOut":"local or non-local visitors who stay at motels, hotels, bed and breakfasts, glamping sites, or other specialty lodging located outside of the park.",
        "NLDay":"non-local visitors who visit the park for a single day and leave the area or return home.",
        "Other":"visitors who stay overnight in the local region but do not have any lodging expenses. This segment includes visitors staying in private homes, with friends or relatives, or in other unpaid lodging.",
        "Tour":"local or non-local visitors who visit the park on a cruise or as part of an inclusive package vacation that includes lodging"
    }

#
def 