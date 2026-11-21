import pymysql
import streamlit as st

#Import query functions and get_mysql function from tools.py
from tools import get_mysql, park_desc_query, segments_desc, segment_split, trip_characteristics, spending_profile, visitor_use_stats, statistic_desc
from tools import trip_characteristic_desc

#Set title, config, and layout for the Streamlit dashboard
st.title("National Parks Database Explorer Dashboard")
st.set_page_config(page_title="National Parks Database Explorer", layout="wide")

#---------------------
#SIDE BAR CONSTRUCTION
#---------------------

#Sidebar title
st.sidebar.title("Query Options")

#Defining the query options section
st.sidebar.subheader("Select a Query")
query_option_lists = ["Parks Table", "Segment Shares Table", "Spending Profiles Table", "Trip Characteristics Table", 
                      "Visitor Use Stat Table", ""]
query_option = st.sidebar.menu_button("Query Options", options=query_option_lists, key="query_option")

#Defining the filter options section
st.sidebar.subheader("Filter Options")

#if the ParkNames list is not already in session state, query the parks table and create a list of park codes and names to use as filter options
if 'ParkNames' not in st.session_state:
    parks = park_desc_query()
    parknames = []
    for park in parks:
        parknames.append(f"{park['park_code']}:{park['park_name']}")
    st.session_state.ParkNames = parknames

#Defining the park code filter option, allowing users to select one or more parks to filter the query results, applied BEFORE the query is run. If no parks are selected, all parks will be included in the query results.
park_code_filter = st.sidebar.multiselect("Select Park(s)", options=st.session_state.ParkNames, key="park_code_filter")

#List of queries that can be filtered by month
month_filer_queries = []
#If the selected query option can be filtered by month, display the month filter option (Month filters applied after the query not before)
if query_option in month_filer_queries:
    month_filter = st.sidebar.selectbox("Select Month", options=[1,2,3,4,5,6,7,8,9,10,11,12], key="month_filter")

#List of queries that can be filtered by segment
segment_filter_queries = []
#If the selected query option can be filtered by segment, display the segment filter option (Segment filters applied after the query not before)
if query_option in segment_filter_queries:
    segment_filter = st.sidebar.segmented_control("Select Segment(s)", options=list(segments_desc().keys()), key="segment_filter")


#List of queries that can be filtered by use statistics
use_statistics_queries = []
if query_option in use_statistics_queries:
    use_statistics_filter = st.sidebar.segmented_control("Select Use Statistic(s)", options=list(statistic_desc().keys()))

#List of queries that can be filtered by trip characteristics
trip_characteristics_queries = []
if query_option in trip_characteristics_queries:
    trip_characteristics_filter = st.sidebar.segmented_control("Select Trip Characteristic(s)", options=list(trip_characteristic_desc().keys()))


#Don't run queries unless the user clicks the "Run Selected Query" button
querybutton_clicked = st.sidebar.button("Run Selected Query", key = "querybutton")

#Run the correct query function 
if querybutton_clicked:
    if query_option == "Parks Table":
        with st.spinner("Running query..."):
            query_result = park_desc_query(park_code_filter)
            st.success("Parks Table query completed successfully!")

    elif query_option == "Segment Shares Table":
        with st.spinner("Running query..."):
            query_result = segment_split(park_code_filter)
            st.success("Segment Shares Table query completed successfully!")

    elif query_option == "Spending Profiles Table":
        with st.spinner("Running query..."):
            query_result = spending_profile(park_code_filter)
            st.success("Spending Profiles Table query completed successfully!")

    elif query_option == "Trip Characteristics Table":
        with st.spinner("Running query..."):
            query_result = trip_characteristics(park_code_filter)
            st.success("Trip Characteristics Table query completed successfully!")

    elif query_option == "Visitor Use Stat Table":
        with st.spinner("Running query..."):
            query_result = visitor_use_stats(park_code_filter)
            st.success("Visitor Use Stats Table query completed successfully!")

    #Save the query result to the session_state
    st.session_state.query_result = query_result 

#If the button is not clicked try to grab the query_result from the session state
else:
    if "query_result" in st.session_state:
        query_result = st.session_state.query_result


#Define this next session as picking what graph to show
st.sidebar.subheader("Graph Selection")

#List what graphic displays can be represented for each given query option
graph_display_options = {"Parks Table":[], "Segment Shares Table":[], 
                         "Spending Profiles Table":[], "Trip Characteristics Table":[], 
                         "Visitor Use Stat Table":[]}

graph_display_select = st.sidebar.menu_button("Graphs", options = graph_display_options[query_option], key="graph_display_select")

#---------------------------
#MAIN DASHBOARD CONSTRUCTION
#---------------------------

#If there is no query result there is nothing to show, so show nothing.
if "query_result" not in st.session_state:
    st.warning("Please select and run a query.")
    st.stop("")

#State what query results are currently being shown
st.caption(f"Showing {query_option} query results.")

#Defining the tabs that will contain the required information
graph_display, raw_data_table = st.tabs(["Graph", "Table"])