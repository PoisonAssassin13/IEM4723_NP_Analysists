import pymysql
import streamlit as st
import pandas as pd
import plotly.express as px

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
st.sidebar.caption("Select a query to run.")

#Defining the query options section
st.sidebar.subheader("Select a Query")
query_option_lists = ["Parks Table", "Segment Shares Table", "Spending Profiles Table", "Trip Characteristics Table", 
                      "Visitor Use Stat Table", "Total Spent"]
query_option = st.sidebar.menu_button("Query Options", options=query_option_lists, key="query_option")

#Defining the filter options section
st.sidebar.subheader("Filter Options")
st.sidebar.caption("Select filters to apply before the query.")

#if the ParkNames list is not already in session state, query the parks table and create a list of park codes and names to use as filter options
if 'ParkNames' not in st.session_state:
    parks = park_desc_query()
    parknames = []
    for park in parks:
        parknames.append(f"{park['park_code']}:{park['park_name']}")
    st.session_state.ParkNames = parknames

#Defining the park code filter option, allowing users to select one or more parks to filter the query results, applied BEFORE the query is run. If no parks are selected, all parks will be included in the query results.
park_code_filter = st.sidebar.multiselect("Select Park(s)", options=st.session_state.ParkNames, key="park_code_filter")

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

st.sidebar.caption("Select filters to apply after the filter.")

#TO FIX, add the lists of valid queries for each filter option below
#List of queries that can be filtered by month
month_filer_queries = ["Visitor Use Stat Table", "Segment Shares Table"]
#If the selected query option can be filtered by month, display the month filter option (Month filters applied after the query not before)
if query_option in month_filer_queries:
    month_filter = st.sidebar.selectbox("Select Month", options=[1,2,3,4,5,6,7,8,9,10,11,12], key="month_filter")

#List of queries that can be filtered by segment
segment_filter_queries = ["Segment Shares Table", "Trip Characteristics Table", "Spending Profiles Table", "Total Spent"]
#If the selected query option can be filtered by segment, display the segment filter option (Segment filters applied after the query not before)
if query_option in segment_filter_queries:
    segment_filter = st.sidebar.segmented_control("Select Segment(s)", options=list(segments_desc().keys()), key="segment_filter")

#List of queries that can be filtered by use statistics
use_statistics_queries = ["Visitor Use Stat Table"]
if query_option in use_statistics_queries:
    use_statistics_filter = st.sidebar.segmented_control("Select Use Statistic(s)", options=list(statistic_desc().keys()))

#List of queries that can be filtered by trip characteristics
trip_characteristics_queries = ["Trip Characteristics Table"]
if query_option in trip_characteristics_queries:
    trip_characteristics_filter = st.sidebar.segmented_control("Select Trip Characteristic(s)", options=list(trip_characteristic_desc().keys()))

#List of queries that can be filtered by spending_group
#TO FIX, add the filter for this
spending_group_queries = ["Segment Shares Table", "Total Spent"]
if query_option in spending_group_queries:
    spending_group_filter = st.sidebar.segmented_control("Select Spending Group(s)", options=['']) #TO FIX, add in the options of valid filter options

#List of queries that can be filtered by state
state_queries = ["Parks Table"]
if query_option in state_queries:
    states = list(query_result['state_id'].unique())
    state_filter = st.sidebar.multiselect("Select State(s)", options=states)

#Define this next session as picking what graph to show
st.sidebar.subheader("Graph Selection")
st.sidebar.caption("Select what graphical representation you want from the selected query option.")

#List what graphic displays can be represented for each given query option
graph_display_options = {"Parks Table":["Number of Parks by State"], 
                         "Segment Shares Table":["Segment Split Ratio"], 
                         "Spending Profiles Table":["Spending PPPDN Line Chart", "Spending PPPDN Bar Chart"], 
                         "Trip Characteristics Table":["Characteristic Bar Chart: One Park", "Characteristic Bar Chart: One Segment"], 
                         "Visitor Use Stat Table":["Stat Line Chart by Month: One Park", "Stat Line Chart by Month: One Stat", "Stat Average Bar Chart"],
                         "Total Spent":[""]}

graph_display_select = st.sidebar.menu_button("Graphs", options = graph_display_options[query_option], key="graph_display_select")

if graph_display_select == "Number of Parks by State":
    state_count_filter_min = st.slider("Minimum Number of States", 1, 100, 1, 1, key="state_count_filter_min")
    state_count_filter_max = st.slider("Maximum Number of States", 1, 100, 100, 1, key="state_count_filter_max")


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
tab_graph, tab_dataframe = st.tabs(["Graph", "Table"])

#----------------------
#Defining the tab_dataframe
#----------------------

#TO FIX, apply the filters in a filtered_query_result and display that either as a new tab or below this one mentioned here, possibly both as expanders
#Setting an expander showing the unfiltered data
with tab_dataframe.expander("Unfiltered Data"):
    st.dataframe(query_result, width="stretch", hide_index=True)

#Creating the filtered_query_result
filtered_query_result = pd.DataFrame(query_result)
#Filtering rows by months in the filter
if query_option in month_filer_queries:
    filtered_query_result = filtered_query_result.query('month in @month_filter')

#Filtering rows by segments in the filter
if query_option in segment_filter_queries:
    filtered_query_result = filtered_query_result.query('segment in @segment_filter')

#Filtering columns by the use_statistics in the filter
if query_option in use_statistics_queries:
    filtered_query_result = filtered_query_result.loc[:, filtered_query_result.columns.isin(use_statistics_filter)]

#Filtering columns by the trip_characteristics in the filter
if query_option in trip_characteristics_queries:
    filtered_query_result = filtered_query_result.loc[:, filtered_query_result.columns.isin(trip_characteristics_filter)]

if query_option in state_queries:
    filtered_query_result = filtered_query_result.query('state_id in @state_filter')

#Setting an expander showing the filtered data
with tab_dataframe.expander("Filtered Data"):
    st.dataframe(filtered_query_result, width="stretch", hide_index=True)

#----------------------
#Defining the tab_graph
#----------------------

#TO FIX, add in the wondeful graphs using filtered_query_result
with tab_graph:
    if graph_display_select == "Number of Parks by State":
        #
        try:
            state_count = dict()
            for state in states:
                state_count[state] = (filtered_query_result['state_id' == state]).sum()

            state_count = pd.DataFrame(list(state_count.items()), columns=["state", "count"])
            state_count = state_count.dropna()
            state_count = state_count[(state_count['count'] >= state_count_filter_min) & (state_count['count'] <= state_count_filter_max)]

            figure = px.bar(state_count,x="state", y="count", title="Number of Parks by State")
            st.plotly_chart(figure, width='stretch')
            
        except:
            st.subtitle("Failed to load graph")


    elif graph_display_select == "Segment Split Ratio":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Spending PPPDN Line Chart":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")


    elif graph_display_select == "Spending PPPDN Bar Chart":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Characteristic Bar Chart: One Park":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Characteristic Bar Chart: One Segment":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Stat Line Chart by Month: One Park":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Stat Line Chart by Month: One Stat":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    elif graph_display_select == "Stat Average Bar Chart":
        #
        try:
            st
        except:
            st.subtitle("Failed to load graph")

    #Error warning if there is somehow not a valid selected graph
    else:
        st.header("No valid graph selected, please try again.")

    #Just in case you want to add more, copy paste
    #elif graph_display_select == ""
    #    try:
    #        st
    #    except:
    #        st.subtitle("Failed to load graph")
