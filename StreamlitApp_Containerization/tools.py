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

def trip_characteristic_desc():
    return {
        "entry_rate":"The number of days a visitor enters or re-enters the park on a trip. (Adjusted to remove counts of multiple entries within a signle day)",
        "length_of_stay_attributable":"Average length of stay in the park and nearby area that is attributed to NPS visitation based on visitor trip purpose.",
        "length_of_stay_local_area":"Average length of stay in the park and nearby area surrounding the park.",
        "party_size":"Average number of people in a personal group - including family and friends who are traveling together and sharing expenditures.",
        "percent_nonlocal":"Percent of visitors who live outside of hte local area surrounding the park.",
        "trip_purpose_equal":"Percent of visitors for whome visiting the NPS site was one of several equally important destinations in the local area.",
        "trip_purpose_incidental":"Percent of visitors for whom visiting the NPS site was an incidental or spur-of-the-moment stop during their time in the local area.",
        "trip_purpose_primary":"Percent of visitors for whome visiting the NPS site was their primary or soule purpose for their trip to the local area."
    }

#For a specified park code, return the segment split and month associated with that park code.
def segment_split(park_codes):
    conn = get_mysql()
    cursor = conn.cursor()
    
    placeholders = ', '.join(['%s'] * len(park_codes))
    cursor.execute(f"""SELECT park_code, month, segment_split
                      FROM segment_shares_monthly
                      WHERE park_code IN ({placeholders})""", (park_codes))
        
    segment_split = []
    for row in cursor.fetchall():
        segment_split.append({
            "park_code": row[0],
            "month": row[1],
            "segment_split": row[2]
        })
        
        cursor.close()
        conn.close()
        return segment_split

#For getting the spending profile and spending_pppdn for a specified park code, listing associated segments and spending categories.
def spending_profile(park_codes):
    conn = get_mysql()
    cursor = conn.cursor()
    
    placeholders = ', '.join(['%s'] * len(park_codes))
    cursor.execute(f"""SELECT park_code, segment, spending_group, spending_pppdn
                      FROM spending_profiles
                      WHERE park_code IN ({placeholders})""", (park_codes))
        
    spending_profile = []
    for row in cursor.fetchall():
        spending_profile.append({
            "park_code": row[0],
            "segment": row[1],
            "spending_group": row[2],
            "spending_pppdn": row[3]
        })
        
        cursor.close()
        conn.close()
        return spending_profile

#Get trip_characteristics for a specified park code, listing associated stats and segments.
def trip_characteristics(park_codes):
    conn = get_mysql()
    cursor = conn.cursor()
    
    placeholders = ', '.join(['%s'] * len(park_codes))
    cursor.execute(f"""SELECT park_code, segment, entry_rate, length_of_stay_attributable, length_of_stay_local_area, party_size, percent_nonlocal, trip_purpose_equal, trip_purpose_incidental, trip_purpose_primary
                      FROM trip_characteristics
                      WHERE park_code IN ({placeholders})""", (park_codes))
        
    trip_characteristics = []
    for row in cursor.fetchall():
        trip_characteristics.append({
            "park_code": row[0],
            "segment": row[1],
            "entry_rate": row[2],
            "length_of_stay_attributable": row[3],
            "length_of_stay_local_area": row[4],
            "party_size": row[5],
            "percent_nonlocal": row[6],
            "trip_purpose_equal": row[7],
            "trip_purpose_incidental": row[8],
            "trip_purpose_primary": row[9]
        })
        
        cursor.close()
        conn.close()
        return trip_characteristics

#Grab the visitor use stats table for a specified park code(s) and return associated stats and months
def visitor_use_stats(park_codes):
    conn = get_mysql()
    cursor = conn.cursor()

    placeholders = ', '.join(['%s'] * len(park_codes))
    cursor.execute(f"""SELECT park_code, month, BC, CCG, CL, MISC, NROS, TH, TNRV, TNRVH, TOS, TRV, TRVH, TRVS, TT, TTRV, TV
                      FROM visitor_use_stats
                      WHERE park_code IN ({placeholders})""", (park_codes))

    visitor_use_stats = []
    for row in cursor.fetchall():
        visitor_use_stats.append({
            "park_code": row[0],
            "month": row[1],
            "BC": row[2],
            "CCG": row[3],
            "CL": row[4],
            "MISC": row[5],
            "NROS": row[6],
            "TH": row[7],
            "TNRV": row[8],
            "TNRVH": row[9],
            "TOS": row[10],
            "TRV": row[11],
            "TRVH": row[12],
            "TRVS": row[13],
            "TT": row[14],
            "TTRV": row[15],
            "TV": row[16]
        })
        
        cursor.close()
        conn.close()
        return visitor_use_stats

#
def total_spent(park_codes):
    conn = get_mysql()
    cursor = conn.cursor()

    placeholders = ', '.join(['%s'] * len(park_codes))
    cursor.execute(f"""SELECT sp.park_code, sp.segment, sp.spending_group, sp.spending_pppdn, vus.TV, tc.length_of_stay_local_area
                      FROM spending_profiles sp, visitor_use_stats vus, trip_characteristics tc
                      WHERE sp.park_code = vus.park_code
                      AND sp.park_code = tc.park_code
                      AND park_code IN ({placeholders})""", (park_codes))

    total_spent = []
    for row in cursor.fetchall():
        total_spent.append({
            "park_code": row[0],
            "segment": row[1],
            "spending_group": row[2],
            "average_spent_per_party_daily": row[3],
            "TV": row[4],
            "length_of_stay_local_area": row[5],
            "total_spent": row[3] * row[4] * row[5]
        })
        
        cursor.close()
        conn.close()
        return total_spent